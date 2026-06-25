# solace-messaging-python-client
#
# Copyright 2025 Solace Corporation. All rights reserved.
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

# MessageQueueBrowserBuilder implementation
# pylint: disable=missing-module-docstring, line-too-long, missing-function-docstring

import logging
import math

from solace.messaging.builder.message_queue_browser_builder import MessageQueueBrowserBuilder
from solace.messaging.receiver.queue_browser import MessageQueueBrowser
from solace.messaging.receiver._impl._queue_browser import _MessageQueueBrowser
from solace.messaging.config.solace_properties import queue_browser_properties
from solace.messaging.utils._solace_utilities import is_type_matches, is_value_out_of_range
from solace.messaging.resources.queue import Queue

logger = logging.getLogger('solace.messaging.receiver')

class _MessageQueueBrowserBuilder(MessageQueueBrowserBuilder):
    def __init__(self, messaging_service: 'MessagingService'):
        self._messaging_service: 'MessagingService' = messaging_service
        self._message_selector: str
        self._message_selector = ''
        self._endpoint_to_consume_from: Queue
        self._endpoint_to_consume_from = None
        self._window_size = 0 # Only if unconfigured: CCSMP default.
        self._reconnection_attempts = -1
        self._reconnection_attempts_wait_interval = 3000

    def from_properties(self, configuration: dict) -> 'MessageQueueBrowserBuilder':
        is_type_matches(configuration, dict, logger=logger)

        setters = {
                    queue_browser_properties.QUEUE_BROWSER_WINDOW_SIZE: self.with_queue_browser_window_size,
                    queue_browser_properties.QUEUE_BROWSER_MESSAGE_SELECTOR_QUERY: self.with_message_selector,
                    queue_browser_properties.QUEUE_BROWSER_RECONNECTION_ATTEMPTS: self.with_reconnection_attempts,
                    queue_browser_properties.QUEUE_BROWSER_RECONNECTION_ATTEMPTS_WAIT_INTERVAL: self.with_reconnection_attempts_wait_interval
                  }

        for key, setter in setters.items():
            if key in configuration.keys():
                setter(configuration[key])

        return self

    def with_message_selector(self, selector_query_expression: str) -> 'MessageQueueBrowserBuilder':
        is_type_matches(selector_query_expression, str, logger=logger)
        self._message_selector = selector_query_expression
        return self

    def with_queue_browser_window_size(self, window_size: int) -> 'MessageQueueBrowserBuilder':
        is_type_matches(window_size, int, logger=logger)
        is_value_out_of_range(1, 255, window_size, logger=logger)
        self._window_size = window_size
        return self

    def with_reconnection_attempts(self, reconnection_attempts: int)  -> 'MessageQueueBrowserBuilder':
        is_type_matches(reconnection_attempts, int, logger=logger)
        is_value_out_of_range(-1, math.inf, reconnection_attempts, logger=logger)
        self._reconnection_attempts = reconnection_attempts
        return self

    def with_reconnection_attempts_wait_interval(self, reconnection_attempts_wait_interval: int)  -> 'MessageQueueBrowserBuilder':
        is_type_matches(reconnection_attempts_wait_interval, int, logger=logger)
        is_value_out_of_range(50, math.inf, reconnection_attempts_wait_interval, logger=logger)
        self._reconnection_attempts_wait_interval = reconnection_attempts_wait_interval
        return self


    @property
    def messaging_service(self):  # pylint: disable=missing-function-docstring
        return self._messaging_service

    @property
    def message_selector(self):
        # Property to hold and return the message selector expression
        return self._message_selector

    @property
    def window_size(self):
        return self._window_size

    @property
    def reconnection_attempts(self):
        return self._reconnection_attempts

    @property
    def reconnection_attempts_wait_interval(self):
        return self._reconnection_attempts_wait_interval

    @property
    def endpoint_to_consume_from(self):
        return self._endpoint_to_consume_from


    def build(self, endpoint_to_consume_from: Queue) -> MessageQueueBrowser:
        is_type_matches(endpoint_to_consume_from, Queue, logger=logger)
        self._endpoint_to_consume_from = endpoint_to_consume_from
        return _MessageQueueBrowser(self)
