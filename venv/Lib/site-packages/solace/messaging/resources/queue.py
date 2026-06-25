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


""" This module contains the classes and functions to work with Queues."""


from abc import ABC
from typing import Union, Optional

from solace.messaging.resources.destination import Destination
from solace.messaging.resources.resource_accessibility import ResourceAccessibility
from solace.messaging.resources.resource_durability import ResourceDurability
from solace.messaging.utils._solace_utilities import is_type_matches


class Queue(Destination, ResourceDurability, ResourceAccessibility, ABC):
    """
    An interface that abstracts a Solace event broker resource used primarily for receiving messages.

    A Queue acts as an endpoint that clients can bind consumers to and consume messages from it can
    also act as a destination that clients can publish messages to. The primary use case for a queue is
    for the consumption of messages. It's recommended that you you add topic
    subscriptions to a queue so messages published to matching topics are delivered to the queue.
    """

    @staticmethod
    def durable_exclusive_queue(queue_name: str) -> 'Queue':
        """
        Create an exclusive queue for durable consumers. More
        than one consumer can bind a flow to the queue, but only the first bound consumer receives messages.
        If the processing consumer fails, the next bound consumer receives unprocessed messages and becomes
        the active processing consumer. The queue persists whether there are consumers bound to the queue or not.

        Args:
            queue_name (str): The name of the exclusive queue.

        Returns:
            Queue: A Queue object representing an exclusive queue.
        """
        is_type_matches(queue_name, str)
        return Queues.SimpleDurableQueue(queue_name, True)

    @staticmethod
    def durable_non_exclusive_queue(queue_name: str) -> 'Queue':
        """
        Create a non-exclusive queue for load-balancing and fault tolerance to durable consumers, and more
        than one consumer can bind to the queue. Messages are delivered in round-robin fashion for load-balancing.
        If a consumer fails, it's unprocessed messages are forwarded to an active consumer. The queue persists whether
        there are consumers bound to the queue or not.

        Args:
            queue_name (str):The name of the non-exclusive queue.

        Returns:
            Queue: A Queue object representing an non-exclusive queue.
        """
        is_type_matches(queue_name, str)
        return Queues.SimpleDurableQueue(queue_name, False)

    @staticmethod
    def non_durable_exclusive_queue(queue_name: Optional[str] = None) -> 'Queue':
        """
        Create an exclusive temporary queue for non-durable consumers. More
        than one consumer can bind a flow to the temporary queue, but only the first bound consumer receives messages.
        If the processing consumer fails, the next bound consumer receives unprocessed messages and becomes
        the active processing consumer. When there are no consumers connected to the queue, the queue doesn't persist.

        Args:
            queue_name (str): The name of the temporary, exclusive queue (optional).

        Returns:
            Queue: A Queue object representing an the temporary, exclusive queue.
        """
        if queue_name is not None:
            is_type_matches(queue_name, str)
        return Queues.SimpleNonDurableQueue(queue_name)


class Queues:  # pylint: disable=too-few-public-methods
    """A class that contains different types of Queues."""

    class DurableQueue(Queue, ABC):
        """
        A class that represents a  durable queue.
        """

        def is_durable(self) -> bool:
            return True

    class NonDurableQueue(Queue, ABC):
        """A class that represents a non-durable queue."""

        def is_durable(self) -> bool:
            return False

    class SimpleDurableQueue(DurableQueue):
        """A class that represents a simple durable queue."""

        def __init__(self, name: str, exclusively_accessible: bool):
            self._name: str = name
            self._exclusively_accessible: bool = exclusively_accessible

        def get_name(self) -> str:
            return self._name

        def is_exclusively_accessible(self) -> bool:
            return self._exclusively_accessible

        def __str__(self):
            return f"name: {str(self._name)}, exclusively_accessible: {str(self._exclusively_accessible)}"

    class SimpleNonDurableQueue(NonDurableQueue):
        """A class that represents a simple non-durable queue."""

        def __init__(self, name: Union[str, None]):
            self._name: Union[str, None] = name
            self._exclusively_accessible: bool = True

        def get_name(self) -> str:
            return self._name

        def is_exclusively_accessible(self) -> bool:
            return self._exclusively_accessible

        def __str__(self):
            return f"name: {self._name}, exclusively_accessible: {str(self._exclusively_accessible)}"
