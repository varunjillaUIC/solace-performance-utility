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
 This module contains a builder for direct message publishers.
 Applications that need to publish direct messages must first create a  ``DirectMessagePublisherBuilder``
 using the :py:meth:`solace.messaging.messaging_service.MessagingService.create_direct_message_publisher_builder()`.

 The ``DirectMessagePublisherBuilder`` then creates one or more ``DirectMessagePublisher`` instances as necessary.
"""
from abc import abstractmethod

from solace.messaging.builder.message_publisher_builder import MessagePublisherBuilder
from solace.messaging.publisher.direct_message_publisher import DirectMessagePublisher


class DirectMessagePublisherBuilder(MessagePublisherBuilder):
    """A class for a builder of direct message publishers."""

    @abstractmethod
    def build(self) -> DirectMessagePublisher:
        """
         Builds a direct message publisher object.

        Returns:
            DirectMessagePublisher: A direct message publisher.
        """
