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
 This module contains a builder for RequestReply message publishers.
 Applications that need to publish request reply messages must first create a  ``RequestReplyMessageReceiverBuilder``
 using the
 :py:meth:`solace.messaging.messaging_service.MessagingService.create_request_reply_message_receiver_builder()`.

 The ``RequestReplyMessageReceiverBuilder`` then creates one or more ``RequestReplyMessageReceiver``
 instances as necessary.
"""

# pylint: disable=too-few-public-methods

from abc import abstractmethod

from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration
from solace.messaging.resources.share_name import ShareName
from solace.messaging.resources.topic_subscription import TopicSubscription


class RequestReplyMessageReceiverBuilder(PropertyBasedConfiguration):
    """This class is used to configure and create instances of RequestReplyMessageReceiver"""

    @abstractmethod
    def build(self, request_topic_subscription: TopicSubscription, share_name: ShareName = None) \
            -> 'RequestReplyMessageReceiver':
        """
        Args:
            request_topic_subscription: topic subscription
            share_name: share name

        Returns:
            An instance of RequestReplyMessageReceiver
        """
