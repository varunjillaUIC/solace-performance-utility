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
 This module contains builders for direct message receivers.
 Applications that need to receive direct messages must first create a  ``DirectMessageReceiverBuilder`` instance
 using the :py:meth:`solace.messaging.message_service.MessagingService.create_direct_message_receiver_builder()`

 The DirectMessageReceiverBuilder then creates one or more  DirectMessageReceiver as necessary.
"""
from abc import abstractmethod

from solace.messaging.builder.message_receiver_builder import MessageReceiverBuilder
from solace.messaging.receiver.direct_message_receiver import DirectMessageReceiver
from solace.messaging.config.direct_receiver_back_pressure_configuration import DirectReceiverBackPressureConfiguration
from solace.messaging.resources.share_name import ShareName


class DirectMessageReceiverBuilder(MessageReceiverBuilder, DirectReceiverBackPressureConfiguration):
    """
    A class for a builder of direct message receivers.
    """

    @abstractmethod
    def build(self, shared_subscription_group: ShareName = None) -> DirectMessageReceiver:
        """
        Creates an instance of a direct message receiver
        (:py:class:`solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver`).
        If the optional ``ShareName`` argument is given, the ``DirectMessageReceiver`` is implemented with Horizontal
        Scalability in mind. This method should be used when more then one
        instance of the application is running for horizontal scaling and messages are distributed
        by the Solace event broker to all applications in the subscription group.
        When the ``ShareName`` argument is not specified, then the ``DirectMessageReceiver`` receives copies of all
        messages that match the configured subscriptions.  If multiple applications have the same subscriptions, then
        all matching messages are sent to all of the applications.

        Args:
            shared_subscription_group (ShareName): ShareName as the shared group name.

        Returns:
            DirectMessageReceiver: A direct message receiver object.
        """
