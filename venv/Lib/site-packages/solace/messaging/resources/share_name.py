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


"""This is a module for the share name."""

from abc import ABC, abstractmethod

from solace.messaging.config._solace_message_constants import SHARE_NAME_CANT_BE_NONE, \
    SHARE_NAME_ILLEGAL_CHAR_ERROR_MESSAGE
from solace.messaging.resources.destination import Destination
from solace.messaging.utils._validation import _Validation


class ShareName(Destination, ABC):
    """A class that abstracts an identifier associated with the shared subscription.

    The ``ShareName`` class, in conjunction with a topic subscription, allows application developers to
    create horizontally-scaled applications.  Messages whose topic match the subscription are delivered
    in a round-robin fashion to all applications with the same shared subscription.
    """

    @staticmethod
    def of(group_name: str) -> 'ShareName':  # pylint: disable=invalid-name
        """
        Creates the instance of ``ShareName`` (:py:class:`solace.messaging.resources.share_name.ShareName`).

        Args:
            group_name(str): The name of the group.

        Returns:
            ShareName: The identifier of the shared subscription.
        """
        return _ShareName(group_name)

    @staticmethod
    def no_op() -> 'ShareName':  # pylint: disable=missing-function-docstring
        return _ShareName('')

    @abstractmethod
    def validate(self) -> None:  # pylint: disable=missing-function-docstring
        # To validate illegal characters in share name
        ...


class _ShareName(ShareName):  # pylint: disable=missing-class-docstring,missing-function-docstring
    # Share name implementation class

    illegal_chars = '.*[\\>\\*].*'

    def __init__(self, share_name: str):
        self.name: str = share_name

    def get_name(self) -> str:
        return self.name

    def validate(self) -> None:
        name = self.get_name()
        _Validation.null_illegal(obj=name, message=SHARE_NAME_CANT_BE_NONE)
        _Validation.regex_match_illegal(to_test=name, pattern=_ShareName.illegal_chars,
                                        message=SHARE_NAME_ILLEGAL_CHAR_ERROR_MESSAGE)

    def __str__(self):
        return f"shared_name : {self.name}"
