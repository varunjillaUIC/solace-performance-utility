# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module contains the implementation cass and methods for the DirectMessageReceiver"""
# pylint: disable=too-many-ancestors, too-many-instance-attributes, missing-class-docstring, missing-function-docstring
# pylint: disable=no-else-break,no-else-return,inconsistent-return-statements,protected-access

import concurrent
import ctypes
import logging
import queue
import weakref
import threading
from typing import Union
from abc import ABC

from solace.messaging.builder._impl._message_receiver_builder import DirectMessageReceiverBackPressure
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_WOULD_BLOCK, SOLCLIENT_IN_PROGRESS, \
    SOLCLIENT_INCOMPLETE, MAX_UNSIGNED_SIXTY_FOUR_BIT_INT
from solace.messaging.config._solace_message_constants import DISPATCH_FAILED, RECEIVE_MESSAGE_FROM_BUFFER, \
    UNABLE_TO_SEND_CACHE_REQUEST, RECEIVER_UNAVAILABLE_FOR_CACHE_REQUESTS, \
    DROPPING_CACHE_RESPONSE, CACHE_UNAVAILABLE_ON_RECEIVER_DUE_TO_INTERNAL_ERROR, \
    UNABLE_TO_PROCESS_CACHE_RESPONSE, INVALID_CACHE_REQUEST_ID, CACHE_REQUEST_TIMEOUT, UNABLE_TO_DESTROY_CACHE_SESSION
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, PubSubPlusCoreClientError, \
    PubSubTimeoutError
from solace.messaging.receiver._cache_requester import _SolaceCacheRequester
from solace.messaging.receiver._impl._message_receiver import _MessageReceiverState, \
    _DirectRequestReceiver
from solace.messaging.receiver._impl._receiver_utilities import validate_subscription_type
from solace.messaging.receiver._impl._solcache_utility import _SolCacheEventInfo, \
    _cache_event_callback_func_type, _CacheResponseDispatcher, generate_cancelled_request_tuple, \
    generate_exception_from_cache_event, generate_failed_cache_event
from solace.messaging.receiver.direct_message_receiver import DirectMessageReceiver
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.resources.cached_message_subscription_request import CachedMessageSubscriptionRequest
from solace.messaging.utils.cache_request_outcome import CacheRequestOutcome
from solace.messaging.utils.cache_request_outcome_listener import CacheRequestOutcomeListener
from solace.messaging.utils._send_utils import _SendTask
from solace.messaging.utils._solace_utilities import is_not_negative, convert_ms_to_seconds, is_type_matches, \
    _PubSubPlusQueue, QueueShutdown, _SolaceThread, Holder, _Released, is_value_out_of_range
from solace.messaging.utils.manageable import Metric

logger = logging.getLogger('solace.messaging.receiver')


class _DirectMessageReceiverThread(_SolaceThread):  # pylint: disable=missing-class-docstring
    # Thread used to dispatch received messages on a receiver.

    def __init__(self, owner_info, owner_logger: 'logging.Logger', direct_message_receiver, messaging_service, *args,
                 **kwargs):
        super().__init__(owner_info, owner_logger, *args, **kwargs)
        self._message_receiver = direct_message_receiver
        self._message_receiver_queue = self._message_receiver.receiver_queue
        self._message_handler = None
        self._stop_event = self._message_receiver.stop_event  # we receive this from direct message impl class
        self._messaging_service = messaging_service
        # This boolean is used to notify the direct receiver async receive thread that the receiver has been
        # terminated or is in the process of being terminated. The receiver will update this boolean as a part
        # of handling termination. Having a simple boolean be updated by the receiver is more performant than
        # checking the state of the receiver in the `run()` method, regardless of what means is used since the
        # receiver has multiple states that could towards termination, which means multiple reads vs. a single
        # read. This, however is only a temporary change until the queue improvements can be made. Do not
        # change this unless as a part of the queue improvements.
        self.asked_to_terminate = False

    def _on_join(self):
        self._stop_event.set()
        self._message_receiver_queue.shutdown()

    @property
    def message_handler(self):
        return self._message_handler

    @message_handler.setter
    def message_handler(self, message_handler):
        self._message_handler = message_handler

    def run(self):
        # Start running thread
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] started', type(self).__name__)
        while not self._stop_event.is_set():
            inbound_message = None
            try:
                inbound_message = self._message_receiver_queue.get()
            except QueueShutdown:
                #the queue has shutdown no need to pull from it anymore
                break

            if inbound_message:
                if inbound_message.get_message_discard_notification().has_internal_discard_indication():
                    # Since we are always dealing with one message at a time,
                    # and the discard indication is a boolean, we only need to
                    # increment by one each time, so we can hardcode it here
                    self._message_receiver._int_metrics. \
                        _increment_internal_stat(Metric.INTERNAL_DISCARD_NOTIFICATIONS, 1)
                try:
                    self._message_handler.on_message(inbound_message)
                except Exception as exception:  # pylint: disable=broad-except
                    self.adapter.warning("%s %s", DISPATCH_FAILED, str(exception))
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] exited', type(self).__name__)


