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


"""
This module contains the abstract base class for a persistent message queue browser.
It allows client applications to look at messages stored in persistent store of
Queue Endpoints without removing them. Messages are browsed from oldest to newest.
After being browsed, messages are still available for consumption over normal persistent
receiver. However, it is possible to selectively remove messages from the persistent store of an
Endpoint. In this case, these removed messages will no longer be available for consumption.
Note: If browsing a queue with an active message consumer, no guarantee is made that
      the browser will receive all messages published to the queue. The consumer can receive and
      acknowledge messages before they are delivered to the browser.
A MessageQueueBrowser can be created using MessageQueueBrowserBuilder.
"""

from abc import abstractmethod
from typing import Union
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.utils.life_cycle_control import LifecycleControl, AsyncLifecycleControl
from solace.messaging.utils.manageable_receiver import ManageableReceiver

class MessageQueueBrowser(LifecycleControl, AsyncLifecycleControl,ManageableReceiver):
    """ An abstract class that defines the interface to a persistent message queue browser. """


    @abstractmethod
    def receive_message(self, timeout: int = None) -> Union[InboundMessage, None]:
        """
           Blocking request to receive the next message from a
           message browser without removing it from the persistent store of Queue Endpoints.
           Caller thread is used to perform operation.
           Args:
               timeout(int): The time, in milliseconds, to wait for a message to arrive.
               0 means no wait, None (default) means wait forever.
           Returns:
               InboundMessage: An object that represents an inbound message. Returns None on timeout, or upon
                   service or receiver shutdown.
           Raises:
               PubSubPlusClientError: If error occurred while receiving or processing the message.
        """


    @abstractmethod
    def remove(self, message: InboundMessage):
        """
           Request to remove a message from the Solace event broker's Queue Endpoint.

           Note: If browsing a queue with an active message consumer, no guarantee is made
                 that message removal removes a message before another consumer received it
           Caller thread is used to perform operation.
          Args:
                      message(InboundMessage): The inbound message.
           Raises:
               PubSubPlusClientError: If error occurred while removing of the message.

        """
