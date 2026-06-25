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
This module provides abstract classes that define the interface for synchronous connection on a
:py:class:`solace.messaging.messaging_service.MessagingService` instance.

Synchronous connections do not return until the connection operation is complete.
"""
from abc import ABC, abstractmethod


class Connectable(ABC):
    """
    An abstract class that provides a interface for synchronous connections.
    """

    @abstractmethod
    def connect(self) -> 'Connectable':
        """
        Initiates the synchronous connection process with a Solace event broker
        on a :py:class:`solace.messaging.messaging_service.MessagingService` instance. In order to operate normally
        this method needs to be called on a service instance. After the method returns,
        the ``MessagingService`` has been successfully connected.

        Raises:
            PubSubPlusClientError: If the ``MessagingService`` cannot be connected.
            IllegalStateError: When another connect/disconnect operation is ongoing.
        """

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Determines whether a service is currently connected and indicate the current state of the
        :py:class:`solace.messaging.messaging_service.MessagingService`.

        Returns:
             bool: True if service is connected to a Solace event broker, otherwise False.

        Raises:
            PubSubPlusClientError: If the state of the service cannot be determined.
        """

    @abstractmethod
    def disconnect(self):
        """
        Initiates the disconnect (synchronous) process on the
        :py:class:`solace.messaging.messaging_service.MessagingService`. The method does not
        return until the disconnect process completes. After the disconnect process completes,
        the ``Messaging Service`` can not be connected again.
        """

    @abstractmethod
    def add_reconnection_listener(self, listener: 'ReconnectionListener') -> "Connectable":
        """
        Registers a :py:class:`solace.messaging.messaging_service.ReconnectionListener` to
        receive notification of successful reconnection. Reconnection notifications are generated when an established
        connection fails and is subsequently successfully reconnects.

        Args:
            listener (ReconnectionListener): The listener to register.

        Returns:
            Connectable: An object representing a synchronous connection.
        """

    @abstractmethod
    def remove_reconnection_listener(self, listener: 'ReconnectionListener') -> "Connectable":
        """
        Removes a :py:class:`solace.messaging.messaging_service.ReconnectionListener`.

        Args:
            listener(ReconnectionListener): A reconnection listener to remove.

        Returns:
            Connectable: An object representing a synchronous connection.
        """

    @abstractmethod
    def add_reconnection_attempt_listener(self, listener: 'ReconnectionAttemptListener') -> "Connectable":
        """
        Registers a :py:class:`solace.messaging.messaging_service.ReconnectionAttemptListener` to
        receive notification of reconnection attempts.  Reconnection attempt notifications are generated when an
        established connection fails and the API begins the reconnection process.

        Args:
            listener (ReconnectionListener): The listener to register with the reconnection attempt.

        Returns:
            Connectable: An object representing a synchronous connection.
        """

    @abstractmethod
    def remove_reconnection_attempt_listener(self, listener: 'ReconnectionAttemptListener') -> "Connectable":
        """
        Remove a :py:class:`solace.messaging.messaging_service.ReconnectionAttemptListener`

        Args:
            listener (ReconnectionListener): The listener to deregister.

        Returns:
            Connectable: An object representing a synchronous connection.
        """
