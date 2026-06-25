# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
    Module to handle back pressure configuration in
    :py:class:`solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder`.
"""
from abc import ABC, abstractmethod

__all__ = ["DirectReceiverBackPressureConfiguration"]


class DirectReceiverBackPressureConfiguration(ABC):
    """
    A class that abstracts configuration of back-pressure features
    All methods in this class are mutually exclusive and therefore should be called only once.

    The default back-pressure configuration is to internally handle back pressure. This is equivalent
    to on_back_pressure_elastic().
    """

    @abstractmethod
    def on_back_pressure_elastic(self) -> 'DirectReceiverBackPressureConfiguration':
        """
        Configures the receiver to buffer indefinitely, consuming as much memory as required for buffered messages.
        On memory exhaustion receiver behaviour is undefined. Elastic, essentially no, back-pressure is an ideal
        strategy for applications that process received messages at a low rate with infrequent small bursts of
        activity.
        It should not be considered for use in all cases.

        Returns:
            DirectReceiverBackPressureConfiguration: An instance of itself for method chaining.

        Raises:
            PubSubPlusClientError: When unable to configure the receiver.
        """

    @abstractmethod
    def on_back_pressure_drop_latest(self, buffer_capacity: int) -> 'DirectReceiverBackPressureConfiguration':
        """
        Configures the publisher with capacity-bounded, buffered back-pressure. If the buffer is full and is still
        receiving messages, the incoming message will be discarded. The maximum capacity of the buffer is given
        by the parameter of this method, ``buffer_capacity``.

        Args:
            buffer_capacity(int): The maximum number of messages to buffer before discarding the latest incoming
                message.

        Returns:
            DirectReceiverBackPressureConfiguration: An instance of itself for method chaining.

        Raises:
            IllegalArgumentError: If an invalid buffer capacity is passed to this method. Valid buffer capacity is
                0 or greater.
            InvalidDataTypeError: If a buffer capacity of invalid type is passed to this method. Valid buffer
                capacity type is int.
        """


    @abstractmethod
    def on_back_pressure_drop_oldest(self, buffer_capacity: int) -> 'DirectReceiverBackPressureConfiguration':
        """
        Configures the publisher with capacity-bounded, buffered back-pressure. If the buffer is full and is
        still receiving messages, the oldest message in the buffer is discarded. The maximum capacity of the
        buffer is given by the parameter of this method, ``buffer_capacity``.

        Args:
            buffer_capacity(int): The maximum number of messages to buffer before discarding the oldest message.

        Returns:
            DirectReceiverBackPressureConfiguration: An instance of itself for method chaining.

        Raises:
            PubSubPlusClientError: If an invalid buffer capacity is passed to this method. Valid buffer
                capacity is 0 or greater.
            InvalidDataTypeError: If a buffer capacity of invalid type is passed to this method. Valid buffer
                capacity type is int.
        """
