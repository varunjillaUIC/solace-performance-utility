# solace-messaging-python-client
#
# Copyright 2025 Solace Corporation. All rights reserved.
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

# Module contains the implementation class and methods for the MessageQueueBrowser
# pylint: disable=too-many-instance-attributes, too-many-arguments, missing-function-docstring,no-else-raise
# pylint: disable=missing-module-docstring,protected-access,missing-class-docstring,inconsistent-return-statements
# pylint: disable=no-else-break,too-many-statements,too-many-public-methods,too-many-nested-blocks,no-else-return
# pylint: disable=expression-not-assigned,broad-except
# pylint: disable=too-many-lines, line-too-long


from queue import Empty
from typing import Union
import ctypes
import weakref
import logging
import concurrent
from threading import Lock
import time


import solace
from solace.messaging import _SolaceServiceAdapter
from solace.messaging.receiver.queue_browser import MessageQueueBrowser
from solace.messaging.receiver._impl._message_receiver import _MessageReceiverState
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.core._receive import _event_callback_func_type, \
    SolClientFlowCreateFuncInfo, _flow_msg_callback_func_type
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_IN_PROGRESS, SOLCLIENT_FLOW_PROP_BROWSER, \
    SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID, SOLCLIENT_FLOW_PROP_BIND_ENTITY_QUEUE, SOLCLIENT_FLOW_PROP_BIND_NAME, \
    SOLCLIENT_FLOW_PROP_SELECTOR, SOLCLIENT_FLOW_PROP_WINDOWSIZE, SOLCLIENT_FLOW_PROP_MAX_RECONNECT_TRIES, \
    SOLCLIENT_FLOW_PROP_RECONNECT_RETRY_INTERVAL_MS, SOLCLIENT_FLOW_PROP_BIND_BLOCKING,\
    SOLCLIENT_CALLBACK_OK, SOLCLIENT_CALLBACK_TAKE_MSG, SOLCLIENT_FAIL, \
    _SolClientFlowEvent, SOLCLIENT_TOPIC_DESTINATION, SOLCLIENT_QUEUE_DESTINATION, \
    SOLCLIENT_TOPIC_TEMP_DESTINATION, SOLCLIENT_QUEUE_TEMP_DESTINATION
from solace.messaging.config._solace_message_constants import GRACE_PERIOD_DEFAULT_MS, \
    BROWSER_CANT_TERMINATE_NOT_RUNNING, CCSMP_INFO_SUB_CODE, CCSMP_SUB_CODE, BROWSER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED, UNABLE_TO_ACK, \
    UNABLE_TO_RECEIVE_MESSAGE_BROWSER_ALREADY_TERMINATED, BROWSER_CANNOT_BE_STARTED_ALREADY_TERMINATED
from solace.messaging.core._core_api_utility import prepare_array
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusCoreClientError, \
    PubSubPlusClientError, IllegalStateError, InvalidDataTypeError
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.core._message import _SolClientDestination
from solace.messaging.receiver._impl._inbound_message import _InboundMessage
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.utils._solace_utilities import get_last_error_info, _PubSubPlusQueue, QueueShutdown, \
    is_type_matches
from solace.messaging.utils.life_cycle_control import TerminationNotificationListener, TerminationEvent
from solace.messaging.utils._impl._manageable_receiver import _PersistentReceiverInfo
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.receiver._inbound_message_utility import flow_destination, pause, nack_message
from solace.messaging.config.message_acknowledgement_configuration import Outcome


logger = logging.getLogger('solace.messaging.receiver')

def flow_cleanup(flow_p, session_p, queue_with_leftover_messages):
    #   Intended for weakref.finalize()
    #   Destroys a previously created Flow. Upon return, the opaque Flow pointer
    #   is set to NULL.
    #   This operation <b>must not</b> be performed in a Flow callback
    #   for the Flow being destroyed.
    # Args:
    #   flow_p :  A pointer to the opaque Flow pointer that was returned when
    #   the Session was created.
    #   session_p: The session pointer.
    #   lefotver_messages: the Queue.queue instance with unwarapped leftover message pointers.
    # Returns:
    #   SOLCLIENT_OK, SOLCLIENT_FAIL
    try:
        if session_p and flow_p:  # proceed to clean-up only if we still have  the session
            return_code = solace.CORE_LIB.solClient_flow_destroy(ctypes.byref(flow_p))
            if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to failure scenario
                exception: PubSubPlusCoreClientError = get_last_error_info(return_code=return_code,
                                                                           caller_description='Browser flow_cleanup')
                logger.warning(str(exception))
            leftover_messages = queue_with_leftover_messages.drain()
            for msg_p in leftover_messages:
                message_p = ctypes.c_void_p(msg_p)
                solace.CORE_LIB.solClient_msg_free(ctypes.byref(message_p))
    except PubSubPlusClientError as exception:  # pragma: no cover # Due to failure scenario
        logger.warning('Browser flow cleanup failed. Exception: %s ', str(exception))

