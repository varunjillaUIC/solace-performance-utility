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


"""A module for topic subscriptions."""
import logging
from abc import ABC

from solace.messaging.config._solace_message_constants import TOPICSUBSCRIPTION_NAME_CANNOT_BE_EMPTY
from solace.messaging.resources.destination import Destination
from solace.messaging.utils._solace_utilities import is_topic_valid

logger = logging.getLogger('solace.messaging.core')


class TopicSubscription(Destination, ABC):
    """
    An interface class that abstracts a topic subscription.

    Topic subscriptions are expressions to match topics. Messages from matching topics
    can be delivered to the  ``MessageReceiver``
    (:py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`) object.
    """

    @staticmethod
    def of(expression: str) -> 'TopicSubscription':  # pylint: disable=invalid-name
        """
        Takes the subscription expression in the form of a string  and returns a ``TopicSubscription`` object.

        Args:
            expression(str): The topic expression.

        Returns:
            TopicSubscription: An expression to match a topic.
        """

        is_topic_valid(expression, logger, TOPICSUBSCRIPTION_NAME_CANNOT_BE_EMPTY)
        return _TopicSubscription(expression)


class _TopicSubscription(TopicSubscription):  # pylint: disable=missing-class-docstring
    # This class provides the implementation for the ``TopicSubscription`` class and extends it.
    def __init__(self, expression):
        self.expression = expression

    def get_name(self) -> str:
        # This method is used to get the name of the topic subscription and returns a string
        return self.expression

    def __str__(self):  # pylint: disable=missing-function-docstring
        # This method is used to get the string from the _TopicSubscription
        return f"TopicSubscription : {self.expression}"
