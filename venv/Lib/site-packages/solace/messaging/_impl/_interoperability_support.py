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

"""Module contains the implementation class and methods for the RestInteroperabilitySupport"""
import logging

from solace.messaging.utils.interoperability_support import RestInteroperabilitySupport

logger = logging.getLogger('solace.messaging.receiver')


class _RestInteroperabilitySupport(RestInteroperabilitySupport):
    """class for implementing the RestInteroperabilitySupport"""

    def __init__(self, http_content_type: str, http_encoding_type: str):
        self._http_content_type = http_content_type
        self._http_encoding_type = http_encoding_type

    def get_http_content_type(self) -> str:
        logger.debug('Get HTTP content type')
        return self._http_content_type

    def get_http_content_encoding(self) -> str:
        logger.debug('Get HTTP content encoding')
        return self._http_encoding_type

    def __str__(self):
        return f"RestInteroperabilitySupport http_content_type: '{self._http_content_type}'," \
               f" http_content_encoding: '{self._http_encoding_type}'"
