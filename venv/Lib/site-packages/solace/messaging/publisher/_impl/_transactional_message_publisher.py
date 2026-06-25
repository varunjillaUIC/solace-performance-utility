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

# pylint: disable=R0904,missing-function-docstring, too-many-instance-attributes, missing-class-docstring
# pylint: disable=too-many-ancestors,broad-except,protected-access,no-member

"""Module contains the Implementation classes and methods for the TransactionalMessagePublisher"""
import logging
import time
from typing import Union, Dict
from threading import Lock

from solace.messaging.publisher.transactional_message_publisher import TransactionalMessagePublisher
from solace.messaging.publisher._impl._outbound_message import _OutboundMessageBuilder
from solace.messaging import _SolaceServiceAdapter
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.resources.topic import Topic
from solace.messaging.core._publish import _SolacePublish
from solace.messaging.core._solace_transport import _SolaceTransportEventInfo
from solace.messaging.publisher._publishable import Publishable
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._sol_constants import SOLCLIENT_DELIVERY_MODE_PERSISTENT
from solace.messaging.config._sol_constants import SOLCLIENT_OK
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, \
    CCSMP_INFO_SUB_CODE, PUBLISHER_NOT_STARTED, DISPATCH_FAILED, \
    TRANSACTIONAL_PUBLISHER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED, PUBLISHER_TERMINATED, \
    PUBLISH_FAILED_TRANSACTIONAL_MESSAGING_SERVICE_NOT_CONNECTED, \
    PUBLISH_FAILED_MESSAGING_SERVICE_NOT_CONNECTED, PUBLISHER_TERMINATED_UNABLE_TO_START, \
    PUBLISHER_ALREADY_TERMINATED, UNABLE_TO_PUBLISH_MESSAGE, TRANSACTIIONAL_OPERATION_UNDERWAY
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, \
    IllegalStateError, InvalidDataTypeError, TransactionError
from solace.messaging.core._solace_sdt import _SolaceSDTMap
from solace.messaging.utils.life_cycle_control import TerminationNotificationListener
from solace.messaging.utils._termination_notification_util import TerminationNotificationEvent
from solace.messaging.publisher.publisher_health_check import PublisherReadinessListener
from solace.messaging.utils._solace_utilities import COMPLETED_FUTURE
from solace.messaging._impl._transactional_error_subcodes import transactional_subcode_list

logger = logging.getLogger('solace.messaging.publisher')