class _ReceiverSendTask(_SendTask, ABC):
    def __init__(self, receiver: '_DirectMessageReciever'):
        self._receiver = receiver

    @property
    def receiver(self):
        return self._receiver


class _CacheRequestSendTask(_ReceiverSendTask):
    def __init__(self, receiver: '_DirectMessageReceiver'):
        super().__init__(receiver)


    def on_publishable_sent(self):
        try:
            self._receiver._cache_requester_queue.get_nowait()
        except (queue.Empty, QueueShutdown):
            # If the queue is empty, then this is odd, but this method doesn't really care since it's only
            # purpose is to remove cache requests from the queue. So, in the case of the queue being empty,
            # this method's job is already complete.
            # If the queue is shutdown, then likely the receiver is terminating or is already terminated
            # If any other exception is raised, then something wrong and unexpected happened, and the
            # exception should be passed up to the caller.
            pass

    def on_publishable_send_error(self, error: Exception = None):
        cache_requester = None
        try:
            cache_requester = self._receiver._cache_requester_queue.get_nowait()
        except queue.Empty as exception:
            # If this happens, something went wrong, so we raise
            self._receiver.adapter.error(UNABLE_TO_SEND_CACHE_REQUEST)
            raise PubSubPlusClientError(UNABLE_TO_SEND_CACHE_REQUEST) from exception
        except QueueShutdown:
            # If this happens, we're terminating, so we can just continue
            pass

        if cache_requester:
            # If we have a cache request, generate a cache event from it.
            # The cache event thread will pass the exception given to this method on to the application,
            # and will only use this event to discern what CacheRequestOutcome should be given to the
            # application, so this event only needs to be generally accurate, i.e. the subcode doesn't
            # really matter as long as it's one that doesn't have a special mapping in the cache event thread.
            generated_cache_event = generate_failed_cache_event(cache_requester)
            try:
                # Put the generated event and the error that started it all on the cache event queue.
                # We rely on the cache event thread to process the event and pass it to the application
                # through the completion listener that was already registered.
                self._receiver._cache_response_dispatcher.submit(self._receiver.process_cache_event,
                                                                 generated_cache_event, error)
            except RuntimeError:
                # According to the implementation of the dispatcher in _solace_utilities.py, only
                # RuntimeError should be raised. Any other error is unexpected and the resulting behaviour is
                # undefined, so those erros should not be caught and should be allowed to halt the program, or at
                # least this thread of the program, since it would be a bug.
                # If this happens, there was an error in the dispatcher, so we raise the exception
                self._receiver.adapter.error(UNABLE_TO_SEND_CACHE_REQUEST)
        else:
            self._receiver.adapter.error(UNABLE_TO_SEND_CACHE_REQUEST)

    def get_cache_requester_for_send(self) -> Union['CachedMessageSubscriptionRequest', None]:
        return self._receiver._cache_requester_queue.peek()


