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


# Abstract base class for DirectMessageReceiverBuilder   # pylint: disable=missing-module-docstring

from abc import abstractmethod
from typing import List

from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration
from solace.messaging.resources.topic_subscription import TopicSubscription


class MessageReceiverBuilder(PropertyBasedConfiguration):  # pylint: disable=missing-class-docstring
    """
    An abstract base class for builders of message receivers.
    """

    @abstractmethod
    def with_subscriptions(self, subscriptions: List[TopicSubscription]) -> 'MessageReceiverBuilder':
        """
        Adds a list of subscriptions to be applied to all MessageReceiver that are subsequently created with
        this builder.

        Args:
            subscriptions (List[TopicSubscription]): The list of topic subscriptions to be added.

        Returns:
            MessageReceiverBuilder: The message receiver builder instance for method chaining.
        """

    @abstractmethod
    def from_properties(self, configuration: dict) -> 'MessageReceiverBuilder':
        """
        Sets the properties for a message receiver using a dictionary.
        The dictionary is comprised of property-value pairs.

        Args:
            configuration(dict): The configuration properties.

        Returns:
           MessageReceiverBuilder: The message receiver builder instance for method chaining.
        """
