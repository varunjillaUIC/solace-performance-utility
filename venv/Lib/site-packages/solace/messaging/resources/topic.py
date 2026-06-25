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


"""This is a module that contains the Abstract, API representation of a Solace Event Broker message topic."""
import logging
from abc import ABC

from solace.messaging.config._solace_message_constants import TOPIC_NAME_CANNOT_BE_EMPTY
from solace.messaging.resources.destination import Destination
from solace.messaging.utils._solace_utilities import is_topic_valid

logger = logging.getLogger('solace.messaging.core')


class Topic(Destination, ABC):
    """
    An interface class that abstracts a Solace event broker resource that's used primarily for publishing messages.
    A topic acts as a destination that a MessagePublisher can publish messages to.
    ``MessageReceivers`` add subscriptions that can be exactly a topic, or expressions that may match one
    or more topics.
    """

    @staticmethod
    def of(topic_string: str) -> 'Topic':  # pylint: disable=invalid-name
        """
        Takes the topic in the form of a string  and returns the topic.

        Args:
            topic_string(str): The topic as a string.
        Returns:
            Topic: An object representing the topic subscription.
        """
        is_topic_valid(topic_string, logger, TOPIC_NAME_CANNOT_BE_EMPTY)
        return _Topic(topic_string)


class _Topic(Topic):  # pylint: disable=missing-class-docstring
    # """A class that implements a topic."""

    def __init__(self, expression):
        self._expression = expression

    def get_name(self) -> str:
        # Returns the name """
        return self._expression

    def __str__(self):
        return f"topic : {self._expression} "
