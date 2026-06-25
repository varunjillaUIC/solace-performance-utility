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

"""module contains persistent message publisher builder
 Applications that need to publish guaranteed messages must first create a PersistentMessagePublisherBuilder
 using the :py:meth:`MessagingService.create_persistent_message_publisher_builder(
 )<solace.messaging.messaging_service.MessagingService.create_persistent_message_publisher_builder>`

 The PersistentMessagePublisherBuilder then creates one or more PersistentMessagePublisher as necessary.
 """
from abc import abstractmethod

from solace.messaging.builder.message_publisher_builder import MessagePublisherBuilder


class PersistentMessagePublisherBuilder(MessagePublisherBuilder):  # pylint: disable=too-many-ancestors
    """
        A class that configures and creates instances of ``PersistentMessagePublisherBuilder``.
        The ``PersistentMessagePublisherBuilder`` builds the
        :py:class:`solace.messaging.publisher.persistent_message_publisher.PersistentMessagePublisher` instances.
    """

    @abstractmethod
    def build(self) -> 'PersistentMessagePublisher':
        """
        Creates an instance of
        :py:class:`solace.messaging.publisher.persistent_message_publisher.PersistentMessagePublisher`.

        Returns:
            PersistentMessagePublisher: A persistent message publisher.
        """
