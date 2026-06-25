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

"""
This module contains classes for an outbound message and the
interface definition for a builder for an outbound message.
 """

from abc import ABC, abstractmethod
from typing import TypeVar, Dict, Union

from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration
from solace.messaging.message import Message
from solace.messaging.utils.converter import ObjectToBytes

T = TypeVar('T', bytearray, str, 'OutboundMessage')  # pylint: disable=invalid-name


class OutboundMessageBuilder(PropertyBasedConfiguration):
    """
    .. _OutboundMessageBuilder:

    This builder is used for building outbound messages which are published using
    :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher`.

    """

    @abstractmethod
    def from_properties(self, configuration: Dict[str, Union[str, int, float, bool, dict, list, tuple,
                                                             bytearray, None]]) -> 'OutboundMessageBuilder':
        """
        Adds user properties/Solace defined properties to the message. User properties are carried in the message
        metadata as key-value pairs.For Solace defined properties the value must be valid data type for the
        respective key

        Args:
            configuration (Dict[str,  Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The message attributes dictionary,it can have the key as string. Each key can be
                customer provided, or it can be a key from
                :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`.

                The value  can either be a string or an integer or a float or a bool or a dict or list or a tuple
                or a bytearray or None. When value is an integer, the
                minimum value is -9223372036854775808 and maximum value is 18446744073709551615.

        Raises:
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value
        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.

        """

    @abstractmethod
    def with_property(self, property_key: str,
                      property_value: Union[str, int, float, bool, dict, list, tuple, bytearray, None])\
            -> 'OutboundMessageBuilder':
        """
        Adds the user property/Solace defined property with the given ``key`` and ``value``.
        For Solace defined property the ``value`` must be valid data type for the given ``key``

        Args:
            property_key (str):
                The key for the configuration. Each key can be customer provided, or it can be a key from
                :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`.

            property_value (Union[str, int, float, bool, dict, list, tuple, None, bytearray]):
                The value for the key, it can be a string or an integer or a float or a bool or a dict or list or a
                tuple or a bytearray or None.  When value is an integer, the
                minimum value is -9223372036854775808 and maximum value is 18446744073709551615.

        Raises:
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.

        """

    @abstractmethod
    def with_expiration(self, timestamp: int) -> 'OutboundMessageBuilder':
        """
        Sets message expiration time.

        Args:
            timestamp(int): The timestamp in milliseconds (Unix Epoch time), or None (to delete).


        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_priority(self, priority: int) -> 'OutboundMessageBuilder':
        """
        Sets the priority (0 to 9), where zero is the lowest priority.  If the priority is
        set to a value larger than 9, it's treated as a 9 (the highest priority possible).

        Args:
            priority(OutboundMessageBuilder.Priority): The priority of the outbound message.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_application_message_type(self, application_message_type: str) -> 'OutboundMessageBuilder':
        """
        Sets the application message type for a message using a string or None (to delete).

        The Application Message type is carried in the message meta data. It is used for application to
        application signaling.

        Args:
            application_message_type (str): The application message type.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_sequence_number(self, sequence_number: int) -> 'OutboundMessageBuilder':
        """
        Sets the sequence number for the message.

        The sequence number is carried in the message meta data.  It is used for application to
        application signaling.

        Args:
            sequence_number (int):  The expected integer value.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_application_message_id(self, application_message_id: str) -> 'OutboundMessageBuilder':
        """
        Sets the application message identifier for a message from a string or None (to delete it).

        The application message identifier is carried in the message metadata. It is used for application to
        application signaling.

        Args:
            application_message_id (str): The application identifier.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_sender_id(self, sender_id: Union[str, None]) -> 'OutboundMessageBuilder':
        """
        Sets the sender ID for a message from a string, or deletes it if None is passed. Note: if
        :py:const:`GENERATE_SENDER_ID<solace.messaging.config.solace_properties.service_properties.GENERATE_SENDER_ID>`
        is enabled on the messaging service, then passing a string to this method will override the
        API generated sender ID, but passing None to this method will not override the API generated sender ID.

        The sender ID is carried in the message metadata. It is used to identify the sender of the message.

        Args:
            sender_id (str): The sender ID.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_http_content_header(self, content_type: str, content_encoding: str) -> 'OutboundMessageBuilder':
        """
        Sets the HTTP content-type and HTTP content-encoding for a message.

        For interoperability with REST clients, it may be necessary to set the HTTP content-type
        and HTTP content-encoding parameters.

        Args:
            content_type (str):  The expected and valid HTTP content-type.
            content_encoding (str):  The expected and valid HTTP content-encoding

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def with_correlation_id(self, correlation_id: str) -> 'OutboundMessageBuilder':
        """
        Sets the correlation ID for the message.
        The correlation ID is user-defined, carried end-to-end, and can also be matched in a selector,
        but otherwise not relevent to the event broker. The correlation ID may be used for peer-to-peer
        message synchronization. In JMS applications this field is carried as the JMSCorrelationID Message
        Header Field.

        Args:
            correlation_id (str): The correlation ID to be set

        Raises:
            InvalidDataTypeError: If the passed correlation_id is not a string.

        Returns:
            OutboundMessageBuilder: A builder object representing an outbound message object for method chaining.
        """

    @abstractmethod
    def build(self, payload: T, additional_message_properties: Dict[str, Union[str, int, float, bool, dict,
                                                                               list, tuple, None, bytearray]] = None,
              converter: ObjectToBytes[T] = None) -> 'OutboundMessage':
        """
        Builds a :py:class:`solace.messaging.publisher.outbound_message.OutboundMessage` instance with the
        specified payload. The payload must be a :py:class:`bytearray` or :py:class:`str`; if it is not,
        you must specify a
        :py:class:`solace.messaging.utils.converter.ObjectToBytes`
        that converts the object to a :py:class:`bytearray`.

        :py:mod:`Message properties<solace.messaging.config.solace_properties.message_properties>` may be set
        on each build.

        Args:
            payload (T): The payload to add to the message.
            additional_message_properties (dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
              The additional message properties to add to the message metadata. Each key can be customer provided,
              or it can be a key from
              :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`.
              The key for the property is a string.

              The value  can either be a string or an integer or a float or a bool or a dict or list or a tuple
              or a bytearray or None. When value is an integer, the
              minimum value is -9223372036854775808 and maximum value is 18446744073709551615.
            converter(ObjectToBytes): The converter to convert the ``payload`` object to :py:class:`bytearray`.
        Raises:
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value
        Returns:
            OutboundMessage: An outbound message object.
        """


class OutboundMessage(Message, ABC):
    """
        An abstract class that defines the interface for an outbound message.

        An instance OutboundMessage can be created using a
        :py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder` instance.
    """
