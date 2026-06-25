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
    Module to handle back pressure configuration in
    :py:class:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder`.
"""
from abc import ABC, abstractmethod

__all__ = ["PublisherBackPressureConfiguration"]


class PublisherBackPressureConfiguration(ABC):
    """
    A class that abstracts configuration of back-pressure features
    All methods in this class are mutually exclusive and therefore should be called only once.

    The default back-pressure configuration is to internally handle back pressure. This is equivalent
    on_back_pressure_elastic().
    """

    @abstractmethod
    def on_back_pressure_reject(self, buffer_capacity: int) -> 'PublisherBackPressureConfiguration':
        """
        Configures the  publisher with capacity-bounded, buffered back-pressure; when the application keeps publishing,
        the publish method raises a :py:class:`solace.messaging.errors.pubsubplus_client_error.PublisherOverflowError`
        if the specified ``buffer_capacity`` is exceeded. If the capacity is 0 an exception is thrown when the
        transport is full. And there is no internal buffer capacity.

        Args:
            buffer_capacity(int): The maximum number of messages to buffer before raising an exception.

        Returns:
            An instance of itself for method chaining.

        Raises:
            IllegalArgumentError: With invalid capacity value. Valid capacity is 0 or greater.
            InvalidDataTypeError: With invalid capacity type. Valid capacity is of type int.
        """

    @abstractmethod
    def on_back_pressure_elastic(self) -> 'PublisherBackPressureConfiguration':
        """
        Configures the publisher to buffer indefinitely, consuming as much memory as required for buffered messages.
        On memory exhaustion publisher behavior is undefined. Elastic, essential no, back-pressure is an ideal strategy
        for applications that publish messages at a low rate with infrequent small bursts of activity.
        It should not be considered for use in all cases.

        Returns:
            An instance of itself for method chaining.

        Raises:
            PubSubPlusClientError: When unable to configure the publisher.
        """

    @abstractmethod
    def on_back_pressure_wait(self, buffer_capacity: int) -> 'PublisherBackPressureConfiguration':
        """
        Configures the  publisher with capacity bounded buffered back-pressure.
        If the application application keeps publishing using the ``publish()`` method,
        it blocks and waits for room if the specified ``buffer_capacity`` has been exceeded.

        Args:
            buffer_capacity (int): The maximum number of messages to buffer before raising an error.

        Returns:
            An instance of itself for method chaining.

        Raises:
            IllegalArgumentError: With invalid capacity value. Valid capacity is 1 or greater.
            InvalidDataTypeError: With invalid capacity type. Valid capacity is of type int.
        """