class _TransactionalMessagePublisher(TransactionalMessagePublisher):
    def __init__(self, config: dict, transactional_messaging_service: 'TransactionalMessagingService'):
        self._config = dict(config)
        self._transactional_messaging_service = transactional_messaging_service
        self._transactional_messaging_service._add_shutdown_callback(self._shutdown)
        self._outbound_message_builder = _OutboundMessageBuilder()
        # Can't let the user publish before making them jump through hoops!
        self._running = False
        self._terminated = False
        self._termination_lock = Lock() # Protects the termination flag.
        self._id_info = f"{self._transactional_messaging_service.logger_id_info} - " \
                        f"[PUBLISHER: {str(hex(id(self)))}]"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        self._termination_future = None
        self._termination_notification_listener = None

    def is_ready(self):
        # the publisher is always ready when running as publisher back pressure is only bound to transport netwrok io.
        return self._running

    def is_running(self):
        return self._running

    def is_terminated(self):
        return self._terminated

    def is_terminating(self):
        # Since publisher state is entirely artificial, termination is instantaneous.
        return False

    # No CAN_SEND on transacted session.
    def set_publisher_readiness_listener(self, listener: PublisherReadinessListener):
        pass

    def notify_when_ready(self):
        pass

    def start(self):
        if (not self._transactional_messaging_service.is_connected) or \
            (not self._transactional_messaging_service._messaging_service.is_connected):
            raise IllegalStateError(TRANSACTIONAL_PUBLISHER_CANNOT_BE_STARTED_MSG_SERVICE_NOT_CONNECTED)
        with self._termination_lock:
            if self._terminated:
                raise IllegalStateError(PUBLISHER_TERMINATED_UNABLE_TO_START)
            self._running = True
        return self

    def start_async(self):
        return self._transactional_messaging_service._run_later(self.start)

    def _shutdown(self, event: _SolaceTransportEventInfo):
        already_terminated = False
        with self._termination_lock:
            if self._terminated:
                already_terminated = True
            else:
                self._running = False
                self._terminated = True
        if already_terminated:
            self.adapter.debug(PUBLISHER_ALREADY_TERMINATED)
            return
        self._transactional_messaging_service._remove_shutdown_callback(self._shutdown)
        if event and self._termination_notification_listener:
            timestamp = int(time.time() * 1000)
            def nested_callback():
                try:
                    error_info = event._event_info
                    ps_client_error = PubSubPlusClientError(error_info, error_info[CCSMP_INFO_SUB_CODE])
                    term_notice = TerminationNotificationEvent(ps_client_error, timestamp)
                    self._termination_notification_listener.on_termination(term_notice)
                except Exception as exception:  # pylint: disable=broad-except
                    self.adapter.warning("%s [%s] %s", DISPATCH_FAILED,
                                         type(self._termination_notification_listener),
                                         str(exception))
            self._transactional_messaging_service._run_later(nested_callback)

    def terminate(self, grace_period: int = 0):
        self._shutdown(event=None)

    def terminate_async(self, grace_period: int = 0):
        self.terminate()
        return COMPLETED_FUTURE


    def publish(self, message: Union[bytearray, str, OutboundMessage], destination: Topic,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, \
                    list, tuple, None, bytearray]] = None):
        return self._transactional_messaging_service._run(self._publish_job, message,
                                                          destination,
                                                          additional_message_properties)

    # pylint: disable=too-many-branches
    def _publish_job(self, message: Union[bytearray, str, OutboundMessage], destination: Topic,
                     additional_message_properties: Dict[str, Union[str, int, float, bool, dict, \
                         list, tuple, None, bytearray]] = None):
        if not self._transactional_messaging_service._messaging_service.is_connected:
            raise IllegalStateError(PUBLISH_FAILED_MESSAGING_SERVICE_NOT_CONNECTED)
        if not self._transactional_messaging_service.is_connected:
            raise IllegalStateError(PUBLISH_FAILED_TRANSACTIONAL_MESSAGING_SERVICE_NOT_CONNECTED)
        if self._terminated:
            raise IllegalStateError(PUBLISHER_TERMINATED)
        if not self._running:
            raise IllegalStateError(PUBLISHER_NOT_STARTED)
        if not isinstance(message, OutboundMessage):
            outbound_message = self._outbound_message_builder.build(message)
        else:
            outbound_message = message

        publishable = Publishable.of(outbound_message.solace_message, destination)
        solace_message = publishable.get_message()
        solace_message.set_delivery_mode(SOLCLIENT_DELIVERY_MODE_PERSISTENT)

        # Double underscore causes name mangling. Now we know.
        _SolacePublish._SolacePublish__set_topic(solace_message, publishable.get_destination())
        if additional_message_properties:
            _OutboundMessageBuilder.add_message_properties(_SolaceSDTMap(additional_message_properties),
                                                           solace_message)

        lock_success = self._transactional_messaging_service._commit_lock.acquire(blocking=False)
        if lock_success:
            try:
                publish_message_status_code = solace_message.transacted_send(
                    self._transactional_messaging_service._transacted_session_p)
            finally:
                self._transactional_messaging_service._commit_lock.release()
        else:
            raise TransactionError(TRANSACTIIONAL_OPERATION_UNDERWAY)

        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug("Message publish on [%s] status: [%d]", destination.get_name(), publish_message_status_code)
        if SOLCLIENT_OK == publish_message_status_code:
            return None

        # Not OK (no WOULD_BLOCK on transacted session):
        core_exception_msg = last_error_info(status_code=publish_message_status_code,
                                             caller_desc='On PUBLISH')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('\nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        if core_exception_msg[CCSMP_SUB_CODE] in transactional_subcode_list:
            raise TransactionError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                   message=core_exception_msg["error_info_contents"])
        raise PubSubPlusClientError(message=UNABLE_TO_PUBLISH_MESSAGE)

    def set_termination_notification_listener(self, listener: TerminationNotificationListener):
        if listener is not None and not hasattr(listener, 'on_termination'):
            raise InvalidDataTypeError(f"Expected to receive instance of {TerminationNotificationListener}")
        self._termination_notification_listener = listener
