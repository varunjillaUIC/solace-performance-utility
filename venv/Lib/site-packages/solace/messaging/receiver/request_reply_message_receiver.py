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

# pylint: disable=too-few-public-methods,arguments-differ,trailing-whitespace,unused-import

"""
This module contains the abstract base class used to receive the reply messages using the direct messaging paradigm.

A RequestReplyMessageReceiver can be instantiated to receive reply messages from a Solace event broker.
"""
import logging
from abc import ABC, abstractmethod
from typing import Union, Tuple

from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageReceiver

logger = logging.getLogger('solace.messaging.receiver')


class Replier(ABC):
    """
    The replier is used to send a reply for a request message that has been received. The API is
    responsible for handling any fields which correlate the request message and the reply message.
    """

    @abstractmethod
    def reply(self, response_message: 'OutboundMessage'):
        """
        Publish a response message as a reply to a received message that has been sent using RequestReply.

        Args:
            response_message: The response message from the replier which correlates to the original request message.
        Raises:
            PubSubPlusClientError: When a reply can't be sent.
        """


# pylint: disable=line-too-long
class RequestMessageHandler(ABC):
    """
    An abstract class that defines the interface for a user defined message handler that can be used by
    :py:meth:`RequestReplyMessageReceiver.receive_async<solace.messaging.receiver.request_reply_message_receiver.RequestReplyMessageReceiver.receive_async>`.
    """

    @abstractmethod
    def on_message(self, message: 'InboundMessage', replier: 'Replier'):
        """Message processing callback method that allow user to implement custom message
        processing business logic combined with an ability to send a response right away.

        Args:
            message: The request message
            replier: The message publishing utility for sending responses. If the API finds
                the reply destination in the inbound message, this will be a
                :py:class:`solace.messaging.receiver.request_reply_message_receiver.Replier`
                object. If the API does not find the reply destination in the inbound message
                this will be a None type object.

        """


class RequestReplyMessageReceiver(MessageReceiver):
    """An interface that abstracts message reply feature for request-reply messaging using direct messaging paradigm"""

    @abstractmethod
    def receive_message(self, timeout: int = None) -> Tuple[Union[InboundMessage, None], Union[Replier, None]]:
        """
        This method returns the received message and the
        :py:class:`solace.messaging.receiver.request_reply_message_receiver.Replier`
        object that can be used to send a reply as a part of the Request/Reply paradigm. This method blocks while
        waiting for the received message.

        Args:
            timeout (int): timeout in milliseconds

        Returns:
            (tuple): tuple containing:

            - if the message is successfully found in the receiver buffer, and if the reply destination is
              successfully found in the message:

              - message (InboundMessage): Received message
              - replier (Replier): replier instance to reply back to request

            - if the message is successfully found in the receiver buffer, but the reply destination is not
              found in the message:

              - message (InboundMessage): Received message
              - replier (None): None type is returned

            - if the receiver buffer is empty or if the timeout passed to this method expires while trying
              to retrieve a message from the receiver buffer, then there is no message or reply destination
              to be found:

              - message (None): None type is returned
              - replier (None): None type is returned

        """

    @abstractmethod
    def receive_async(self, message_handler: 'RequestMessageHandler'):
        """
        Register an asynchronous message receiver on the
        :py:class:`solace.messaging.receiver.request_reply_message_receiver.RequestReplyMessageReceiver` instance.
        This message receiver will use the passed RequestMessageHandler to process the message and send the reply
        associated with the request.

        Args:
            message_handler (RequestMessageHandler): User defined request/reply message handler.
                See :py:class:`solace.messaging.receiver.request_reply_message_receiver.RequestMessageHandler`
                for more information on request message handlers.

        """
