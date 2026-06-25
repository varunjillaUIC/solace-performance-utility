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
 This module contains  request reply message publisher builder.
 Applications that requires request and reply messages must first create a  RequestReplyMessagePublisherBuilder
 using the :py:meth:`MessagingService.create_request_reply_message_publisher_builder(
 )<solace.messaging.messaging_service.MessagingService.create_request_reply_message_publisher_builder>`

 The ``RequestReplyMessagePublisherBuilder`` then creates one or more ``RequestReplyMessagePublisher`` as necessary.
"""

from abc import abstractmethod, ABC

from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration


class RequestReplyMessagePublisherBuilder(PropertyBasedConfiguration, ABC):
    """This class is used to configure and create instances of RequestReplyMessagePublisher."""

    @abstractmethod
    def build(self) -> 'RequestReplyMessagePublisher':
        """
        Creates an instance of
        :py:class:`solace.messaging.publisher.request_reply_message_publisher.RequestReplyMessagePublisher`.

        Returns:
            RequestReplyMessagePublisher: A RequestReply message publisher.

        """
