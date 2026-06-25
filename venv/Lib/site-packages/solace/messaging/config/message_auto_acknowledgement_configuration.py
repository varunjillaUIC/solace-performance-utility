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
This module defines the interface to enable message auto-acknowledgement. In some scenarios,
when a specific message is published, the receiver that has received that message and send an
acknowledgement for the message that was received back to the publisher. With auto-acknowledgement,
you can automatically acknowledge each message.
"""

from abc import ABC, abstractmethod

class MessageAutoAcknowledgementConfiguration(ABC):
    """
    NOTE: THIS CLASS IS BEING ONLY FOR BACKWARDS-COMPATIBILITY, AND HAS BEEN DEPRECATED IN FAVOR OF
    :py:class:`solace.messaging.config.message_acknowledgement_configuration.MessageAcknowledgementConfiguration`.

    An abstract class that defines the interface to enable message auto-acknowledgement.

    Auto-acknowledgement is disabled by default.
    """

    @abstractmethod
    def with_message_auto_acknowledgement(self) -> 'MessageAutoAcknowledgementConfiguration':  # pylint: disable=line-too-long
        """
        Enables support for message auto acknowledgement (auto-ack) on all receiver methods,
        which includes both synchronous and asynchronous  methods.

        NOTE:
            - For callback-based methods, auto-ack is performed when the message-processing callback method
              is finished without an error. This means that if the message-processing callback method processes
              a message using another thread, the message acknowledgement may be performed before that other thread
              finishes and any errors raised in the other thread are not considered.

            - For blocking receive (without callback) methods: auto-ack is performed immediately after the
              :py:meth:`PersistentMessageReceiver.receive_message<solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver.receive_message>`
              call returns.
            - Should the underlying network connectivity fail auto acknowledgement may fail after the message-processing
              callback method. In this case it is not guaranteed to acknowledge messages automatically.

        Returns:
            An instance of itself for method chaining.
        """  # pylint: disable=line-too-long
