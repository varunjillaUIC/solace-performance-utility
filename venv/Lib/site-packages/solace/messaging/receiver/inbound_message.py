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


""" This module defines the interface to an inbound message used to receive data from the Solace event broker. """
import ctypes
import logging
import enum
from abc import ABC, abstractmethod
from typing import TypeVar, Union

from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._sol_constants import MAX_RMID_STR_LEN, SOLCLIENT_FAIL, SOLCLIENT_OK, SOLCLIENT_NOT_FOUND
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, IllegalArgumentError, \
    InvalidDataTypeError
from solace.messaging.message import Message
from solace.messaging.receiver._inbound_message_utility import _SolClientReplicationGroupMessageId, \
    get_replication_group_message_id_from_string, compare_replication_group_message_id, \
    get_replication_group_message_id_to_string, get_group_message_id
from solace.messaging.utils.converter import BytesToObject

T = TypeVar('T')  # pylint: disable=invalid-name
logger = logging.getLogger('solace.messaging.receiver')

class CacheStatus(enum.Enum):
    """
    An enum with cache status options for the given message.
    """

    LIVE = 0
    """
    The message was retrieved directly from a Solace event broker
    and not from a Solace Cache instance.
    """

    CACHED = 1
    """
    The message was retrieved from a Solace Cache instance.
    """

    SUSPECT = 2
    """
    The message was retrieved from a suspect Solace Cache instance.
    """

class InboundMessage(Message):
    """
    An abstract class that defines the interfaces for an inbound message.
    """

    @abstractmethod
    def get_cache_status(self) -> CacheStatus:
        """
        Retrieves the indicator of whether or not this message was part of a cache reply.

        Returns:
            CacheStatus: The indicator.
        """

    @abstractmethod
    def get_cache_request_id(self) -> Union[int, None]:
        """
        Retrieves the request ID that was set in the cache request from the message.

        Returns:
            int: The request ID, if the message is a cached message.
            None: If the message was not a cached message, and so didn't have a request ID to retrieve.
        """

    @abstractmethod
    def is_redelivered(self) -> bool:
        """
        Retrieves the message redelivery status.

        Returns:
            bool: True if the message redelivery occurred in the past, otherwise False.
        """

    @abstractmethod
    def get_and_convert_payload(self, converter: BytesToObject[T], output_type: type) -> T:
        """
        Retrieve the payload and converts it to the target object using given ``converter``.

        Args:
            converter(BytesToObject): An application provided converter to deserialize the payload to a Python object.
            output_type (type):  The Python Class returned by the BytesToObject type.

        Returns:
            T: The user-defined type for returned value.

        Raises:
            PubSubPlusClientError:  When the converter returns a non-matching object type.
        """

    @abstractmethod
    def get_destination_name(self) -> Union[str, None]:
        """
        Retrieves the destination which the message was received, which can be a topic or a queue.

        Returns:
            str: The destination name.

        """

    @abstractmethod
    def get_time_stamp(self) -> Union[int, None]:
        """
        Retrieves the timestamp (Unix epoch time) of the message when it arrived at the Client API.
        The time is in milliseconds.

        Returns:
            int: The timestamp (Unix Epoch time) or None if not set. The time is in milliseconds.
        """

    @abstractmethod
    def get_sender_timestamp(self) -> Union[int, None]:
        """
        Retrieves the sender's timestamp (Unix epoch time). This field can be set during message publishing.
        The time is in milliseconds.

        Returns:
            int: The timestamp (Unix Epoch time) or None if not set. The time is in milliseconds.
        """

    @abstractmethod
    def get_message_discard_notification(self) -> 'MessageDiscardNotification':
        """
        Retrieves the message discard notification about previously discarded messages.
        This is for non-durable consumers that use Direct Transport.

        Returns:
            MessageDiscardNotification: A value not expected to be None.
        """

    @abstractmethod
    def get_sender_id(self) -> Union[str, None]:
        """
        Returns the sender's ID. This field can be set automatically during message publishing, but
        existing values are not overwritten if non-None, as when a message is sent multiple times.

        Returns:
            str: The sender's ID or None if not set.
        """

    def get_replication_group_message_id(self) -> Union['ReplicationGroupMessageId', None]:
        """
        Retrieves the Replication Group Message Id

        Returns:
            ReplicationGroupMessageId : can be None for direct message or unsupported broker versions
        """

    class MessageDiscardNotification(ABC):
        """
         An interface to Discard Notification Information.
        """

        @abstractmethod
        def has_broker_discard_indication(self) -> bool:
            """
            Retrieves the broker discard indication. A receiving client can use a message
            discard indication method or function to query whether the Solace event broker
            has for any reason discarded any Direct messages previous to the current received message.

            When the Solace event broker discards messages before sending them,
            the next message successfully sent to the receiver will have discard indication set.

            Returns:
                bool: True if Solace event broker has discarded one or more messages prior to the current message.
            """

        @abstractmethod
        def has_internal_discard_indication(self) -> bool:
            """
            Retrieves the internal discard indication.
            A receiving client can use a message discard indication method or function to
            query whether Python API has for any reason discarded any messages previous to the current
            received message.

            Returns:
                bool: True if the Python API has discarded one or more messages prior to the current message.
            """

