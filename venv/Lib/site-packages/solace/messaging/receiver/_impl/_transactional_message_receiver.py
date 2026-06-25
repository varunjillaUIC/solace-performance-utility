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

# pylint: disable=protected-access
"""Module contains the implementation class and methods for the TransactionalMessageReceiver"""

import logging
import time
from typing import Union
import concurrent.futures
from ctypes import c_void_p, cast, POINTER, c_char_p, byref, c_int32, sizeof
from threading import Lock

import solace
from solace.messaging.receiver.transactional_message_receiver import TransactionalMessageReceiver, \
    TransactionalMessageHandler
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, IllegalStateError, \
    InvalidDataTypeError, MessageReplayError, TransactionError
from solace.messaging.receiver._impl._message_receiver import _MessageReceiverState
from solace.messaging.core._core_api_utility import prepare_array
from solace.messaging.utils._termination_notification_util import TerminationNotificationEvent
from solace.messaging.config.receiver_activation_passivation_configuration import ReceiverState
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_FAIL, _SolClientFlowEvent, \
    SOLCLIENT_FLOW_PROP_BIND_NAME, SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID, SOLCLIENT_FLOW_PROP_BIND_BLOCKING, \
    SOLCLIENT_PROP_ENABLE_VAL, SOLCLIENT_CALLBACK_OK, SOLCLIENT_CALLBACK_TAKE_MSG, SOLCLIENT_ENDPOINT_PROP_NAME, \
    SOLCLIENT_ENDPOINT_PROP_ID, SOLCLIENT_FLOW_PROP_ACTIVE_FLOW_IND, SOLCLIENT_FLOW_PROP_BIND_ENTITY_DURABLE, \
    SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE, SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_NONEXCLUSIVE, \
    SOLCLIENT_FLOW_PROP_SELECTOR, SOLCLIENT_FLOW_PROP_START_STATE, SOLCLIENT_PROP_DISABLE_VAL
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, CCSMP_INFO_SUB_CODE, \
    TRANSACTIONAL_RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED, RECEIVER_TERMINATED_UNABLE_TO_START, \
    UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_ALREADY_TERMINATED, RECEIVER_ALREADY_TERMINATED, CANNOT_ADD_SUBSCRIPTION, \
    CANNOT_REMOVE_SUBSCRIPTION, DISPATCH_FAILED, UNABLE_TO_RECEIVE_MESSAGE_MESSAGE_SERVICE_NOT_CONNECTED, \
    UNABLE_TO_RECEIVE_MESSAGE_TRANSACTIONAL_MESSAGE_SERVICE_NOT_CONNECTED, \
    TRANSACTIONAL_RECEIVER_ALREADY_IN_ASYNC_MODE, TRANSACTIONAL_RECEIVER_ALREADY_IN_BLOCKING_MODE, \
    TRANSACTIONAL_RECEIVER_MSG_CALLBACK_OVERRIDE, BIND_FAILED, TRANSACTIIONAL_OPERATION_UNDERWAY
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.receiver._impl._inbound_message import _InboundMessage
from solace.messaging.utils.life_cycle_control import TerminationNotificationListener
from solace.messaging import _SolaceServiceAdapter
from solace.messaging.receiver._inbound_message_utility import topic_endpoint_subscribe, topic_endpoint_unsubscribe, \
    end_point_provision, flow_destination
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.config._ccsmp_property_mapping import end_point_props
from solace.messaging.core._message import _SolClientDestination
from solace.messaging.core._receive import _event_callback_func_type, _flow_msg_callback_func_type, \
    SolClientFlowCreateFuncInfo, SolClientFlowCreateRxMsgCallbackFuncInfo
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationStrategy
from solace.messaging.utils._solace_utilities import is_not_negative, convert_config
from solace.messaging.receiver._impl._receiver_utilities import validate_subscription_type
from solace.messaging.utils.manageable_receiver import TransactionalReceiverInfo
from solace.messaging.utils._impl._manageable_receiver import _TransactionalReceiverInfo
from solace.messaging.config._ccsmp_property_mapping import CCSMP_SESSION_PROP_MAPPING
from solace.messaging.builder._impl._message_replay_config import incorporate_replay_props, replay_error_list
from solace.messaging._impl._transactional_error_subcodes import transactional_subcode_list
from solace.messaging.core._solace_transport import _SolaceTransportEventInfo


logger = logging.getLogger('solace.messaging.receiver')

