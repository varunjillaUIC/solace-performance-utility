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

# pylint: disable=missing-function-docstring

"""
module contains  request reply message publisher builder.
 Applications that requires request and reply messages must first create a  RequestReplyMessagePublisherBuilder
 using the :py:meth:`MessagingService.create_request_reply_message_publisher_builder(
 )<solace.messaging.messaging_service.MessagingService.create_request_reply_message_publisher_builder>`

 The RequestReplyMessagePublisherBuilder then creates one or more  RequestReplyMessagePublisher as necessary.
"""
import logging

from solace.messaging.builder._impl._message_publisher_builder import PublisherBackPressure
from solace.messaging.builder.request_reply_message_publisher_builder import RequestReplyMessagePublisherBuilder
from solace.messaging.publisher._impl._request_reply_message_publisher import _RequestReplyMessagePublisher

logger = logging.getLogger('solace.messaging.publisher')


class _RequestReplyMessagePublisherBuilder(RequestReplyMessagePublisherBuilder):
    """builder class for RequestReplyMessagePublisherBuilder"""

    def __init__(self, messaging_service: 'MessagingService'):
        logger.debug('[%s] initialized', type(self).__name__)
        self._messaging_service: 'MessagingService' = messaging_service
        self._publisher_back_pressure_type = PublisherBackPressure.No

    @property
    def publisher_back_pressure_type(self):
        # property to hold the publisher backpressure type
        return self._publisher_back_pressure_type

    @property
    def messaging_service(self):
        # property to hold and return the messaging service instance
        return self._messaging_service

    # Reserved for future use
    def from_properties(self, configuration: dict) \
            -> '_RequestReplyMessagePublisherBuilder':  # pylint: disable=unused-argument
        return self

    def build(self) -> '_RequestReplyMessagePublisher':
        logger.debug('Build [%s]', RequestReplyMessagePublisherBuilder.__name__)
        return _RequestReplyMessagePublisher(self)
