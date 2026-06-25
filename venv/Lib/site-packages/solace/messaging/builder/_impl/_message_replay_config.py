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

"""Module contains common MessageReplayConfig implementation """
# pylint: disable=missing-function-docstring,inconsistent-return-statements,no-else-return
import logging
import datetime

from solace.messaging.config.replay_strategy import ReplayStrategy, AllMessagesReplay, TimeBasedReplay, \
    ReplicationGroupMessageIdReplay
from solace.messaging.utils._solace_utilities import is_type_matches
from solace.messaging.config.solace_properties import receiver_properties
from solace.messaging.config.solace_constants import receiver_constants
from solace.messaging.config._sol_constants import SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.config._ccsmp_property_mapping import replay_prop


logger = logging.getLogger('solace.messaging.receiver')


class _MessageReplayConfiguration():  # pylint: disable=attribute-defined-outside-init
    # We are not doing cooperative multi-inheritance, so better stay out of __init__:
    def init_replay_strategy(self):
        self._replay_strategy: ReplayStrategy
        self._replay_strategy = None


    def _with_message_replay(self, replay_strategy: 'ReplayStrategy'):
        is_type_matches(replay_strategy, ReplayStrategy, logger=logger)
        self._replay_strategy = replay_strategy
        return self

    @property
    def replay_strategy(self):
        # Property to hold and return the ReplayStrategy
        return self._replay_strategy

    def _build_replay_strategy_from_props(self, configuration: dict):
        if receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY in configuration.keys():
            if configuration[receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY] \
                    == receiver_constants.PERSISTENT_REPLAY_ALL:
                self._replay_strategy = AllMessagesReplay()
            elif configuration[receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY] \
                    == receiver_constants.PERSISTENT_REPLAY_TIME_BASED:
                self._replay_strategy = TimeBasedReplay(
                    configuration[receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY_TIME_BASED_START_TIME])
            elif configuration[receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY] \
                    == receiver_constants.PERSISTENT_REPLAY_ID_BASED:
                self._replay_strategy = ReplicationGroupMessageIdReplay(
                    configuration[receiver_properties \
                        .PERSISTENT_MESSAGE_REPLAY_STRATEGY_ID_BASED_REPLICATION_GROUP_MESSAGE_ID])
            return self
        else:
            logger.debug('KEY is not available in the receiver properties')



def incorporate_replay_props(replay_strategy, old_config):
    new_config = old_config
    if isinstance(replay_strategy, AllMessagesReplay):
        new_config = {**replay_prop, **old_config}
    elif isinstance(replay_strategy, TimeBasedReplay):

        # the input datetime object is converted to utc and then to epoch value here
        replay_date_epoch = replay_strategy.get_replay_date().astimezone(datetime.timezone.utc).timestamp()

        replay_date_epoch_with_prefix = f'DATE:{int(replay_date_epoch)}'

        new_config[SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION] = replay_date_epoch_with_prefix
    elif isinstance(replay_strategy, ReplicationGroupMessageIdReplay):
        replay_strategy: ReplicationGroupMessageIdReplay
        new_config[SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION] = \
            str(replay_strategy.replication_group_message_id)
    return new_config

replay_error_list = [SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_NOT_SUPPORTED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_DISABLED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_NON_EXCLUSIVE_NOT_ALLOWED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_INACTIVE_FLOW_NOT_ALLOWED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_BROWSER_FLOW_NOT_ALLOWED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_TEMPORARY_NOT_SUPPORTED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_UNKNOWN_START_LOCATION_TYPE.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_MESSAGE_UNAVAILABLE.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_STARTED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_CANCELLED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_START_TIME_NOT_AVAILABLE.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_MESSAGE_REJECTED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_LOG_MODIFIED.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_MISMATCHED_ENDPOINT_ERROR_ID.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_OUT_OF_REPLAY_RESOURCES.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_START_MESSAGE_UNAVAILABLE.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_MESSAGE_ID_NOT_COMPARABLE.name,
                     SolClientSubCode.SOLCLIENT_SUBCODE_REPLAY_ANONYMOUS_NOT_SUPPORTED.name]
