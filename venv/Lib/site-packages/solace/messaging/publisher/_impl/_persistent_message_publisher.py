# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module contains the implementation class and methods for the PersistentMessagePublisher"""

# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-ancestors,protected-access
# pylint: disable=missing-function-docstring, unused-variable,no-else-break,no-else-return,no-else-continue
# pylint: disable=no-else-raise,broad-except,import-outside-toplevel

import itertools
import logging
import queue
import threading
import time
import weakref
from typing import Union, Any, Dict

from solace.messaging.config._sol_constants import SOLCLIENT_DELIVERY_MODE_PERSISTENT
from solace.messaging.config._solace_message_constants import VALUE_CANNOT_BE_NEGATIVE, \
    UNABLE_TO_SET_LISTENER, PUBLISH_TIME_OUT, UNCLEANED_TERMINATION_EXCEPTION_MESSAGE_PUBLISHER, \
    UNPUBLISHED_MESSAGE_COUNT, UNPUBLISHED_PUBLISH_RECEIPT_COUNT
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, PubSubTimeoutError, \
    IllegalArgumentError, IncompleteMessageDeliveryError, IllegalStateError
from solace.messaging.publisher._impl._message_publisher import _MessagePublisher, _MessagePublisherState, \
    _CommonSendTask, _MessagePublisherUnpublishedState
from solace.messaging.publisher._impl._publisher_utilities import validate_topic_type, _PublisherUtilities
from solace.messaging.publisher._impl._outbound_message import _OutboundMessage
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.publisher.persistent_message_publisher import PersistentMessagePublisher \
    , MessagePublishReceiptListener, PublishReceipt
from solace.messaging.resources.topic import Topic
from solace.messaging.utils._solace_utilities import is_type_matches, convert_ms_to_seconds, \
    _PubSubPlusQueue, QueueShutdown, _ThreadingUtil, executor_shutdown

logger = logging.getLogger('solace.messaging.publisher')

class _PersistentMessagePublisherUnpublishedState(_MessagePublisherUnpublishedState):
    def __init__(self):
        super().__init__()
        self.remaining_correlation = 0
        self.pending_pub_receipts = []
        self.pending_await_acks = []
        self.unacked_messages = 0
    @property
    def receipt_count(self) -> int:
        # the receipt count in the count of publish receipts that did not arrive
        return self.unacked_messages + self.remaining_correlation - len(self.pending_pub_receipts)

class _DeliveryDispatcher:
    def __init__(self, upper_bound: int = 3):
        self._upper_bound = upper_bound
        self._executor = None
        self._submit_count = 0

    def start(self):
        if self._executor is None:
            logger.debug('Starting delivery dispatcher')
            self._executor = _ThreadingUtil.create_serialized_executor('DeliveryDispatcher')

    def dispatch_delivery(self, handler, context=None, force: bool = False):
        self._submit_count += 1
        # logger.warning('Delivery dispatcher dispatch_delivery with submit count[%s]', self._submit_count)
        executor = self._executor
        if executor and (force or self._submit_count <= self._upper_bound):
            def _dispatch_handler():
                try:
                    handler(context)
                except Exception as error:
                    import traceback
                    logger.error('Error on Delivery dispatcher dispatch_delivery with submit count[%s], error: [%s], '
                                 'tb: %s',
                                 self._submit_count,
                                 str(error),
                                 traceback.format_exc())

                    raise
                finally:
                    self._submit_count -= 1

            try:
                return executor.submit(_dispatch_handler)
            except Exception as ex_error:
                # on rare occurrences of unexpected shutdown executor can be shutdown
                # without the publisher unregistering for events
                # only occurs when the application receives an unexpected error
                # and all api object are being cleaned up with finalizers and GC
                # log any failure at debug
                logger.debug('Error on executor submit: [%s]', str(ex_error))
                # correct submit count to prevent multiple errors from blocking
                # new submit tasks
                self._submit_count -= 1
                # leave to default return of None

        else:
            self._submit_count -= 1
        return None

    def shutdown(self, wait: bool = True):
        executor = self._executor

        if executor:
            executor.shutdown(wait=wait)
            self._executor = None


class _PersistentSendTask(_CommonSendTask):
    def get_publishable_for_send(self) -> 'TopicPublishable':
        element: tuple = self._publisher.publishable_buffer.peek()
        publishable = None if element is None else element[0]
        correlation_tag = None if element is None else element[1]
        if correlation_tag and publishable:
            self._publisher.add_correlation(publishable, correlation_tag)
        return publishable


