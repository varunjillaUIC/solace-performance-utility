# solace-messaging-python-client
#
# Copyright 2023-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" This module contains the class for updating the configuration of an API object."""

from typing import Any
from abc import ABC, abstractmethod

class UpdatableConfiguration(ABC):  # pylint: disable=missing-class-docstring

    @abstractmethod
    def update_property(self, name: str, value: Any):
        """
        Updates configuration property.
        Modification of a property may or may not occur instantly.

        Args:
            name(str): The name of the property to modify. None values are not accepted
            value(Any): The new value of the property. None values are not accepted

        Raises:
            IllegalArgumentError: If the specified property cannot be modified.
            IllegalStateError: If the specified property cannot
                be modified in the current service state.
            PubSubPlusClientError: If other transport or communication related errors occur.
        """
