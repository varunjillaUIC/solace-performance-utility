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
This module contains a class that pertains to resource durability.
"""
from abc import ABC, abstractmethod


class ResourceDurability(ABC):
    """
    An abstract class that abstracts a remote resource durability.

    Solace event broker resources (queues and topic endpoints) may be durable or non-durable.
    A durable resource is a provisioned object on the event broker that has a lifespan independent
    of a particular client ``MessageService``.  They also survive an event broker restart and are
    preserved as part of the event broker configuration for backup and restoration purposes.
    A non-durable resource exists only so long as a ``MessageService`` is connected to the Solace event broker.
    """

    @abstractmethod
    def is_durable(self) -> bool:
        """
        Determines if resource is durable. Durable endpoints are provisioned objects on the event
        broker that have a life span independent of a particular client session.

        Returns:
            bool: True if resource is durable, False otherwise.
        """
