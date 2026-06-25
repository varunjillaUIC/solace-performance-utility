# solace-messaging-python-client
#
# Copyright 2023-2025 Solace Corporation. All rights reserved.
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
An interface for constant property values to define user message properties that have a special
reserved meaning or behaviour.
"""

QUEUE_PARTITION_KEY = "JMSXGroupID"

"""
A standard property key that clients should use if they want to group messages. It is used to
specify a partition queue name, when supported by a Solace event broker. Expected value
is UTF-8 encoded up to 255 bytes long string. This constant can be passed as the property
string to any generic property setter on the OutboundMessageBuilder that can take properties from
:py:mod:`message_properties<solace.messaging.config.solace_properties.message_properties>` as a parameter, such as
:py:meth:`with_property()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_property>`.
"""
