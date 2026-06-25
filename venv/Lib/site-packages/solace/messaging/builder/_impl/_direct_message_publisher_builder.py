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

"""Module contains the implementation class and methods for the DirectMessagePublisherBuilder"""

import logging

from solace.messaging.builder._impl._message_publisher_builder import _MessagePublisherBuilder
from solace.messaging.builder.direct_message_publisher_builder import DirectMessagePublisherBuilder
from solace.messaging.publisher._impl._direct_message_publisher import _DirectMessagePublisher
from solace.messaging.publisher.direct_message_publisher import DirectMessagePublisher

logger = logging.getLogger('solace.messaging.publisher')


class _DirectMessagePublisherBuilder(_MessagePublisherBuilder, DirectMessagePublisherBuilder)\
        :   # pylint: disable=missing-class-docstring, missing-module-docstring
    # Builder class for direct message publisher

    def __init__(self, messaging_service: 'MessagingService'):
        logger.debug('[%s] initialized', type(self).__name__)
        super().__init__(messaging_service)

    def build(self) -> DirectMessagePublisher:
        # Implementation method to build direct message publisher instance
        logger.debug('Build [%s]', DirectMessagePublisher.__name__)
        return _DirectMessagePublisher(self)
