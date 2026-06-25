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

#  pylint: disable=line-too-long

"""
This module defines the interface for configuring message acknowledgement strategy. In some scenarios,
when a specific message is published, the receiver that has received that message can send an
acknowledgement for the message that was received back to the publisher. With auto-acknowledgement,
you can automatically acknowledge each message. With client-acknowledgement, the user-defined
application must deliberately acknowledge messages.
"""

from abc import abstractmethod
from enum import Enum
from solace.messaging.config.message_auto_acknowledgement_configuration import MessageAutoAcknowledgementConfiguration

class Outcome(Enum) :
    """
    A class that represents the outcomes to settle a message.
    This is for use both in PersistentMessageReceiverBuilder configuration, and in PersistentMessageReceiver settle() calls.
    Specifically,
    :py:meth:`PersistentMessageReceiverBuilder.with_required_message_outcome_support()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`.
    and
    :py:meth:`PersistentMessageReceiver.settle()<solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver.settle>`.
    """
    ACCEPTED = 0
    """
        Settles the message with a positive acknowledgement, removing it from the queue.
        Same as calling ack() on the message.
    """

    FAILED = 2
    """
        Settles the message with a negative acknowledgement without removing it from the queue.
        This may or may not make the message eligible for redelivery or eventually the DMQ, depending on the queue configuration.
    """

    REJECTED = 3
    """
        Settles the message with a negative acknowledgement, removing it from the queue.
    """

class MessageAcknowledgementConfiguration(MessageAutoAcknowledgementConfiguration):
    """
    An abstract class that defines the interface to configure message acknowledgement strategy.

    The default strategy enables client-acknowledgement, disables auto-acknowledgement, and allows only the ACCEPTED settlement outcome.
    """

    @abstractmethod
    def with_message_client_acknowledgement(self) -> 'MessageAcknowledgementConfiguration':
        """
        Enables support for message client-acknowledgement (client-ack) on all receiver methods,
        which includes both synchronous and asynchronous methods. Client-acknowledgement must be
        executed by the user-defined application. It is recommended that client-acknowledgement
        be written in the on_message method of the user defined message handler. This message handler would be
        of type :py:class:`solace.messaging.receiver.message_receiver.MessageHandler`.

        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def with_required_message_outcome_support(self, *outcomes:Outcome) -> 'MessageAcknowledgementConfiguration':
        r"""
        The types of settlements the receiver can use. Any combination of ACCEPTED, FAILED, and REJECTED, the order is irrelevant.
        Attempting to settle() a message later with an Outcome not listed here may result in an error.

        Args:
            outcomes (\*Outcome): The types of outcomes the settle() method of the consumer will support.

        Returns:
            An instance of itself for method chaining.
        """
