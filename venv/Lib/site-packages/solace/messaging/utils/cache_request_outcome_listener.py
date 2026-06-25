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
This module contains an abstract cache request completion listener class.
"""

from abc import ABC, abstractmethod
from typing import Union

from solace.messaging.utils.cache_request_outcome import CacheRequestOutcome

class CacheRequestOutcomeListener(ABC):
    """
    A callback for listening for the results of a future computation with request id support.
    """

    @abstractmethod
    def on_completion(self, result: CacheRequestOutcome, cache_request_id: int, exception: Union[Exception, None]):
        """
        A callback listener that accepts the results of a future computation. This callback
        executes on completion of an action with a result of the execution passed in or an
        exception as an indicator for failed execution.

        Args:
            result(CacheRequestOutcome): The future execution result.
            cache_request_id(int): The cache request ID associated with the given completed computation unit.
            exception(Exception): An Exception, if execution fails, otherwise None.
        """
