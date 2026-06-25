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

"""
This module defines the interface to enable message replay strategy. Message Replay is a feature
of persistent messages receivers.  When a persistent message receiver starts, it may choose to replay
messages from the broker replay log, which will be received first before live messages.
"""

from abc import ABC, abstractmethod


class MessageReplayConfiguration(ABC):
    """
    An abstract class that defines the interface to configure message message replay strategy in a
    persistent message receiver builder.
    """

    @abstractmethod
    def with_message_replay(self, replay_strategy: 'ReplayStrategy') -> 'MessageReplayConfiguration':
        """
        ADd a message replay message strategy to a persistent receiver.

        Args:
            replay_strategy(ReplayStrategy): Specify the message replay strategy.

        Returns:
            MessageReplayConfiguration: A reference to self for method chaining.
        """
