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

# Module contains the implementation class and methods for the PersistentMessageReceiver
# pylint: disable=too-many-instance-attributes, too-many-arguments, missing-function-docstring,no-else-raise
# pylint: disable=missing-module-docstring,protected-access,missing-class-docstring,inconsistent-return-statements
# pylint: disable=no-else-break,too-many-statements,too-many-public-methods,too-many-nested-blocks,no-else-return
# pylint: disable=expression-not-assigned,broad-except
# pylint: disable=too-many-lines

import concurrent
import ctypes
import logging
import queue
import time
import weakref
from ctypes import c_void_p, POINTER, c_char_p, cast, byref, sizeof
from queue import Queue
from typing import Union

import solace
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._ccsmp_property_mapping import end_point_props, CCSMP_SESSION_PROP_MAPPING
from solace.messaging.config._ccsmp_property_mapping import flow_props
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_FLOW_PROP_BIND_NAME, \
    SOLCLIENT_FLOW_PROP_BIND_ENTITY_DURABLE, SOLCLIENT_CALLBACK_TAKE_MSG, SOLCLIENT_CALLBACK_OK, \
    SOLCLIENT_ENDPOINT_PROP_NAME, _SolClientFlowEvent, HIGH_THRESHOLD, \
    LOW_THRESHOLD, SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE, SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_NONEXCLUSIVE, \
    SOLCLIENT_FLOW_PROP_SELECTOR, SOLCLIENT_FAIL, SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_REJECTED, \
    SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_FAILED
from solace.messaging.config._solace_message_constants import UNABLE_TO_SUBSCRIBE_TO_TOPIC, DISPATCH_FAILED, \
    UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_NOT_STARTED, RECEIVER_TERMINATED, UNABLE_TO_UNSUBSCRIBE_TO_TOPIC, FLOW_PAUSE, \
    FLOW_RESUME, \
    UNABLE_TO_ACK, RECEIVER_TERMINATED_UNABLE_TO_START, FLOW_INACTIVE, FLOW_DOWN, FLOW_RESUME_FAILURE, \
    FLOW_RESUME_SUCCESS, RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED, CCSMP_INFO_SUB_CODE, CCSMP_SUB_CODE
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationStrategy
from solace.messaging.config.receiver_activation_passivation_configuration import ReceiverStateChangeListener, \
    ReceiverState
from solace.messaging.config.message_acknowledgement_configuration import Outcome
from solace.messaging.core._core_api_utility import prepare_array
from solace.messaging.core._message import _SolClientDestination
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.core._receive import _event_callback_func_type, \
    SolClientFlowCreateFuncInfo, \
    _flow_msg_callback_func_type
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, IllegalStateError, \
    PubSubPlusCoreClientError, MessageReplayError
from solace.messaging.receiver._impl._inbound_message import _InboundMessage
from solace.messaging.receiver._impl._message_receiver import _MessageReceiver, _MessageReceiverState
from solace.messaging.receiver._impl._receiver_utilities import validate_subscription_type
from solace.messaging.receiver._inbound_message_utility import pause, resume, \
    flow_topic_subscribe_with_dispatch, flow_topic_unsubscribe_with_dispatch, end_point_provision, \
    topic_endpoint_subscribe, flow_destination, nack_message
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.receiver.persistent_message_receiver import PersistentMessageReceiver
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._impl._manageable_receiver import _PersistentReceiverInfo
from solace.messaging.utils._solace_utilities import get_last_error_info, is_type_matches, is_not_negative, \
    convert_ms_to_seconds, COMPLETED_FUTURE, _Released, _PubSubPlusQueue, QueueShutdown, \
    _SolaceThread, Holder
from solace.messaging.builder._impl._message_replay_config import incorporate_replay_props, replay_error_list

logger = logging.getLogger('solace.messaging.receiver')


def flow_cleanup(flow_p, session_p):
    #   Destroys a previously created Flow. Upon return, the opaque Flow pointer
    #   is set to NULL.
    #   This operation <b>must not</b> be performed in a Flow callback
    #   for the Flow being destroyed.
    # Args:
    #  flow_p :  A pointer to the opaque Flow pointer that was returned when
    #   the Session was created.
    # Returns:
    #   SOLCLIENT_OK, SOLCLIENT_FAIL
    try:
        if session_p and flow_p:  # proceed to clean-up only if we still have  the session
            return_code = solace.CORE_LIB.solClient_flow_destroy(ctypes.byref(flow_p))
            if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to failure scenario
                exception: PubSubPlusCoreClientError = get_last_error_info(return_code=return_code,
                                                                           caller_description='flow_cleanup')
                logger.warning(str(exception))
    except PubSubPlusClientError as exception:  # pragma: no cover # Due to failure scenario
        logger.warning('Flow cleanup failed. Exception: %s ', str(exception))


