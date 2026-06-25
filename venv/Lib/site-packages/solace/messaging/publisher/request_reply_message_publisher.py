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
A Request Message Publisher must be created by
:py:class:`solace.messaging.builder.request_reply_message_publisher_builder.RequestReplyMessagePublisherBuilder`.The
RequestReplyMessagePublisher instance is used to send request-reply messages created by a
:py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder`. Topic (destination)
must be specified when the message is published.
"""
import concurrent.futures
import logging
from abc import abstractmethod, ABC
from typing import Dict, Union

from solace.messaging.publisher.message_publisher import MessagePublisher

logger = logging.getLogger('solace.messaging.publisher')


class RequestReplyMessagePublisher(MessagePublisher, ABC):
    """An interface that abstracts message request publishing feature for request-reply messaging using
     direct messaging paradigm Request destination is specified at publisher time"""

    @abstractmethod
    def publish(self, request_message: 'OutboundMessage',
                request_destination: 'Topic', reply_timeout: int,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple, None,
                                                               bytearray]] = None) -> concurrent.futures.Future:
        """Sends a request for reply message; nonblocking

        No correlation id is required to be provided, correlation is handled internally by API

        Args:
            request_message: request message to be sent
            request_destination: destination for request messages
            reply_timeout: wait time in ms to get a reply message. Timeout has to be a positive integer value, and must
                be be passed since there is no default value.
            additional_message_properties:(Dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The additional message properties to add to the message metadata.Each key can be customer provided, or
                it can be a key from of type `solace.messaging.config.solace_properties.message_properties`.
                The key for the configuration is a string, the value  can either be a string or an integer  or a float
                or a bool or a dict or list or a tuple or a None or a bytearray. property_value's int type parameter can
                have minimum value as -9223372036854775808 and maximum value as 18446744073709551615
        Returns:
            A future object that can be used to retrieve the reply message after is has been received.
        """

    @abstractmethod
    def publish_await_response(self, request_message: 'OutboundMessage',
                               request_destination: 'Topic',
                               reply_timeout: int,
                               additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list,
                                                                              tuple, None, bytearray]] = None) \
            -> 'InboundMessage':
        """Sends a request message return response message, blocking until response is received or timeout occurs

        Args:
            request_message: request message to be sent
            request_destination: destination for request messages
            reply_timeout: wait time in ms to get a reply message. Timeout has to be a positive integer value, and must
                be passed since there is no default value.
            additional_message_properties:(Dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The additional message properties to add to the message metadata.Each key can be customer provided, or
                it can be a key from of type `solace.messaging.config.solace_properties.message_properties`.
                The key for the configuration is a string, the value  can either be a string or an integer  or a float
                or a bool or a dict or list or a tuple or a None or a bytearray. property_value's int type parameter can
                have minimum value as -9223372036854775808 and maximum value as 18446744073709551615

        Returns:
            response message when any received

        Raises:
            PubSubTimeoutError: if response from a replier does not come on time
            MessageRejectedByBrokerError: if broker is rejecting messages from a publisher(only when service
                interruption listener available , warning log will be emitted)
            PubSubPlusClientError: if some internal error occurs
            IllegalArgumentError: if the value of timeout is negative
            InvalidDataTypeError: if the value of timeout is None also  when additional_message_properties's int
            type value is not in  between the range of minimum value & maximum value"""
