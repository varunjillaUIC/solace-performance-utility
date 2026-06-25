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

"""Module contains the abstract classes for ReceiverActivationPassivationConfiguration and ReceiverStateChangeListener
and ReceiverState"""

import enum
from abc import ABC, abstractmethod


class ReceiverState(enum.Enum):  # pylint: disable=too-few-public-methods
    """
     The receiver states.
    """
    ACTIVE = 5  # state in which receiver can receive messages from a broker (broker feature)
    PASSIVE = 6  # state in which receiver can NOT receive messages from a broker (broker feature), usually
    # another instance of receiver becomes active, when given instance is passivated


class ReceiverStateChangeListener:
    """
      A class  that abstracts notifications processing about activation/passivation of the consumer
      receiver.
    """

    def on_change(self, old_state: ReceiverState, new_state: ReceiverState, change_time_stamp: float):
        """
        Changes the receiver state.

        Args:
            old_state(ReceiverState): The old state to change from, which can be ``ACTIVE`` or ``PASSIVE``.
            new_state(ReceiverState): The new state to change to, which can be ``ACTIVE`` or ``PASSIVE``.
            change_time_stamp(float): The timestamp to use for the change.
        """


class ReceiverActivationPassivationConfiguration(ABC):
    """
    Abstract class that defines the interface to support for activation/passivation notifications send from a
    Solace event broker to the particular instance of the receiver.
    """

    @abstractmethod
    def with_activation_passivation_support(self, receiver_state_change_listener: ReceiverStateChangeListener) \
            -> 'ReceiverActivationPassivationConfiguration':
        """
        Enables the receiver to receive event broker notifications about state changes of the
        specified receiver instance.

        Args:
            receiver_state_change_listener(ReceiverStateChangeListener): The receiver instance to receive state
             changes about.
        """
