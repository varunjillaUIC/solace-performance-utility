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
This module includes any API items directly related to the CacheRequestOutcome enum.
"""

import enum

class CacheRequestOutcome(enum.Enum):
    """
    Represents available cache request outcomes.
    """

    OK = 0
    """
    Cached data was returned in a cache reply, or the cache request was fulfilled by live data.
    """

    NO_DATA = 1
    """
    There was no data in the reply.
    """

    SUSPECT_DATA = 2
    """
    There was suspect data in the cache reply.
    """

    FAILED = 3
    """
    The request failed for some reason, accompanied exception should be used to determine a root cause.
    """
