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


# Internal module with validation methods   # pylint: disable=missing-module-docstring
import re

from solace.messaging.errors.pubsubplus_client_error import IllegalArgumentError


class _Validation:
    # A class for validating the illegal null values and the illegal regex values while given as input

    @staticmethod
    def null_illegal(obj, message: str) -> None:  # pylint: disable=missing-function-docstring
        # Method raises IllegalArgumentError if the object is None
        if obj is None:
            raise IllegalArgumentError(message)

    @staticmethod
    def regex_match_illegal \
                    (to_test: str, pattern: str, message: str) -> None:  # pylint: disable=missing-function-docstring
        # Method raises IllegalArgumentError if the regex pattern is not present
        if re.search(pattern, to_test):
            raise IllegalArgumentError(message)
