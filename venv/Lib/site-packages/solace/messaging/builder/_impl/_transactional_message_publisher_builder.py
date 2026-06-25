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

"""Module contains the implementation class and methods for the TransactionalMessagePublisherBuilder"""

from solace.messaging.builder.transactional_message_publisher_builder import TransactionalMessagePublisherBuilder
from solace.messaging.publisher._impl._transactional_message_publisher import _TransactionalMessagePublisher
from solace.messaging.publisher.transactional_message_publisher import TransactionalMessagePublisher

class _TransactionalMessagePublisherBuilder(TransactionalMessagePublisherBuilder):
    def __init__(self, config: dict, transactional_messaging_service: 'TransactionalMessagingService'):
        self._config = dict(config)
        self._transactional_messaging_service = transactional_messaging_service
    def from_properties(self, configuration: dict) -> TransactionalMessagePublisherBuilder:
        if isinstance(configuration, dict):
            self._config = {**self._config, **configuration}
        return self


    def build(self) -> TransactionalMessagePublisher:
        return _TransactionalMessagePublisher(config=self._config,
                                              transactional_messaging_service=self._transactional_messaging_service)
