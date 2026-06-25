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
# pylint: disable=missing-function-docstring,no-else-raise,no-member,no-else-return,inconsistent-return-statements

"""
Module that abstracts message receiving behavior; it is a base class for all receivers.
"""
import concurrent
import copy
import logging
import threading
import weakref
from concurrent.futures.thread import ThreadPoolExecutor
from ctypes import c_uint32, py_object, c_void_p, Structure, CFUNCTYPE, c_int
from enum import Enum
from queue import Full
from typing import List
import time

from solace.messaging import _SolaceServiceAdapter
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_CALLBACK_OK, SOLCLIENT_CALLBACK_TAKE_MSG, \
    SOLCLIENT_DISPATCH_TYPE_CALLBACK
from solace.messaging.config._solace_message_constants import GRACE_PERIOD_DEFAULT_MS, \
    RECEIVER_TERMINATED_UNABLE_TO_START, CANNOT_ADD_SUBSCRIPTION, RECEIVER_TERMINATED, \
    CANNOT_REMOVE_SUBSCRIPTION, RECEIVER_ALREADY_TERMINATED, \
    UNCLEANED_TERMINATION_EXCEPTION_MESSAGE_RECEIVER, UNABLE_TO_RECEIVE_MESSAGE_MESSAGE_SERVICE_NOT_CONNECTED, \
    UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_ALREADY_TERMINATED, \
    UNABLE_TO_UNSUBSCRIBE_TO_TOPIC, RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED, \
    RECEIVER_TERMINATION_IS_IN_PROGRESS, CCSMP_INFO_SUB_CODE
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.core._receive import _SolaceReceiverEvent
from solace.messaging.errors.pubsubplus_client_error import IllegalStateError, IncompleteMessageDeliveryError, \
    PubSubPlusCoreClientError, PubSubPlusClientError, InvalidDataTypeError
from solace.messaging.receiver._impl._inbound_message import _InboundMessage
from solace.messaging.receiver._inbound_message_utility import topic_unsubscribe_with_dispatch, \
    topic_subscribe_with_dispatch
from solace.messaging.receiver.message_receiver import MessageReceiver
from solace.messaging.utils.life_cycle_control import TerminationNotificationListener
from solace.messaging.utils.manageable import Metric
from solace.messaging.utils._solace_utilities import executor_shutdown, convert_ms_to_seconds, COMPLETED_FUTURE, \
    _Released, _PubSubPlusQueue, QueueShutdown, get_last_error_info, validate_grace_period
from solace.messaging.utils._termination_notification_util import TerminationNotificationDispatcher

logger = logging.getLogger('solace.messaging.receiver')


class _MessageReceiverState(Enum):  # pylint: disable=too-few-public-methods, missing-class-docstring
    # enum class for defining the message receiver state
    NOT_STARTED = 0
    STARTING = 1
    STARTED = 2
    TERMINATING = 3
    TERMINATED = 4


class _MessageReceiverQueueDrainType:  # pylint: disable=too-few-public-methods
    """
    This class holds the index constants for reading from and writing to the list of drained queue items for
    a receiver.
    """
    RECEIVER_MESSAGE_QUEUE = 0