class PersistentStateChangeListenerThread(_SolaceThread) \
        :  # pylint: disable=missing-class-docstring, too-many-instance-attributes, too-many-arguments
    # Thread used to dispatch received flow state on a receiver.

    def __init__(self, owner_info: str, owner_logger: 'logging.Logger', state_change_queue: Queue,
                 receiver_state_change_listener: ReceiverStateChangeListener,
                 messaging_service, *args, **kwargs):
        super().__init__(owner_info, owner_logger, *args, **kwargs)
        self._state_change_queue = state_change_queue
        self.receiver_state_change_listener = receiver_state_change_listener
        self._running = False
        self._messaging_service_state = messaging_service.state

    def _on_join(self):
        self._state_change_queue.shutdown()

    def run(self):
        # Start running thread
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] started', type(self).__name__)

        def dispatch_state_change_event(listener, old_state, new_state, time_stamp):
            try:
                listener.on_change(old_state, new_state, time_stamp)
            except Exception as exception \
                    :  # pylint: disable=broad-except  # pragma: no cover # Due to failure scenario
                self.adapter.warning("%s %s", DISPATCH_FAILED, str(exception))

        while self._is_running.is_set():
            # This will block until the state change queue has an item to pop
            try:
                old_state, new_state, time_stamp = self._state_change_queue.get()
            except QueueShutdown as error:
                self.adapter.debug(f"Persistent receiver state change listener queue was " \
                                   f"shutdown with the following message: {str(error)}")
                break
            dispatch_state_change_event(self.receiver_state_change_listener, old_state, new_state, time_stamp)
        # drain the remaining events
        events = self._state_change_queue.drain()
        # ensure all remaining events are dispatched
        for old_state, new_state, time_stamp in events:
            dispatch_state_change_event(self.receiver_state_change_listener, old_state, new_state, time_stamp)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] exited', type(self).__name__)


class PersistentMessageReceiverThread(_SolaceThread):  # pylint: disable=missing-class-docstring
    # Thread used to dispatch received messages on a receiver.
    def __init__(self, owner_info: str, owner_logger: 'logging.Logger', persistent_message_receiver,
                 message_pop_func, messaging_service, auto_ack, stop_event, thread_on_join_func,
                 *args, **kwargs):
        super().__init__(owner_info, owner_logger, *args, **kwargs)
        self._stop_event = stop_event
        self._persistent_message_receiver = persistent_message_receiver
        self._message_handler = None  # update via property every time new message handler is provided
        # closure function to return an inbound message
        # function signature is parameterless
        self._message_pop = message_pop_func
        self._message_on_join = thread_on_join_func
        self._messaging_service = messaging_service
        self._auto_ack = auto_ack

    def _on_join(self):
        self._stop_event.set()
        self._message_on_join()

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
        while not self._persistent_message_receiver.stop_event.is_set():
            inbound_message = None
            try:
                inbound_message = self._message_pop()
            except QueueShutdown:
                break
            if inbound_message:
                try:
                    self._message_handler.on_message(inbound_message)
                    if self._auto_ack:  # if auto ack is enabled send ack to broker after sending  the message
                        self._messaging_service._increase_duplicate_ack_count()
                        self._persistent_message_receiver._settle(inbound_message)
                except Exception as exception:  # pylint: disable=broad-except
                    self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                         type(self._message_handler),
                                         str(exception))
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] stopped', type(self).__name__)

