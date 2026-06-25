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

# pylint: disable=too-few-public-methods, missing-class-docstring, missing-module-docstring, missing-function-docstring
# pylint:disable=no-else-return

import ctypes
import logging
from typing import TypeVar, Union

from solace.messaging.config._sol_constants import SOLCLIENT_NOT_FOUND, SOLCLIENT_OK, _SOLCLIENTCACHESTATUS
from solace.messaging.config._solace_message_constants import INCOMPATIBLE_MESSAGE
from solace.messaging.core._message import _Message, _SolClientDestination
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, PubSubPlusCoreClientError
from solace.messaging.receiver._inbound_message_utility import get_message_id
from solace.messaging.receiver.inbound_message import InboundMessage, _ReplicationGroupMessageId, CacheStatus
from solace.messaging.utils._solace_utilities import handle_none_for_str, get_last_error_info
from solace.messaging.utils.converter import BytesToObject

logger = logging.getLogger('solace.messaging.receiver')


class _InboundMessage(_Message, InboundMessage):
    # Implementation class for InboundMessage

    T = TypeVar('T')

    def __init__(self, solace_message: _SolaceMessage):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        super().__init__(solace_message)
        self.__discard_notification: 'InboundMessage.MessageDiscardNotification' = \
            _InboundMessage.MessageDiscardNotification(self._solace_message)

    def get_cache_status(self) -> CacheStatus:
        cache_status = self._solace_message.get_cache_status()
        if cache_status == _SOLCLIENTCACHESTATUS.SOLCLIENT_CACHE_MESSAGE.value:
            return CacheStatus.CACHED
        elif cache_status == _SOLCLIENTCACHESTATUS.SOLCLIENT_CACHE_SUSPECT_MESSAGE.value:
            return CacheStatus.SUSPECT
        else:
            # Returning LIVE is the default.
            return CacheStatus.LIVE

    def get_cache_request_id(self) -> Union[None, int]:
        return self._solace_message.get_cache_request_id()

    @property
    def message_id(self):
        return get_message_id(self.solace_message.msg_p)

    def is_redelivered(self) -> bool:
        # Get redelivery status on message.
        #
        # Returns:
        #    bool: True if redelivered, false if otherwise
        message_has_been_redelivered = self._solace_message.get_message_is_redelivered()
        if not isinstance(message_has_been_redelivered, int):  # pragma: no cover # Due to core error  scenarios
            logger.warning("Core api doesn't return boolean flag for message redelivery.")
            return False
        if message_has_been_redelivered not in [0, 1]:  # pragma: no cover # Due to core error  scenarios
            logger.warning("Core api doesn't return boolean flag for message redelivery.")
            return False
        result = bool(message_has_been_redelivered)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Message has been redelivered; message redelivery bool is [%s]', result)
        return result

    def get_replication_group_message_id(self) -> Union['ReplicationGroupMessageId', None]:
        return _ReplicationGroupMessageId.create_from_msg(self.solace_message.msg_p)

    def get_and_convert_payload(self, converter: BytesToObject[T], output_type: type) -> T:
        # Get payload and converts to the target type using given converter
        # Args:
        #     converter:
        #     output_type:
        # Returns:
        received_message = self.get_binary_attachment()
        bytes_to_object = converter.convert(received_message)
        if isinstance(bytes_to_object, output_type):
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Get and convert payload')
            return bytes_to_object
        logger.warning(INCOMPATIBLE_MESSAGE)  # pragma: no cover # Due to core error scenario
        raise PubSubPlusClientError(message=INCOMPATIBLE_MESSAGE)  # pragma: no cover # Due to core error scenario

    def get_destination_name(self) -> Union[str, None]:  # type: ignore
        # Get name of the destination on which message was received (topic or queue)
        # Returns:
        #     destination (str) : destination name

        destination = _SolClientDestination()
        return_code = self.solace_message.get_destination(destination)
        if return_code == SOLCLIENT_OK:
            return destination.dest.decode()
        elif return_code == SOLCLIENT_NOT_FOUND:  # pragma: no cover
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_InboundMessage->get_destination_name',
                                exception_message="Failed to get destination name.")  # pragma: no cover
        logger.warning(exception)  # pragma: no cover # Due to core error scenario
        raise exception  # pragma: no cover # Due to core error scenario

    def get_time_stamp(self) -> Union[int, None]:
        # Get the timestamp of the message when it arrived on a broker in ms
        # Returns:
        #     timestamp (int) : timestamp in ms
        timestamp_p = ctypes.c_uint64()
        return_code = self.solace_message.get_message_timestamp(timestamp_p)
        if return_code == SOLCLIENT_OK:
            timestamp_in_ms = timestamp_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Message receive timestamp: %d', timestamp_in_ms)
            return timestamp_in_ms
        elif return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_InboundMessage->get_time_stamp',
                                exception_message="Unable to get message receive timestamp.")  # pragma: no cover
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenario
        raise exception  # pragma: no cover # Due to core error scenarios

    def get_sender_timestamp(self) -> Union[int, None]:
        # Gets the sender's timestamp. This field is mostly set automatically during message publishing.
        # Returns:
        #     timestamp (int) : timestamp (in ms, from midnight, January 1, 1970 UTC) or null if not set
        timestamp_p = ctypes.c_uint64()
        return_code = self.solace_message.get_message_sender_timestamp(timestamp_p)
        if return_code == SOLCLIENT_OK:
            timestamp_in_ms = timestamp_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Message sender timestamp: %d', timestamp_in_ms)
            return timestamp_in_ms
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_InboundMessage->get_sender_timestamp',
                                exception_message="Unable to get message send timestamp.")  # pragma: no cover
        # Due to core error scenario
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenarios
        raise exception  # pragma: no cover # Due to core error scenario

    def get_sender_id(self) -> Union[str, None]:
        # Gets the sender's ID. This field is mostly set automatically during message publishing.
        # Returns:
        #     sender_id (str): The sender's ID or None if not set.
        sender_id_p = ctypes.c_char_p()
        return_code = self.solace_message.get_message_sender_id(sender_id_p)
        if return_code == SOLCLIENT_OK:
            sender_id = sender_id_p.value.decode("utf-8")  # pylint: disable=no-member
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Message sender ID: %s', sender_id)
            return sender_id
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_InboundMessage->get_sender_id',
                                exception_message="Unable to get message sender ID.")  # pragma: no cover
        # Due to core error scenario
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenarios
        raise exception  # pragma: no cover # Due to core error scenario

    def get_message_discard_notification(self) -> 'InboundMessage.MessageDiscardNotification':
        return self.__discard_notification

    class MessageDiscardNotification(InboundMessage.MessageDiscardNotification) \
            :  # pylint: disable=missing-class-docstring
        def __init__(self, msg_p: _SolaceMessage):
            self._has_discard_notification = msg_p.has_discard_indication()
            self._has_internal_discard_notification = False

        def set_internal_discard_indication(self):
            self._has_internal_discard_notification = True

        def has_internal_discard_indication(self) -> bool:
            return self._has_internal_discard_notification

        def has_broker_discard_indication(self) -> bool:  # pylint: disable=no-else-return
            """ Retrieve Broker Discard Indication

            When the Solace event broker discards messages before sending them, the next message successfully
            sent to the receiver will have Discard Indication set.

            Returns: true if Solace event broker has discarded one or more messages prior to the current message.
            """
            if not isinstance(self._has_discard_notification, int):  # pragma: no cover # Due to core error  scenarios
                logger.warning("Core api doesn't return boolean flag, and it has [%s]", self._has_discard_notification)
                return False
            if self._has_discard_notification not in [0, 1]:  # pragma: no cover # Due to core error  scenarios
                logger.warning("Core api doesn't return boolean flag, and it has [%s]", self._has_discard_notification)
                return False
            result = bool(self._has_discard_notification)
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Has discard indication!: [%s]', result)
            return result

    # When message is too large, it will be truncated to 640kb character.
    # This prevents any hangs while printing large messages.
    # The truncated message usually has headers, binary meta-data prior to binary attachment hence binary attachment
    # gets truncated but incase the user properties are too large then it will be truncated to accommodate for
    # the limited buffer size.
    def __str__(self):
        return handle_none_for_str(input_value=self.solace_message.get_message_dump())
