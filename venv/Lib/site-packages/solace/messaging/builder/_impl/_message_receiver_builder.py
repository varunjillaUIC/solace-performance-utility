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


# Abstract base class for DirectMessageReceiverBuilder """  # pylint: disable=missing-module-docstring
import logging
from enum import Enum
from typing import List

from solace.messaging.builder.message_receiver_builder import MessageReceiverBuilder
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._solace_utilities import is_type_matches

logger = logging.getLogger('solace.messaging.receiver')

class DirectMessageReceiverBackPressure(Enum):  # pydoc: no  # pylint: disable=missing-class-docstring
    # class which extends Enum to hold the direct receiver back pressure
    # these enum are internal only and are used for quick comparisons
    # in direct receivers

    # Unbound buffer which will continue to add capacity as needed until memory failure.
    Elastic = 0  # pylint: disable=invalid-name

    # Finite buffer capacity greater than 0. If the buffer capacity is exceeded the oldest
    # message in the buffer is discarded.
    DropOldest = 1  # pylint: disable=invalid-name

    # Finite buffer capacity greater than 0. If the buffer capacity is exceeded incoming messages
    # are discarded.
    DropLatest = 2  # pylint: disable=invalid-name

class _MessageReceiverBuilder(MessageReceiverBuilder):
    def __init__(self, messaging_service: 'MessagingService'):
        self._messaging_service: 'MessagingService' = messaging_service
        self._topic_subscriptions = []

    @property
    def messaging_service(self):  # pylint: disable=missing-function-docstring
        return self._messaging_service

    def with_subscriptions(self, subscriptions: List[TopicSubscription]) -> \
            'MessageReceiverBuilder':
        is_type_matches(subscriptions, List, raise_exception=True)
        self._topic_subscriptions = []
        for topic in subscriptions:
            is_type_matches(topic, TopicSubscription, raise_exception=True)
            self._topic_subscriptions.append(topic.get_name())
        return self

    def from_properties(self, configuration: dict) -> 'MessageReceiverBuilder':
        is_type_matches(configuration, dict, logger=logger)
        return self
