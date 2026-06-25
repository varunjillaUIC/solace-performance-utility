# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Module contains the implementation class and methods for the MessagePublisher
# pylint: disable=missing-module-docstring, too-many-branches,no-else-break,too-many-boolean-expressions
# pylint: disable=missing-function-docstring,protected-access,no-else-raise,no-else-return,useless-super-delegation

"""
This module contains send utils that can be used by both consumers and producers.
"""

from abc import ABC, abstractmethod

class _SendTask(ABC):
    @abstractmethod
    def on_publishable_sent(self):
        """ Remove item from buffer """

    def get_publishable_for_send(self) -> 'TopicPublishable':  # pylint: disable=no-self-use
        """ peek first item can, return None """
        return None

    def get_cache_requester_for_send(self) -> 'CachedMessageSubscriptionRequest':  # pylint: disable=no-self-use
        """ peek first item can, return None """
        return None

    @abstractmethod
    def on_publishable_send_error(self, error: Exception = None):
        """ Error occurred on sending that can not be recovered remove poison message from buffer """
