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

# pylint: disable=line-too-long

"""This module contains the abstract class and methods for the AcknowledgementSupport."""

from abc import ABC, abstractmethod

from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.config.message_acknowledgement_configuration import Outcome


class AcknowledgementSupport(ABC):
    """
        A class that defines the interface for manual message settlement (receiver signals to the broker it accepts,
        rejects, or fails a message).

        Client acknowledgement (ACCEPTED outcome) signals to the event broker the message has been received and
        processed. When all receivers have acknowledged that a message has been delivered, the message is removed
        from the permanent storage on the event broker.
            
        Rejecting a message (REJECTED outcome) signals to the event broker the message is bad and should be removed
        from the queue without any attempt of redelivery.
            
        Failing to process a message (FAILED outcome) signals to the event broker this client is currently unable to
        accept the message. Depending on queue configuration it may be redelivered to this or other receivers for a
        set number of times, or moved to the DMQ.

        Settlement, or withholding settlement has no bearing on flow-control or back-pressure.
    """

    @abstractmethod
    def ack(self, message: InboundMessage):
        """
        Generates and sends an acknowledgement for an inbound message (:py:class:`InboundMessage<solace.messaging.receiver.inbound_message.InboundMessage>`).

        Args:
            message (InboundMessage): The inbound message.

        Raises:
            PubSubPlusClientError: If it was not possible to acknowledge the message.
        """

    @abstractmethod
    def settle(self, message: InboundMessage, outcome: Outcome = Outcome.ACCEPTED):
        """
        Generates and sends a positive or negative acknowledgement for an inbound message (:py:class:`InboundMessage<solace.messaging.receiver.inbound_message.InboundMessage>`) from this receiver as indicated by 
        the outcome (:py:class:`Outcome<solace.messaging.config.message_acknowledgement_configuration.Outcome>`) argument.
        To use the negative outcomes FAILED and REJECTED, the receiver has to have been preconfigured via its builder to support that using the 
        :py:meth:`with_required_message_outcome_support()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`
        method, or the
        :py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_REQUIRED_MESSAGE_OUTCOME_SUPPORT`
        receiver property.
 
        This method should not be called more than once for the same message.
 
        Attempts to settle a message on an auto-acking receiver is ignored, and causes a warning log for FAILED and REJECTED.
 
        Args:
            message (InboundMessage): The inbound message from this receiver.
            outcome (Outcome): The settlement outcome (ACCEPTED, FAILED, REJECTED) Defaults to ACCEPTED, making this call equivalent to ack().
 
        Raises:
            PubSubPlusClientError: If it was not possible to settle the message.
        """
