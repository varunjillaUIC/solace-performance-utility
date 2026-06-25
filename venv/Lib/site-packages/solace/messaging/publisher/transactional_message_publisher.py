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
This module contains the TramsactionalMessagePublisher class.

A transactional message publisher must be created using
:py:class:`solace.messaging.builder.transactional_message_publisher_builder.TransactionalMessagePublisherBuilder`. The
TransactionalMessagePublisher instance is used to publish messages created by a
:py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder` on the transacted session.
The topic (or destination)
can be added when the message is a published.

The transactional message publisher may also be used to publish simple messages
containing only a bytearray or string payload.
"""

from abc import ABC
from typing import Union, Dict

from solace.messaging.publisher.message_publisher import MessagePublisher
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.resources.topic import Topic

class TransactionalMessagePublisher(MessagePublisher, ABC):
    """
        An interface for publishing transactional messages.
    """
    def publish(self, message: Union[bytearray, str, OutboundMessage], \
                destination: Topic, \
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple, \
                                                               None, bytearray]] = None):
        """
        Sends {@link OutboundMessage} to the given destination
        {@link OutboundMessageBuilder} can be used to create a new message
        instance.

        Args:
            message:(bytearray, str, OutboundMessage): The message or the or payload to publish.
            destination:(Topic): The destination to add to the message.
            additional_message_properties:(Dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The additional message properties to add to the message metadata.Each key can be customer
                provided, or it can be a key from of type
                `solace.messaging.config.solace_properties.message_properties`.
                The key for the configuration is a string, the value  can either be a string or an integer
                or a float or a bool or a dict or list or a tuple or a None or a bytearray.
                property_value's int type parameter can
                have minimum value as -9223372036854775808 and maximum value as 18446744073709551615

        Raises:
            PubSubPlusClientError: When message can't be send and retry attempts would not help.
            PublisherOverflowError: When a publisher publishes messages faster than the I/O
                capabilities allow or internal message buffering capabilities are exceeded.
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
                range of minimum value & maximum value

        """