class _MessageReceiver(MessageReceiver):  # pylint: disable=too-many-instance-attributes
    msg_callback_func_type = CFUNCTYPE(c_int, c_void_p, c_void_p, py_object)

    def __init__(self, builder):
        self._messaging_service = builder.messaging_service
        self._id_info = f"[SERVICE: {str(hex(id(self._messaging_service.logger_id_info)))}] " \
                        f"[RECEIVER: {str(hex(id(self)))}]"

        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        self._message_receiver_state = _MessageReceiverState.NOT_STARTED
        self.__init_back_pressure(builder)
        self._start_future = None
        self._terminate_future = None
        self._start_async_lock = threading.Lock()
        self._terminate_async_lock = threading.Lock()
        self._receive_lock = threading.Lock()
        self._mutex = threading.Lock()
        self._executor = ThreadPoolExecutor(thread_name_prefix=self._id_info)
        self._finalizer = weakref.finalize(self, executor_shutdown, self._executor)
        self._receiver_empty_event = threading.Event()
        self._message_receiver_thread_stop_event = threading.Event()
        self._message_receiver_thread = None
        self._is_unsubscribed = False
        self._running = None
        self._topic_dict = {}

        self._solace_receiver_handlers = {}
        self._solace_receiver_emitter = self._messaging_service.create_receiver().emitter

        self._termination_notification_dispatcher: TerminationNotificationDispatcher = \
            TerminationNotificationDispatcher(self.adapter)

    @property
    def _asked_to_terminate(self):
        return self._message_receiver_state in [_MessageReceiverState.TERMINATING,
                                                _MessageReceiverState.TERMINATED]

    def _emit_notify_event(self, error_info) -> concurrent.futures.Future:
        return self._termination_notification_dispatcher.on_exception(
            PubSubPlusClientError(error_info,
                                  error_info[CCSMP_INFO_SUB_CODE]),
            int(time.time() * 1000))

    def set_termination_notification_listener(self, listener: TerminationNotificationListener):
        if isinstance(listener, TerminationNotificationListener):
            self._termination_notification_dispatcher.set_termination_notification_listener(listener)
        else:
            raise InvalidDataTypeError(f"Expected to receive instance of {TerminationNotificationListener}, " \
                                       f"but received instance of {listener} instead.")

    # pylint: disable=protected-access
    def _do_metrics(self, drained: List[list]):
        # Incrementing the internal discarded received messages metrics after acquiring lock
        drained_len = len(drained[_MessageReceiverQueueDrainType.RECEIVER_MESSAGE_QUEUE])
        if drained_len != 0:
            self._int_metrics._increment_internal_stat(Metric.RECEIVED_MESSAGES_TERMINATION_DISCARDED, drained_len)

    def _notify_metrics_and_cleanup(self, error_info):
        # Acquire a metrics lock to update the message discard count variable and then reset Queue
        with self._mutex:
            drained_queue_contents = self._cleanup_queues()
            self._do_metrics(drained_queue_contents)
            self._emit_notify_event(error_info)
            self._resource_cleanup()

    def _register_receiver_event(self, event: _SolaceReceiverEvent, handler):
        handler_id = self._solace_receiver_emitter.register_receiver_event_handler(event, handler)
        self._solace_receiver_handlers[event] = handler_id

    def _on_receiver_down(self, error_info: dict):
        with self._mutex:
            if not self._asked_to_terminate:
                self._message_receiver_state = _MessageReceiverState.TERMINATED
                self._handle_events_on_terminate()
                self._message_receiver_queue.shutdown()
                self._executor.submit(self._notify_metrics_and_cleanup, error_info)
            else:
                self._message_receiver_queue.shutdown() # unblock the terminate method if its called

    def _register_receiver_events(self):
        def on_receiver_down(error_info: dict):
            if logger.isEnabledFor(logging.DEBUG):
                self.adapter.debug("Receiver went down with the following event information: [%s]", error_info)
            self._on_receiver_down(error_info)

        self._register_receiver_event(_SolaceReceiverEvent.RECEIVER_DOWN, on_receiver_down)

    def _unregister_receiver_events(self):
        for handler_id in self._solace_receiver_handlers.values():
            self._solace_receiver_emitter.unregister_receiver_event_handler(handler_id)

        self._solace_receiver_handlers.clear()

    def __init_back_pressure(self, builder):  # pylint: disable=unused-argument
        self._force = False
        self._block = True
        self._message_receiver_queue = _PubSubPlusQueue()

    @property
    def receiver_state(self):
        return self._message_receiver_state

    @property
    def receiver_queue(self):
        return self._message_receiver_queue

    @property
    def stop_event(self):
        return self._message_receiver_thread_stop_event

    @property
    def receiver_empty_event(self):
        return self._receiver_empty_event

    def is_running(self) -> bool:
        is_running = self._message_receiver_state == _MessageReceiverState.STARTED
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('%s is running?: %s', type(self).__name__, is_running)
        return is_running

    def is_terminated(self) -> bool:
        is_terminated = _MessageReceiverState.TERMINATED == self._message_receiver_state
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('%s  is terminated?: %s', type(self).__name__, is_terminated)
        return is_terminated

    def is_terminating(self) -> bool:
        is_terminating = _MessageReceiverState.TERMINATING == self._message_receiver_state
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('%s is terminating?', is_terminating)
        return is_terminating

    def start_async(self) -> concurrent.futures.Future:
        # Start the Receiver asynchronously (non-blocking)
        if self.__is_connecting() or self.__is_connected():
            return self._start_future
        with self._start_async_lock:
            self._is_receiver_terminated(error_message=RECEIVER_TERMINATED_UNABLE_TO_START)
            # Even after acquiring lock still we have to check the state to avoid spinning up the executor
            if self.__is_connecting() or self.__is_connected():
                return self._start_future
            self._start_future = self._executor.submit(self.start)
            return self._start_future

    def terminate(self, grace_period: int = GRACE_PERIOD_DEFAULT_MS):
        validate_grace_period(grace_period=grace_period, logger=logger)

        if not self._is_receiver_available_for_terminate() or \
                self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
            return

        with self._mutex:
            if not self._is_receiver_available_for_terminate() or \
                    self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
                return
            self._message_receiver_state = _MessageReceiverState.TERMINATING

            grace_period_in_seconds = convert_ms_to_seconds(grace_period)
            self._halt_messaging()
            self._handle_events_on_terminate()
            # we have unsubscribed all topics as well as
            # we dropping messages in message callback routine in TERMINATING state (in case of persistent ,
            # we have already paused the flow and dropping the messages in the flow message
            # callback routine in  TERMINATING state)
            # Release the terminate lock when queue size drain to be done.
            with _Released(self._mutex):
                self.receiver_queue.wait_for_empty(timeout=grace_period_in_seconds)
            self._cleanup()
            drained_queue_contents = self._cleanup_queues()
            self._do_metrics(drained_queue_contents)
            self._check_undelivered_messages(drained_queue_contents)

    def terminate_async(self, grace_period: int = GRACE_PERIOD_DEFAULT_MS) -> concurrent.futures.Future:
        # Terminate the Receiver asynchronously (non-blocking).
        validate_grace_period(grace_period=grace_period, logger=logger)
        if self.__is_in_terminal_state():
            self._is_receiver_available_for_terminate()
            return self._terminate_future

        with self._terminate_async_lock:
            # Even after acquiring lock still we have to check the state to avoid spinning up the executor
            if self.__is_in_terminal_state():
                self._is_receiver_available_for_terminate()
                return self._terminate_future
            if self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
                self._terminate_future = COMPLETED_FUTURE
            elif self._message_receiver_state not in [_MessageReceiverState.TERMINATED,
                                                      _MessageReceiverState.TERMINATING]:
                self._terminate_future = self._executor.submit(self.terminate, grace_period)
            # If the receiver is in the TERMINATED or TERMINATING state, then we assume
            # the _cleanup() method has set the self._terminate_future attribute
            return self._terminate_future

    def _can_add_subscription(self, error_message=None, raise_error=True):
        error_message = f'{CANNOT_ADD_SUBSCRIPTION}{self._message_receiver_state.name}' \
            if error_message is None else error_message
        self._is_receiver_available(error_message=error_message, raise_error=raise_error)

    def _can_remove_subscription(self, error_message=None, raise_error=True):
        error_message = f'{CANNOT_REMOVE_SUBSCRIPTION}{self._message_receiver_state.name}' \
            if error_message is None else error_message
        self._is_receiver_available(error_message=error_message, raise_error=raise_error)

    def _is_receiver_available(self, error_message=None, raise_error=True):
        self._is_receiver_started(error_message=error_message, raise_error=raise_error)
        self._is_receiver_terminated(error_message=error_message, raise_error=raise_error)

    def _is_receiver_available_for_terminate(self):
        return not self._is_receiver_terminating(error_message=None, raise_error=False)

    def _is_receiver_started(self, error_message, raise_error=True):
        if self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
            self.adapter.warning("%s", error_message)
            if raise_error:
                raise IllegalStateError(error_message)
            else:
                return False
        return True

    def _is_receiver_terminating(self, error_message=None, raise_error=True):
        if self._message_receiver_state in [_MessageReceiverState.TERMINATING,
                                            _MessageReceiverState.TERMINATED]:
            if self._message_receiver_state == _MessageReceiverState.TERMINATING:
                error_message = RECEIVER_TERMINATION_IS_IN_PROGRESS if error_message is None else error_message
            elif self._message_receiver_state == _MessageReceiverState.TERMINATED:
                error_message = RECEIVER_ALREADY_TERMINATED if error_message is None else error_message
            self.adapter.warning("%s", error_message)
            if raise_error:
                raise IllegalStateError(error_message)
            else:
                return True
        return False

    def _is_receiver_terminated(self, error_message=None, raise_error=True):
        if self._message_receiver_state == _MessageReceiverState.TERMINATED:
            error_message = RECEIVER_TERMINATED if error_message is None else error_message
            self.adapter.warning("%s", error_message)
            if raise_error:
                raise IllegalStateError(error_message)
            else:
                return True
        return False

    def _check_undelivered_messages(self, drained: List[list]):
        # notify application of any remaining buffered data
        if len(drained[_MessageReceiverQueueDrainType.RECEIVER_MESSAGE_QUEUE]) != 0:
            message = f'{UNCLEANED_TERMINATION_EXCEPTION_MESSAGE_RECEIVER}. ' \
                      f'Message count: [{len(drained)}]'
            self.adapter.warning("%s", message)
            raise IncompleteMessageDeliveryError(message)

    def _handle_events_on_terminate(self):
        """
        This method processes all receiver eventing on termination. This includes
        unregistering events, unblocking all waiters for events.
        """
        self._unregister_receiver_events()

        # note this wakes the message delivery even when receiver is paused
        # this is better then blocking for the whole grace period

    def _is_message_service_connected(self, raise_error=True):
        # Method to validate message service is connected or not
        if not self._messaging_service.is_connected:
            self.adapter.warning("%s", UNABLE_TO_RECEIVE_MESSAGE_MESSAGE_SERVICE_NOT_CONNECTED)
            if raise_error:
                raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_MESSAGE_SERVICE_NOT_CONNECTED)
            else:
                return False
        return True

    def _can_receive_message(self):
        # """can able to receive message if message service is connected and it is not terminated"""
        self._is_message_service_connected()
        if self._message_receiver_state == _MessageReceiverState.TERMINATED:
            error_message = UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_ALREADY_TERMINATED
            self.adapter.warning("%s", error_message)
            raise IllegalStateError(error_message)

    def _cleanup(self):
        # Assume the mutex has been acquired before this method is called
        self._message_receiver_state = _MessageReceiverState.TERMINATED
        self.adapter.info("%s", RECEIVER_TERMINATED)
        self._resource_cleanup()

    def _resource_cleanup(self):
        self.receiver_queue.shutdown()
        if self._message_receiver_thread is not None:
            # set thread termination flag before waking delivery thread
            # to ensure clean exit from python message delivery thread
            self._message_receiver_thread_stop_event.set()

            # wake message delivery thread
            # join on python message delivery thread
            with _Released(self._mutex):
                self._message_receiver_thread.join()

        with self._start_async_lock:
            if self._start_future is None:
                self._start_future = COMPLETED_FUTURE
        with self._terminate_async_lock:
            if self._terminate_future is None:
                self._terminate_future = COMPLETED_FUTURE
        # shutdown async executor non blocking
        self._executor.shutdown(wait=False)
        with _Released(self._mutex):
            if self._termination_notification_dispatcher is not None:
                self._termination_notification_dispatcher.shutdown()

    def _cleanup_queues(self) -> List[list]:
        drained_queue_contents = self._drain_queues()
        self._free_drained_queue_contents_in_core_api(drained_queue_contents)
        return drained_queue_contents

    def _drain_queues(self) -> List[list]:
        receiver_queue_contents = []
        drained_messages = self._message_receiver_queue.drain() if self._message_receiver_queue is not None else []
        receiver_queue_contents.insert(_MessageReceiverQueueDrainType.RECEIVER_MESSAGE_QUEUE,
                                       drained_messages)
        return receiver_queue_contents

    # pylint: disable=no-self-use, protected-access
    def _free_drained_queue_contents_in_core_api(self, drained_contents: List[list]):
        """
        This method frees CCSMP resources referenced by the Python API _InboundMessage objects after
        they have been drained from a shutdown _PubSubPlusQueue. This method does not free the _InboundMessage
        object from Python, since this can be handled by garbage collection.
        """
        drained_messages = drained_contents[_MessageReceiverQueueDrainType.RECEIVER_MESSAGE_QUEUE]
        for message in drained_messages:
            message._solace_message.cleanup()

    def __is_connecting(self):
        return self._start_future and self._message_receiver_state == _MessageReceiverState.STARTING

    def __is_connected(self):
        return self._start_future and self._message_receiver_state == _MessageReceiverState.STARTED

    def __is_in_terminal_state(self):
        return self._terminate_future and (self.__is_terminating() or self.__is_terminated())

    def __is_terminating(self):
        return self._terminate_future and self._message_receiver_state == _MessageReceiverState.TERMINATING

    def __is_terminated(self):
        return self._terminate_future and self._message_receiver_state == _MessageReceiverState.TERMINATED

    def _do_subscribe(self, topic_subscription: str):
        """ implementation will be given in child class"""

    def _do_unsubscribe(self, topic_subscription: str):
        """ implementation will be given in child class"""

    def start(self) -> MessageReceiver:
        # Start theMessageReceiver synchronously (blocking).
        # return self if we already started the receiver
        if self._message_receiver_state == _MessageReceiverState.STARTED:
            return self

        with self._mutex:
            self._is_receiver_terminated(error_message=RECEIVER_TERMINATED_UNABLE_TO_START)
            # Even after acquiring lock still we have to check the state to avoid re-doing the work
            if self._message_receiver_state == _MessageReceiverState.STARTED:
                return self

            elif self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
                if self._messaging_service.is_connected:
                    self._message_receiver_state = _MessageReceiverState.STARTING
                    if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                        self.adapter.debug(' [%s] is %s', type(self).__name__,
                                           self._message_receiver_state.name)
                else:
                    logger.debug('Receiver is [%s]. MessagingService NOT connected',
                                 self._message_receiver_state.name)
                    error_message = RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED
                    logger.warning(error_message)
                    raise IllegalStateError(error_message)

                self._register_receiver_events()
                self._do_start()
                return self

    def _do_start(self):
        # Assume that this method is called after the mutex has already been acquired.
        # start the MessageReceiver (always blocking).
        errors = None
        try:
            with _Released(self._mutex):
                for topic, subscribed in self._topic_dict.items():
                    if not subscribed:
                        self._do_subscribe(topic)
                        self._topic_dict[topic] = True
        except PubSubPlusClientError as exception:  # pragma: no cover # Due to core error scenarios
            errors = str(exception)
            if self._message_receiver_state == _MessageReceiverState.STARTING:
                self._message_receiver_state = _MessageReceiverState.TERMINATED
            self.adapter.warning("%s %s", RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED,
                                 str(errors))
            raise PubSubPlusClientError \
                (message=f"{RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED}{str(errors)}") from exception
            # pragma: no cover # Due to core error scenarios
        if self._message_receiver_state == _MessageReceiverState.STARTING:
            self._running = True
            self._message_receiver_state = _MessageReceiverState.STARTED
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('%s is %s', type(self).__name__, _MessageReceiverState.STARTED.name)

    def _halt_messaging(self):
        """ for terminating appropriately based on the receiver type"""


