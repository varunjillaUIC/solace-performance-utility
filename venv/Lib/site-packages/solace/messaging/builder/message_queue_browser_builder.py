# solace-messaging-python-client
#
# Copyright 2025 Solace Corporation. All rights reserved.
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
 This module contains a persistent message queue browser builder. It can be used to look at
 persistent messages without consuming them. A client can selectively remove spooled persistent
 messages while browsing a Queue. Removing browsed messages deletes them from the Queue, so that
 they can no longer be delivered to consuming clients (or redelivered if they were already
 delivered to consumers at some point.) No confirmation is returned when a message is removed.
 Applications that need to browse persistent messages must first create a ``MessageQueueBrowserBuilder``
 instance using the the :py:meth:`MessagingService.create_message_queue_browser_builder()` method.
 The MessageQueueBrowserBuilder then creates one or more ``MessageQueueBrowser`` instances as necessary."""

from abc import abstractmethod

from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration
from solace.messaging.receiver.queue_browser import MessageQueueBrowser
from solace.messaging.resources.queue import Queue


class MessageQueueBrowserBuilder(PropertyBasedConfiguration):
    """
    A class that configures and creates instances of ``MessageQueueBrowser``.
    The ``MessageQueueBrowserBuilder`` builds the
    :py:class:`solace.messaging.receiver.message_queue_browser.MessageQueueBrowser` instances.
    """


    @abstractmethod
    def from_properties(self, configuration: dict) -> 'MessageQueueBrowserBuilder':
        """
        Sets the properties for queue browser (``MessageQueueBrowser``) using a dictionary.
        The dictionary is comprised of property-value pairs.
        Args:
            configuration(dict): The configuration properties.
        Returns:
           MessageQueueBrowserBuilder: The message receiver builder instance for method chaining.
        """

    @abstractmethod
    def with_message_selector(self, selector_query_expression: str) -> 'MessageQueueBrowserBuilder':
        """
        Enables support for message selection based on the message header parameter and message properties values.
        When a selector is applied, then the receiver only gets messages whose headers and properties match
        the selector. A message selector cannot select messages on the basis of the content of the message body.
        Args:
            selector_query_expression(str): The selector query expression
        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def with_queue_browser_window_size(self, window_size: int) -> 'MessageQueueBrowserBuilder':
        """
        Provides an option to configure a maximum number of messages that can be pre-fetched by the Browser.
        Args:
            window_size(int): The window size. Range: 1-255. Default: 255
        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def with_reconnection_attempts(self, reconnection_attempts: int)  -> 'MessageQueueBrowserBuilder':
        """
        When the session is up but the flow is unbound (e.g. on queue shutdown),
        this is the number of times to try to reconnect the flow. -1 means keep trying forever.
        Args:
            reconnection_attempts(int): Times to try. Range: -1 and up. Default: -1
        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def with_reconnection_attempts_wait_interval(self, reconnection_attempts_wait_interval: int)  \
        -> 'MessageQueueBrowserBuilder':
        """
        Cooldown time in miliseconds between flow reconnect acttempts.
        Args:
            reconnection_attempts_wait_interval(int): Wait time. Range: 50 and up. Default: 3000
        Returns:
            An instance of itself for method chaining.
        """

    @abstractmethod
    def build(self, endpoint_to_consume_from: Queue) -> MessageQueueBrowser:
        """
        Creates an instance of
        :py:class:`solace.messaging.receiver.message_queue_browser.MessageQueueBrowser`.
        Args:
            endpoint_to_consume_from(Queue): The Queue to receive message.
        Returns:
            MessageQueueBrowser: A queue browser.
        """
