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

"""Module contains the implementation class and methods for the PersistentMessagePublisherBuilder"""

import logging

from solace.messaging.builder._impl._message_publisher_builder import _MessagePublisherBuilder
from solace.messaging.builder.persistent_message_publisher_builder import PersistentMessagePublisherBuilder
from solace.messaging.publisher._impl._persistent_message_publisher import _PersistentMessagePublisher
from solace.messaging.publisher.persistent_message_publisher import PersistentMessagePublisher

logger = logging.getLogger('solace.messaging.publisher')


class _PersistentMessagePublisherBuilder(_MessagePublisherBuilder, PersistentMessagePublisherBuilder)\
        :  # pylint: disable=missing-class-docstring, missing-module-docstring, too-many-ancestors
    # builder class for PersistentMessagePublisherBuilder

    def __init__(self, messaging_service: 'MessagingService'):
        logger.debug('[%s] initialized', type(self).__name__)
        super().__init__(messaging_service)

    def build(self) -> PersistentMessagePublisher:
        # Implementation method to build persistent message publisher instance
        return _PersistentMessagePublisher(self)
