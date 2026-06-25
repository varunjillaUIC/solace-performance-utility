
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
This module contains the abstract base class used to receive transactional messages.

A TransactionalMessageReceiver can be instantiated to receive messages from a Solace event broker
as part of a transacted session.
"""

from abc import ABC, abstractmethod
from typing import Union
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageReceiver
from solace.messaging.receiver.receiver_subscriptions import ReceiverSubscriptions
from solace.messaging.receiver.async_receiver_subscriptions import AsyncReceiverSubscriptions
from solace.messaging.utils.manageable_receiver import TransactionalReceiverInfo, ManageableReceiver
from solace.messaging.receiver.receiver_flow_control import ReceiverFlowControl

class TransactionalMessageHandler(ABC):
    """
        An interface for the message handler within a transaction.
    """

    @abstractmethod
    def on_message(self, message: InboundMessage):
        """
            Definition for a message processing function within a transaction.

            Args:
                message(InboundMessage): The inbound message.
        """

# pylint: disable=line-too-long
class TransactionalMessageReceiver(MessageReceiver, ReceiverFlowControl, ReceiverSubscriptions,
                                   AsyncReceiverSubscriptions, ManageableReceiver, ABC):
    """
        An interface for receiving transactional messages.

        WARNING:
            Use of an asynchronous (non-blocking) method (has the 'Async' suffix) is
            mutually-exclusive to any another method. An asynchronous method cannot be called multiple times
            or in combination with any another message receiving method on a same instance of a
            :py:class:`MessageReceiver<solace.messaging.receiver.message_receiver.MessageReceiver>`.

        For LifecycleControl terminate, once terminate completes no further messages will be dispatched,
        either from :py:meth:`receive_async()<solace.messaging.receiver.transactional_message_receiver.TransactionalMessageReceiver.receive_async>`
        or :py:meth:`receive_message()<solace.messaging.receiver.transactional_message_receiver.TransactionalMessageReceiver.receive_message>`.
        The grace_period for terminate is ignored as any pending data is flushed and not included in the transaction.
    """

    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        """
            Receives a message within a given transaction in a pull fashion.
            The methods behaviour is undefined when a TransactionalMessageHandler is set using
            :py:meth:`receive_async()<solace.messaging.receiver.transactional_message_receiver.TransactionalMessageReceiver.receive_async>`.

            Args:
                timeout(int): The time, in milliseconds, to wait for a message to arrive.

            Returns:
                InboundMessage: An object that represents an inbound message.
                Returns None on timeout, or upon service or receiver shutdown.

            Raises:
                PubSubPlusClientError: When the receiver can not receive.
        """

    def receive_async(self, message_handler: 'TransactionalMessageHandler'):
        """
            Register an asynchronous message handler on the receiver.
            Once set, the receiver starts in "push" mode, and the
            :py:meth:`receive_message()<solace.messaging.receiver.transactional_message_receiver.TransactionalMessageReceiver.receive_message>`
            method can not be used. "Push" and "pull" receivers do not mix well on a single transactional service.
            In fact it is strongly advised to either completely avoid this method,
            or constrain all transactional operations (publish, commit, rollback) to the message handler callback.

            Args:
                message_handler(TransactionalMessageHandler): The object that receives all inbound messages
                    (InboundMessage) through the
                    :py:meth:`on_message()<solace.messaging.receiver.transactional_message_receiver.TransactionalMessageHandler.on_message>`
                    handler method. If the provided value is None, then asynchronous receiver is removed.
        """

    @abstractmethod
    def pause(self):
        """
            Pauses message delivery for an asynchronous message handler or stream. Message delivery can be
            resumed by executing :py:meth:`ReceiverFlowControl.resume()` on a
            :py:class:`solace.messaging.receiver.transactional_message_receiver.TransactionalMessageReceiver` instance.

        Raises:
            PubSubPlusClientError: If an error occurred while pausing message delivery.
        """

    @abstractmethod
    def receiver_info(self) -> TransactionalReceiverInfo:
        """
        Provides access to the receiver information

        Returns:
            TransactionalReceiverInfo : an object that represents message receiver manageability.
        """
