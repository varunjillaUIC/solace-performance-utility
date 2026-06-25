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
This module contains the abstract base class that defines the interface for asynchronous subscription operations.
"""
from abc import ABC, abstractmethod
from concurrent.futures import Future

from solace.messaging.resources.topic_subscription import TopicSubscription


class AsyncReceiverSubscriptions(ABC):
    """
    An abstract class for asynchronous receiver subscriptions.

    All :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` classes support both synchronous
    (blocking) and asynchronous (non-blocking) subscription operations.  This class defines the interface for
    asynchronous subscription operations.
    """

    @abstractmethod
    def add_subscription_async(self, topic_subscription: TopicSubscription) -> Future:
        """
        Makes a request to subscribe asynchronously to a given topic subscription.

        This method initiates the subscription process on the
        :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`.  The subscription request
        proceeds asynchronously, with the success or failure status available in the returned
        :py:class:`concurrent.futures.Future` object.

        Args:
            topic_subscription(TopicSubscription): The subscription expression to subscribe to. Messages with
                a topic that matches the subscription are  directed to this client.

        Returns:
            Future: An object used to determine when the connection attempt has completed.

        Raises:
            PubSubPlusClientError: If an operation could not be performed for some internal reason.
        """

    @abstractmethod
    def remove_subscription_async(self, topic_subscription: TopicSubscription) -> Future:
        """
        Makes a request to unsubscribe asynchronously from a given topic subscription.

        This method initiates the subscription removal process on the
        :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` instance.

        The unsubscribe request proceeds asynchronously, with the success or failure status available in the returned
        :py:class:`concurrent.futures.Future`. Once the process is complete, no more messages whose topic match the
        given subscription will be received in the
        :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` instance.

        Args:
            topic_subscription(TopicSubscription): The subscription expression to remove from the ``MessageReceiver``.

        Returns:
            concurrent.futures.Future: An object used to determine when the connection attempt has completed.

        Raises:
            PubSubPlusClientError: If an operation could not be performed for some internal reason.
            IllegalStateError: If the service is not running.
        """
