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
This module contains the abstract base classes that defines the interface for synchronous subscription operations.
"""
from abc import ABC, abstractmethod

from solace.messaging.resources.topic_subscription import TopicSubscription


class ReceiverSubscriptions(ABC):
    """
    This class defines an abstract class for the interface for synchronous subscription operations.

    The :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` class supports both synchronous
    (blocking) and asynchronous (non-blocking) subscription operations.
    """

    @abstractmethod
    def add_subscription(self, another_subscription: TopicSubscription):
        """
        Makes a request to subscribe synchronously to a given topic subscription.

        This definition performs the subscription operation on the
        :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`.  The subscription request
        proceeds are sent and the function blocks waiting for a response from the Solace event broker.

        Args:
            another_subscription(TopicSubscription): The additional subscription to attract messages where
                topics match the subscriptions.

        Returns:
            When the function successfully completes, it returns otherwise, it raises an exception.

        Raises:
            PubSubPlusClientError: When an operation could not be performed for some reason.
            IllegalStateError: When the service is not running.
        """

    @abstractmethod
    def remove_subscription(self, subscription: TopicSubscription):
        """
        Makes a request to unsubscribe synchronously from the specified  topic subscription.

        This method performs the subscription removal operation on the
        :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`.

        Unsubscribe from a previously subscribed message source on the Solace event broker.
        Once the process is complete, no more messages where topics match the given subscription are
        received by the :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` object.

        Args:
            subscription(TopicSubscription): The subscription expression to remove from the ``MessageReceiver``
                instance.

        Returns:
            When the function successfully completes, it returns otherwise, it raises an exception.

        Raises:
            PubSubPlusClientError: When an operation could not be performed for some reason.
            IllegalStateError: When the service is not running.
        """