def publisher_cleanup(delivery_dispatcher, executor):
    executor_shutdown(executor)
    if delivery_dispatcher:
        delivery_dispatcher.shutdown(wait=False)


class _PersistentMessagePublisher(_MessagePublisher, PersistentMessagePublisher) \
        :  # pylint: disable=too-many-instance-attributes, too-many-ancestors

    # implementation class for persistent message publisher
    def __init__(self, builder):
        super().__init__(builder)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('[%s] initialized', type(self).__name__)
        # create unique puack id for publisher
        self._pub_id = _PublisherUtilities.create_publisher_id(self)
        # id(self).to_bytes(8, byteorder='big')
        # init messaging gen, note this is only unique to the publisher
        # this uses a implementation detail of cpython and Pypy for thread safety
        # this should be revisited if other python implementation must be supported
        self._pub_msg_id_gen = itertools.count()

        self._persistent_ack_queue = _PubSubPlusQueue()

        self._persistent_await_ack_queue = _PubSubPlusQueue()

        self._publish_receipt_listener: 'MessagePublishReceiptListener' = None

        self._delivery_dispatcher = _DeliveryDispatcher()
        self._correlation = {}
        self._publish_await_mutex = threading.Lock()
        self._finalizer = weakref.finalize(self, publisher_cleanup, self._delivery_dispatcher, self._executor)

    def _next_msg_id(self) -> int:
        # used built-in GIL lock for thread safe increment and return
        return next(self._pub_msg_id_gen)

    def set_message_publish_receipt_listener(self, listener: 'MessagePublishReceiptListener'):
        # Method for setting the message publish listener"""
        is_type_matches(listener, MessagePublishReceiptListener, logger=logger)
        if self._state in [_MessagePublisherState.STARTED]:
            self._publish_receipt_listener = listener
            self._delivery_dispatcher.start()
            if self._persistent_ack_queue.qsize() > 0:
                self._delivery_dispatcher.dispatch_delivery(self._on_delivery_task)
        else:
            error_message = f'{UNABLE_TO_SET_LISTENER}. Message Publisher is NOT started/ready'
            self.adapter.warning(error_message)
            raise IllegalStateError(error_message)

    def publish(self, message: Union[bytearray, str, dict, list, tuple, OutboundMessage], destination: Topic,
                user_context: Any = None,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple,
                                                               bytearray]] = None):
        # Sends message to the given destination
        validate_topic_type(destination=destination, logger=logger)
        _PublisherUtilities.validate_payload_type(message)
        # if additional_message_properties:
        #     is_none_or_empty_exists(additional_message_properties,
        #                             error_message=INVALID_ADDITIONAL_PROPS, logger=logger)
        # verify publisher can publish
        self._check_message_publish(message, destination)
        # create correlation state iff there is a receipt listener
        # persistent messages published without can not receive publish receipts
        if self._publish_receipt_listener is not None:
            # uniquely identify this message for publish
            msg_id = self._next_msg_id()
            # create correlation tag to map ack events bad to this publisher for a specific message
            correlation_tag = _PublisherUtilities.create_message_correlation_tag(self._pub_id, msg_id=msg_id)
            # add user_context to correlation mapping
            self._correlation[correlation_tag] = (None, user_context)
            if self._solace_publisher.correlation_manager.register_correlation_tag(correlation_tag) is False:
                self.adapter.error(f'Failed to add reference for correlation tag [{correlation_tag}]')
        else:
            # prevent correlation mapping on acknowledgement handler events
            correlation_tag = None
        # publish message on internal solace publisher
        self._message_publish(message, destination, additional_message_properties, correlation_tag=correlation_tag)

    def publish_await_acknowledgement(self, message: Union[bytearray, str, dict, list, tuple, OutboundMessage],
                                      destination: Topic, time_out: int = None,
                                      additional_message_properties: Dict[str, Union[str, int, float, bool, dict,
                                                                                     list, tuple, bytearray]] = None):
        # Sends OutboundMessage to the given destination, blocking until delivery acknowledgement is received or timeout
        # occurs
        #
        # :py:class:`solace.messaging.builder.direct_message_publisher_builder.DirectMessagePublisherBuilder`
        #  can be used to create the OutboundMessage instance.  Alternatively, a bytearray or string payload may be
        #  passed to publish() and the API will create a py:class:`solace.messaging.core.message.Message` to send.
        #
        # Args:
        #     message ():   py:class:`solace.messaging.core.message.Message` or payload to publish
        #     destination (): Destination to add to the message
        #     time_out (:obj:`int`, optional):  max time in ms to wait for the message acknowledgement
        #     additional_message_properties (Dict[str, Union[str, int, bytearray]]):additional properties,
        #     to customize a particular message, each key can be customer provided, or it can be a key from a
        #     :py:mod:`solace.messaging.config.solace_properties.message_properties`, The value can be either a string
        #      or an integer or a bytearray
        #
        # Returns:
        #
        # Raises:
        # PubSubTimeoutError:  is thrown after specified timeout when no response received
        # MessageRejectedByBrokerError: when message was rejected from a broker for some reason
        # PublisherOverflowError: when publisher publishes too fast, application may attempt to
        # republish the message.
        # MessageDestinationDoesNotExistError: given message destination does not exist
        # IllegalArgumentError: if the value of timeout is negative or invalid
        validate_topic_type(destination=destination, logger=logger)
        if time_out is not None and time_out < 0:
            raise IllegalArgumentError(VALUE_CANNOT_BE_NEGATIVE)
        # protect with mutex for thread safe access to target correlation tag
        with self._publish_await_mutex:
            # create await correlation tag
            msg_id = self._next_msg_id()
            correlation_tag = \
                _PublisherUtilities.create_message_correlation_tag(self._pub_id, \
                                                                   pub_type=_PublisherUtilities.AWAIT_TYPE,
                                                                   msg_id=msg_id)
            if self._solace_publisher.correlation_manager.register_correlation_tag(correlation_tag) is False:
                self.adapter.error(f'Failed to add reference for correlation tag [{correlation_tag}]')
            # publish message with correlation tag
            self.message_publish(message, destination, additional_message_properties, correlation_tag=correlation_tag)
            # wait for acknowledgement
            try:
                timeout_in_seconds = convert_ms_to_seconds(time_out) if time_out is not None else None
                start = time.time()
                # get first item for ack await queue
                tag, event, exception = self._persistent_await_ack_queue.get(True, timeout=timeout_in_seconds)
                # since this can be an ack from a previous publish drain await queue
                # until published tag is received from ack
                if timeout_in_seconds is not None:
                    # handle remaining timeout if any left
                    remaining = timeout_in_seconds - (time.time() - start)
                    while tag != correlation_tag and self._is_active and remaining > 0.0:
                        tag, event, exception = self._persistent_await_ack_queue.get(True, timeout=remaining)
                        remaining = timeout_in_seconds - (time.time() - start)
                    if tag != correlation_tag and not remaining > 0.0:
                        exception = PubSubTimeoutError(PUBLISH_TIME_OUT)
                else:
                    # block until ack is received
                    while tag != correlation_tag and self._is_active:
                        tag, event, exception = self._persistent_await_ack_queue.get(True, timeout=None)
                if exception:
                    raise exception
                elif tag != correlation_tag:
                    raise PubSubPlusClientError('Failed to confirm message was published')
            except QueueShutdown as exception:
                raise IllegalStateError('Publisher terminated') from exception
            except queue.Empty as exception:
                raise PubSubTimeoutError(PUBLISH_TIME_OUT) from exception

    def notify_publish_error(self, exception: 'Exception', publishable: 'TopicPublishable', tag: bytes = None):
        def _handle_publishable_exception(pub: 'TopicPublishable'):
            if tag:
                # enqueue publish receipt event
                user_context = None
                if tag in self._correlation:
                    _, user_context = self._correlation[tag]
                # ensure correlation map is complete
                self._correlation[tag] = (pub, user_context)
                # put error event on ack queue
                try:
                    self._persistent_ack_queue.put_nowait((tag, -1, exception))
                except QueueShutdown:
                    return
                if self._publish_receipt_listener:
                    # submit error event dispatch task for enqueue error event
                    self._delivery_dispatcher.dispatch_delivery(self._on_delivery_task)

            else:
                self.adapter.error("Received asynchronous persistent publisher failure without identifiable tag,"
                                   "message destination='%s' exception='%s'",
                                   str(pub.get_destination()), str(exception))

        if not _PublisherUtilities.is_correlation_type(tag, _PublisherUtilities.ASYNC_TYPE):
            # log synchronous failures at info as exceptions should be raised instead of passed to notify
            self.adapter.info(
                "Received synchronous publisher failure, tag='%s' exception='%s'",
                str(tag) if tag else 'None',
                str(exception))
            # exit early
            return
        if publishable:
            _handle_publishable_exception(publishable)
        else:
            # check if there is a publishable in the correlation map
            pub = None
            if tag and tag in self._correlation:
                pub, _ = self._correlation[tag]
                if pub:
                    _handle_publishable_exception(pub)
                else:
                    self.adapter.error(
                        "Received asynchronous publisher failure without publishable message, tag='%s' exception='%s'",
                        str(tag), str(exception))
            else:
                self.adapter.error(
                    "Received asynchronous publisher failure without publishable message, tag='%s' exception='%s'",
                    str(tag), str(exception))

    def add_correlation(self, publishable: 'TopicPublishable', tag: bytes):
        if _PublisherUtilities.is_correlation_type(tag, _PublisherUtilities.ASYNC_TYPE) and \
                self._correlation and tag in self._correlation:
            _, user_context = self._correlation[tag]
            self._correlation[tag] = (publishable, user_context)

    def remove_correlation(self, tag: bytes):
        if _PublisherUtilities.is_correlation_type(tag, _PublisherUtilities.ASYNC_TYPE) and \
                self._correlation and tag in self._correlation:
            self._correlation.pop(tag)
            self._solace_publisher.correlation_manager.unregister_correlation_tag(tag)

    def _create_send_task(self):
        return _PersistentSendTask(self)

    def _cleanup_message_state(self) -> _PersistentMessagePublisherUnpublishedState:
        sup_message_contents = super()._cleanup_message_state()
        unpub_message_contents = _PersistentMessagePublisherUnpublishedState()
        unpub_message_contents.unpublished_messages.extend(sup_message_contents.unpublished_messages)
        if self._publish_receipt_listener:
            # enqueue error notification on dispatch thread instead of event thread
            def _cancel_pending_closure(ctx=None):
                self._on_cancel_pending_publishables_task(unpub_message_contents, context=ctx)
            self._delivery_dispatcher.dispatch_delivery(_cancel_pending_closure, force=True)
        return unpub_message_contents

    def _cleanup_unpublished_state(self, unpub_state: _MessagePublisherUnpublishedState) \
        -> _MessagePublisherUnpublishedState:
        unpub_contents = super()._cleanup_unpublished_state(unpub_state)
        unpub_contents.pending_pub_receipts.extend(self._persistent_ack_queue.drain())
        unpub_contents.pending_await_acks.extend(self._persistent_await_ack_queue.drain())
        unpub_contents.remaining_correlation = len(self._correlation)
        self._correlation.clear()
        return unpub_contents

    def _check_unpublished_state(self, unpub_contents: _MessagePublisherUnpublishedState):
        unpublished_count = len(unpub_contents.unpublished_messages)
        receipt_count = unpub_contents.receipt_count
        if unpublished_count != 0 or receipt_count != 0:
            error_message = f"{UNCLEANED_TERMINATION_EXCEPTION_MESSAGE_PUBLISHER}. " \
                            f"{UNPUBLISHED_MESSAGE_COUNT} [{unpublished_count}]. "
            if receipt_count != 0:
                error_message += f"{UNPUBLISHED_PUBLISH_RECEIPT_COUNT} [{receipt_count}]"
            self.adapter.warning(error_message)
            raise IncompleteMessageDeliveryError(error_message)

    def _wait_pending_tasks(self, timeout: float) -> float:
        # waiting for all pending sends
        remaining = super()._wait_pending_tasks(timeout)

        # wait for all pending acks
        # use correlation map to count pending publishable acknowledgement
        def are_pending_publish_receipts() -> bool:
            return len(self._correlation) != 0

        # The _persistent_ack_queue is only the currently received acknowledgement from the network protocol
        # must add the condition that the correlation map must be empty for all published messages.
        # Additions to the correlation map occur for every publish requested by the application.
        if self._publish_receipt_listener:
            remaining = self._persistent_ack_queue.wait_for_empty(remaining,
                                                                  are_pending_publish_receipts) if remaining > 0 else 0
        return remaining

    def _resource_cleanup(self):
        super()._resource_cleanup()
        self._persistent_await_ack_queue.shutdown()
        self._delivery_dispatcher.shutdown(wait=True)
        self._persistent_ack_queue.shutdown()

    def _register_publisher_events(self):
        super()._register_publisher_events()

        def _on_ack_closure(tag, event, error):
            self._on_ack(tag, event, error)

        self._solace_publisher.ack_emitter.register_acknowledgement_handler(_on_ack_closure, self._pub_id)

    def _unregister_publisher_events(self):
        self._solace_publisher.ack_emitter.unregister_acknowledgement_handler(self._pub_id)
        super()._unregister_publisher_events()

    def _on_cancel_pending_publishables_task(self, unpub_state, context=None): # pylint: disable=unused-argument
        # drain all pending publishable task
        # `context` is reserved for future use to handle event trigger info.
        error = PubSubPlusClientError('Publisher Terminated can not get receipt')
        #handle all in-flight messages, aka all publishables in the correlation table
        tags = list(self._correlation.keys())
        unpub_tags = [t for _, t in unpub_state.unpublished_messages]
        unacked_count = 0
        for tag in tags:
            # enqueue error notification for each publishable
            if tag in unpub_tags:
                continue
            publishable, _ = self._correlation[tag]
            if publishable:
                self.notify_publish_error(error, publishable, tag)
                unacked_count += 1
        unpub_state.unacked_messages = unacked_count
        # handle all buffered messages discarded
        error = PubSubPlusClientError('Publisher Terminated can not publish')
        for publishable, tag in unpub_state.unpublished_messages:
            self.notify_publish_error(error, publishable, tag)
        # maybe in shutdown so dispatcher might not fire again
        # dispatch final delivery for publish receipt errors
        self._on_delivery_task(context=context)


    def _on_ack(self, correlation_tag: bytes, event, error: Exception = None):
        # clean up publisher reference to correlation tag
        if not self._solace_publisher.correlation_manager.unregister_correlation_tag(correlation_tag):
            self.adapter.info(f'Failed to release correlation tag reference for tag [{correlation_tag}]')
        if self._is_active:
            try:
                if _PublisherUtilities.is_correlation_type(correlation_tag, _PublisherUtilities.ASYNC_TYPE):
                    self._persistent_ack_queue.put_nowait((correlation_tag, event, error))
                    if self._publish_receipt_listener:
                        self._delivery_dispatcher.dispatch_delivery(self._on_delivery_task)
                else:
                    self._persistent_await_ack_queue.put_nowait((correlation_tag, event, error))
            except QueueShutdown:
                pass

    def _on_delivery_task(self, context=None): # pylint: disable=unused-argument
        # if there is no listener, there is nothing to do
        # listener may not change from set to None on the fly, by checks in
        # set_message_publish_receipt_listener, so no need to check after entry
        # to this method.
        if self._publish_receipt_listener is None:
            return
        # `context` is reserved for future use to handle event trigger info.
        # verify everything for a delivery is available
        # tag, _, exception = self._persistent_ack_queue.unsafe_peek()
        element: tuple = self._persistent_ack_queue.unsafe_peek()
        # to dispatch a delivery task:
        # the publisher must be active
        # the publisher must have a listener
        # the delivery task must have a tag
        #while self._is_active and tag and listener:
        while element:
            tag = element[0]
            # peek exception as well
            exception = element[2]
            # prepare publish receipt components
            outbound_message, timestamp, user_context = \
                self._prepare_publish_receipt(tag)
            if any([outbound_message, timestamp, user_context]):
                publish_receipt = PublishReceipt(outbound_message,
                                                 exception,
                                                 timestamp,
                                                 exception is None,
                                                 user_context)
                try:
                    self._publish_receipt_listener.on_publish_receipt(publish_receipt)
                except Exception as error:
                    self.adapter.warning("Failed to dispatch. Message handler type: [%s]. "
                                         "Exception: %s",
                                         type(self._publish_receipt_listener),
                                         str(exception))
            else:
                # log the tag, _, exception that was returned from the last call to
                # self._persistent_ack_queue.unsafe_peek()
                if self.adapter.isEnabledFor(logging.DEBUG):
                    self.adapter.debug("In _PersistentMessagePublisher._on_delivery_task(), received tag %s and " \
                                       "exception %s from _persistent_ack_queue.", tag, exception)

            # advance queue as delivery is complete (error or not)
            try:
                tag, _, exception = self._persistent_ack_queue.get_nowait()
            except QueueShutdown:
                break
            # peek the next delivery and keep pushing out deliveries if available
            element: tuple = self._persistent_ack_queue.unsafe_peek()

    def _prepare_publish_receipt(self, correlation_tag: bytes):
        if self._correlation and correlation_tag in self._correlation:
            publishable, user_context = self._correlation.pop(correlation_tag)
            solace_message = publishable.get_message()
            delivery_mode = solace_message.get_delivery_mode()
            outbound_message = _OutboundMessage(solace_message)
            return outbound_message, int(time.time() * 1000), user_context
        else:
            return None, None, None

    @property
    def _delivery_mode(self):
        return SOLCLIENT_DELIVERY_MODE_PERSISTENT