class _DirectRequestReceiver(_MessageReceiver):
    def __init__(self, builder):
        super().__init__(builder)
        self._group_name = None
        self._msg_callback_func_routine = self.msg_callback_func_type(self._message_receive_callback_routine)
        self._dispatch_info = \
            self.SolClientReceiverCreateRxMsgDispatchFuncInfo(c_uint32(SOLCLIENT_DISPATCH_TYPE_CALLBACK),
                                                              self._msg_callback_func_routine,
                                                              py_object(self),
                                                              c_void_p(None))

    class SolClientReceiverCreateRxMsgDispatchFuncInfo(Structure) \
            :  # pylint: disable=too-few-public-methods, missing-class-docstring
        # """ Conforms to solClient_session_rxMsgDispatchFuncInfo """

        _fields_ = [
            ("dispatch_type", c_uint32),  # The type of dispatch described
            ("callback_p", CFUNCTYPE(c_int, c_void_p, c_void_p, py_object)),  # An application-defined callback
            # function; may be NULL if there is no callback.
            ("user_p", py_object),  # A user pointer to return with the callback; must be NULL if callback_p is NULL.
            ("rffu", c_void_p)  # Reserved for Future use; must be NULL
        ]
        # common for direct & RR receiver

    def _unsubscribe(self):
        # called as part of terminate
        if self._is_unsubscribed:
            return
        if self._topic_dict and self._messaging_service.is_connected:
            self._is_unsubscribed = True
            topics = [*copy.deepcopy(self._topic_dict)]
            # unsubscribe topics as part of teardown activity
            # must release mutex as do_unsubscribe is a blocking io call
            with _Released(self._mutex):
                for topic in topics:
                    try:
                        self._do_unsubscribe(topic)
                    except PubSubPlusClientError as exception:  # pragma: no cover # Due to core error scenarios
                        self.adapter.warning(exception)

    # pylint: disable=protected-access
    def _message_receive_callback_routine(self, _opaque_session_p, msg_p, _user_p) \
            :  # pragma: no cover
        # The message callback is invoked for each Direct/Request Reply message received by the Session
        # only enqueue message while the receiver is live
        if self._message_receiver_state not in [_MessageReceiverState.STARTING,
                                                _MessageReceiverState.STARTED]:
            # Unfortunately its not possible to determine how many
            # in-flight messages remaining in the  message window on shutdown.
            # Drop messages while terminating to prevent a race between
            # native layer message dispatch and draining the python
            # internal message queue for graceful terminate.
            return SOLCLIENT_CALLBACK_OK  # return the received message to native layer
        ret = SOLCLIENT_CALLBACK_TAKE_MSG # By default the Python API takes the received message
        void_pointer = None
        try:
            void_pointer = c_void_p(msg_p)
            rx_msg = _InboundMessage(_SolaceMessage(void_pointer))
            removed_message = self._message_receiver_queue.put(rx_msg, force=self._force, block=self._block)
            if removed_message:
                removed_message._solace_message.cleanup()
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('PUT message to %s buffer/queue', type(self).__name__)
        except QueueShutdown:
            ret = SOLCLIENT_CALLBACK_OK # Dropped message is returned to the C API
            if void_pointer:
                void_pointer.value = None
                rx_msg._solace_message.cleanup(as_detach=True)
            if logger.isEnabledFor(logging.INFO):  # pragma: no cover # Ignored due to log level
                self.adapter.info('DROPPED message since the receiver was terminated.')
        except Full:
            if void_pointer:
                void_pointer.value = None
                rx_msg._solace_message.cleanup(as_detach=True)

            if logger.isEnabledFor(logging.INFO):  # pragma: no cover # Ignored due to log level
                self.adapter.info('DROPPED message since there was no room left in the queue.')
            ret = SOLCLIENT_CALLBACK_OK # Dropped message is returned to the C API
        except Exception as exception:
            self.adapter.error(exception)
            raise PubSubPlusClientError(message=exception) from exception
        return ret

    def _do_subscribe(self, topic_subscription: str):
        # Subscribe to a topic (always blocking).
        if self._group_name is None or self._group_name == '':
            subscribe_to = topic_subscription
        else:
            subscribe_to = "#share/" + self._group_name + "/" + topic_subscription
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('SUBSCRIBE to: [%s]', subscribe_to)

        return_code = topic_subscribe_with_dispatch(self._messaging_service.session_pointer,
                                                    subscribe_to, self._dispatch_info)
        if return_code == SOLCLIENT_OK:
            self._topic_dict[topic_subscription] = True
        else:
            failure_message = f'{UNABLE_TO_UNSUBSCRIBE_TO_TOPIC} [{topic_subscription}].'
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description=f'{type(self).__name__}->_do_subscribe',
                                    exception_message=failure_message)
            self.adapter.warning('%s. Status code: %d. %s', failure_message, return_code,
                                 str(exception))  # pragma: no cover # Due to core error scenarios
            raise exception  # pragma: no cover

    def _do_unsubscribe(self, topic_subscription: str):
        # Unsubscribe from a topic (always blocking).
        if self._group_name is None or self._group_name == '':
            unsubscribe_to = topic_subscription
        else:
            unsubscribe_to = "#share/" + self._group_name + "/" + topic_subscription
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('UNSUBSCRIBE to: [%s]', unsubscribe_to)

        return_code = topic_unsubscribe_with_dispatch(self._messaging_service.session_pointer, unsubscribe_to,
                                                      self._dispatch_info)
        if topic_subscription in self._topic_dict:
            del self._topic_dict[topic_subscription]
        if return_code != SOLCLIENT_OK:
            failure_message = f'{UNABLE_TO_UNSUBSCRIBE_TO_TOPIC} [{unsubscribe_to}].'
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description=f'{type(self).__name__}->_do_unsubscribe',
                                    exception_message=failure_message)
            self.adapter.warning("%s", str(exception))
            raise exception
