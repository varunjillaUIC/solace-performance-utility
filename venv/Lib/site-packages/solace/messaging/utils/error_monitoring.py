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


"""This is a module for classes and methods for error monitoring."""

from abc import ABC, abstractmethod


class ErrorMonitoring(ABC):
    """An class for the global error monitoring capabilities."""

    @abstractmethod
    def add_service_interruption_listener(self, listener: 'ServiceInterruptionListener'):
        """Adds a service listener for listening to non recoverable service interruption events.

        Args:
            listener: service interruption listener
        """

    @abstractmethod
    def remove_service_interruption_listener(self, listener: 'ServiceInterruptionListener') -> bool:
        """Removes a service listener for listening to non-recoverable service interruption events.

        Args:
            listener(ServiceInterruptionListener): service interruption listener

        Returns:
            bool: True if removal was successful, False otherwise.

        """