def do_nothing():
    pass

class _BrowserTerminationEvent(TerminationEvent):
     # This class differs from the TerminationNotificationEvent used elsewhere in that
     # it carries a human readable message even if the cause of the termination
     # is not an exception: Garbage colllection or explicit termination.
    def __init__(self, cause: Union[PubSubPlusClientError, None], message:str, timestamp: Union[float, None]):
        # This constructor signature is different from TerminationNotificationEvent in solace/messaging/utils/_termination_notification_util.py
        # If no cause is provided, it defaults to "OK".
        # A separate message string can explain the reason of the termination even if not an error.
        # The timestamp is a standard python seconds since epoch float, defaulting to the time of construction if not provided.
        self._cause = cause if cause is not None else \
            PubSubPlusClientError("OK", SolClientSubCode.SOLCLIENT_SUBCODE_OK )
        self._message = message
        self._timestamp = timestamp if timestamp is not None else time.time()
    @property
    def timestamp(self):
        """Retrieves the timestamp of the event, number of seconds from the epoch of 1970-01-01T00:00:00Z

        Returns:
            long value of the timestamp
        """
        return self._timestamp

    @property
    def cause(self):
        """Retrieves exception associated with a given event

        Returns:
            exception for the event
        """
        return self._cause

    @property
    def message(self):
        return self._message



