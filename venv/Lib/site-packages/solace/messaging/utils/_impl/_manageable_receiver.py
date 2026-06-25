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

"""This Module contains the implementation classes and methods regarding the Receiver Info and Resource Info"""

# pylint: disable=missing-function-docstring
from solace.messaging.utils.manageable_receiver import ResourceInfo, PersistentReceiverInfo, TransactionalReceiverInfo


class _ResourceInfo(ResourceInfo):
    def __init__(self, is_durable, name):
        self._is_durable = is_durable
        self._name = name

    def is_durable(self) -> bool:
        return self._is_durable

    def get_name(self) -> str:
        return self._name


class _PersistentReceiverInfo(PersistentReceiverInfo):

    def __init__(self, is_durable, name):
        self._is_durable = is_durable
        self._name = name

    def get_resource_info(self) -> _ResourceInfo:
        return _ResourceInfo(self._is_durable, self._name)

class _TransactionalReceiverInfo(TransactionalReceiverInfo):

    def __init__(self, is_durable, name):
        self._is_durable = is_durable
        self._name = name

    def get_resource_info(self) -> _ResourceInfo:
        return _ResourceInfo(self._is_durable, self._name)
