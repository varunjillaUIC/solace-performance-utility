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
This module contains a class that pertains to  resource accessibility.
"""
from abc import ABC, abstractmethod


class ResourceAccessibility(ABC):
    """
    An abstract class that abstracts remote resource accessibility.

    Solace Event Broker resources (queues and topic endpoints) can be accessed exclusively
    or non-exclusively. A resource with exclusive accessibility can serve only one consumer at any one time,
    while additional consumers may be connected as standby. A resource with non-exclusive accessibility
    can serve multiple consumers and each consumer is serviced in a round‑robin fashion.
    """

    @abstractmethod
    def is_exclusively_accessible(self) -> bool:
        """
        Determines if a remote resource supports exclusive or shared access mode.

        Returns:
            bool: True if a remote resource can serve only one consumer at any one time, False if a remote
            resource can serve multiple consumers; each consumer is serviced in round‑robin fashion.
        """