class _PersistentMessageReceiver(_MessageReceiver, PersistentMessageReceiver) \
        :  # pylint: disable=missing-class-docstring, too-many-ancestors, too-many-instance-attributes

    _event_callback_func_routine = None
    _flow_msg_callback_func_routine = None

    def __init__(self, builder: '_PersistentMessageReceiverBuilder') \
            :  # pylint: disable=duplicate-code
        super().__init__(builder)
        self._flow_p = c_void_p(None)
        self._messaging_service = builder.messaging_service
        self._missing_resource_strategy = builder.missing_resources_creation_strategy
        self._replay_strategy = builder.replay_strategy
        self._is_durable = builder.endpoint_to_consume_from.is_durable()
        self._is_exclusive = builder.endpoint_to_consume_from.is_exclusively_accessible()
        self._queue_name = builder.endpoint_to_consume_from.get_name()
        self._auto_ack = builder.auto_ack
        self._allow_rejected = builder.allow_rejected
        self._allow_failed = builder.allow_failed
        # we can add topic subscription before starting the flow only for durable queue,
        # but for non durable queue we can add topic subscription only after starting the flow
        self._end_point_topics_list = list(
            topic for topic in builder.topics) if self._is_durable else []
        self._topic_list = list(
            topic for topic in builder.topics) if not self._is_durable else []

        self._end_point_props = end_point_props
        self._msg_wait_time = None
        self._receiver_state_change_listener = builder.receiver_state_change_listener
        self._flow_state = []  # to keep track of flow state when listener is provided
        self._running = False  # used for pause & resume when True application callbacks should be dispatching
        self._flow_stopped = True  # used for flow control to close the flow message window
        self._end_point_arr = None
        self._int_metrics = self._messaging_service.metrics()
        self._state_change_listener_queue = None
        if self._receiver_state_change_listener:
            self._state_change_listener_queue = _PubSubPlusQueue()
            self._state_change_listener_thread = None
        self._flow_msg_callback_func_routine = _flow_msg_callback_func_type(
            self._flow_message_receive_callback_routine)
        self._message_receiver_state = _MessageReceiverState.NOT_STARTED
        self._config = {}

        # pylint: disable=unnecessary-comprehension
        # add props received from builder
        for key, value in builder.config.items():
            if key in CCSMP_SESSION_PROP_MAPPING:
                # Note: Here order if elif to check bool & int is very important don't change them
                if isinstance(value, bool):
                    value = str(int(value))
                elif isinstance(value, int):
                    value = str(value)

                self._config[CCSMP_SESSION_PROP_MAPPING[key]] = value
        if not self._is_durable and self._queue_name is None:
            # don't add  SOLCLIENT_FLOW_PROP_BIND_NAME when we didn't receive queue name for non-durable exclusive queue
            pass
        else:
            self._config[SOLCLIENT_FLOW_PROP_BIND_NAME] = self._queue_name
        self._config[SOLCLIENT_FLOW_PROP_BIND_ENTITY_DURABLE] = str(int(self._is_durable))
        if builder.message_selector:  # Message selector applied here
            self._config[SOLCLIENT_FLOW_PROP_SELECTOR] = builder.message_selector
        self._config[SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_REJECTED] = str(int(builder.allow_rejected))
        self._config[SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_FAILED] = str(int(builder.allow_failed))
        self._event_callback_func_routine = _event_callback_func_type(self._event_callback_routine)
        self._flow_msg_callback_func_routine = self.msg_callback_func_type(self._flow_message_receive_callback_routine)
        # Add REPLAY property based on ReplayStrategy
        self._config = incorporate_replay_props(self._replay_strategy, self._config)
        self._config = {**flow_props, **self._config}  # Merge & override happens here
        self._flow_arr = prepare_array(self._config)
        self._is_receiver_down = False  # when receiver goes down don't attempt to deliver the messages
        self._flow_clean_not_needed = False  # set to True when flow clean up is not needed.
        self._persistent_state_change_listener_holder = Holder()
        self._persistent_message_receiver_thread_holder = Holder()

        # initialize the message queue threshold marks

        def on_low_threshold():
            if self._flow_stopped \
                and self._message_receiver_state == _MessageReceiverState.STARTED:
                return_code = resume(self._flow_p)  # open C layer flow message window
                if return_code == SOLCLIENT_OK:
                    self._flow_stopped = False  # set C layer flow stopped state flag to started
                    self.adapter.info("%s", FLOW_RESUME)

        def on_high_threshold():
            if not self._flow_stopped:
                # close c layer flow message window
                return_code = pause(self._flow_p)
                if return_code == SOLCLIENT_OK:
                    # set c layer flow stopped state flag to stopped
                    self._flow_stopped = True
                    self.adapter.info("%s", FLOW_PAUSE)

        self._message_receiver_queue.register_on_low_watermark(on_low_threshold, LOW_THRESHOLD)
        self._message_receiver_queue.register_on_high_watermark(on_high_threshold, HIGH_THRESHOLD)

        # clean-up the flow as part of gc
        self._finalizer = weakref.finalize(self, flow_cleanup, self._flow_p,
                                           self._messaging_service.session.session_pointer)

        self._persistent_state_change_listener_finalizer = \
            weakref.finalize(self,
                             persistent_state_change_listener_cleanup,
                             self._persistent_state_change_listener_holder)

        self._persistent_message_receiver_thread_finalizer = \
            weakref.finalize(self,
                             persistent_message_receiver_thread_cleanup,
                             self._persistent_message_receiver_thread_holder)

    @property
    def is_receiver_down(self):
        return self._is_receiver_down

    def _start_state_listener(self):
        # This method will be used to start the receiver state change listener thread
        if self._receiver_state_change_listener:
            self._state_change_listener_thread = PersistentStateChangeListenerThread(
                self._id_info, logger, self._state_change_listener_queue, self._receiver_state_change_listener,
                self._messaging_service)
            self._persistent_state_change_listener_holder.value = self._state_change_listener_thread
            self._state_change_listener_thread.daemon = True
            self._state_change_listener_thread.start()

    def _flow_message_receive_callback_routine(self, _opaque_flow_p, msg_p, _user_p):  # pragma: no cover
        # The message callback will be invoked for each Persistent message received by the Session
        # only enqueue message while the receiver is live
        if self._message_receiver_state not in [_MessageReceiverState.STARTING,
                                                _MessageReceiverState.STARTED]:
            # Unfortunately its not possible to determine how many
            # in-flight messages remaining in the flow message window on shutdown.
            # Drop messages while terminating to prevent a race between
            # native layer message dispatch and draining the python
            # internal message queue for graceful terminate.
            return SOLCLIENT_CALLBACK_OK  # return the received message to native layer
        # python receiver is life enqueue native message to python delivery queue
        ret = SOLCLIENT_CALLBACK_TAKE_MSG # take the received message from native caller
        message_p = c_void_p(msg_p)
        try:
            solace_message = _SolaceMessage(message_p)
            rx_msg = _InboundMessage(solace_message)
            self._msg_queue_put(rx_msg)
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('PUT message to %s buffer/queue', PersistentMessageReceiver.__name__)
        except QueueShutdown:
            if message_p:
                message_p.value = None
            ret = SOLCLIENT_CALLBACK_OK # return the message
        except Exception as exception:
            self.adapter.error("%s ", exception)
            raise PubSubPlusClientError(message=exception) from exception
        return ret  # signal back to native layer ownship of message

    def _event_callback_routine(self, _opaque_flow_p, event_info_p, _user_p) \
            :  # pragma: no cover # Due to invocation in callbacks
        # Flow event callback from the C API.

        event = event_info_p.contents.flow_event

        if event in [_SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_DOWN_ERROR.value]:

            self._flow_clean_not_needed = True
            self._is_receiver_down = True  # signals receiver thread stops from delivering messages

            response_code = event_info_p.contents.response_code

            error_info = last_error_info(response_code, "flow callback")

            # set the receiver state to Terminated when the flow event or session is down.
            self.adapter.info(FLOW_DOWN)
            self._on_receiver_down(error_info)
        #  pause the receiver thread when flow goes inactive this will also prevents
        #  the race between receive_async &
        #  receive_message when we put None to unblock receive_message
        if event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_INACTIVE.value:
            self.adapter.info(FLOW_INACTIVE)
        self.__do_state_change_event(event)
        return SOLCLIENT_CALLBACK_OK

    def __do_state_change_event(self, event):
        if self._state_change_listener_queue:
            events = {_SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_ACTIVE.value:
                          (ReceiverState.PASSIVE, ReceiverState.ACTIVE),
                      _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_INACTIVE.value:
                          (ReceiverState.ACTIVE, ReceiverState.PASSIVE)}
            if event in events:
                old_state, new_state = events[event]
                time_stamp = int(time.time() * 1000)
                try:
                    self._state_change_listener_queue.put((old_state, new_state, time_stamp))
                except QueueShutdown:
                    self.adapter.info(f"While trying to buffer the state change events, the buffer was shutdown. " \
                                      f"The old state was: {old_state}. " \
                                      f"The new state was: {new_state}. " \
                                      f"The timestamp was: {time_stamp}")

    def _create_end_point(self):
        # create only for durable Queue, non-durable(temporary) Queue will be created during flow creation automatically
        if self._missing_resource_strategy and \
                self._missing_resource_strategy.value == MissingResourcesCreationStrategy.CREATE_ON_START.value and \
                self._is_durable:

            self._end_point_props[SOLCLIENT_ENDPOINT_PROP_NAME] = self._queue_name  # set Queue name
            if not self._is_exclusive:
                self._end_point_props[SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE] = \
                    SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_NONEXCLUSIVE

            self._end_point_arr = prepare_array(self._end_point_props)

            # provision endpoint and ignore dup provisions
            # CREATE_ON_START should not fail on already provisioned endpoints
            return_code = end_point_provision(self._end_point_arr,
                                              self._messaging_service.session.session_pointer,
                                              ignore_already_provisioned=True)

            error_info = last_error_info(status_code=return_code, caller_desc="Endpoint Creation ")

            if return_code != SOLCLIENT_OK:
                self.adapter.warning("%s creation failed with the following sub code %s(%d)", self._queue_name,
                                     error_info[CCSMP_SUB_CODE], error_info[CCSMP_INFO_SUB_CODE])
                raise PubSubPlusClientError(f"{self._queue_name}creation failed with the " \
                                            f"following sub code " \
                                            f"{error_info[CCSMP_SUB_CODE]}({error_info[CCSMP_INFO_SUB_CODE]}) ")
            elif return_code == SOLCLIENT_OK:
                self.adapter.info("%s endpoint is created successfully", self._queue_name)

    def _msg_queue_put(self, message: 'InboundMessage'):
        self._message_receiver_queue.put(message)

    def _msg_queue_get(self, block: bool = True, timeout: float = None):
        if timeout is not None:
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('Get message from queue/buffer with block: %s, timeout: %f', block, timeout)
        elif timeout is None and logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('Get message from queue/buffer with block: %s, timeout: %s', block, timeout)
        msg = self._message_receiver_queue.get(block, timeout)

        return msg

    def _resource_cleanup(self):
        self.receiver_queue.shutdown() # this wake up the thread
        with self._start_async_lock:
            if self._start_future is None:
                self._start_future = COMPLETED_FUTURE
        with self._terminate_async_lock:
            if self._terminate_future is None:
                self._terminate_future = COMPLETED_FUTURE
        if self._message_receiver_thread is not None:
            # stop the receiver thread
            # set termination flag first
            self.stop_event.set()  # this stops the thread
            with _Released(self._mutex):
                self._message_receiver_thread.join()

        # stop the state change listener thread
        if self._receiver_state_change_listener:
            with _Released(self._mutex):
                self._state_change_listener_thread.join()

        self._executor.shutdown(wait=False)
        session_p = self._messaging_service.session.session_pointer \
            if self._messaging_service.session and self._messaging_service.session.session_pointer \
            else c_void_p(None)
        # # release c resources
        if not self._flow_clean_not_needed:
            with _Released(self._mutex):
                flow_cleanup(self._flow_p, session_p)
            self._flow_clean_not_needed = False
        # shut down the termination event dispatcher thread
        with _Released(self._mutex):
            if self._termination_notification_dispatcher is not None:
                self._termination_notification_dispatcher.shutdown()

    def __do_start(self):  # pylint: disable=no-else-raise
        # Method to start

        flow_func_info = SolClientFlowCreateFuncInfo(
            (c_void_p(None), c_void_p(None)),
            (self._event_callback_func_routine, self),
            (self._flow_msg_callback_func_routine, self))
        # Creates a new Flow within a specified Session. Flow characteristics and behavior are
        # defined by Flow properties. The Flow properties
        #   are supplied as an array of name/value pointer pairs, where the name and value are both strings.
        #   \ref flowProps "FLOW" and \ref endpointProps "ENDPOINT" configuration property names are
        # processed; other property names
        #   are ignored. If the Flow creation specifies a non-durable endpoint, ENDPOINT properties can
        # be used to change the default
        #   properties on the non-durable endpoint. Any values not supplied are set to default values.
        #
        #   When the Flow is created, an opaque Flow pointer is returned to the caller, and this value
        # is then used for any
        #   Flow-level operations (for example, starting/stopping a Flow, getting statistics, sending
        # an acknowledgment).
        #   The passed-in structure functInfo_p provides information on the message receive callback
        #   function and the Flow event function which the application has provided for this Flow.
        #   Both of these callbacks are mandatory. The message receive callback is invoked for each
        #   received message on this Flow. The Flow event callback is invoked when Flow events
        #   occur, such as the Flow going up or down. Both callbacks are invoked in the context
        #   of the Context thread to which the controlling Session belongs.
        #
        #   Flow creation can be carried out in a blocking or
        #   non-blocking mode, depending upon the Flow property
        #   SOLCLIENT_FLOW_PROP_BIND_BLOCKING.
        #   In blocking mode, the calling thread is blocked until the Flow connection attempt either
        #   succeeds or is determined to have failed. If the connection succeeds, SOLCLIENT_OK is
        #   returned, and if the Flow could not be connected, SOLCLIENT_NOT_READY is returned.
        #   In non-blocking mode, SOLCLIENT_IN_PROGRESS is returned upon a successful Flow create
        #   request, and the connection attempt proceeds in the background.
        #   In both a non-blocking and blocking mode, a Flow event is generated for the Session:
        #   SOLCLIENT_FLOW_EVENT_UP_NOTICE, if the Flow was connected successfully; or
        #   SOLCLIENT_FLOW_EVENT_BIND_FAILED_ERROR, if the Flow failed to connect.
        #  For blocking mode, the Flow event is issued before the call to
        #  solClient_session_createFlow() returns. For non-blocking mode, the timing is undefined (that is,
        #  it could occur before or after the call returns, but it will typically be after).
        #  A Flow connection timer, controlled by the Flow property
        #  SOLCLIENT_SESSION_PROP_BIND_TIMEOUT_MS, controls the maximum amount of
        #  time a Flow connect attempt lasts for. Upon expiry of this time,
        #  a SOLCLIENT_FLOW_EVENT_BIND_FAILED_ERROR event is issued for the Session.
        #  If there is an error when solClient_session_createFlow() is invoked, then SOLCLIENT_FAIL
        #  is returned, and a Flow event is not subsequently issued. Thus, the caller must
        #  check for a return code of SOLCLIENT_FAIL if it has logic that depends upon a subsequent
        #  Flow event to be issued.
        #  For a non-blocking Flow create invocation, if the Flow create attempt eventually
        #  fails, the error information that indicates the reason for the failure cannot be
        #  determined by the calling thread. It must be discovered through the Flow event
        #  callback (and solClient_getLastErrorInfo can be called in the Flow event callback
        #  to get further information).
        #  For a blocking Flow create invocation, if the Flow create attempt does not
        #  return SOLCLIENT_OK, then the calling thread can determine the failure reason by immediately
        #  calling solClient_getLastErrorInfo. For a blocking Flow creation, SOLCLIENT_NOT_READY is returned
        #  if the created failed due to the bind timeout expiring (see SOLCLIENT_FLOW_PROP_BIND_TIMEOUT_MS).
        #  Note that the property values are stored internally in the API and the caller does not have to maintain
        #  the props array or the strings that are pointed to after this call completes. The API does not modify any of
        #  the strings pointed to by props when processing the property list.
        #
        #  If the flow property SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID is set to SOLCLIENT_FLOW_PROP_BIND_ENTITY_TE,
        #  the flow Topic property SOLCLIENT_FLOW_PROP_TOPIC <b>must</b> be set, which will replace any existing
        #  topic on the topic-endpoint.
        #
        #  <b>WARNING:</b> By default the SOLCLIENT_FLOW_PROP_ACKMODE is set to SOLCLIENT_FLOW_PROP_ACKMODE_AUTO,
        #  which automatically acknowledges all received messages.
        # Function SolClient_flow_sendAck returns SOLCLIENT_OK
        #  in the mode SOLCLIENT_FLOW_PROP_ACKMODE_AUTO, but with a warning that solClient_flow_sendAck
        #  is ignored as flow is in auto-ack mode.
        # return SOLCLIENT_OK, SOLCLIENT_FAIL, SOLCLIENT_NOT_READY, SOLCLIENT_IN_PROGRESS
        with _Released(self._mutex):
            return_code = solace.CORE_LIB.solClient_session_createFlow(cast(self._flow_arr, POINTER(c_char_p)),
                                                                       self._messaging_service.session.session_pointer,
                                                                       byref(self._flow_p),
                                                                       byref(flow_func_info),
                                                                       sizeof(flow_func_info))
        if return_code != SOLCLIENT_OK:  # pylint: disable=no-else-raise
            error_info = last_error_info(status_code=return_code, caller_desc="flow topic add sub ")
            self.adapter.warning("Flow creation failed for Queue[%s] with sub code [%s]",
                                 self._queue_name, error_info[CCSMP_SUB_CODE])
            # Cleanup any resources and update the state to TERMINATED before raising the exception
            self._cleanup()
            if error_info[CCSMP_SUB_CODE] in replay_error_list:
                raise MessageReplayError(error_info, error_info[CCSMP_INFO_SUB_CODE])
            else:
                raise PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])
        else:
            self._flow_stopped = False  # set C layer flow stopped state flag to started
            # can not hold mutex on flow start as failure can occur deadlocking the context thread
            with _Released(self._mutex):
                return_code = resume(self._flow_p)  # open C layer flow message window
            if return_code != SOLCLIENT_OK:
                last_error = last_error_info(return_code, f"{type(self).__name__}->__do_start")
                session_p = self._messaging_service.session.session_pointer
                if session_p:
                    flow_cleanup(flow_p=self.flow_p, session_p=session_p)
                self.adapter.warning('%s. Status code: %d. %s',
                                     FLOW_RESUME_FAILURE,
                                     return_code, last_error)
                raise PubSubPlusClientError(message=f'{FLOW_RESUME_FAILURE}. '
                                                    f'Status code: {return_code}. {last_error}')
            self.adapter.info("%s", FLOW_RESUME_SUCCESS)
            # must check state after flow start to ensure an error did not occur
            if self._message_receiver_state == _MessageReceiverState.STARTING:
                self._message_receiver_state = _MessageReceiverState.STARTED

    def _do_subscribe(self, topic_subscription):
        # Method to subscribe
        if self._flow_p.value is None:
            self.adapter.warning("%s", "Flow Pointer is NULL")
            return
        # Unlike direct receivers, persistent receivers have a one-to-one mapping for flows and hence do not
        # require separate dispatch per subscription. In fact having topic dispatch is causing duplicate message
        # delivery for overlapping subscriptions like t1/t2 and t1/>. Therefore, topic dispatch has been removed
        # With this change the behaviour is similar to solClient_session_endpointTopicSubscribe().
        return_code = flow_topic_subscribe_with_dispatch(self._flow_p, topic_subscription, c_void_p(None))
        if return_code != SOLCLIENT_OK:
            last_error = last_error_info(return_code, f"{type(self).__name__}->_do_subscribe")
            self.adapter.warning('%s %s. Status code: %d. %s',
                                 UNABLE_TO_SUBSCRIBE_TO_TOPIC, topic_subscription,
                                 return_code, last_error)  # pragma: no cover # Ignored due to core error scenarios
            raise PubSubPlusClientError(message=f'{UNABLE_TO_SUBSCRIBE_TO_TOPIC} {topic_subscription}. '
                                                f'Status code: {return_code}. {last_error}')  # pragma: no cover
            # Ignored due to core error scenarios

    def _do_unsubscribe(self, topic_subscription):
        # Method to unsubscribe
        if self._flow_p.value is None:
            self.adapter.warning("%s", "Flow Pointer is NULL")
            return

        # topic dispatch removed in _do_subscribe and hence removing from _do_unsubscribe
        return_code = flow_topic_unsubscribe_with_dispatch(self._flow_p, topic_subscription, c_void_p(None))
        if return_code == SOLCLIENT_OK:
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('Unsubscribed [%s]', topic_subscription)
        else:
            last_error = last_error_info(return_code, f"{type(self).__name__}->_do_unsubscribe")
            self.adapter.warning('%s %s. Status code: %d. %s',
                                 UNABLE_TO_UNSUBSCRIBE_TO_TOPIC, topic_subscription,
                                 return_code, last_error)  # pragma: no cover # Ignored due to core error scenarios
            raise PubSubPlusClientError(message=f'{UNABLE_TO_UNSUBSCRIBE_TO_TOPIC} {topic_subscription}. '
                                                f'Status code: {return_code}. {last_error}')  # pragma: no cover
            # Ignored due to core error scenarios

    def __is_receiver_started(self) -> bool:
        # Method to validate receiver is properly started or not
        if not self._messaging_service.is_connected:
            logger.debug('Receiver is [%s]. MessagingService NOT connected',
                         self._message_receiver_state.name)
            error_message = RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED
            logger.warning(error_message)
            raise IllegalStateError(error_message)

        if self._message_receiver_state in [_MessageReceiverState.NOT_STARTED,
                                            _MessageReceiverState.STARTING]:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_NOT_STARTED)
        elif self._message_receiver_state in [_MessageReceiverState.TERMINATING,
                                              _MessageReceiverState.TERMINATED]:
            raise IllegalStateError(RECEIVER_TERMINATED)
        elif self._message_receiver_state != _MessageReceiverState.STARTED:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_NOT_STARTED)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Due to core error scenarios
            self.adapter.debug('[%s] %s', PersistentMessageReceiver.__name__, _MessageReceiverState.STARTED.name)
        return True

    def _stop_flow(self):
        # Shutdown all c api message dispatching
        if not self._flow_stopped and self._messaging_service.session.session_pointer and self._flow_p:
            # pause the flow of inbound messages only if its not done already
            # close the c layer flow message window to stop receiver new messages for dispatch
            with _Released(self._mutex):
                return_code = pause(self._flow_p)
            # confirm success
            if return_code != SOLCLIENT_OK:
                exception: PubSubPlusCoreClientError = \
                    get_last_error_info(return_code=return_code,
                                        caller_description='_PersistentMessageReceiver->_stop_flow')
                self.adapter.warning(str(exception))
                raise exception
            else:
                # update c layer flow start stop state flag
                self._flow_stopped = True

    # for non durable queue this should be called after start method if queue name
    # wasn't given while building the receiver
    def receiver_info(self) -> _PersistentReceiverInfo:
        return _PersistentReceiverInfo(self._is_durable, self._queue_name)

    @property
    def flow_p(self):
        # Property which holds and returns the flow pointer
        return self._flow_p

    def start(self) -> 'PersistentMessageReceiver':
        # return self if we already started the receiver
        if self._message_receiver_state == _MessageReceiverState.STARTED:
            return self

        with self._mutex:
            self._is_receiver_terminated(error_message=RECEIVER_TERMINATED_UNABLE_TO_START)
            # Even after acquiring lock still we have to check the state to avoid re-doing the work
            if self._message_receiver_state == _MessageReceiverState.STARTED:
                return self

            if self._message_receiver_state == _MessageReceiverState.NOT_STARTED:
                if self._messaging_service.is_connected:
                    self._message_receiver_state = _MessageReceiverState.STARTING
                else:
                    # Don't need to update the receiver state to NOT_STARTED since it is already in that state
                    logger.debug('Receiver is [%s]. MessagingService NOT connected',
                                 self._message_receiver_state.name)
                    error_message = RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED
                    logger.warning(error_message)
                    raise IllegalStateError(error_message)

                self._create_end_point()
                if self._end_point_arr is None and self._is_durable:  # need to prepare array
                    # for durable queue to add topic subscription
                    self._end_point_props[SOLCLIENT_ENDPOINT_PROP_NAME] = self._queue_name  # set Queue name
                    self._end_point_arr = prepare_array(self._end_point_props)

                for topic in self._end_point_topics_list:  # add end point topic for durable queue
                    # before starting the flow
                    self.__endpoint_topic_subscribe(topic)
                self._start_state_listener()
                self._register_receiver_events()
                self.__do_start()  # flow start
                # we cant add topic subscriptions for non durable queue before starting the flow
                for topic in self._topic_list:
                    self.add_subscription(TopicSubscription.of(topic))
                self._message_receiver_state = _MessageReceiverState.STARTED
                self._running = True
                self.__get_queue_name()
                return self

    def __get_queue_name(self):
        if not self._is_durable and self._queue_name is None:  # attempt to get  the queue name only
            # for non durable queue when queue name is empty
            try:
                destination = _SolClientDestination()
                return_code = flow_destination(self._flow_p, destination)
                if return_code == SOLCLIENT_OK:
                    self._queue_name = destination.dest.decode()
                elif return_code == SOLCLIENT_FAIL:  # pragma: no cover
                    self.adapter.warning(last_error_info((return_code, "flow destination")))
            except ValueError as error:
                # This exception can be raised when we fail to decode the destination name. This is unlikely to occur
                # since it would only occur if there was a problem translating the C character array
                # into a UTF-8 string.
                self.adapter.warning(str(error))

    def __endpoint_topic_subscribe(self, topic):
        return_code = topic_endpoint_subscribe(self._end_point_arr, self._messaging_service.session.session_pointer,
                                               topic)
        if return_code != SOLCLIENT_OK:
            last_error = last_error_info(return_code, "_PersistentMessageReceiver->__endpoint_topic_subscribe")
            self.adapter.warning(last_error)
            raise PubSubPlusClientError(last_error)

    def pause(self):
        # Pause message delivery to an asynchronous message handler or stream
        if self.__is_receiver_started():
            self._running = False
            # halt queue get from removing items from the queue
            # this is a noop on a suspended queue
            self._message_receiver_queue.suspend()

    def resume(self):
        # Resumes previously paused message delivery
        if self.__is_receiver_started():
            self._running = True
            # unblock waiters for queue get
            # this is a noop on a running queue
            self._message_receiver_queue.resume()

    def add_subscription(self, another_subscription: TopicSubscription):
        # Method to add the topic subscription
        validate_subscription_type(subscription=another_subscription, logger=logger)
        self._can_add_subscription()
        self._do_subscribe(another_subscription.get_name())

    def add_subscription_async(self, topic_subscription: TopicSubscription) -> concurrent.futures.Future:
        # method to add the subscription asynchronously
        return self._executor.submit(self.add_subscription, topic_subscription)

    def remove_subscription(self, subscription: TopicSubscription):
        # Method to remove topic subscriptions
        validate_subscription_type(subscription)
        self._can_remove_subscription()
        self._do_unsubscribe(subscription.get_name())

    def remove_subscription_async(self, topic_subscription: TopicSubscription) -> concurrent.futures.Future:
        # """method to remove the subscription asynchronously"""
        return self._executor.submit(self.remove_subscription, topic_subscription)

    def _emit_notify_event(self, error_info) -> concurrent.futures.Future:
        if error_info[CCSMP_SUB_CODE] in replay_error_list:
            error_type = MessageReplayError
        else:
            error_type = PubSubPlusClientError
        return self._termination_notification_dispatcher.on_exception(
            error_type(error_info,
                       error_info[CCSMP_INFO_SUB_CODE]),
            int(time.time() * 1000))

    def receive_async(self, message_handler: 'MessageHandler'):
        # Receives the messages asynchronously
        is_type_matches(message_handler, MessageHandler, logger=logger)
        self._can_receive_message()

        def _receiver_thread_msg_queue_pop():
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                self.adapter.debug('Receiver [%s]: dispatching message, for endpoint [%s]', type(self).__name__,
                                   self._queue_name)
            return self._msg_queue_get()

        def _receiver_thread_on_join():
            self._message_receiver_queue.shutdown()

        with self._receive_lock:
            if self._message_receiver_thread is None:
                self._message_receiver_thread = \
                    PersistentMessageReceiverThread(self._id_info, logger, self, _receiver_thread_msg_queue_pop,
                                                    self._messaging_service, self._auto_ack, self.stop_event,
                                                    _receiver_thread_on_join)
                self._persistent_message_receiver_thread_holder.value = self._message_receiver_thread
                self._message_receiver_thread.message_handler = message_handler
                self._message_receiver_thread.daemon = True
                self._message_receiver_thread.start()
            else:  # just update the thread's message handler
                self._message_receiver_thread.message_handler = message_handler

    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        # Get a message, blocking for the time passed in timeout,
        # None will be returned  as part of clean-up process after terminate method is called to
        # prevent infinite blocking when the api is waiting for a new message
        self._can_receive_message()
        if timeout is not None:
            is_not_negative(timeout, logger=logger)
        try:
            message = self._msg_queue_get(block=True,
                                          timeout=convert_ms_to_seconds(timeout) if timeout is not None else None)
            if self._auto_ack and message is not None:
                self._messaging_service._increase_duplicate_ack_count()
                self._settle(message)
            return message
        except QueueShutdown:
            # unblock waiter on terminate
            self.adapter.info("While trying to receive a message through %s.receive_message(), " \
                              "the internal buffer was shutdown, preventing access to further messages.",
                              type(self).__name__)
            return
        except queue.Empty:  # when timeout arg is given just return None on timeout
            self.adapter.info("%s.receive_message() timed out while trying to receive a message.",
                              type(self).__name__)
            return
        except (PubSubPlusClientError, KeyboardInterrupt) as exception:
            logger.warning(str(exception))
            raise exception

    def ack(self, message: 'InboundMessage'):
        self.settle(message, Outcome.ACCEPTED)

    def settle(self, message: InboundMessage, outcome: Outcome = Outcome.ACCEPTED):
        if self._auto_ack:
            if outcome != Outcome.ACCEPTED:
                logger.warning("Settling is ignored because the message acknowledgement mode is auto-ack")
            return
        self._settle(message, outcome)

    # Internal use variant, usable by the fake autoack mechanism.
    def _settle(self, message: InboundMessage, outcome: Outcome = Outcome.ACCEPTED):
        is_type_matches(message, InboundMessage, logger=logger)
        is_type_matches(outcome, Outcome, logger=logger)
        if message is not None:  # None may be received on receive_message time out
            if self._message_receiver_state in [_MessageReceiverState.STARTED, _MessageReceiverState.TERMINATING]:
                return_code = nack_message(self._flow_p, message.message_id, outcome)
                if return_code != SOLCLIENT_OK:
                    exception: PubSubPlusCoreClientError = \
                        get_last_error_info(return_code=return_code,
                                            caller_description='PersistentMessageReceiver->settle')
                    self.adapter.warning(str(exception))
                    raise exception
            else:
                exception_message = f"{UNABLE_TO_ACK}: {self._message_receiver_state}"
                self.adapter.warning(exception_message)
                raise IllegalStateError(exception_message)

    def _halt_messaging(self):
        self._stop_flow()

def persistent_state_change_listener_cleanup(thread_holder: 'Holder'):
    thread = thread_holder.value
    if thread is not None and thread.is_alive:
        thread.join()

def persistent_message_receiver_thread_cleanup(thread_holder: 'Holder'):
    thread = thread_holder.value
    if thread is not None and thread.is_alive:
        thread.join()
