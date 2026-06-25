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

"""This module contains the acceptable dictionary values for the keys found in
:py:class:`solace.messaging.config.solace_properties.receiver_properties`.
These keys are used to configure the properties of
:py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`."""

RECEIVER_BACK_PRESSURE_STRATEGY_ELASTIC = "ELASTIC"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration
object to configure elastic back pressure for a direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.from_properties()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the back pressure of a
direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.on_back_pressure_elastic()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_elastic>`
method."""

RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST = "BUFFER_DROP_OLDEST_WHEN_FULL"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration 
object to configure drop-oldest back pressure for a direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.from_properties()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the back pressure of a
direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.on_back_pressure_oldest()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_oldest>`
method."""

RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST = "BUFFER_DROP_LATEST_WHEN_FULL"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration
object to configure drop-latest back pressure for a direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.from_properties()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the back pressure of a
direct receiver through the
:py:meth:`DirectMessageReceiverBuilder.on_back_pressure_latest().solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_latest>`
method."""

PERSISTENT_REPLAY_ALL = "REPLAY_ALL"  # Replay all the messages from the replay log
"""This is a constant containing an acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration
object to configure message replay for all messages for persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the replay strategy of a
persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_replay_strategy()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_replay_strategy>`
method."""

PERSISTENT_REPLAY_TIME_BASED = "REPLAY_TIME_BASED"  # Replay messages from a specified start time
"""This is a constant containing an acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration
object to configure message replay from a point of time in replay log for persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the replay strategy of a
persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_replay_strategy()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_replay_strategy>`
method."""

PERSISTENT_REPLAY_ID_BASED = "REPLAY_ID_BASED"  # Replay messages after a specified replay id
"""This is a constant containing an acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MESSAGE_REPLAY_STRATEGY`
property key. This property-constant mapping can be used in a dict typed configuration
object to configure message replay all messages after a message identified by a message ID in replay log
for persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the replay strategy of a
persistent receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_replay_strategy()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_replay_strategy>`
method."""

PERSISTENT_RECEIVER_DO_NOT_CREATE_MISSING_RESOURCES = "DO_NOT_CREATE"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY`
property key. This constant represents a strategy to avoid the creation of any 
potentially missing resources (i.e. queues) on a broker. This property-constant mapping
can be used in a dict typed configuration object to configure the strategy for creating
missing resources through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the missing
resource creation strategy of a persistent message receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy()`<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy>`
method.
"""

PERSISTENT_RECEIVER_CREATE_ON_START_MISSING_RESOURCES = "CREATE_ON_START"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY`
property key. This constant represents a strategy that tries to create all potentially 
missing resources (i.e. queues) on a broker when the receiver starts.This property-constant mapping
can be used in a dict typed configuration object to configure the strategy for creating
missing resources through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the missing
resource creation strategy of a persistent message receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy()`<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy>`
method.
"""

PERSISTENT_RECEIVER_AUTO_ACK = "AUTO_ACK"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MESSAGE_ACK_STRATEGY`
property key. This constant represents a strategy for the auto-acknowledgement 
of messages before they are processed by the application with any of receive methods.
This property-constant mapping can be used in a dict typed configuration object to 
configure the strategy for acknowledging received messages through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the strategy
for acknowledging messages received by a persistent message receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_message_auto_acknowledgement<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_auto_acknowledgement>`
method.
"""

PERSISTENT_RECEIVER_CLIENT_ACK = "CLIENT_ACK"
"""This is a constant containing the acceptable value of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_MESSAGE_ACK_STRATEGY`
property key. This constant represents a strategy for the manual acknowledgement of
messages by the client. This property-constant mapping can be used in a dict typed
configuration object to configure the strategy for acknowledging received messages
through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the strategy
for acknowledging messages received by a persistent message receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_message_client_acknowledgement<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_client_acknowledgement>`
method.
"""

PERSISTENT_RECEIVER_OUTCOME_ACCEPTED = "ACCEPTED"
"""This is a constant containing one of the three acceptable values of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_REQUIRED_MESSAGE_OUTCOME_SUPPORT`
property key. This constant represents that the user intends to accept (positively acknowledge) some messages on the receiver.
This is the default.
This property-constant mapping can be used in a comma-separated string value in a dict typed
configuration object to configure the outcome types on the receiver
through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the outcomes
for the receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_required_message_outcome_support<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`
method.
"""
 
PERSISTENT_RECEIVER_OUTCOME_FAILED = "FAILED"
"""This is a constant containing one of the three acceptable values of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_REQUIRED_MESSAGE_OUTCOME_SUPPORT`
property key. This constant represents that the user intends to indicate it failed to process the message (negatively acknowledge without removing from the queue)
on the receiver. Depending on configuration and the current redelivery count on the message, it may remain eligible for redelivery, or be moved to the DMQ, or neither.
This property-constant mapping can be used in a comma-separated string value in a dict typed
configuration object to configure the outcome types on the receiver
through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the outcomes
for the receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_required_message_outcome_support<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`
method.
"""
 
PERSISTENT_RECEIVER_OUTCOME_REJECTED = "REJECTED"
"""This is a constant containing one of the three acceptable values of the
:py:const:`solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_REQUIRED_MESSAGE_OUTCOME_SUPPORT`
property key. This constant represents that the user intends to reject (negatively acknowledge and remove from the queue) some messages on the receiver.
This property-constant mapping can be used in a comma-separated string value in a dict typed
configuration object to configure the outcome types on the receiver
through the
:py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
method. This method is an alternative to the direct means of setting the outcomes
for the receiver through the
:py:meth:`PersistentMessageReceiverBuilder.with_required_message_outcome_support<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`
method.
"""
