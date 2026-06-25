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
This module contains dictionary keys for the :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver`
properties.
"""  # pylint: disable=trailing-whitespace, disable=line-too-long


PERSISTENT_NO_LOCAL_PUBLISHED_MESSAGES = "solace.messaging.receivers.persistent.no-local-published-messages"
""" Reserved for future use."""

DIRECT_BACK_PRESSURE_STRATEGY = "solace.messaging.receiver.direct.back-pressure.strategy"
"""
    This is a property constant containing the key for configuring the back pressure type/strategy of the
    :py:class:`DirectMessageReceiver<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver>`.
    
    The acceptable values for this property are:

      * :py:const:`ELASTIC<solace.messaging.config.solace_constants.receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_ELASTIC>`
      * :py:const:`DROP_OLDEST<solace.messaging.config.solace_constants.receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST>`
      * :py:const:`DROP_LATEST<solace.messaging.config.solace_constants.receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST>`
    
    This property-constant mapping can be used in a dictionary configuration
    object to configure back pressure for a direct receiver through the
    :py:meth:`DirectMessageReceiverBuilder.from_properties()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.from_properties>`
    method. This method is an alternative to the direct means of setting the back pressure of a
    direct receiver through the
    :py:meth:`DirectMessageReceiverBuilder.on_back_pressure_elastic()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_elastic>`,
    :py:meth:`DirectMessageReceiverBuilder.on_back_pressure_drop_oldest()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_drop_oldest>`,
    or
    :py:meth:`DirectMessageReceiverBuilder.on_back_pressure_drop_latest()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_drop_latest>`,
    methods.
"""

DIRECT_BACK_PRESSURE_BUFFER_CAPACITY = "solace.messaging.receiver.direct.back-pressure.buffer-capacity"
"""This is a property constant containing the key for configuring the back pressure buffer capacity of the
    :py:class:`DirectMessageReceiverBuilder<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver>`.
    The acceptable value for this property is an integer that is greater than 0. This property-constant
    mapping can be used in a dict typed configuration object to configure back pressure for a direct 
    receiver through the
    :py:meth:`DirectMessageReceiverBuilder.from_properties()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.from_properties>`
    method. This property only has an effect if 
    :py:const:`DIRECT_BACK_PRESSURE_STRATEGY<solace.messaging.config.solace_properties.receiver_properties.DIRECT_BACK_PRESSURE_STRATEGY>`
    is configured using
    :py:const:`RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST<solace.messaging.config.solace_constants.receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_LATEST>`
    or
    :py:const:`RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST<solace.messaging.config.solace_constants.receiver_constants.RECEIVER_BACK_PRESSURE_STRATEGY_DROP_OLDEST>`.
    This method is an alternative to the direct means of setting the back pressure buffer capacity 
    of a direct receiver by passing it as a parameter to the
    :py:meth:`DirectMessageReceiverBuilder.on_back_pressure_drop_oldest()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_drop_oldest>`
    or
    :py:meth:`DirectMessageReceiverBuilder.on_back_pressure_drop_latest()<solace.messaging.builder.direct_message_receiver_builder.DirectMessageReceiverBuilder.on_back_pressure_drop_latest>`
    methods."""

PERSISTENT_MESSAGE_REPLAY_STRATEGY = "solace.messaging.receiver.persistent.replay.strategy"
""" Property constant defining the key for configuring the message replay strategy of the 
    :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`.
    
    The acceptable values for this property are

      * :py:const:`PERSISTENT_REPLAY_ALL<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_REPLAY_ALL>`
      * :py:const:`PERSISTENT_REPLAY_TIME_BASED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_REPLAY_TIME_BASED>`
      * :py:const:`PERSISTENT_REPLAY_ID_BASED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_REPLAY_ID_BASED>`
    
    This property-constant mapping can be used in a dictionary configuration
    object to configure replay strategy for a direct receiver through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to setting the replay strategey of a persistent receiver by
    :py:meth:`PersistentMessageReceiverBuilder.with_message_replay()`<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_replay>`.
"""

PERSISTENT_MESSAGE_REPLAY_STRATEGY_TIME_BASED_START_TIME = "solace.messaging.receiver.persistent.replay.timebased-start-time"
""" Property constant defining the key for configuring the message replay start time when
    :py:const:`PERSISTENT_REPLAY_TIME_BASED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_REPLAY_TIME_BASED>`
    replay strategy is configured for a
    :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`.
    
    The acceptable value for this property is a valid :py:class:`datetime.datetime` objects with or without
    timezone information.
    
    This property-constant mapping can be used in a dictionary configuration
    object to configure replay strategy for a persistent receiver through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to creating a
    :py:class:`solace.messaging.config.replay_strategy.TimeBasedReplay`
    to use in the persistent receiver builder method
    :py:meth:`PersistentMessageReceiverBuilder.with_message_replay()`<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_replay>`.
"""

PERSISTENT_MESSAGE_REPLAY_STRATEGY_ID_BASED_REPLICATION_GROUP_MESSAGE_ID =\
    "solace.messaging.receiver.persistent.replay.replication-group-message-id"
""" Property constant defining the key for configuring the Replication Group Message ID when
    :py:const:`PERSISTENT_REPLAY_ID_BASED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_REPLAY_ID_BASED>`
    replay strategy is configured for a
    :py:class:`solace.messaging.receiver.persistent_message_receiver.PersistentMessageReceiver`.
    
    The acceptable value for this property is a valid Replication Group Message Id in String format as returned by 
    :py:class:`solace.messaging.receiver.inbound_message.ReplicationGroupMessageId`
    
    This property-constant mapping can be used in a dictionary configuration
    object to configure replay strategy for a persistent receiver through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to creating a
    :py:class:`solace.messaging.config.replay_strategy.ReplicationGroupMessageIdReplay`
    to use in the persistent receiver builder method
    :py:meth:`PersistentMessageReceiverBuilder.with_message_replay()`<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_replay>`.
