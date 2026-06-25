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
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
"""Module contains the implementation class and methods for the MessagePublisherBuilder"""

import logging
from enum import Enum

from solace.messaging.builder.message_publisher_builder import MessagePublisherBuilder
from solace.messaging.config.solace_constants import publisher_constants
from solace.messaging.config import _solace_message_constants
from solace.messaging.config.solace_properties import publisher_properties
from solace.messaging.errors.pubsubplus_client_error import IllegalArgumentError
from solace.messaging.utils._solace_utilities import is_type_matches

logger = logging.getLogger('solace.messaging.publisher')


class PublisherBackPressure(Enum):  # pydoc: no  # pylint: disable=missing-class-docstring
    # class which extends Enum to hold the publisher back pressure
    # these enum are internal only and are used for quick  comparisons
    # in publishers
    No = -1 # pylint: disable=invalid-name
    # No back pressure is a short for reject with no buffer
    # as publishing path in the code differ quite greatly without a buffer.
    # Ideally this should be removed if possible without impacted performance in the publisher.
    Reject = 0 # pylint: disable=invalid-name
    # Reject back pressure type with a finite buffer capacity
    Elastic = 1 # pylint: disable=invalid-name
    # Elastic back pressure type for an unbound buffer (will allocate buffer space until oom)
    Wait = 2 # pylint: disable=invalid-name
    # Wait back pressure type with a finite buffer capacity will block on capacity limit


class _MessagePublisherBuilder(MessagePublisherBuilder):
    def __init__(self, messaging_service: 'MessagingService'):
        logger.debug('[%s] initialized', type(self).__name__)
        self._messaging_service: 'MessagingService' = messaging_service
        self._buffer_capacity: int = 0  # queue value either 0(infinite size or no buffer) or +ve number
        self._publisher_back_pressure_type: PublisherBackPressure = PublisherBackPressure.Elastic

    @property
    def messaging_service(self):
        # property to hold and return the messaging service instance
        return self._messaging_service

    @property
    def buffer_capacity(self):
        # Property to hold and return the buffer capacity
        return self._buffer_capacity

    @property
    def publisher_back_pressure_type(self):
        # Property to hold and return the publisher back pressure type
        return self._publisher_back_pressure_type

    def from_properties(self, configuration: dict) -> 'MessagePublisherBuilder':
        # Enables dict  based configuration#
        is_type_matches(configuration, dict, logger=logger)
        self.__build_back_pressure_from_props(configuration)
        return self

    def on_back_pressure_reject(self, buffer_capacity: int) -> 'MessagePublisherBuilder':
        #
        # :py:class:`solace.messaging.publisher.direct_message_publisher.DirectMessagePublisher` that are built will
        # throw an :py:class:`solace.messaging.errors.pubsubplus_client_error.BackPressureError`
        # when unable to publish message because the publisher buffer capacity is exceeded.  Messages are queued
        # for transmit whenever the publisher exceeds the network transmit capacity, which is a function
        # of network speed and network transit time.
        #
        # Args:
        #     buffer_capacity (int): an integer value which represents the maximum queue size in number of messages.
        #     When 0 no buffer is used and when the publisher exceed network transmit capacity and Error is raised.
        #
        # Raises:
        #     IllegalArgumentError: if the provided buffer size is any negative number
        # Returns:
        #     DirectMessagePublisherBuilder for method chaining.
        is_type_matches(buffer_capacity, int, logger=logger)
        if buffer_capacity < 0:
            logger.warning("Buffer size::'%d' %s", buffer_capacity, _solace_message_constants.VALUE_CANNOT_BE_NEGATIVE)
            raise IllegalArgumentError(
                f"Buffer size::'{buffer_capacity}' {_solace_message_constants.VALUE_CANNOT_BE_NEGATIVE}")

        logger.debug('Enabled back pressure with reject mechanism, buffer/queue max capacity: %d', buffer_capacity)
        self._publisher_back_pressure_type = \
            PublisherBackPressure.Reject if buffer_capacity > 0 else PublisherBackPressure.No
        self._buffer_capacity = buffer_capacity
        return self

    def on_back_pressure_elastic(self) -> 'MessagePublisherBuilder':
        #
        # :py:class:`solace.messaging.publisher.direct_message_publisher.DirectMessagePublisher` that are built will
        # buffer all messages until memory is exhausted. Messages are queued for transmit whenever the publisher
        # exceeds the network transmit capacity, which is a function of network speed and network transit time.
        #
        # Usage of this strategy can lead to out of memory situation and application could crash. This strategy
        # may be useful for microservices which are running in a managed environment that can detect crashes and perform
        # restarts of a microservices.
        # Returns:
        #     DirectMessagePublisherBuilder for method chaining.
        #
        logger.debug('Enabled back pressure with elasticity mechanism, buffer/queue capacity: MAX')
        self._publisher_back_pressure_type = PublisherBackPressure.Elastic
        return self

    def on_back_pressure_wait(self, buffer_capacity: int) -> 'MessagePublisherBuilder':
        #
        # :py:class:`solace.messaging.publisher.direct_message_publisher.DirectMessagePublisher` that are built will
        # wait when unable to publish message because the publisher buffer capacity is exceeded. Messages are queued
        # for transmit whenever the publisher exceeds the network transmit capacity, which is a function of network
        # speed and network transit time. Attempts to publish beyond specified bufferCapacity will pause a publisher
        # thread
        #
        # Args:
        #     buffer_capacity (int):  max number of messages that can be buffered in between before publishing
        #     thread is put on hold
        # Raises:
        #     IllegalArgumentError: if either the  provided buffer size
        # Returns:
        #     DirectMessagePublisherBuilder for method chaining.
        #
        is_type_matches(buffer_capacity, int, logger=logger)
        if buffer_capacity <= 0:
            logger.warning("Buffer size:'%d' %s", buffer_capacity, _solace_message_constants.VALUE_CANNOT_BE_NEGATIVE)
            raise IllegalArgumentError(
                f"Buffer size:'{buffer_capacity}' {_solace_message_constants.VALUE_CANNOT_BE_NEGATIVE}")
        self._publisher_back_pressure_type = PublisherBackPressure.Wait
        self._buffer_capacity = buffer_capacity
        return self

    def __build_back_pressure_from_props(self, configuration: dict):
        if publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY in configuration.keys():
            if configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY] \
                    == publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_ELASTIC:
                self.on_back_pressure_elastic()
            elif configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY] == \
                    publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_REJECT_WHEN_FULL:
                self.__validate_buffer_capacity_key(configuration)
                self.on_back_pressure_reject(
                    buffer_capacity=configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_BUFFER_CAPACITY])
            elif configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY] == \
                    publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_WAIT_WHEN_FULL:
                self.__validate_buffer_capacity_key(configuration)
                self.on_back_pressure_wait(
                    buffer_capacity=configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_BUFFER_CAPACITY])

    @staticmethod
    def __validate_buffer_capacity_key(configuration: dict):
        if publisher_properties.PUBLISHER_BACK_PRESSURE_BUFFER_CAPACITY not in configuration.keys():
            raise IllegalArgumentError(_solace_message_constants.MISSING_BUFFER_CAPACITY)
        is_type_matches(configuration[publisher_properties.PUBLISHER_BACK_PRESSURE_BUFFER_CAPACITY], int,
                        logger=logger)
