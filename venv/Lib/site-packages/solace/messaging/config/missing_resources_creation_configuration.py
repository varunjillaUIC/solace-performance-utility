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
This module defines the interface for ``MissingResourceCreationStrategy``. When the
client attempts to create a ``MessageReceiver`` or ``MessagePublisher`` but the necessary
resources are not configured on the event broker, such as a Queue, then the ``MissingResourceCreationStrategy```
defines what remedial action the API may take.
"""

# pylint: disable=trailing-whitespace

from abc import ABC, abstractmethod
from enum import Enum


class MissingResourcesCreationStrategy(Enum):  # pydoc: no  # pylint: disable=missing-class-docstring
    """
    A class that represents the available missing resources creation strategies.
    """
    DO_NOT_CREATE = 0
    #
    # Disables any attempt to create a missing resources (DEFAULT value, recommended
    # in production)
    #
    CREATE_ON_START = 1
    #
    # Attempt creation of missing resource when connection established (only for
    # known resources at that time)
    #


class MissingResourcesCreationConfiguration(ABC):
    """
    An interface for classes that support a missing resource creation strategy. Classes that
    inherit this interface may be configured with a strategy.

    If not set, the default is to not create missing resources.
    """

    @abstractmethod
    def with_missing_resources_creation_strategy(self,
                                                 strategy: 'MissingResourcesCreationStrategy') -> \
            'MissingResourcesCreationConfiguration':
        """
        Adds the missing creation strategy that defines what remedial action the API may take.

        Args:
            strategy(MissingResourcesCreationStrategy): Specify the missing creation strategy.

        Returns:
            MissingResourcesCreationConfiguration: A reference to the creation strategy for method chaining.

        """
