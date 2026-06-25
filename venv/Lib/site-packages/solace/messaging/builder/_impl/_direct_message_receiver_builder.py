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

"""Module contains the implementation class and methods for the DirectMessageReceiverBuilder"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import logging
from typing import List

from solace.messaging.builder._impl._message_receiver_builder import _MessageReceiverBuilder, \
    DirectMessageReceiverBackPressure
from solace.messaging.builder.direct_message_receiver_builder import DirectMessageReceiverBuilder
from solace.messaging.receiver._impl._direct_message_receiver import _DirectMessageReceiver
from solace.messaging.receiver._impl._receiver_utilities import validate_subscription_type
from solace.messaging.resources.share_name import ShareName, _ShareName
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._solace_utilities import is_type_matches
from solace.messaging.errors.pubsubplus_client_error import IllegalArgumentError
from solace.messaging.config import _solace_message_constants
from solace.messaging.config.solace_properties import receiver_properties
from solace.messaging.config.solace_constants import receiver_constants

logger = logging.getLogger('solace.messaging.receiver')

class _DirectMessageReceiverBuilder(_MessageReceiverBuilder, DirectMessageReceiverBuilder):

    def __init__(self, messaging_service):
        super().__init__(messaging_service)
        self._topic_dict = {}
        self._buffer_capacity = 0
        self._receiver_back_pressure_type: DirectMessageReceiverBackPressure = DirectMessageReceiverBackPressure.Elastic

    @property
    def topic_dict(self):
        return self._topic_dict

    @property
    def receiver_back_pressure_type(self):
        return self._receiver_back_pressure_type

    def with_subscriptions(self, subscriptions: List[TopicSubscription]) -> 'DirectMessageReceiverBuilder':
        #
        # Add a list of subscriptions to be applied to all DirectMessageReceiver subsequently created with
        # this builder.
        # Args:
        #     subscriptions (List[TopicSubscription]): subscriptions list of topic subscriptions to be added
        # Returns:
        #     DirectMessageReceiverBuilder instance for method chaining
        #
        is_type_matches(subscriptions, List, logger=logger)
        self._topic_subscriptions = []
        self._receiver_back_pressure_type: DirectMessageReceiverBackPressure = DirectMessageReceiverBackPressure.Elastic
        for topic in subscriptions:
            validate_subscription_type(subscription=topic, logger=logger)
            self._topic_subscriptions.append(topic.get_name())
        return self

    def from_properties(self, configuration: dict) -> 'DirectMessageReceiverBuilder':
        #
        # Set DirectMessageReceiver properties from the dictionary of (property,value) tuples.
        # Args:
        #     configuration (dict): configuration properties
        # Returns:
        #     DirectMessageReceiverBuilder instance for method chaining
        #
        is_type_matches(configuration, dict, logger=logger)
        self.__build_back_pressure_from_props(configuration)
        return self

    def build(self, shared_subscription_group: ShareName = None) -> 'DirectMessageReceiver':
        self._topic_dict['subscriptions'] = self._topic_subscriptions
        if shared_subscription_group:
            is_type_matches(shared_subscription_group, ShareName, logger=logger)
            name = shared_subscription_group.get_name()
            share_name = _ShareName(name)
            share_name.validate()
            self._topic_dict['group_name'] = name
        return _DirectMessageReceiver(self)

    def on_back_pressure_elastic(self) -> DirectMessageReceiverBuilder:
        #
        # :py:class:`solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver` that are built
        # will buffer all incoming messages until memory is exhausted.
        #
        # Usage of this strategy can lead to memory shortage situations and can cause applications to crash.
        # This strategy may be useful for microservices which are running in a managed environment that can
        # detect crashes and perform restarts of a microservice.
        # Returns:
        #     DirectMessageReceiverBuilder for method chaining.
        #
        self._receiver_back_pressure_type = DirectMessageReceiverBackPressure.Elastic
        logger.debug('Enabled elastic back pressure for direct message receiver; buffer/queue capacity: MAX')
        return self

    def on_back_pressure_drop_latest(self, buffer_capacity: int) -> 'DirectMessageReceiverBuilder':
        #
        # :py:class:`solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver` that are built
        # will buffer incoming messages until the buffer capacity is reached. Once the buffer capacity is
        # reached, incoming messages will be discarded.
        #
        # Args:
        #     buffer_capacity (int): Maximum number of messages that can be buffered before discarding
        #     incoming messages.
        # Raises:
        #     IllegalArgumentError: If the buffer capacity is negative, this error will be raised.
        #     InvalidDataTypeError: IF the buffer capacity is not an int.
        # Returns:
        #     DirectMessageReceiverBuilder for method chaining.
        #
        is_type_matches(buffer_capacity, int, logger=logger)
        if buffer_capacity <= 0:
            logger.warning("Buffer size: '%d' %s", buffer_capacity, _solace_message_constants.VALUE_MUST_BE_POSITIVE)
            raise IllegalArgumentError(
                f"Buffer size:'{buffer_capacity}' {_solace_message_constants.VALUE_MUST_BE_POSITIVE}")

        self._receiver_back_pressure_type = DirectMessageReceiverBackPressure.DropLatest
        self._buffer_capacity = buffer_capacity
        logger.debug('Enabled drop_latest back pressure for direct message receiver; ' \
                     'buffer/queue capacity: %d', buffer_capacity)
        return self

    def on_back_pressure_drop_oldest(self, buffer_capacity: int) -> 'DirectMessageReceiverBuilder':
        #
        # :py:class:`solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver` that are built
        # will buffer incoming messages until the buffer capacity is reached. Once the buffer capacity is
        # reached, the oldest message in the buffer will be discarded before the incoming message is added
        # to the buffer.
        #
        # Args:
        #     buffer_capacity (int): Maximum number of messages that can be buffered before discarding
        #     incoming messages.
        # Raises:
        #     IllegalArgumentError: If the buffer capacity is negative, this error will be raised.
        # Returns:
        #     DirectMessageReceiverBuilder for method chaining.
        #
        is_type_matches(buffer_capacity, int, logger=logger)
        if buffer_capacity <= 0:
            logger.warning("Buffer size: '%d' %s", buffer_capacity, _solace_message_constants.VALUE_MUST_BE_POSITIVE)
            raise IllegalArgumentError(
                f"Buffer size:'{buffer_capacity}' {_solace_message_constants.VALUE_MUST_BE_POSITIVE}")
        self._receiver_back_pressure_type = DirectMessageReceiverBackPressure.DropOldest
        self._buffer_capacity = buffer_capacity
        logger.debug('Enabled drop_oldest back pressure for direct message receiver; ' \
                     'buffer/queue capacity: %d', buffer_capacity)
        return self

    def __build_back_pressure_from_props(self, configuration: dict):
        if receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY in configuration.keys():
            self.__validate_direct_back_pressure_strategy_value(configuration[receiver_properties \
                .DIRECT_BACK_PRESSURE_STRATEGY])
            if configuration[receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY] \
                    == receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_ELASTIC:
                self.on_back_pressure_elastic()
            elif configuration[receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY] == \
                    receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST:
                self.__validate_buffer_capacity_key(configuration)
                self.on_back_pressure_drop_oldest(
                    buffer_capacity=configuration[receiver_properties.DIRECT_BACK_PRESSURE_BUFFER_CAPACITY])
            elif configuration[receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY] == \
                    receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST:
                self.__validate_buffer_capacity_key(configuration)
                self.on_back_pressure_drop_latest(
                    buffer_capacity=configuration[receiver_properties.DIRECT_BACK_PRESSURE_BUFFER_CAPACITY])

    @staticmethod
    def __validate_direct_back_pressure_strategy_value(back_pressure_strategy: str):
        supported_direct_receiver_back_pressure_strategies = \
            [receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_ELASTIC,
             receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST,
             receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST]
        if back_pressure_strategy not in supported_direct_receiver_back_pressure_strategies:
            raise IllegalArgumentError(
                f"Direct receiver back pressure strategy type, '{back_pressure_strategy}', is not supported. " \
                 "Supported back pressure strategies are {supported_direct_receiver_back_pressure_strategies}")

    @staticmethod
    def __validate_buffer_capacity_key(configuration: dict):
        if receiver_properties.DIRECT_BACK_PRESSURE_BUFFER_CAPACITY not in configuration.keys():
            raise IllegalArgumentError(_solace_message_constants.MISSING_BUFFER_CAPACITY)
        is_type_matches(configuration[receiver_properties.DIRECT_BACK_PRESSURE_BUFFER_CAPACITY], int, logger=logger)
