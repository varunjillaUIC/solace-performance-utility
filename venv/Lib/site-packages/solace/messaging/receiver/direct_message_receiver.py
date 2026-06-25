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

# pylint: disable=too-many-ancestors, too-few-public-methods

"""
This module contains the abstract base class used to receive direct messages.

A DirectMessageReceiver can be instantiated to receive direct messages from a Solace event broker.
"""
from abc import ABC, abstractmethod
from typing import Union

from solace.messaging.receiver.async_receiver_subscriptions import AsyncReceiverSubscriptions
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageReceiver
from solace.messaging.receiver.receiver_subscriptions import ReceiverSubscriptions
from solace.messaging.receiver.receiver_cache_requests import ReceiverCacheRequests


class DirectMessageReceiver(MessageReceiver, ReceiverSubscriptions,
                            AsyncReceiverSubscriptions, ReceiverCacheRequests, ABC):
    """
    An abstract class that defines the interface to a Solace event broker direct message consumer/receiver.

    NOTE:
        A caller of any of blocking message receiving methods , those without the *async* suffix such as the
        :py:func:`solace.messaging.receiver.message_receiver.MessageReceiver.receive_message()` function.
        will receive a new message for each call.

    WARNING:
        When you use this class, these are some considerations to aware of:

        - Concurrent use of asynchronous and synchronous message receiving methods on a single instance of
          receiver can have some unintended side effects and should be avoided.

        - Asynchronous methods should NOT be called multiple times or in combination with blocking message
          receiving function on the same  :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`
          object to avoid any unintended side effects.

    """

    @abstractmethod
    def receive_async(self, message_handler: 'MessageHandler'):
        """
        Register an asynchronous message receiver on the
        :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver` instance.

        Args:
            message_handler(MessageHandler): The object that receives all inbound messages (InboundMessage)
                in its onMessage() callback. If the provided value is None, then asynchronous receiver is removed &
                receive_message()
                (:py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`) is used.
        """

    # pylint: disable=line-too-long
    @abstractmethod
    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        """
        Blocking request to receive the next message. You acknowledge the message using the
        :py:func:`AcknowledgementSupport.ack()<solace.messaging.receiver.acknowledgement_support.AcknowledgementSupport.ack()>` function
        for :py:class:`PersistentMessageReceiver<solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver>`.

        This method is usually used in loop an its use is mutually exclusive when
        used asynchronously.

        Args:
            timeout(int): The time, in milliseconds, to wait for a message to arrive.

        Returns:
            InboundMessage: An object that represents an inbound message. Returns None on timeout, or upon
                service or receiver shutdown.

        Raises:
            PubSubPlusClientError: If error occurred while receiving or processing the message.
    """