class ReplicationGroupMessageId(ABC):
    """An abstract class that defines the interfaces for a Replication Group Message ID."""

    # pylint: disable=invalid-name
    @staticmethod
    def of(replication_group_message_id_string: str):
        """
        A factory method to create an instance of a ReplicationGroupMessageId from a specified string.
        This method can be used to create a ReplicationGroupMessageId for message
        replay configuration. The string may be retrieved from str() or it can be retrieved
        from any of the broker admin interfaces.

        Args:
            replication_group_message_id_string (str): the string identifier associated with Replication Group
             Message ID previously returned from str() method.

        Returns:
            ReplicationGroupMessageId: object representing the Replication Group Message Id

        Raises:
            IllegalArgumentError : if string argument is empty or is not in the proper format as
            returned from str() previously
        """
        if replication_group_message_id_string == '':
            raise IllegalArgumentError("replication_group_message_id_string cannot be empty")
        if not isinstance(replication_group_message_id_string, str):
            raise InvalidDataTypeError("replication_group_message_id_string must be type of string")
        return _ReplicationGroupMessageId.from_str(replication_group_message_id_string)

    @abstractmethod
    def compare(self, replication_group_message_id: 'ReplicationGroupMessageId') -> int:
        """
        Compare the Replication Group Message Id to another. Not all valid Replication Group Message
        Id can be compared.  If the messages identifed by the Replication Message Id were not published to
        the same broker or HA pair, then they are not comparable and this method throws an
        IllegalArgumentError exception.

        Args:
            replication_group_message_id(ReplicationGroupMessageId):to compare current instance with

        Returns:
            negative integer, zero, or a positive integer if this object is less than, equal to,
            or greater than the specified one.
        Raises:
            IllegalArgumentError if the both Replication Group Message Ids can't be compared,
                                       i.e when corresponding messages were not published to the
                                       same broker or HA pair.
        """


class _ReplicationGroupMessageId(ReplicationGroupMessageId):
    def __init__(self):
        self._rmid_struct = _SolClientReplicationGroupMessageId()

    def _load_from_string(self, rmid_str: str):
        return get_replication_group_message_id_from_string(ctypes.byref(self._rmid_struct),
                                                            ctypes.sizeof(self._rmid_struct),
                                                            ctypes.c_char_p(rmid_str.encode()))

    # pylint: disable=missing-function-docstring, protected-access
    @classmethod
    def from_str(cls, rmid_str: str):
        rmid = cls()
        return_code = rmid._load_from_string(rmid_str)
        if return_code == SOLCLIENT_FAIL:
            raise PubSubPlusClientError(last_error_info(return_code, "load from string"))
        return rmid

    def _load_from_msg(self, msg_p):
        return get_group_message_id(msg_p, ctypes.byref(self._rmid_struct), ctypes.sizeof(self._rmid_struct))

    # pylint: disable=missing-function-docstring
    @classmethod
    def create_from_msg(cls, msg_p):
        rmid = cls()
        return_code = rmid._load_from_msg(msg_p)
        if return_code == SOLCLIENT_OK:
            return rmid
        if return_code == SOLCLIENT_NOT_FOUND:
            logger.debug("ReplicationGroupMessageId is not supported")
            return None
        raise PubSubPlusClientError(last_error_info(return_code), "create from message")

    def compare(self, replication_group_message_id: 'ReplicationGroupMessageId') -> int:
        if not isinstance(replication_group_message_id, ReplicationGroupMessageId):
            raise InvalidDataTypeError("replication_group_message_id must be type of ReplicationGroupMessageId")
        compare_p = ctypes.c_int(0)
        return_code = compare_replication_group_message_id(ctypes.byref(self._rmid_struct),
                                                           ctypes.byref(replication_group_message_id._rmid_struct),
                                                           ctypes.byref(compare_p))
        if return_code == SOLCLIENT_FAIL:
            raise IllegalArgumentError(last_error_info(return_code, "compare ReplicationGroupMessageId"))
        return compare_p.value

    def __str__(self):
        id_str = ctypes.create_string_buffer(MAX_RMID_STR_LEN)
        return_code = get_replication_group_message_id_to_string(ctypes.byref(self._rmid_struct),
                                                                 ctypes.sizeof(self._rmid_struct), id_str)
        if return_code == SOLCLIENT_OK:
            try:
                return id_str.value.decode()
            except UnicodeError as exception:
                logger.error(str(exception))
                return repr(self)
        else:
            return repr(self)
