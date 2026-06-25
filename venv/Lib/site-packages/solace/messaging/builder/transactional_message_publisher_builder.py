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
"""
 This module contains a builder for the transactional message publisher.
 Applications that need to publish messages on a transacted session
 must first create a  ``TrannsactionalMessagePublisherBuilder``
 using the
 :py:meth:`create_transaction_message_publisher_builder()<solace.messaging.messaging_service.TransactionalMessagingService.create_transactional_message_publisher_builder()>`.

 The ``TransactionalMessagePublisherBuilder`` then creates the ``TransactionalMessagePublisher``
"""

from abc import ABC
from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration

class TransactionalMessagePublisherBuilder(PropertyBasedConfiguration, ABC):
    """
        A class to configure and create instances of {@link TransactionalMessagePublisher} to publish
        transactional messages.
    """
    def build(self) -> 'TransactionalMessagePublisher':
        """
            Builds a transactional message publisher.
            Returns:
                TransactionalMessagePublisher instance.
            Raises:
                PubSubPlusClientError: When the publisher can not be created.
        """
