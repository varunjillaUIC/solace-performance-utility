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
This module contains the abstract base class for a persistent message receiver.

A PersistentMessageReceiver can be instantiated to receive Persistent Messages from a Solace event broker.

"""
# pylint: disable=too-many-ancestors
import logging
from abc import ABC, abstractmethod
from typing import Union


from solace.messaging.receiver.acknowledgement_support import AcknowledgementSupport
from solace.messaging.receiver.async_receiver_subscriptions import AsyncReceiverSubscriptions
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.message_receiver import MessageReceiver
from solace.messaging.receiver.receiver_flow_control import ReceiverFlowControl
from solace.messaging.receiver.receiver_subscriptions import ReceiverSubscriptions
from solace.messaging.utils.manageable_receiver import PersistentReceiverInfo, ManageableReceiver

logger = logging.getLogger('solace.messaging.receiver')


# pylint: disable=line-too-long
class PersistentMessageReceiver(MessageReceiver, ReceiverFlowControl, AcknowledgementSupport, ReceiverSubscriptions,
                                AsyncReceiverSubscriptions, ManageableReceiver, ABC):
    """
    An abstract class that defines the interface to a persistent message receiver.

    Note:
        A caller of any of blocking message receiving methods , those without the *async* suffix such as the
        :py:func:`PersistentMessageReceiver.receive_message()<solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver.receive_message()>`,
        method will receive a new message for each call.

    WARNING:
        When you use this class, these are some considerations to aware of:

        - Concurrent use of asynchronous and synchronous message receiving methods on a single instance of
          receiver can have some unintended side effects and should be avoided.

        - Asynchronous methods should NOT be called multiple times or in combination with blocking message
          receiving function on the same :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`
          instance to avoid any unintended side effects.

        - After a broker initiated termination has occurred, PersistentMessageReceiver.ack would raise and exception.
          This behavior can occur before the TerminateEvent is pushed to the application via the handler.
          Termination Notification Event is dispatched on termination triggered by flow down or flow session down event.
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

    @abstractmethod
    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        """
        Blocking request to receive the next message. You acknowledge the message using the
        :py:func:`solace.messaging.receiver.acknowledgement_support.AcknowledgementSupport.ack()` function
        for (:py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`).

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

    @abstractmethod
    def receiver_info(self) -> PersistentReceiverInfo:
        """
        Provides access to the Persistent receiver information

        Returns:
            PersistentReceiverInfo : an object that represents message receiver manageability.
       """
