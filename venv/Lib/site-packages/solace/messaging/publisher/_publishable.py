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


#  # pylint: disable=missing-module-docstring
# Module implements internal class publishable.  OutboundMessage are carried in
# Publishable objects that contain the message and the destination


from abc import ABC, abstractmethod
from typing import TypeVar, Generic


T = TypeVar('T')  # pylint: disable=invalid-name


class Publishable(Generic[T], ABC):  # pylint: disable=missing-class-docstring
    # Class contains methods for getting the message and destination

    @abstractmethod
    def get_message(self) -> '_SolaceMessage':  # pylint: disable=missing-function-docstring
        # To get OutboundMessage
        ...  # pragma: no cover  # execution happens in listener thread

    @abstractmethod
    def get_destination(self) -> T:  # pylint: disable=missing-function-docstring
        # To get destination
        ...  # pragma: no cover  # execution happens in listener thread

    @staticmethod
    def of(message: '_SolaceMessage', destination: 'Topic') \
            -> 'Publishable':  # pylint: disable=invalid-name, missing-function-docstring
        # Returns: an instance of TopicPublishable
        return TopicPublishable(message=message, destination=destination)

    @staticmethod
    def none() -> 'Publishable':  # pylint: disable=missing-function-docstring
        # Returns: None values for message and destination
        return TopicPublishable(message=None, destination=None)


class TopicPublishable(Publishable):  # pylint: disable=missing-class-docstring,missing-function-docstring
    # Class contains methods for getting the message and destination name
    def __init__(self, message: '_SolaceMessage', destination: 'Topic'):
        self._message = message.message_duplicate()
        self._destination = destination

    def get_message(self) -> '_SolaceMessage':
        # To get OutboundMessage
        return self._message

    def get_destination(self) -> 'Topic':
        # To get destination
        return self._destination

    def __str__(self):
        return "TopicPublishable{message=" + str(self._message) + ", destination=" + str(self._destination) + "}"
