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
This module provides abstract classes that define the interface for asynchronous connection on a
:py:class:`solace.messaging.messaging_service.MessagingService`

Asynchronous connections actions return a concurrent.futures.Future object rather than wait for the connection to
complete.
"""

import concurrent.futures
from abc import ABC, abstractmethod


class AsyncConnectable(ABC):
    """
    An abstract class that provides an interface for asynchronous connections.
    """

    @abstractmethod
    def connect_async(self) -> concurrent.futures.Future:
        """
        Connects asynchronously with a Solace event broker. This method initiates the connection process on the
        :py:class:`solace.messaging.messaging_service.MessagingService`.  The connection proceeds asynchronously,
        with the success or failure status available in the returned concurrent.futures.Future object.

        This method initiates the connect process on the
        :py:class:`solace.messaging.messaging_service.MessagingService`.  The connection proceeds asynchronously,
        with the success or failure status available in the returned concurrent.futures.Future object.

        Returns:
            concurrent.futures.Future: An object that the application may use to determine when the connection
            attempt has completed.

        Raises:
            PubSubPlusClientError: If the messaging service cannot be connected.
            IllegalStateError: if an attempt to connect to a messaging service that's been disconnected.

        """

    @abstractmethod
    def disconnect_async(self) -> concurrent.futures.Future:
        """
        Initiates the disconnection process on a :py:class:`solace.messaging.messaging_service.MessagingService`
        instance.
        The disconnection process proceeds asynchronously with the completion notice available in the returned
        :py:class:`concurrent.futures.Future`

        Once disconnect is complete, the ``MessagingService`` can not be connected again.

        Returns:
            concurrent.futures.Future: An object that your application can use to determine when
            the disconnection process has completed.

        Raises:
            PubSubPlusClientError: If the messaging service cannot be disconnected.
        """
