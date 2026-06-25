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


"""This module contains dictionary keys for :py:class:`solace.messaging.messaging_service.MessagingService`
properties. """  # pylint: disable=trailing-whitespace, line-too-long

VPN_NAME = "solace.messaging.service.vpn-name"
"""Property constant defining the key for configuring the message vpn name. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
"""

GENERATE_SENDER_ID = "solace.messaging.service.generate-sender-id"
"""Property constant defining the key for enabling sender-id auto-generation. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  When enabled, GENERATE_SENDER_ID applies to all messages published by 
  :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` that exist on the messaging service. 
  Each message published will include the SenderId property. The application_id set in 
  :py:meth:`MessagingServiceClientBuilder.build()<solace.messaging.messaging_service.MessagingServiceClientBuilder.build>`
  is used as the SenderId.
"""

GENERATE_RECEIVE_TIMESTAMPS = "solace.messaging.service.generate-receive-timestamps"
"""Property constant defining the key for enabling receive timestamps in received messages. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  When enabled, GENERATE_RECEIVE_TIMESTAMPS applies to all messages received by
  :py:class:`solace.messaging.receiver.message_receiver.MessageReceiver` that exist on the messaging service. Each 
  message received will include a receive timestamp that reflects the time the message was received from the
  Solace event broker by the underlying native API.
"""

GENERATE_SEND_TIMESTAMPS = "solace.messaging.service.generate-send-timestamps"
"""Property constant defining the key for generating send timestamps in published messages. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  When enabled, GENERATE_SEND_TIMESTAMPS applies to all messages published by
  :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` that exist on the messaging service. Each 
  message published includes a timestamp that reflects the time that the message was queued for transmission to
  the Solace event broker by the underlying native API.
"""
PAYLOAD_COMPRESSION_LEVEL = "solace.messaging.service.payload-compression-level"
"""Property constant defining the key for payload compression.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary.

  Valid values for the payload compression level to be applied to the payload of a message published by a client are 0-9.

  Value meanings:
  0 - "disable payload compression" (the default)
  1 - least amount of compression and the fastest data throughput
  9 - most compression and slowest data throughput

  The payload compression value should be adjusted according to particular network requirements and the performance required.

  Note: Please ensure that both publishers and consumers are updated to support payload compression before enabling this property.
  In the case where a publisher compresses the payload and a consumer does not support payload decompression, the untouched compressed message
  will be received which can lead to potential issues within the consuming application. Therefore, the consumer would either need to update
  to a newer version of the API or the user would need to handle the decompression on the receiving side in their own application.
  If a publishing application is able to send a compressed message, the broker's treatment of message-type will vary depending on the protocol.
  Lastly, do not enable payload compression when sending cache-requests. Applications that are sending cache-requests and receiving cache-responses
  may end up getting compressed messages that they are not able to handle.
"""
