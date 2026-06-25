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

"""This module consists of the Receiver Information and its respective methods"""

from abc import ABC, abstractmethod


class ReceiverInfo(ABC):
    """An interface that abstracts access to advanced receiver information information at runtime"""

    @abstractmethod
    def get_instance_name(self) -> str:
        """
        Provides a name for an instance of a receiver.

        Returns:
          str : a string representing the instance name of the receiver.

        """


class ManageableReceiver(ABC):
    """An interface that abstracts different aspects of message receiver manageability"""

    @abstractmethod
    def receiver_info(self) -> ReceiverInfo:
        """
        Provides access to the receiver information

        Returns:
            ReceiverInfo : an object that represents message receiver manageability.
        """


class ResourceInfo(ABC):
    """
        An interface that abstracts access to the remote resource endpoint information particular
        receiver instance is bonded to at runtime
    """

    @abstractmethod
    def is_durable(self) -> bool:
        """
        Returns whether the resource is durable.

        Returns:
          bool : a boolean that indicates whether the resource is durable ``True`` or not ``False``.

        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the resource.

        Returns:
          str : a string representing the name of the resource.
        """


class PersistentReceiverInfo(ABC):
    """An interface that abstracts access to advanced persistent receiver information at runtime"""

    @abstractmethod
    def get_resource_info(self) -> ResourceInfo:
        """
        Returns the remote endpoint (resource) info for particular receiver at runtime.

        Returns:
          information about bonded resource endpoint at runtime

        Raises:
          IllegalStateError : will be thrown when receiver is not in connected to the
                              appliance and endpoint binding is not established
        """

class TransactionalReceiverInfo(ABC):
    """An interface that abstracts access to advanced transactional receiver information at runtime"""

    @abstractmethod
    def get_resource_info(self) -> ResourceInfo:
        """
        Returns the remote endpoint (resource) info for particular receiver at runtime.

        Returns:
          information about bonded resource endpoint at runtime

        Raises:
          IllegalStateError : will be thrown when receiver is not in connected to the
                              appliance and endpoint binding is not established
        """
