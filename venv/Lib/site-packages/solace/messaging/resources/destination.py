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


""" This module contains an abstract class for named resources."""
from abc import ABC, abstractmethod


class Destination(ABC):
    """ An abstract class that defines the interface to a remote resource that has a name."""

    @abstractmethod
    def get_name(self) -> str:
        """
        Retrieves the name of the resource.

        Returns:
            str: The name of the resource.
        """
