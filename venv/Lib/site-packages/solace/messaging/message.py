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
# pylint: disable=no-else-break

"""
This module is an abstract base class for a Message.

``Message`` is the base class for:

- :py:class:`solace.messaging.publisher.outbound_message.OutboundMessage`
- :py:class:`solace.messaging.receiver.inbound_message.InboundMessage`

``Message`` instances are the objects that carry the payload and meta data to and from the
:py:class:`solace.messaging.message_service.MessageService`
"""

import logging
from abc import abstractmethod

from typing import Union, Dict, List

from solace.messaging.utils.interoperability_support import InteroperabilitySupport

logger = logging.getLogger('solace.messaging.core')


class Message(InteroperabilitySupport):
    """
    An abstract class that abstracts a Solace Event Broker Message.
    """

    @abstractmethod
    def get_properties(self) -> Dict[str, Union[str, int, float, bool, dict, list,
                                                bytearray, None]]:
        """
        Retrieves the non-solace properties attached to the message.

        Any property defined in
        :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`
        is not returned in this dictionary. Solace defined property
        keys all begin with "solace.messaging", however any key even those beginning with "solace." may be a
        a non solace property if it is not defined in this API.

        Message Properties are carried in Message meta data in addition to the Message payload.  Properties are
        stored in a dictionary of key-value pairs where the `key` is controlled by the application.

        Returns:
            dict: The non-solace properties attached to the message.
        """

    @abstractmethod
    def has_property(self, name: str) -> bool:
        """
        Checks if the message has a specific non-solace property attached.

        Any property defined in
        :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`
        is not available and this method will return false. Solace defined
        property keys all begin with "solace.messaging", however any key even those beginning with "solace." may be a
        a non solace property if it is not defined in this API.

        Args:
            name(str): the name of the property.

        Returns:
            True if the property is present. False otherwise.
        """

    @abstractmethod
    def get_property(self, name: str) -> Union[str, int, float, bool, dict, list,
                                               bytearray, None]:
        """
        Retrieves  The value of a specific non-solace property.

        Any property defined in
        :py:mod:`Message Properties<solace.messaging.config.solace_properties.message_properties>`
        is not available and this method will return None. Solace defined
        property keys all begin with "solace.messaging", however any key even those beginning with "solace." may be a
        a non solace property if it is not defined in this API.

        Args:
            name(str): The name of the property.

        Returns:
             str, int, float, bool, dict, list, bytearray, None: The value of the named property if found in the
                 message otherwise, returns None.
        """

    @abstractmethod
    def get_payload_as_bytes(self) -> Union[bytearray, None]:
        """
        Retrieves the payload of the message.

        Returns:
            bytearray : the byte array with the message payload or None if there is no payload.
        """

    @abstractmethod
    def get_payload_as_string(self) -> Union[str, None]:
        """
        Retrieves the string-encoded payload of message.

        Solace Event Broker messages can be published with a string-encoded payload.
        This is a platform-agnostic string format that allows strings to be sent and received
        in messages that is independent of the publisher or consumer applications.
        For example, in this way a non-Python publishing application can send a Unicode string
        that can still be consumed by a Python-based application.

        If message payload is not specifically encoded as a string, it cannot be retrieved as a string. For instance,
        a publisher if the publisher sends a UTF-8 string as a bytearray, this method cannot be used to extract the
        string.  Even though the payload is a string (``str``), it is not encoded to identify it as such.

        Returns:
            str : String found in the payload or None if there is no payload, or the payload is not a String.
        """

    @abstractmethod
    def get_payload_as_dictionary(self) -> Union[Dict, None]:
        """
            Retrieves the dictionary format of payload of message.

            Solace Event Broker messages can be published with a SDTMap payload.
            This is a platform-agnostic dictionary format that allows data types to be sent
            and received in messages that is independent of the publisher or consumer applications.

            Returns:
                dict : dictionary found in the payload or None if there is no payload, or the payload is not a
                    dictionary

            Raises:
                PubSubPlusCoreClientError : Raises when there is an internal error
                SolaceSDTError : Raises when unsupported data type is received
        """

    @abstractmethod
    def get_payload_as_list(self) -> Union[List, None]:
        """
            Retrieves the list format of payload of message.

            Solace Event Broker messages can be published with a SDTStream payload.
            This is a platform-agnostic list format that allows data types to be sent and
            received in messages that is independent of the publisher or consumer applications.

            Returns:
                list : list found in the payload or None if there is no payload, or the payload is not a List

            Raises:
                PubSubPlusCoreClientError : Raises when there is an internal error
                SolaceSDTError : Raises when unsupported data type is received
        """

    @abstractmethod
    def get_correlation_id(self) -> Union[str, None]:
        """
        Retrieves the correlation ID from the message.
        The correlation ID is user-defined, carried end-to-end, and can also be matched in a
        selector, but otherwise is not relevant to the event broker. The correlation ID may be
        used for peer-to-peer message synchronization. In JMS applications this field is
        carried as the JMSCorrelationID Message Header Field.

        Returns:
            str : A unique identifier for the message set by producer or None.
        """

    @abstractmethod
    def get_expiration(self) -> Union[int, None]:
        """
        Retrieves the expiration time.

        The expiration time is the UTC time (in ms, from midnight, January 1, 1970 UTC)
        when the message is considered expired. A value of 0 means the message never expires.
        The default value is 0.

        Returns:
            int :
              The UTC time when the message is discarded or moved to a Dead Message Queue
              by the Solace Event Broker or None if it was not set.
        """

    @abstractmethod
    def get_sequence_number(self) -> Union[int, None]:
        """
        Gets the sequence number of the message.

        Sequence numbers may be set by publisher applications or automatically generated by publisher APIs.  The
        sequence number is carried in the Message meta data in addition to the payload and may be retrieved by
        consumer applications.

        Returns:
            int : The positive sequence number or None if it was not set.
        """

    @abstractmethod
    def get_priority(self) -> Union[int, None]:
        """
        Retrieves the priority value. Valid values range from 0 to 255.

        Returns:
            int: A priority value from 0 to 255, or None if the priority is not set.

        Raises:
            PubSubPlusClientError: Any error if the priority of the message could not be retrieved.
        """

    @abstractmethod
    def get_application_message_id(self):
        """
        Gets an optional application message identifier when sender application sets one.

        Returns:
            str: Sender application identifier if set by message publisher, or None/empty if not set.
        """

    @abstractmethod
    def get_application_message_type(self):
        """
        Gets the application message type. This value is used by applications only, and is passed through the
        API unmodified.

        Returns:
            str: Application message type or None if not set.
        """

    @abstractmethod
    def get_class_of_service(self) -> Union[int, None]:
        """
        Retrieves the class of service level of a given message. This feature is only relevant.
        for direct messaging. If no class of service is set, the message is given
        a default class of service of 0.

        Returns:
            (int): An integer between 0 and 2, inclusive, representing the class of service of the message.

        Raises:
            PubSubPlusClientError: If an error was encountered while trying to retrieve the class of
                                       service of the message.
        """
