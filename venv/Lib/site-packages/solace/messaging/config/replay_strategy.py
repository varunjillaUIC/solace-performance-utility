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

# pylint: disable=too-few-public-methods, line-too-long
""" This module contains abstract base class for strategies for replay and its concrete implementations.

The :py:class:`ReplayStrategy` instance is configured in the
:py:class:`PersistentMessageReceiver<solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver>`
with the
:py:func:`PersistentMessageReceiverBuilder.with_message_replay() <solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_replay>`
method.

The following implementations of ReplayStrategy exist:

- :py:class:`AllMessagesReplay`
- :py:class:`TimeBasedReplay`
- :py:class:`ReplicationGroupMessageIdReplay`

"""

import datetime
import logging
from abc import ABC

from solace.messaging.utils._solace_utilities import is_type_matches

logger = logging.getLogger('solace.messaging')


class ReplayStrategy(ABC):
    """
        This class represents the message replay strategy. Message replay lets applications retrieve information
        long after it was sent and delivered. The replay strategies available are:

        - :py:class:`AllMessagesReplay <solace.messaging.config.replay_strategy.AllMessagesReplay>`:
          Will replay all the messages available in the replay log.
        - :py:class:`TimeBasedReplay <solace.messaging.config.replay_strategy.TimeBasedReplay>`:
          Will replay the messages from a specified date and time.
        - :py:class:`ReplicationGroupMessageIdReplay <solace.messaging.config.replay_strategy.ReplicationGroupMessageIdReplay>`:
          Will replay messages after a specified Replication Group Message Id.

        Static factory methods are provide to instantiate each of the above ReplayStrategy.
    """

    @staticmethod
    def all_messages() -> 'AllMessagesReplay':
        """Factory method to create replay strategy for ALL available messages

        Returns:
            A new instance of the class
                :py:class:`AllMessagesReplay<solace.messaging.config.replay_strategy.AllMessagesReplay>`.
        """
        return AllMessagesReplay()

    @staticmethod
    def time_based(replay_date: datetime.datetime) -> 'TimeBasedReplay':
        """Factory method to create time based replay strategy based on start time and timezone

        An example building the
        :py:class:`TimeBasedReplay<solace.messaging.config.replay_strategy.TimeBasedReplay>`
        strategy using a datetime object::

            datetime_object = datetime.datetime.now(datetime.timezone.utc)
            new_time_based_replay_strategy_obj = ReplayStrategy.time_based(datetime_object)

        Args:
            replay_date(datetime.datetime): the date and time from which messages will be replayed. The replay_date
             should be a timezone aware datetime object.  If the passed
             datetime object is naive, the API will assume it represents the system's local time zone.

        Returns:
            A new instance of :py:class:`TimeBasedReplay<solace.messaging.config.replay_strategy.TimeBasedReplay>`.
        """
        is_type_matches(replay_date, datetime.datetime, logger=logger)

        return TimeBasedReplay(replay_date)

    @staticmethod
    def replication_group_message_id_based(replication_group_message_id: 'ReplicationGroupMessageId') \
            -> 'ReplicationGroupMessageIdReplay':  # pylint: disable=line-too-long
        """
        Factory method to create a replay strategy based on Replication Group Message ID.

        There are two ways to acquire
        :py:func:`ReplicationGroupMessageId <solace.messaging.receiver.inbound_message.InboundMessage.get_replication_group_message_id>`
	for this method:

        - Using a Replication Group Message ID from a previously received message
          :py:func:`InboundMessage.get_replication_group_message_id() <solace.messaging.receiver.inbound_message.InboundMessage.get_replication_group_message_id>`
        - Using a Replication Group Message ID created from the factory method
          :py:func:`ReplicationGroupMessageId.of() <solace.messaging.receiver.inbound_message.ReplicationGroupMessageId.of>`

        Args:
            replication_group_message_id(ReplicationGroupMessageId): Replication Group Message ID. If found, all messages after the
              Replication Group Message ID are replayed.

        Returns:
            A new instance of :py:class:`ReplicationGroupMessageIdReplay<solace.messaging.config.replay_strategy.ReplicationGroupMessageIdReplay>`

        """
        return ReplicationGroupMessageIdReplay(replication_group_message_id)

class AllMessagesReplay(ReplayStrategy):
    """
    Replay strategy to replay all messages in the replay log.
    """


class TimeBasedReplay(ReplayStrategy):
    """
    Replay strategy to replay all messages from a given time.
    """

    def __init__(self, replay_date: datetime.datetime):
        self._replay_date = replay_date

    def get_replay_date(self) -> datetime.datetime:
        """
        Returns:
            The date used to construct this
                :py:class:`TimeBasedReplay<solace.messaging.config.replay_strategy.TimeBasedReplay>`
                object.
        """
        return self._replay_date

    def __str__(self):
        return f"TimeBasedReplay replay_date: {str(self._replay_date)}"


class ReplicationGroupMessageIdReplay(ReplayStrategy):
    """
    Replay strategy to replay all messages after a given Replication Group Message Id.
    """
    def __init__(self, replay_id: 'ReplicationGroupMessageId'):
        self._replay_id = replay_id

    @property
    def replication_group_message_id(self):
        """ Replication Group Message Id"""
        return self._replay_id

    def __str__(self):
        return f"ReplicationGroupMessageIdReplay  replay_id : {str(self._replay_id)}"
