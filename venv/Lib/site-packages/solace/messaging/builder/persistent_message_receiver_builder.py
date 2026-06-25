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
 This module contains a persistent message receiver builder.
 Applications that need to receive persistent messages must first create a ``PersistentMessageReceiverBuilder``
 instance using the the :py:meth:`MessagingService.create_persistent_message_receiver_builder()` method.

 The PersistentMessageReceiverBuilder then creates one or more ``PersistentMessageReceiver`` instances as necessary."""

# pylint: disable=too-many-ancestors

from abc import abstractmethod

from solace.messaging.builder.message_receiver_builder import MessageReceiverBuilder
from solace.messaging.config.message_acknowledgement_configuration import MessageAcknowledgementConfiguration
from solace.messaging.config.message_replay_configuration import MessageReplayConfiguration
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationConfiguration
from solace.messaging.config.receiver_activation_passivation_configuration import \
    ReceiverActivationPassivationConfiguration
from solace.messaging.receiver.persistent_message_receiver import PersistentMessageReceiver
from solace.messaging.resources.queue import Queue


class PersistentMessageReceiverBuilder(MessageReceiverBuilder,
                                       ReceiverActivationPassivationConfiguration,
                                       MissingResourcesCreationConfiguration,
                                       MessageAcknowledgementConfiguration,
                                       MessageReplayConfiguration):
    """
    A class that configures and creates instances of ``PersistentMessageReceiverBuilder``.
    The ``PersistentMessageReceiverBuilder`` builds the
    :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver` instances.
    """

    @abstractmethod
    def with_message_selector(self, selector_query_expression: str) -> 'PersistentMessageReceiverBuilder':
        """
        Enables support for message selection based on the message header parameter and message properties values.
        When a selector is applied, then the receiver only gets messages whose headers and properties match
        the selector. A message selector cannot select messages on the basis of the content of the message body.

        Args:
            selector_query_expression(str): The selector query expression

        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def build(self, endpoint_to_consume_from: Queue) -> PersistentMessageReceiver:
        """
        Creates an instance of
        :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`.

        Args:
            endpoint_to_consume_from(Queue): The Queue to receive message.

        Returns:
            PersistentMessageReceiver: A persistent message receiver.
        """
