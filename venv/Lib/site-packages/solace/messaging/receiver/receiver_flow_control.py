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
This module contains an abstract base class for flow control interfaces on a persistent message receiver.
Only persistent messaging prevents the broker from sending messages through the use of flow control methods.
"""
from abc import ABC, abstractmethod


class ReceiverFlowControl(ABC):
    """
    An abstract class that defines the interface that may stop the broker from delivering messages to a
    a :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`.
    """

    @abstractmethod
    def pause(self):
        """
            Pauses message delivery for an asynchronous message handler or stream. Message delivery can be
            resumed by executing :py:meth:`ReceiverFlowControl.resume()` on a
            :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver` instance.

        Raises:
            PubSubPlusClientError: If an error occurred while pausing message delivery.
        """

    @abstractmethod
    def resume(self):
        """
            Resumes a previously paused message delivery.

        Raises:
            PubSubPlusClientError: If an error occurred while trying to resume a paused messaged delivery.
        """