"""

PERSISTENT_MISSING_RESOURCE_CREATION_STRATEGY = "solace.messaging.receiver.persistent.missing-resource-creation-strategy"
""" Property constant defining the key for configuring the messing resource strategy. 
    If a remote resource (i.e. queue) is missing the API may optionaly create that object automatically. The valid
    values for this property are 
    :py:const:`PERSISTENT_RECEIVER_CREATE_ON_START_MISSING_RESOURCES<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_CREATE_ON_START_MISSING_RESOURCES>`
    and
    :py:const:`PERSISTENT_RECEIVER_DO_NOT_CREATE_MISSING_RESOURCES<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_DO_NOT_CREATE_MISSING_RESOURCES>`.
    
    This property-constant mapping can be used in a dictionary configuration object to
    configure the strategy for creating missing resources through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to the setting the missing
    resource creation strategy of a persistent message receiver by
    :py:meth:`PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_missing_resources_creation_strategy>`.
"""

PERSISTENT_MESSAGE_SELECTOR_QUERY = "solace.messaging.receiver.persistent.selector-query"
""" Property constant defining the key for configuring a message-selection query. 

    When a selector is applied then the receiver receives only
    messages whose headers and properties match the selector. A message selector cannot select
    messages on the basis of the content of the message body.
    
    An acceptable value for this property is a string formatted according to
    `Solace Selectors <https://docs.solace.com/Solace-JMS-API/Selectors.htm>`_.
    
    This property-constant mapping can be used in a dictionary
    configuration object to configure the message-selection query for a persistent message
    receiver through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to setting the message-selection
    query of a persistent message receiver by
    :py:meth:`PersistentMessageReceiverBuilder.with_message_selector()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_selector>`.
"""

PERSISTENT_MESSAGE_ACK_STRATEGY = "solace.messaging.receiver.persistent.ack.strategy"
""" Property constant defining the key for configuring the acknowledgement strategy for the message receiver.
    
    The acceptables values are
    :py:const:`PERSISTENT_RECEIVER_AUTO_ACK<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_AUTO_ACK>`
    :py:const:`PERSISTENT_RECEIVER_CLIENT_ACK<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_CLIENT_ACK>`.
    
    This property-constant mapping can be used in a dictionary configuration object to configure the
    strategy for acknowledging received messages through the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
    
    This method is an alternative to setting the strategy by
    :py:meth:`PersistentMessageReceiverBuilder.with_message_auto_acknowledgement()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_auto_acknowledgement>`.
    or by
    :py:meth:`PersistentMessageReceiverBuilder.with_message_client_acknowledgement()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_message_client_acknowledgement>`
    method.
"""

PERSISTENT_REQUIRED_MESSAGE_OUTCOME_SUPPORT = "solace.messaging.receiver.persistent.ack.required-message-outcome-support"
""" Property constant defining the key for configuring the settlement outcomes of the message receiver.
     
    The value can be a comma separated list of these constants, any combination:
    :py:const:`PERSISTENT_RECEIVER_OUTCOME_ACCEPTED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_OUTCOME_ACCEPTED>`
    :py:const:`PERSISTENT_RECEIVER_OUTCOME_FAILED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_OUTCOME_FAILED>`
    :py:const:`PERSISTENT_RECEIVER_OUTCOME_REJECTED<solace.messaging.config.solace_constants.receiver_constants.PERSISTENT_RECEIVER_OUTCOME_REJECTED>`
     
    This property-constant mapping can be used in a dictionary configuration object to configure the
    settlement outcomes with the
    :py:meth:`PersistentMessageReceiverBuilder.from_properties()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.from_properties>`
    method.
     
    This configuration method is an alternative to setting the outcomes by the
    :py:meth:`PersistentMessageReceiverBuilder.with_required_message_outcome_support()<solace.messaging.builder.persistent_message_receiver_builder.PersistentMessageReceiverBuilder.with_required_message_outcome_support>`.
     
    method.
"""
