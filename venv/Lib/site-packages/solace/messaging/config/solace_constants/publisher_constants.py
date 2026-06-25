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


# pylint: disable=trailing-whitespace, line-too-long

"""
This module contains the acceptable dictionary values for the keys found in
:py:mod:`solace.messaging.config.solace_properties.publisher_properties`.
These keys are used to configure the properties of
:py:class:`solace.messaging.publisher.message_publisher.MessagePublisher`."""



PUBLISHER_BACK_PRESSURE_STRATEGY_ELASTIC = "ELASTIC"
"""This constant contains the acceptable value for configuring elastic back pressure using the
:py:const:`solace.messaging.config.solace_properties.publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY`
property. This property of the message publisher can be configured using the
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder.from_properties` method.
This from_properties method is an alternative means to the direct means of setting the back pressure of a 
publisher through the 
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisher.on_back_pressure_elastic`
method."""

PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_REJECT_WHEN_FULL = "BUFFER_REJECT_WHEN_FULL"
"""This constant contains the acceptable value for configuring reject back pressure using the
:py:const:`solace.messaging.config.solace_properties.publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY`
property. This property of the message publisher can be configured using the
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder.from_properties` method.
This from_properties method is an alternative measn to the direct means of setting the back pressure of a
publisher through the
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisher.on_back_pressure_reject`
method."""

PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_WAIT_WHEN_FULL = "BUFFER_WAIT_WHEN_FULL"
"""This constant contains the acceptable value for configuring wait back pressure using the
:py:const:`solace.messaging.config.solace_properties.publisher_properties.PUBLISHER_BACK_PRESSURE_STRATEGY`
property. This property of the message publisher can be configured using the
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder.from_properties` method.
This from_properties method is an alternative means to the direct means of setting the back pressure of a 
publisher through the
:py:meth:`solace.messaging.builder.message_publisher_builder.MessagePublisher.on_back_pressure_wait`
method.
"""
