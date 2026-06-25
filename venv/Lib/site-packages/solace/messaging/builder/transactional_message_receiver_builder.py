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
 This module contains a builder for the transactional message receivers.
 Applications that need to receive messages on a transacted session
 must first create a  ``TrannsactionalMessageReceiverBuilder``
 using the
 :py:meth:`solace.messaging.messaging_service.TransactionalMessagingService.create_transactional_receiver_builder()`.

 The ``TransactionalMessageReceiverBuilder`` then creates one or more
 ``TransactionalMessageReceiver`` instances as needed.
"""

from abc import ABC
from solace.messaging.builder.message_receiver_builder import MessageReceiverBuilder
from solace.messaging.config.receiver_activation_passivation_configuration import \
    ReceiverActivationPassivationConfiguration
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationConfiguration
from solace.messaging.resources.queue import Queue
from solace.messaging.config.message_replay_configuration import MessageReplayConfiguration

class TransactionalMessageReceiverBuilder(MessageReceiverBuilder,
                                          ReceiverActivationPassivationConfiguration,
                                          MissingResourcesCreationConfiguration,
                                          MessageReplayConfiguration, ABC):
    """
       A class to configure and create instances of {@link TransactionalMessageReceiver} to receive
       transactional messages.
    """

    def build(self, endpoint_to_consume_from: Queue) -> 'TransactionalMessageReceiver':
        """
            Builds a transactional message receiver.
            Args:
                endpoint_to_consume_from(Queue): The Queue to receive message.
        """

    def with_message_selector(self, selector_query_expression: str) -> 'TransactionalMessageReceiverBuilder':
        """
            Enables support for message selection based on message header parameter and message properties values.
            When selector is applied, then the receiver gets only messages
            whose headers and properties match the selector.
            A message selector cannot select messages on the basis of the content of the message body.
            Args:
            selector_query_expression(str): The selector query expression
            Returns:
                An instance of itself for method chaining.
        """