class _DirectMessageReceiver(_DirectRequestReceiver, DirectMessageReceiver):
    # class for direct message receiver, it is the base class used to receive direct messages

    def __init__(self, builder: 'DirectMessageReceiverBuilder'):  # pylint: disable=duplicate-code
        super().__init__(builder)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('[%s] initialized', type(self).__name__)
        self._running = False
        self._set_next_discard_indication = False

        self._message_handler = None
        self._int_metrics = self._messaging_service.metrics()
        key = "subscriptions"
        if key in builder.topic_dict:
            subscription = builder.topic_dict[key]
            if isinstance(subscription, str):
                self._topic_dict[subscription] = False  # not applied
            else:
                for topic in subscription:
                    self._topic_dict[topic] = False  # not applied
        self._cache_session_dict = {}
        key = "group_name"
        if key in builder.topic_dict:
            self._group_name = builder.topic_dict[key]
        self._message_receiver_state = _MessageReceiverState.NOT_STARTED
        self.__init_back_pressure(builder)
        self._serial_publisher = self._messaging_service.serial_publisher
        self._cache_requester_dict = {}
        self._cache_response_dispatcher = _CacheResponseDispatcher(self.adapter)
        self._cache_requester_dict_is_empty = threading.Condition(self._mutex)
        self._cache_requester_queue = _PubSubPlusQueue()
        self._event_callback_p = _cache_event_callback_func_type(self._cache_event_callback_routine)
        self._cache_request_send_task = _CacheRequestSendTask(self)
        self._message_receiver_thread_holder = Holder()
        self._listener_service_finalizer = weakref.finalize(self,
                                                            direct_receiver_thread_cleanup,
                                                            self._message_receiver_thread_holder)
        self._cache_response_dispatcher_finalizer = weakref.finalize(self,
                                                            cache_response_dispatcher_cleanup,
                                                            self._cache_response_dispatcher)


    def _handle_events_on_terminate(self):
        super()._handle_events_on_terminate()
        if self._message_receiver_thread is not None:
            self._message_receiver_thread.asked_to_terminate = True

    def __init_back_pressure(self, builder: 'DirectMessageReceiverBuilder'):
        # This method presumes that the buffer type and capacity have previously been validated.
        if builder.receiver_back_pressure_type != DirectMessageReceiverBackPressure.Elastic:
            if builder.receiver_back_pressure_type == DirectMessageReceiverBackPressure.DropOldest:
                self._force = True
                self._block = True
                self._message_receiver_queue = _PubSubPlusQueue(maxsize=builder._buffer_capacity)

            elif builder.receiver_back_pressure_type == DirectMessageReceiverBackPressure.DropLatest:
                self._force = False
                self._block = False
                self._message_receiver_queue = _PubSubPlusQueue(maxsize=builder._buffer_capacity)

            def on_buffer_overflow(discarded):
                if discarded and isinstance(discarded, InboundMessage):
                    peeked_message = self._message_receiver_queue.unsafe_peek()
                    if peeked_message:
                        peeked_message.get_message_discard_notification().set_internal_discard_indication()
                    # We do this for every message that is received if the queue is full, so we only need to
                    # increment the metric by one each time. Since we increment by the same amount every time,
                    # we can hardcode it
                    self._int_metrics._increment_internal_stat(Metric.RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED, 1)

            # pylint: disable=unused-argument
            def on_buffer_overflow_discard_latest(discarded):
                self._set_next_discard_indication = True
                self._int_metrics._increment_internal_stat(Metric.RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED, 1)

            def on_item_put(item):
                if self._set_next_discard_indication:
                    item.get_message_discard_notification().set_internal_discard_indication()
                    self._set_next_discard_indication = False

            if builder.receiver_back_pressure_type == DirectMessageReceiverBackPressure.DropOldest:
                self._message_receiver_queue.register_on_event(_PubSubPlusQueue.ON_BUFFER_OVERFLOW_EVENT,
                                                               on_buffer_overflow)
            elif builder.receiver_back_pressure_type == DirectMessageReceiverBackPressure.DropLatest:
                self._message_receiver_queue.register_on_event(_PubSubPlusQueue.ON_PUT_ITEM_EVENT, on_item_put)
                self._message_receiver_queue.register_on_event(_PubSubPlusQueue.ON_BUFFER_OVERFLOW_EVENT,
                                                               on_buffer_overflow_discard_latest)

        else:
            # elastic case
            self._message_receiver_queue = _PubSubPlusQueue()

    def add_subscription(self, another_subscription: TopicSubscription):
        # Subscribe to a topic synchronously (blocking). """
        validate_subscription_type(subscription=another_subscription, logger=logger)
        self._can_add_subscription()
        self._do_subscribe(another_subscription.get_name())

    def add_subscription_async(self, topic_subscription: TopicSubscription) -> concurrent.futures.Future:
        # method to add the subscription asynchronously
        return self._executor.submit(self.add_subscription, topic_subscription)

    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        # Get a message, blocking for the time configured in the receiver builder.
        # may return None when the flow goes api is called after TERMINATING state & internal buffer is empty
        # as well as when service goes down """
        self._can_receive_message()
        if timeout is not None:
            is_not_negative(input_value=timeout, logger=logger)

        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug("%s", RECEIVE_MESSAGE_FROM_BUFFER)
        try:
            message = self._message_receiver_queue.get(block=True,
                                                       timeout=convert_ms_to_seconds(
                                                           timeout) if timeout is not None else None)
            # This first condition checks to make sure the message is not None
            if message and message.get_message_discard_notification().has_internal_discard_indication():
                # Since we are always dealing with one message at a time, and the discard indication is a boolean,
                # we only need to increment by one each time, so we can hardcode it here
                self._int_metrics._increment_internal_stat(Metric.INTERNAL_DISCARD_NOTIFICATIONS, 1)

            return message
        except queue.Empty:  # when timeout arg is given just return None on timeout
            return
        except QueueShutdown:
            # unblock wait on terminate
            return
        except (PubSubPlusClientError, KeyboardInterrupt) as exception:
            logger.warning(str(exception))
            raise exception

    def receive_async(self, message_handler: MessageHandler):
        # Specify the asynchronous message handler.
        is_type_matches(actual=message_handler, expected_type=MessageHandler, logger=logger)
        with self._receive_lock:
            self._can_receive_message()
            if self._message_receiver_thread is None:
                self._message_receiver_thread = _DirectMessageReceiverThread(self._id_info, logger, self,
                                                                             self._messaging_service)
                self._message_receiver_thread_holder.value = self._message_receiver_thread
                self._message_receiver_thread.message_handler = message_handler
                self._message_receiver_thread.daemon = True
                self._message_receiver_thread.start()
            else:  # just update the thread's message handler
                self._message_receiver_thread.message_handler = message_handler

    def remove_subscription(self, subscription: TopicSubscription):
        # Unsubscribe from a topic synchronously (blocking).
        validate_subscription_type(subscription=subscription, logger=logger)
        self._can_remove_subscription()
        self._do_unsubscribe(subscription.get_name())

    def remove_subscription_async(self, topic_subscription: TopicSubscription) -> concurrent.futures.Future:
        # method to remove the subscription asynchronously
        validate_subscription_type(topic_subscription)
        return self._executor.submit(self.remove_subscription, topic_subscription)

    def _halt_messaging(self):
        self._unsubscribe()

    def _is_receiver_available_for_cache(self, raise_error: bool=True) -> bool:
        """
        This method checks whether the receiver is available to perform cache operations.
        The criteria for this are:
            * the service is connected
            * the receiver is started

        Args:
            raise_error(bool): If true, this method will raise an error when the receiver fails the check.
                If false, this method will not raise an error when the receiver fails the check.

        Returns:
            bool: True if the receiver is available for cache operations, False otherwise.

        Raises:
            IllegalStateError: If the service is not connected, or the receiver is not started.
        """
        error_message = f"{RECEIVER_UNAVAILABLE_FOR_CACHE_REQUESTS}{self._message_receiver_state}"
        if not self._is_message_service_connected(raise_error) or \
            not self._is_receiver_started(error_message, raise_error) or \
            self._is_receiver_terminating(error_message, raise_error):
            # Return early because we failed the check
            if self.adapter.isEnabledFor(logging.DEBUG):
                self.adapter.debug("Receiver is not available for cache.")
            return False
        if self.adapter.isEnabledFor(logging.DEBUG):
            self.adapter.debug("Receiver is available for cache.")
        return True

    def _cache_event_callback_routine(self, _opaque_session_p, cache_event_info_p, user_p):
        # At the time of this writing, 2023-07-27, SOL-42602, the only variant of the solCache_event variant
        # returned by CCSMP to this callback is SOLCACHE_EVENT_REQUEST_COMPLETED_NOTICE. More details on the result
        # of the cache request are available through the return code and sub code fields of the event info struct.
        # However, any significant or time sensitive information regarding lifecycle etc. that would need to be
        # acted on immediately would be given by the event, not the return code. Since there is only one event that
        # can be processed in this function, no filter or action is, necessary.

        cache_event_info = _SolCacheEventInfo.from_solcache_struct(cache_event_info_p.contents,
                                                                   ctypes.cast(user_p, ctypes.py_object).value)
        # last_error_info is not reliably populated before this callback is called, so we cannot retrieve error info
        # from the core library, and instead have to generate it based on the event info.
        exception = generate_exception_from_cache_event(cache_event_info)

        try:
            self._cache_response_dispatcher.submit(self.process_cache_event, cache_event_info, exception)
        except Exception as exception:
            # An unexpected issue was encountered, so we raise an exception
            # * The cache event queue should only be shutdown after all requests have been cancelled and their
            #       corresponding events pushed to the queue, so QueueShutdown should not be caught here.
            # * The cache event queue is elastic, so queue.Full should not be caught here.

            error_message = f"{DROPPING_CACHE_RESPONSE}{cache_event_info_p.contents.cache_request_id}. " \
                            f"Exception: {exception}"
            self.adapter.error(error_message)
            raise PubSubPlusClientError(message=error_message) from exception

    def _teardown_cache(self):
        """
        This method terminates the cache resources of the receiver without terminating the receiver itself. This
        method is intended to be invoked by the receiver termination methods, while terminating the receiver. This
        method is intended to be used either both in solicited and unsolicited termination, but not during an
        interpreter exit which preceeds termination, i.e. falling off main with calling terminate.

        This method:
            * terminates the cache request queue:
                * this prevents future cache requests from being submitted by the application
                * this prevents future cache requests from being sent by the API
            * cancels all in-flight cache requests
            * empties the cache request queue, and pushes the associated responses onto the cache event queue
            * terminates the cache event queue
        """
        # NOTE:
        # There is a race condition in the cache feature:
        #     When the serial publisher attempts to send a cache request, it first peeks the request from the queue,
        #     and then sends it. After confirming that the request has been sent, the serial publisher then removes
        #     the request from the queue. This introduces the possibility of the cache request queue being shutdown
        #     and drained after the serial publisher has peeked the cache request at the top of the queue, but before
        #     the serial publisher has removed the cache request from the top of the queue. This results in two
        #     cache events being added to the cache event queue.
        #
        #     One is a cache event that was transformed from the
        #     request that was drained from the cache request queue, and the other is a cache event that was generated
        #     by an in-flight cache request which eventually completed. The first event will always be a cancellation
        #     event generated by the Python API. The second event could be generated by the core library after
        #     the associated cache request was cancelled by the API; or, could be generated by the request completing
        #     before being cancelled, which could result in many different event types such as OK or NO_DATA.
        #     In the case that the second event completed with data, the application would receive data in the
        #     receiver message callback, and should be able to expect a corresponding cache event.
        #      Therefore, the API needs to guarantee that in the case of this race condition, the application receives
        #     the event generated by the core library.
        #
        #     It is also unreasonable to expect the application to discern
        #     multiple events passed to it that appear to be associated with the same operation through their cache
        #     request ID, but have conflicting contents, which would be the case if the API generated event described
        #     the operation as cancelled, and the core library generated event described the operation as complete.
        #     Therefore, the API needs to be able to discern that there are multiple events associated with the same
        #     operation, and that only the event generated by the core library should be passed to the application.
        #
        #     To do this, during teardown, the API cancels all in-flight cache requests after shutting down and
        #     draining the cache request queue. This way, if the described race condition occurs, the in-flight cache
        #     request is cancelled or completes, the core library will generate the appropriate event and place it
        #     on the queue BEFORE the API generates cancellation events for the drained cache requests. This guarantees
        #     that the first event for the operation that will be taken from the queue will be the event generated by
        #     the core library. To guarantee that only the first event is passed to the application, the cache event
        #     thread removes the cache requester entry from the dictionary of cache requesters after each event is
        #     processed. This way, once the second event does not have a corresponding cache requester, so it is
        #     logged, but otherwise ignored.
        #
        #     Refer to _DirectMessageReceiver.process_cache_event() for details on how the cache events are processed.

        # Terminate the cache request queue to prevent future cache requests
        self._cache_requester_queue.shutdown()
        # Drain the cache requests so that an associated cancellation notification can be given to the application
        # through the cache event thread
        drained_cache_requests = self._cache_requester_queue.drain()

        # Clean up cache sessions
        for cache_requester, _ in self._cache_requester_dict.values():
            self._cache_response_dispatcher.submit(self._dispatch_cache_request_cancellation, cache_requester)
        # For each cache request that was submitted by the application but not sent by the API, generate a cancellation
        # event, and push it to the event queue so that it can be processed by the cache event thread, and passed to
        # the application
        if len(drained_cache_requests) > 0:
            # Only push contents to the event queue if there are any
            for cache_requester in drained_cache_requests:
                event_info, error = generate_cancelled_request_tuple(cache_requester)
                self._cache_response_dispatcher.submit(self.process_cache_event, event_info, error)

    def _dispatch_cache_request_cancellation(self, cache_requester: 'CacheRequester'):
        # It's a rare occurrence that the cache requester will be removed after this method was submitted, but
        # completed before this method was executed. Checking this state is only relevant in this corner case, and even
        # then does not give significant performance improvements, since that case only occurs during termination.
        # Also, we handle the case of the cancellation failing in this corner case, so there is no undefined behaviour
        # for this case, so the cost of the case is both low probability, and without risk.
        try:
            cache_requester.cancel_pending_cache_requests()
        except PubSubPlusCoreClientError as error:
            # This can occur because this method was submitted to the dispatcher before the request completed,
            # but was executed after the request completed. We can't hold a mutex across CCSMP operations, so we
            # can't guarantee state for the duration of the call. Because we can't guarantee state, it is possible
            # that the request will complete and the cache session will be destroyed, resulting in an exception.
            #
            # If we get the exception, then the cache session was already destroyed, so we can't cancel anything
            # anyways, and we can just move on.
            if self.adapter.isEnabledFor(logging.DEBUG):
                self.adapter.warning(f"Failed to cancel cache requests with cache request ID " \
                                     f"{cache_requester.cache_request_id}, with error: {error}")

    def _resource_cleanup(self):
        # The cache_response_dispatcher is started before any other cache operations are executed,
        # so we know that the cache resources only need to be cleaned up if this dispatcher is running.
        if self._cache_response_dispatcher.is_running:
            self._teardown_cache()
            # Check that the dict has entries before waiting on it to be empty. This is necessary because the last
            # cache response could be processed, and result in the Condition being notified, long before we actually
            # call wait in this method, which would result in the Condition waiting forever to be notified, and the
            # _CacheResponseDispatcher never having a new event to process and then notify the Condition about.
            if not self._cache_requester_dict_is_empty_predicate():
                # Wait for cache requester_queue to be empty before joining the dispatcher thread. This guarantees that
                # there are no pending tasks for the dispatcher to execute
                self._cache_requester_dict_is_empty.wait()
            # We need to call teardown_cache() before joining the thread because the cache event queue must be
            # shutdown before the thread can join.
            with _Released(self._mutex):
                self._cache_response_dispatcher.shutdown()
        super()._resource_cleanup()

    def _cache_requester_dict_is_empty_predicate(self) -> 'bool':
        # This method is able to read the cache_requester_dict without acquiring the mutex because it assumes
        # that all mutations to that dictionary are done under mutex protection. As of 2023-11-06, the implementation
        # satisfies this assumption.
        return len(self._cache_requester_dict) == 0

    def remove_cache_entry(self, cache_session_id: int):
        # This is safe because we only add to the _cache_session_dict under the receiver mutex protection in
        # `request_cached()`, and only remove from the _cache_session_dict under the receiver mutex protection
        # here. Reading from the _cache_session_dict is done only in the cache event thread. Reading a given entry
        # from that thread is done only before this method is called, so it is not possible for this deletion to
        # occur concurrent with the read from the cache event thread.
        with self._mutex:
            self._remove_cache_entry_without_mutex_unsafe(cache_session_id)
            if self._cache_requester_dict_is_empty_predicate():
                # Unblock termination thread. This is only relevant if the termination thread has been blocked
                # waiting for the dispatcher to complete processing cache responses. In case termination has not
                # been run and the current cache response happens to be the last one, we unblock this waiter, but
                # doing so will have no impact on the rest of the API, other than immediately unblocking the
                # another thread that subsequently tries to terminate the receiver.
                self._cache_requester_dict_is_empty.notify_all()

    def _remove_cache_entry_without_mutex_unsafe(self, cache_session_id: int):
        # This code is unsafe because it mutates shared memory without acquiring a mutex.
        # The caller must ensure that the mutex is acquired before calling this method.
        del self._cache_requester_dict[cache_session_id]

    def request_cached(self,
                       cached_message_subscription_request: CachedMessageSubscriptionRequest,
                       cache_request_id: int,
                       completion_listener: CacheRequestOutcomeListener):
        _ = is_type_matches(cache_request_id, int, logger=self.adapter)
        _ = is_type_matches(completion_listener, CacheRequestOutcomeListener, ignore_none=True, logger=self.adapter)
        _ = is_value_out_of_range(0, MAX_UNSIGNED_SIXTY_FOUR_BIT_INT, cache_request_id, 64, logger=self.adapter)
        # Do a dirty read first, in case we can't send a cache request, so that we don't need to wait for mutex
        self._is_receiver_available_for_cache()
        # Acquire mutex and re-read receiver and service state, since it could have changed between the dirty read
        # and now.
        with self._mutex:
            self._is_receiver_available_for_cache()

            # Check if the cache event thread has already been started. If not, start it.
            # We always confirm that the thread exists before allocating cache resources
            # so that in _resource_cleanup we can assume to only need to cleanup cache
            # resources if the thread exists.
            if not self._cache_response_dispatcher.is_running:
                if self.adapter.isEnabledFor(logging.DEBUG):
                    self.adapter.debug("Starting cache response dispatcher for direct receiver.")
                self._cache_response_dispatcher.start()

            cache_requester = _SolaceCacheRequester(cached_message_subscription_request,
                                              cache_request_id,
                                              self)

            try:
                cache_requester.setup()
            except PubSubPlusCoreClientError as error:
                # cache_requester.setup() already logs the error, so we don't need to log it again here.
                # We transform the PubSubPlusCoreClientError into a PubSubPlusClientError because only
                # the latter are expected through the DirectMessageReceiver.request_cached interface.
                raise PubSubPlusClientError(UNABLE_TO_SEND_CACHE_REQUEST) from error

            # Add the correlation id and (cache requester, completion listener) tuple to a dictionary, so that
            # they can be used and then cleaned up once the cache response is received.
            self._cache_requester_dict[cache_requester.id] = (cache_requester, completion_listener)

            # Add cache request to cache request queue
            try:
                self._cache_requester_queue.put(cache_requester)
            except QueueShutdown as exception:
                # The queue cache request queue was shutdown by lifecycle management. This was done because a
                # fatal error was encountered while processing cache requests. Because this entire block of code
                # is executed under mutex protectin, this QueueShutdown exception cannot be encountered because
                # the receiver is terminating or terminated.
                self._remove_cache_entry_without_mutex_unsafe(cache_requester.id)
                self.adapter.error(str(exception))
                with _Released(self._mutex):
                    # Need to release the mutex over CCSMP calls
                    cache_requester.cleanup()
                raise PubSubPlusClientError(CACHE_UNAVAILABLE_ON_RECEIVER_DUE_TO_INTERNAL_ERROR) from exception

            def _serialized_cache_request(cache_request_send_task):
                cache_request_send_task.receiver.send_cache_request_asynchronously(cache_request_send_task)
            self._serial_publisher.submit(_serialized_cache_request, self._cache_request_send_task)

    def send_cache_request_asynchronously(self, cache_request_send_task: '_CacheRequestSendTask'):
        # Make sure that the receiver is ready to send the cache request
        # Because this task will be run asynchronously, it is reasonable to expect that it might be run shortly after
        # the receiver has terminated or the service has disconnected. Therefore, is is not an exceptional case and
        # does not warrant raising an exception.
        if not self._is_receiver_available_for_cache(raise_error=False):
            return

        try:
            cache_requester = cache_request_send_task.get_cache_requester_for_send()
            # If there is no cache request to send, we can just return
            if cache_requester:
                # Assume that the transport is blocking
                cache_request_status = SOLCLIENT_WOULD_BLOCK
                # Continuously attempt to send the cache request, unless the cache request has been sent
                # (SOLCLIENT_IN_PROGRESS), or the receiver is no longer available to send the cache request
                while cache_request_status != SOLCLIENT_IN_PROGRESS and \
                    self._is_receiver_available_for_cache(raise_error=False):
                    cache_request_status = self._serial_publisher.send_cache_request(cache_requester)
                    if cache_request_status is SOLCLIENT_WOULD_BLOCK:
                        self._serial_publisher.wait_for_writable()
                    cache_request_send_task.on_publishable_sent()
        except PubSubPlusClientError as exception:
            cache_request_send_task.on_publishable_send_error(exception)
        except Exception as exception:
            self.adapter.error("Error on receiver cache request send thread: [%s]", str(exception))
            raise PubSubPlusClientError("Error on receiver cache request send thread") from exception

    def process_cache_event(self, cache_event_info: 'SolCacheEventInfo', exception: Exception=None):  # pylint: disable=missing-function-docstring,too-many-branches
        if cache_event_info:
            # Retrieve relevant information from cache event info struct
            cache_session_id = cache_event_info.cache_session_id

            # This read of the cache requester dict can be done without mutex protection, because it is assumed that
            # all mutations of the dictionary are done under mutex protection. As of 2023-11-06, the implementation
            # satisfies this assumption.
            query_result = self._cache_requester_dict.get(cache_session_id)
            if query_result:
                # If the cache request exists, extract the tuple values and continue
                cache_requester, completion_listener = query_result
            else:
                # If the cache request does not exist, then we can't clean up an associated cache session,
                # and we can't give the application a callback, so log the error and move on
                if self.adapter.isEnabledFor(logging.DEBUG):
                    self.adapter.debug("[%s][%s]", UNABLE_TO_PROCESS_CACHE_RESPONSE, INVALID_CACHE_REQUEST_ID)
                return

            # According to arch, it is valid for the completion listener to be None, and in that case it should
            # be ignored.

            # If completion listener is not None, process event
            if completion_listener is not None:
                # We only need to format the CacheRequestOutcome if the completion_listener is not None, because
                # otherwise, there is no need for it
                return_code = cache_event_info.return_code
                sub_code = cache_event_info.sub_code
                if return_code == SOLCLIENT_OK:
                    cache_request_outcome = CacheRequestOutcome.OK
                elif return_code == SOLCLIENT_INCOMPLETE:
                    if sub_code == SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_SUSPECT_DATA.value:
                        cache_request_outcome = CacheRequestOutcome.SUSPECT_DATA
                    elif sub_code == SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_NO_DATA.value:
                        cache_request_outcome = CacheRequestOutcome.NO_DATA
                    elif sub_code == SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_TIMEOUT.value:
                        cache_request_outcome = CacheRequestOutcome.FAILED
                        if not is_type_matches(exception, PubSubTimeoutError, raise_exception=False):
                            # We don't need to check if exception is None, because we can raise a new error from None,
                            # which will just appear to the application as though there was only a single error, which
                            # is correct.
                            exception = PubSubTimeoutError(f"{CACHE_REQUEST_TIMEOUT}, " \
                                                           f" this error was generated from event: {exception}",
                                                           sub_code)
                    else:
                        # None of the other possible rc=incomplete subcodes are captured in arch as needing a
                        cache_request_outcome = CacheRequestOutcome.FAILED
                else:
                    cache_request_outcome = CacheRequestOutcome.FAILED

                completion_listener.on_completion(cache_request_outcome, cache_event_info.cache_request_id, exception)

            # If completion listener is None, skip to lifecycle management of cache session
            try:
                # We need to remove the cache entry before we cleanup the cache requester, because we need to make
                # sure that _teardown_cache() can cancel only cache requests whose cache sessions have not been
                # destroyed. In other words, the mutex acquisition of remove_cache_entry() competes with the
                # mutex acquisition of terminate(), which provides synchronization between the main thread calling
                # terminate, and the cache event thread calling remove_cache_entry().
                self.remove_cache_entry(cache_requester.id)
                # We have already received the event from CCSMP notifying that the cache request is complete,
                # so we don't need to cancel anything before cleaning up resources.
                cache_requester.cleanup()
            except PubSubPlusCoreClientError:
                # The only other return code from cache_session_destroy is SOLCLIENT_FAIL.
                error_message = f"{UNABLE_TO_DESTROY_CACHE_SESSION}{cache_requester.cache_session_p}"
                self.adapter.warning(error_message)


def direct_receiver_thread_cleanup(thread_holder):
    direct_receiver_thread = thread_holder.value
    if direct_receiver_thread is not None and direct_receiver_thread.is_alive():
        direct_receiver_thread.join()

def cache_response_dispatcher_cleanup(dispatcher):
    dispatcher.shutdown()