class _MessageQueueBrowser(MessageQueueBrowser):

    _event_callback_func = None
    _msg_callback_func = None

    def __init__(self, builder: '_MessageQueueBrowserBuilder'):  # pylint: disable=duplicate-code

        self._messaging_service = builder.messaging_service
        self._queue_name = builder.endpoint_to_consume_from.get_name()
        self._is_durable = builder.endpoint_to_consume_from.is_durable()
        self._message_selector = builder.message_selector
        self._window_size = builder.window_size
        self._reconnection_attempts = builder.reconnection_attempts
        self._reconnection_attempts_wait_interval = builder.reconnection_attempts_wait_interval

        self._id_info = f"[SERVICE: {str(hex(id(self._messaging_service.logger_id_info)))}] " \
            f"[RECEIVER: {str(hex(id(self)))}]"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})

        # This is where we keep the arriving messages, a windowful at a time.
        self._messages = _PubSubPlusQueue()

        self._event_callback_func = _event_callback_func_type(self._event_callback)
        self._msg_callback_func = _flow_msg_callback_func_type(self._msg_callback)
        self._flow_p = ctypes.c_void_p(None)
        self._finalizer = None

        self._flow_down = False
        self._state = _MessageReceiverState.NOT_STARTED
        # Lock for _state. Never held for any non-immediate length of time
        # (CCSMP call, user code, wait for other lock, etc)
        self._state_lock = Lock()
        # _state holds user visible state,
        # _flow_down indicates the flow got a DOWN_ERROR event.
        # On a DOWN_ERROR event, the browser only goes to TERMINATED state when it runs out of queued messsages.
        # When the user calls terminate() on the browser, the flow is stopped and receive_message() starts throwing.

        # These are only ever set while locked.
        # The callback is called when all three are set.
        # E.g. the callback could be set late when we already wanted to call it.
        # Or we produce the event on DOWN_ERROR, but only call when the queue runs dry.
        # This way the callback is called exactly once no matter the order and timing of
        # termination vs setting the callback.
        # A dead finalizer (one whose callback has executed or been detached) signifies
        # that the termination listener has been called already.
        self._termination_callback_atomizer_lock = Lock()
        self._termination_listener = None
        self._termination_finalizer = weakref.finalize(self, do_nothing)
        self._termination_event = None
        self._call_terminate = False
        self._terminate_called = False

        # Fulfilled with self on bind. Handed out to users on start_async()
        self._flow_start_promise = concurrent.futures.Future()

    # Creates the "flow_arr" representation of the flow properties from the top level configuration elements (window_size, etc)
    def _prepare_flow_props(self):
        props = {}
        props[SOLCLIENT_FLOW_PROP_BROWSER] = str(int(True))
        props[SOLCLIENT_FLOW_PROP_BIND_BLOCKING] = str(int(False))
        props[SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID] = SOLCLIENT_FLOW_PROP_BIND_ENTITY_QUEUE
        props[SOLCLIENT_FLOW_PROP_BIND_NAME] = self._queue_name
        if self._message_selector:
            props[SOLCLIENT_FLOW_PROP_SELECTOR] = self._message_selector
        if self._window_size > 0:
            props[SOLCLIENT_FLOW_PROP_WINDOWSIZE] = str(self._window_size)
        props[SOLCLIENT_FLOW_PROP_MAX_RECONNECT_TRIES] = str(self._reconnection_attempts)
        props[SOLCLIENT_FLOW_PROP_RECONNECT_RETRY_INTERVAL_MS] = str(self._reconnection_attempts_wait_interval)
        return prepare_array(props)

    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]: # pylint: disable=too-many-branches

        # Convert timeout to seconds.
        if timeout is not None:
            if not isinstance(timeout, (int, float)):
                raise TypeError(f"timeout must be int or float, got {type(timeout).__name__}")
            if timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            timeout = timeout / 1000.0 # ms to s

        # Wait for flow to come up.
        if self._state in [_MessageReceiverState.NOT_STARTED, _MessageReceiverState.STARTING]:
            start_time = time.time()
            try:
                self._flow_start_promise.result(timeout)
            except TimeoutError:
                return None
            except Exception:
                # This was logged properly where it was generated, no need to re-log.
                # Just stop waiting and handle the TERMINATED state below.
                pass
            end_time = time.time()
            if timeout is not None:
                timeout = timeout - (end_time - start_time)
                if timeout < 0:
                    return None
        # Bail if terminated
        if self._state in [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_BROWSER_ALREADY_TERMINATED)

        msg_p = None
        try:
            # Non-blocking pop attempt, reset window and actually start waiting if fails.
            msg_p = self._messages.get(block=False)
        except Empty:
            if self._flow_down and self._state not in \
                [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
                # We were holding off with termination until the queue runs dry, and it just did.
                self._delayed_terminate()

        except QueueShutdown:
            return None

        if msg_p is None and not self._flow_down:
            # re-open window
            # We don't lock against a race with terminate(), so it is possible to restart the flow
            # that's supposed to be stopped for good.
            # But it's not a big deal because we'll just ignore all the incoming messages,
            # which is harmless on a browser flow.
            return_code = solace.CORE_LIB.solClient_flow_start(self._flow_p)
            if return_code != SOLCLIENT_OK:  # pylint: disable=no-else-raise
                error_info = last_error_info(status_code=return_code, caller_desc="queue browser flow restart")
                self.adapter.warning("Browser Flow Start failed for Queue[%s] with sub code [%s]",
                                     self._queue_name, error_info[CCSMP_SUB_CODE])
                raise PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])

            # Wait for message (unless timeout was set to 0.)
            try:
                # If timeout is 0, don't block.
                # If non-zero number, wait that long.
                # If None, which is the default, block forever waiting for a message.
                msg_p = self._messages.get(block=(timeout != 0), timeout=timeout)
            except (Empty, QueueShutdown):
                return None
        if msg_p is None:
            return None
        # The raw pointer was saved on the queue, needs wrapping here.
        message_p = ctypes.c_void_p(msg_p)
        solace_message = _SolaceMessage(message_p)
        rx_msg = _InboundMessage(solace_message)
        return rx_msg

    def start_async(self) -> 'MessageQueueBrowser':
        if not self._messaging_service.is_connected:
            raise IllegalStateError(BROWSER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED)
        with self._state_lock:
            if self._state in [_MessageReceiverState.STARTING, _MessageReceiverState.STARTED]:
                return self._flow_start_promise
            if self._state in [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
                raise IllegalStateError(BROWSER_CANNOT_BE_STARTED_ALREADY_TERMINATED)

            self._state = _MessageReceiverState.STARTING
        self._flow_start_promise.set_running_or_notify_cancel()

        flow_func_info = SolClientFlowCreateFuncInfo(
            (ctypes.c_void_p(None), ctypes.c_void_p(None)),
            (self._event_callback_func, self),
            (self._msg_callback_func, self))

        flow_arr = self._prepare_flow_props()

        return_code = solace.CORE_LIB.solClient_session_createFlow(ctypes.cast(flow_arr, ctypes.POINTER(ctypes.c_char_p)),
                                                                   self._messaging_service.session.session_pointer,
                                                                   ctypes.byref(self._flow_p),
                                                                   ctypes.byref(flow_func_info),
                                                                   ctypes.sizeof(flow_func_info))

        if return_code != SOLCLIENT_IN_PROGRESS:  # pylint: disable=no-else-raise
            error_info = last_error_info(status_code=return_code, caller_desc="queue browser start")
            self.adapter.warning("Browser Flow creation failed for Queue[%s] with sub code [%s]",
                                 self._queue_name, error_info[CCSMP_SUB_CODE])
            self._state = _MessageReceiverState.TERMINATED
            self._flow_start_promise.set_exception(PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE]))

        self._finalizer = weakref.finalize(self, flow_cleanup, self._flow_p, self._messaging_service.session.session_pointer, self._messages)

        return self._flow_start_promise


    def start(self) -> 'MessageQueueBrowser':
        return self.start_async().result()


    def _event_callback(self, _opaque_flow_p, event_info_p, _user_p) \
            :  # pragma: no cover # Due to invocation in callbacks
        # Flow event callback from the C API.

        event = event_info_p.contents.flow_event

        if event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_DOWN_ERROR.value:
            if self._state in [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
                # Already terminating, ignore.
                return SOLCLIENT_CALLBACK_OK

            response_code = event_info_p.contents.response_code
            error_info = last_error_info(response_code, "browser flow event callback")
            logger.warning(str(error_info))
            exception = PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])
            if self._state == _MessageReceiverState.STARTING:
                self._flow_start_promise.set_exception(exception)
            self._state = _MessageReceiverState.TERMINATED
            with self._termination_callback_atomizer_lock:
                self._termination_event = _BrowserTerminationEvent(exception, "Flow DOWN_ERROR event", None)
            # We'll call the termination event listener when the queue runs empty.
            self._flow_down = True
        elif event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_UP_NOTICE.value:
            if self._state == _MessageReceiverState.STARTING:
                self._state = _MessageReceiverState.STARTED
                self._update_destination() # This is an immediate, non-network CCSMP call, fine in the callback.
                self._flow_start_promise.set_result(self)
        elif event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_BIND_FAILED_ERROR.value:
            response_code = event_info_p.contents.response_code
            error_info = last_error_info(response_code, "browser flow event callback")
            logger.warning(str(error_info))
            exception = PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])
            if self._state == _MessageReceiverState.STARTING:
                self._flow_start_promise.set_exception(exception)
            self._state = _MessageReceiverState.TERMINATED
        else:
            self.adapter.debug("Browser flow inconsequential event: %d", event)

        return SOLCLIENT_CALLBACK_OK


    def _msg_callback(self, _opaque_flow_p, msg_p, _user_p):  # pragma: no cover
        if self._state == _MessageReceiverState.TERMINATING:
            return SOLCLIENT_CALLBACK_OK # Release the received message, we don't want it anymore.
        if self._state == _MessageReceiverState.TERMINATED:
            # In the terminated state we think we stopped the flow, but apparently we didn't.
            # So let's do it again.
            pause(self._flow_p)
            return SOLCLIENT_CALLBACK_OK # Release the received message, we don't want it anymore.

        try:
            self._messages.put(msg_p)
        except QueueShutdown:
            # This can easily happen during a terminate() call, because we don't lock.
            # But since this is a browser flow, it is entirely inconsequential.
            return SOLCLIENT_CALLBACK_OK # Release the received message, we can't save it.
        except Exception as exception:
            self.adapter.error("%s ", exception)
            return SOLCLIENT_CALLBACK_OK # Release the received message, we can't save it.
        return SOLCLIENT_CALLBACK_TAKE_MSG # take the received message from CCSMP



    def is_running(self) -> bool:
        return self._state == _MessageReceiverState.STARTED

    def is_terminated(self) -> bool:
        return self._state == _MessageReceiverState.TERMINATED

    def is_terminating(self) -> bool:
        return self._state == _MessageReceiverState.TERMINATING

    def _update_destination(self):
        try:
            destination = _SolClientDestination()
            return_code = flow_destination(self._flow_p, destination)
            if return_code == SOLCLIENT_OK:
                self._queue_name = destination.dest.decode()
                dest_type = destination.destType
                if dest_type in [SOLCLIENT_TOPIC_DESTINATION, SOLCLIENT_QUEUE_DESTINATION]:
                    self._is_durable = True
                elif dest_type in [SOLCLIENT_TOPIC_TEMP_DESTINATION, SOLCLIENT_QUEUE_TEMP_DESTINATION]:
                    self._is_durable = False
            elif return_code == SOLCLIENT_FAIL:  # pragma: no cover
                self.adapter.warning(str(last_error_info()))
        except ValueError as error:
            # This exception can be raised when we fail to decode the destination name. This is unlikely to occur
            # since it would only occur if there was a problem translating the C character array
            # into a UTF-8 string.
            self.adapter.warning(str(error))

    def receiver_info(self) -> _PersistentReceiverInfo:
        return _PersistentReceiverInfo(self._is_durable, self._queue_name)

    def _delayed_terminate(self):
        # Internal method factoring out the nitty-gritty of the delayed termination
        # of a DOWN_ERROR flow: notification and state transition.
        with self._state_lock:
            if self._state not in \
                [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
                self._state = _MessageReceiverState.TERMINATED
        # call termination listener.
        termination_listener = None
        detach = None
        with self._termination_callback_atomizer_lock:
            self._call_terminate = True
            termination_listener = self._termination_listener
            detach = self._termination_finalizer.detach()
        if termination_listener is not None and detach is not None:
            termination_listener.on_termination(self._termination_event)


    def remove(self, message: InboundMessage):
        is_type_matches(message, InboundMessage, logger=logger)
        if self._state != _MessageReceiverState.STARTED:
            exception_message = f"{UNABLE_TO_ACK}: {self._state}"
            self.adapter.warning(exception_message)
            raise IllegalStateError(exception_message)
        if self._flow_down:
            # The jig is up, report termination.
            self._delayed_terminate()
        return_code = nack_message(self._flow_p, message.message_id, Outcome.ACCEPTED)
        if return_code != SOLCLIENT_OK:
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='PersistentMessageReceiver->settle')
            self.adapter.warning(str(exception))
            raise exception

    def set_termination_notification_listener(self, listener: TerminationNotificationListener):
        termination_event = None
        call_terminate = False
        detach = None
        if listener is not None and not hasattr(listener, 'on_termination'):
            raise InvalidDataTypeError(f"Expected to receive instance of {TerminationNotificationListener}, " \
                                       f"but received instance of {type(listener).__name__} instead.")
        if listener is not None:
            with self._termination_callback_atomizer_lock:
                self._termination_listener = listener
                termination_event = self._termination_event
                call_terminate = self._call_terminate
                detach = self._termination_finalizer.detach()
                if (not call_terminate) and (detach is not None):
                    self._termination_finalizer = weakref.finalize(self, listener.on_termination, \
                        termination_event or \
                            _BrowserTerminationEvent(None, "Browser garbage collected", None))
        else:
            with self._termination_callback_atomizer_lock:
                self._termination_listener = None
                detach = self._termination_finalizer.detach()
                if detach is not None:
                    self._termination_finalizer = weakref.finalize(self, do_nothing)

        if call_terminate and detach is not None:
            listener.on_termination(termination_event)

    def terminate(self, grace_period: int = GRACE_PERIOD_DEFAULT_MS):
        with self._state_lock:
            if self._state in [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
                return
            if self._state != _MessageReceiverState.STARTED:
                raise IllegalStateError(BROWSER_CANT_TERMINATE_NOT_RUNNING)
            self._state = _MessageReceiverState.TERMINATING

        self._messages.shutdown()

        return_code = pause(self._flow_p)
        # This calls flow_destroy(). Using a finalizer makes sure it's only called once.
        # Since there is no message callback on the browser,
        # user code can never call terminate() from a callback of the same flow.
        self._finalizer()
        self._state = _MessageReceiverState.TERMINATED

        termination_listener = None
        detach = None
        with self._termination_callback_atomizer_lock:
            self._call_terminate = True
            self._termination_event = _BrowserTerminationEvent(None, "Termination requested", None)
            termination_listener = self._termination_listener
            if termination_listener is not None:
                detach = self._termination_finalizer.detach()

        if (termination_listener is not None) and (detach is not None):
            termination_listener.on_termination(self._termination_event)

        if return_code != SOLCLIENT_OK:  # pylint: disable=no-else-raise
            error_info = last_error_info(status_code=return_code, caller_desc="queue browser flow stop for terminate")
            self.adapter.warning("Browser Flow Stop failed for Queue[%s] with sub code [%s] during terminate",
                                 self._queue_name, error_info[CCSMP_SUB_CODE])
            raise PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])


    def terminate_async(self, grace_period: int = GRACE_PERIOD_DEFAULT_MS) -> concurrent.futures.Future:
        # Doesn't actually take time, and can be run on any thread,
        # so just fake the promise and return a pre-resolved future:
        ret = concurrent.futures.Future()
        try:
            self.terminate()
        except Exception as e:
            ret.set_exception(e)
            return ret
        ret.set_result(None)
        return ret