# pylint: disable=too-many-instance-attributes
class _TransactionalMessageReceiver(TransactionalMessageReceiver):
    def __init__(self, config: dict, builder: '_TransactionalMessageReceiverBuilder',
                 transactional_messaging_service: 'TransactionalMessagingService'):
        self._config = convert_config(config, CCSMP_SESSION_PROP_MAPPING)
        self._transactional_messaging_service = transactional_messaging_service
        self._transactional_messaging_service._add_shutdown_callback(self._shutdown)

        # Can only be changed before start() by calling receive_async().
        self._async_mode = False
        self._async_message_handler = None
        self._termination_notification_listener = None
        self._missing_resource_strategy = builder._missing_resources_creation_strategy
        self._is_durable = builder._endpoint_to_consume_from.is_durable()
        self._is_exclusive = builder._endpoint_to_consume_from.is_exclusively_accessible()
        self._queue_name = builder._endpoint_to_consume_from.get_name()
        self._replay_strategy = builder.replay_strategy
        # Add REPLAY property based on ReplayStrategy
        self._config = incorporate_replay_props(self._replay_strategy, self._config)
        self._config[SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID] = '2'
        if not self._is_durable and self._queue_name is None:
            # don't add  SOLCLIENT_FLOW_PROP_BIND_NAME when we didn't receive queue name for non-durable exclusive queue
            pass
        else:
            self._config[SOLCLIENT_FLOW_PROP_BIND_NAME] = self._queue_name
        self._config[SOLCLIENT_FLOW_PROP_BIND_ENTITY_DURABLE] = str(int(self._is_durable))
        if builder._message_selector:  # Message selector applied here
            self._config[SOLCLIENT_FLOW_PROP_SELECTOR] = builder._message_selector

        # active flow indication.
        self._receiver_state_change_listener = builder._receiver_state_change_listener
        self._topic_subscriptions = builder._topic_subscriptions
        self._flow_p = c_void_p(None)
        # flow created/destroyed, start/stop states...
        # STARTING STARTED TERMINATING TERMINATED
        self._message_receiver_state = _MessageReceiverState.NOT_STARTED
        self._termination_future = None
        self._termination_lock = Lock() # guards the future...
        self._flow_stopped = False

        self._id_info = f"{self._transactional_messaging_service.logger_id_info} - " \
                        f"[RECEIVER: {str(hex(id(self)))}]"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        self._prepared_array = None
        self._event_callback_func_routine = None
        self._flow_msg_callback_func_routine = None
        self._paused = False
        self._termination_reason = None

    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        return self._transactional_messaging_service._run(self._receive_message_job, timeout)

    # pylint: disable=too-many-branches
    def _receive_message_job(self, timeout: int = None) -> Union[InboundMessage, None]:
        if timeout is None:
            timeout = 0
        else:
            is_not_negative(timeout, logger=logger)
        if self._async_mode:
            raise PubSubPlusClientError(message=TRANSACTIONAL_RECEIVER_ALREADY_IN_ASYNC_MODE)
        if not self._transactional_messaging_service._messaging_service.is_connected:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_MESSAGE_SERVICE_NOT_CONNECTED)
        if not self._transactional_messaging_service.is_connected:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_TRANSACTIONAL_MESSAGE_SERVICE_NOT_CONNECTED)
        if self._message_receiver_state in [_MessageReceiverState.TERMINATED, _MessageReceiverState.TERMINATING]:
            raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_ALREADY_TERMINATED)
        msg_p = c_void_p(None)
        # Measuring the time spent waiting for the lock...
        before_locking = time.time()
        lock_success = self._transactional_messaging_service._commit_lock.acquire(timeout=timeout/1000)
        after_locking = time.time()
        secs_spent_locking = after_locking - before_locking
        # ... then waiting for a message that much less.
        remaining_timeout_ms = timeout - round(secs_spent_locking * 1000)
        if lock_success:
            try:
                ret = solace.CORE_LIB.solClient_flow_receiveMsg(self._flow_p,
                                                                byref(msg_p),
                                                                c_int32(remaining_timeout_ms))
            finally:
                self._transactional_messaging_service._commit_lock.release()
        else:
            raise TransactionError(TRANSACTIIONAL_OPERATION_UNDERWAY)
        if ret == SOLCLIENT_OK:
            if msg_p:
                solace_message = _SolaceMessage(msg_p)
                inbound_message = _InboundMessage(solace_message)
                return inbound_message
            #else:
            return None
        # not OK:
        core_exception_msg = last_error_info(status_code=ret,
                                             caller_desc='ON RECEIVE')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('\nNon-OK response from receiveMsg. Sub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        if core_exception_msg[CCSMP_SUB_CODE] in transactional_subcode_list:
            raise TransactionError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                   message=core_exception_msg["error_info_contents"])
        raise PubSubPlusClientError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                    message=core_exception_msg["error_info_contents"])

    def receive_async(self, message_handler: TransactionalMessageHandler):
        # Must be called before start() first, later on can only be used to change the handler.
        if message_handler is not None and not hasattr(message_handler, 'on_message'):
            raise InvalidDataTypeError(f"Expected to receive instance of {TransactionalMessageHandler}")
        if _MessageReceiverState.NOT_STARTED == self._message_receiver_state:
            self._async_mode = True
            self._async_message_handler = message_handler
        elif self._async_mode:
            if self._message_receiver_state in [_MessageReceiverState.TERMINATED, _MessageReceiverState.TERMINATING]:
                raise IllegalStateError(UNABLE_TO_RECEIVE_MESSAGE_RECEIVER_ALREADY_TERMINATED)
            logger.info(TRANSACTIONAL_RECEIVER_MSG_CALLBACK_OVERRIDE)
            self._async_message_handler = message_handler
        else:
            raise IllegalStateError(message=TRANSACTIONAL_RECEIVER_ALREADY_IN_BLOCKING_MODE)


    def set_termination_notification_listener(self, listener: TerminationNotificationListener):
        if listener is not None and not hasattr(listener, 'on_termination'):
            raise InvalidDataTypeError(f"Expected to receive instance of {TerminationNotificationListener}")
        self._termination_notification_listener = listener

    def _add_remove_subscription(self, topic: str, add: bool):
        if add:
            sub_or_unsub = topic_endpoint_subscribe
        else:
            sub_or_unsub = topic_endpoint_unsubscribe

        if not self._prepared_array:
            self._prepared_array = prepare_array(self._config)
        endpoint_props = {}
        endpoint_props[SOLCLIENT_ENDPOINT_PROP_NAME] = self._queue_name
        endpoint_props[SOLCLIENT_ENDPOINT_PROP_ID] = '2'
        prep_props = prepare_array(endpoint_props)
        return_code = sub_or_unsub(prep_props, \
                                   self._transactional_messaging_service._messaging_service.session.session_pointer, \
                                   topic)
        if return_code != SOLCLIENT_OK:
            last_error = last_error_info(return_code, "_TransactionalMessageReceiver->_add_remove_subscription")
            logger.warning(last_error)
            raise PubSubPlusClientError(last_error)

    def add_subscription(self, another_subscription: TopicSubscription):
        validate_subscription_type(subscription=another_subscription, logger=logger)
        if _MessageReceiverState.STARTED != self._message_receiver_state:
            raise IllegalStateError(CANNOT_ADD_SUBSCRIPTION)
        return self._add_remove_subscription(another_subscription.get_name(), add=True)
    def add_subscription_async(self, topic_subscription: TopicSubscription):
        validate_subscription_type(subscription=topic_subscription, logger=logger)
        if _MessageReceiverState.STARTED != self._message_receiver_state:
            raise IllegalStateError(CANNOT_ADD_SUBSCRIPTION)
        return self._transactional_messaging_service._run_later(self.add_subscription, topic_subscription)

    def remove_subscription(self, subscription):
        validate_subscription_type(subscription=subscription, logger=logger)
        if _MessageReceiverState.STARTED != self._message_receiver_state:
            raise IllegalStateError(CANNOT_REMOVE_SUBSCRIPTION)
        return self._add_remove_subscription(subscription.get_name(), add=False)

    def remove_subscription_async(self, topic_subscription: TopicSubscription):
        validate_subscription_type(subscription=topic_subscription, logger=logger)
        if _MessageReceiverState.STARTED != self._message_receiver_state:
            raise IllegalStateError(CANNOT_REMOVE_SUBSCRIPTION)
        return self._transactional_messaging_service._run_later(self.remove_subscription, topic_subscription)

    def is_running(self):
        # paused still reports as running.
        # There is in fact no way to query the paused state by desig.
        return _MessageReceiverState.STARTED == self._message_receiver_state

    def is_terminated(self):
        return _MessageReceiverState.TERMINATED == self._message_receiver_state

    def is_terminating(self):
        return _MessageReceiverState.TERMINATING == self._message_receiver_state

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
                # since it would only occur if there was a problem translating the C character array into a UTF-8
                # string.
                self.adapter.warning(str(error))

    def _create_end_point(self):
        # create only for durable Queue, non-durable(temporary) Queue will be created during flow creation automatically
        if self._missing_resource_strategy and \
                self._missing_resource_strategy.value == MissingResourcesCreationStrategy.CREATE_ON_START.value and \
                self._is_durable:
            logger.debug('_create_end_point() creating queue %s', self._queue_name)
            _end_point_props = dict(end_point_props)
            _end_point_props[SOLCLIENT_ENDPOINT_PROP_NAME] = self._queue_name  # set Queue name
            if not self._is_exclusive:
                _end_point_props[SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE] = \
                    SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_NONEXCLUSIVE

            end_point_arr = prepare_array(_end_point_props)

            return_code = \
                end_point_provision(end_point_arr,
                                    self._transactional_messaging_service._messaging_service.session.session_pointer,
                                    ignore_already_provisioned=True)

            error_info = last_error_info(status_code=return_code, caller_desc="Endpoint Creation ")

            if return_code != SOLCLIENT_OK:
                self.adapter.warning("%s creation failed with the following sub code %s", self._queue_name,
                                     error_info['sub_code'])
                raise PubSubPlusClientError(f"{self._queue_name}creation failed with the"
                                            f" following sub code{error_info['sub_code']} ")
            #else:
            self.adapter.info("%s endpoint is created successfully", self._queue_name)

    def _event_callback_routine(self, _opaque_flow_p, event_info_p, _user_p) \
            :  # pragma: no cover # Due to invocation in callbacks
        # Flow event callback from the C API.

        logger.debug("_event_callback_routine called")
        logger.debug(event_info_p.contents)
        try:
            event = _SolClientFlowEvent(event_info_p.contents.flow_event)
        except ValueError:
            logger.warning("unknown event: %d", event_info_p)
            return SOLCLIENT_CALLBACK_OK
        if event in [_SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_DOWN_ERROR,
                     _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_BIND_FAILED_ERROR]:
            response_code = event_info_p.contents.response_code
            error_info = last_error_info(response_code, "transactional flow event callback")
            logger.warning(BIND_FAILED)
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('\nTransactional receiver event callback called with error.' \
                             'Sub code: %s. Error: %s. Sub code: %s. Return code: %s',
                             error_info[CCSMP_INFO_SUB_CODE],
                             error_info["error_info_contents"],
                             error_info[CCSMP_SUB_CODE],
                             error_info["return_code"])
            if error_info['sub_code'] in replay_error_list:
                self._termination_reason = MessageReplayError(error_info, error_info['error_info_sub_code'])
            else:
                self._termination_reason = PubSubPlusClientError(error_info, error_info['error_info_sub_code'])
            self._shutdown(event=self._termination_reason)
        elif event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_UP_NOTICE:
            self._message_receiver_state = _MessageReceiverState.STARTED
            logger.debug("flow up notice.")
        elif event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_ACTIVE:
            if self._receiver_state_change_listener:
                def nested_callback():
                    try:
                        self._receiver_state_change_listener.on_change(ReceiverState.PASSIVE, ReceiverState.ACTIVE, \
                                                                       round(time.time() * 1000))
                    except Exception as exception:  # pylint: disable=broad-except
                        self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                             type(self._receiver_state_change_listener),
                                             str(exception))
                self._transactional_messaging_service._run_later(nested_callback)
        elif event == _SolClientFlowEvent.SOLCLIENT_FLOW_EVENT_INACTIVE:
            if self._receiver_state_change_listener:
                def nested_callback():
                    try:
                        self._receiver_state_change_listener.on_change(ReceiverState.ACTIVE, ReceiverState.PASSIVE, \
                                                                       round(time.time() * 1000))
                    except Exception as exception:  # pylint: disable=broad-except
                        self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                             type(self._receiver_state_change_listener),
                                             str(exception))
                self._transactional_messaging_service._run_later(nested_callback)
        else:
            # SOLCLIENT_FLOW_EVENT_SESSION_DOWN, SOLCLIENT_FLOW_EVENT_RECONNECTING, SOLCLIENT_FLOW_EVENT_RECONNECTED :
            logger.debug("Transacted flow has nothing to do with event %s", event)

        return SOLCLIENT_CALLBACK_OK


    def _flow_message_receive_callback_routine(self, _opaque_flow_p, msg_p, _user_p):  # pragma: no cover
        # This is not perfect, because the lock is not acquired before ccsmp invokes the callback.
        with self._transactional_messaging_service._commit_lock:
            if not self._async_message_handler:
                logger.warning("Transacted message handler not registered, dropping message.")
                return SOLCLIENT_CALLBACK_OK  # Abandoning the received message
            # We start the transacted session with a dedicated message dispatch thread.
            # The application is allowed to hold up this thread as a form of flow control
            # or for transaction demaracation.
            try:
                solace_message = _SolaceMessage(c_void_p(msg_p))
                rx_msg = _InboundMessage(solace_message)
                # This is important, otherwise a commit() on the callback would get serialized to the executor,
                # which can apparently leapfrog the return from the callback, confusing CCSMP.
                self._transactional_messaging_service._mark_dispatch_thread()
                self._async_message_handler.on_message(rx_msg)
            except Exception as exception:  # pylint: disable=broad-except
                self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                     type(self._async_message_handler),
                                     str(exception))

            return SOLCLIENT_CALLBACK_TAKE_MSG  # we took the received message

    # pylint: disable=too-many-branches
    def _start_job(self):
        if (not self._transactional_messaging_service.is_connected) or \
           (not self._transactional_messaging_service._messaging_service.is_connected):
            raise IllegalStateError(TRANSACTIONAL_RECEIVER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED)
        if _MessageReceiverState.STARTED == self._message_receiver_state:
            return self
        if self._message_receiver_state in [_MessageReceiverState.TERMINATED, _MessageReceiverState.TERMINATING]:
            raise IllegalStateError(RECEIVER_TERMINATED_UNABLE_TO_START)

        self._message_receiver_state = _MessageReceiverState.STARTING

        self._create_end_point()

        if self._is_durable:
            for topic in self._topic_subscriptions:
                self._add_remove_subscription(topic, add=True)

        self._event_callback_func_routine = _event_callback_func_type(self._event_callback_routine)
        self._flow_msg_callback_func_routine = \
            _flow_msg_callback_func_type(self._flow_message_receive_callback_routine)

        flow_func_info = SolClientFlowCreateFuncInfo(
            (c_void_p(None), c_void_p(None)),
            (self._event_callback_func_routine, self),
            (self._flow_msg_callback_func_routine, self)
        )
        if not self._async_mode:
            logger.debug("_TransactionalMessageReceiver start in polling mode")
            flow_func_info.rx_msg_info = \
                SolClientFlowCreateRxMsgCallbackFuncInfo(cast(None, _flow_msg_callback_func_type), self)
        else:
            logger.debug("_TransactionalMessageReceiver start in push mode")

        self._config[SOLCLIENT_FLOW_PROP_BIND_BLOCKING] = SOLCLIENT_PROP_ENABLE_VAL
        # This gets around a CCSMP bug in async_receive firinig (allowing the user to commit)
        # before the flow bind is fully processed causing empty commits.
        self._config[SOLCLIENT_FLOW_PROP_START_STATE] = \
            SOLCLIENT_PROP_DISABLE_VAL if self._async_mode else SOLCLIENT_PROP_ENABLE_VAL
            #SOLCLIENT_PROP_ENABLE_VAL
        if self._receiver_state_change_listener:
            self._config[SOLCLIENT_FLOW_PROP_ACTIVE_FLOW_IND] = SOLCLIENT_PROP_ENABLE_VAL

        #saved for subscribe/unsubscribe?
        self._prepared_array = prepare_array(self._config)
        flow_arr_byref = byref(self._prepared_array)

        with self._transactional_messaging_service._commit_lock:
            ret = solace.CORE_LIB.solClient_transactedSession_createFlow(cast(flow_arr_byref, POINTER(c_char_p)),
                                                                         self._transactional_messaging_service. \
                                                                             _transacted_session_p,
                                                                         byref(self._flow_p),
                                                                         byref(flow_func_info),
                                                                         sizeof(flow_func_info))
        if ret != SOLCLIENT_OK:
            error_info = last_error_info(status_code=ret, caller_desc="create transactional flow")
            logger.info("transactedSession_createFlow returned %d", ret)
            logger.warning("Flow creation failed for Queue[%s] with sub code [%s]",
                           self._queue_name, error_info['sub_code'])
            if error_info['sub_code'] in replay_error_list:
                raise MessageReplayError(error_info, error_info['error_info_sub_code'])
            #else:
            raise PubSubPlusClientError(error_info, error_info['error_info_sub_code'])
        #else:
        self.__get_queue_name()
        # This will need review when non-durable queue flows can start replays:
        if not self._is_durable:
            for topic in self._topic_subscriptions:
                self._add_remove_subscription(topic, add=True)
        if self._async_mode:
            self._resume_job()
        self._message_receiver_state = _MessageReceiverState.STARTED
        self._flow_stopped = False
        return self


    def start_async(self) -> concurrent.futures.Future:
        return self._transactional_messaging_service._run_later(self._start_job)

    def start(self):
        return self._transactional_messaging_service._run(self._start_job)

    def _shutdown(self, event: _SolaceTransportEventInfo):
        self._message_receiver_state = _MessageReceiverState.TERMINATED
        self._transactional_messaging_service._remove_shutdown_callback(self._shutdown)
        if event and self._termination_notification_listener:
            timestamp = int(time.time() * 1000)
            def nested_callback():
                try:
                    if isinstance(event, _SolaceTransportEventInfo):
                        error_info = event._event_info
                        ps_client_error = PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])
                        term_notice = TerminationNotificationEvent(ps_client_error, timestamp)
                    else:
                        term_notice = TerminationNotificationEvent(event, timestamp)
                    self._termination_notification_listener.on_termination(term_notice)
                except Exception as exception:  # pylint: disable=broad-except
                    self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                         type(self._termination_notification_listener),
                                         str(exception))
            self._transactional_messaging_service._run_later(nested_callback)


    def terminate(self, grace_period: int = 0):
        already_terminated = True
        with self._termination_lock:
            if not self._termination_future:
                already_terminated = False
                self._termination_future = concurrent.futures.Future()
        if already_terminated:
            self.adapter.debug(RECEIVER_ALREADY_TERMINATED) # There is a test for this.
        else:
            self._termination_future.set_result(self._transactional_messaging_service._run(self._terminate_job))
        return self._termination_future.result()

    # pylint: disable=unused-argument
    def _terminate_job(self, grace_period: int = 0):
        if self._message_receiver_state in [_MessageReceiverState.TERMINATING, _MessageReceiverState.TERMINATED]:
            self.adapter.debug(RECEIVER_ALREADY_TERMINATED)
            return None
        self._message_receiver_state = _MessageReceiverState.TERMINATING
        solace.CORE_LIB.solClient_flow_destroy(byref(self._flow_p))
        self._shutdown(event=None)
        return None

    def terminate_async(self, grace_period: int = 0):
        already_terminated = True # This is just for the debug log.
        with self._termination_lock:
            if not self._termination_future:
                already_terminated = False
                self._termination_future = self._transactional_messaging_service._run_later(self._terminate_job)
        if already_terminated:
            self.adapter.debug(RECEIVER_ALREADY_TERMINATED) # There is a test for this.

        return self._termination_future

    def _pause_job(self):
        ret = solace.CORE_LIB.solClient_flow_stop(self._flow_p)
        if ret != SOLCLIENT_OK:
            error_info = last_error_info(status_code=ret, caller_desc="flow stop ")
            logger.info("solClient_flow_stop returned %d", ret)
            logger.warning("Flow stopping failed for Queue[%s] with sub code [%s]",
                           self._queue_name, error_info['sub_code'])
            raise PubSubPlusClientError(error_info, error_info['error_info_sub_code'])
        #else:
        self._paused = True

    def pause(self):
        return self._transactional_messaging_service._run(self._pause_job)


    def _resume_job(self):
        ret = solace.CORE_LIB.solClient_flow_start(self._flow_p)
        if ret != SOLCLIENT_OK:
            error_info = last_error_info(status_code=ret, caller_desc="flow start ")
            logger.info("solClient_flow_start returned %d", ret)
            logger.warning("Flow (re-)starting failed for Queue[%s] with sub code [%s]",
                           self._queue_name, error_info['sub_code'])
            raise PubSubPlusClientError(error_info, error_info['error_info_sub_code'])
        #else:
        self._paused = False

    def resume(self):
        return self._transactional_messaging_service._run(self._resume_job)

    def receiver_info(self) -> TransactionalReceiverInfo:
        return _TransactionalReceiverInfo(self._is_durable, self._queue_name)
