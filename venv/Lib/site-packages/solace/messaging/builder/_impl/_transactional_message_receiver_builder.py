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

import logging
from typing import List
from solace.messaging.builder.transactional_message_receiver_builder import TransactionalMessageReceiverBuilder
from solace.messaging.receiver.transactional_message_receiver import TransactionalMessageReceiver
from solace.messaging.receiver._impl._transactional_message_receiver import _TransactionalMessageReceiver
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.config.receiver_activation_passivation_configuration import ReceiverStateChangeListener
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationStrategy
from solace.messaging.resources.queue import Queue
from solace.messaging.utils._solace_utilities import is_type_matches
from solace.messaging.config.solace_properties import receiver_properties
from solace.messaging.config.solace_constants import receiver_constants
from solace.messaging.config.replay_strategy import ReplayStrategy
from solace.messaging.builder._impl._message_replay_config import _MessageReplayConfiguration


logger = logging.getLogger('solace.messaging.receiver')

class _TransactionalMessageReceiverBuilder(TransactionalMessageReceiverBuilder, _MessageReplayConfiguration):
    def __init__(self, config: dict, transactional_messaging_service: 'TransactionalMessagingService'):
        self.init_replay_strategy()
        self._config = dict(config)
        self._transactional_messaging_service = transactional_messaging_service
        self._topic_subscriptions = []
        self._receiver_state_change_listener = None
        self._endpoint_to_consume_from = None
        self._missing_resources_creation_strategy = None
        self._message_selector = None

    def build(self, endpoint_to_consume_from: Queue) -> TransactionalMessageReceiver:
        is_type_matches(endpoint_to_consume_from, Queue, logger=logger)
        self._endpoint_to_consume_from = endpoint_to_consume_from
        return _TransactionalMessageReceiver(config=self._config,
                                             builder=self,
                                             transactional_messaging_service=self._transactional_messaging_service)

    #MessageReceiverBuilder:
    def with_subscriptions(self, subscriptions: List[TopicSubscription]) -> 'TransactionalMessageReceiverBuilder':
        is_type_matches(subscriptions, List, raise_exception=True)
        self._topic_subscriptions = []
        for topic in subscriptions:
            is_type_matches(topic, TopicSubscription, raise_exception=True)
            self._topic_subscriptions.append(topic.get_name())
        return self

    def with_message_replay(self, replay_strategy: ReplayStrategy) -> 'TransactionalMessageReceiverBuilder':
        return self._with_message_replay(replay_strategy)

    def from_properties(self, configuration: dict) -> 'TransactionalMessageReceiverBuilder':
        self.__build_missing_resources_creation_strategy_from_props(configuration)
        self.__build_message_selector_from_props(configuration)
        self._build_replay_strategy_from_props(configuration)
        self._config = {**self._config, **configuration}
        return self

    #ReceiverActivationPassivationConfiguration:
    def with_activation_passivation_support(self, receiver_state_change_listener: ReceiverStateChangeListener) \
        -> 'TransactionalMessageReceiverBuilder':
        is_type_matches(receiver_state_change_listener, ReceiverStateChangeListener, logger=logger)
        self._receiver_state_change_listener = receiver_state_change_listener
        return self

    def with_message_selector(self, selector_query_expression: str) -> 'TransactionnalMessageReceiverBuilder':
        is_type_matches(selector_query_expression, str, logger=logger)
        self._message_selector = selector_query_expression
        return self

    #MissingResourcesCreationConfiguration:
    def with_missing_resources_creation_strategy(self,
                                                 strategy: 'MissingResourcesCreationStrategy') \
        -> 'TransactionalMessageReceiverBuilder':
        is_type_matches(strategy, MissingResourcesCreationStrategy, logger=logger)
        self._missing_resources_creation_strategy = strategy
        return self

    def __build_missing_resources_creation_strategy_from_props(self, configuration: dict):
        if receiver_properties.PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY in configuration.keys():
            if configuration[receiver_properties.PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY] \
                    == receiver_constants.PERSISTENT_RECEIVER_CREATE_ON_START_MISSING_RESOURCES:
                self.with_missing_resources_creation_strategy(MissingResourcesCreationStrategy.CREATE_ON_START)
            elif configuration[receiver_properties.PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY] \
                    == receiver_constants.PERSISTENT_RECEIVER_DO_NOT_CREATE_MISSING_RESOURCES:
                self.with_missing_resources_creation_strategy(MissingResourcesCreationStrategy.DO_NOT_CREATE)

    def __build_message_selector_from_props(self, configuration: dict):
        if receiver_properties.PERSISTENT_MESSAGE_SELECTOR_QUERY in configuration.keys():
            self.with_message_selector(configuration[receiver_properties.PERSISTENT_MESSAGE_SELECTOR_QUERY])
