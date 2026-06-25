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

# pylint: disable=line-too-long
""" This module contains the dictionary keys for :py:class:`solace.messaging.message.Message` properties."""

APPLICATION_MESSAGE_TYPE = "solace.messaging.message.application-message-type"
""" Property constant defining the key for configuring application message type. This value is set by applications
 and passed through the API and broker unmodified.

 The value set may be any string the application chooses.
 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_application_message_type()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_application_message_type>`.
 """

CLASS_OF_SERVICE = "solace.messaging.message.class-of-service"
"""Property constant defining the key for configuring the class of service of the message.
   Class of service is only relevant for Direct Messaging. Acceptable values for this property
   are 0, 1, or 2, where 0 represents the lowest class of service and 2 represents the highest class of service.
"""

ELIDING_ELIGIBLE = "solace.messaging.message.eliding-eligible"
"""Property constant defining the key for configuring whether the message is eligible for eliding."""

PRIORITY = "solace.messaging.message.priority"
"""Property constant defining the key for configuring message priority.
 The valid priority value range is 0-255 (0 is the lowest priority and 255 is the
 highest priority). A value of -1 indicates the priority is not set and a default priority value is used instead.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_priority()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_priority>`.
 """

SENDER_ID = "solace.messaging.message.sender-id"
"""Property constant defining the key for configuring the custom sender ID in the message header. The
 accepted values are string type, or None type. If a string is passed, the sender ID field will be set
 to that string. If None is passed, any previously set sender ID will be deleted. Note: passing None
 as the value of this property will not delete a sender ID which was automatically generated using the
 service property
 :py:const:`GENERATE_SENDER_ID<solace.messaging.config.solace_properties.service_properties.GENERATE_SENDER_ID>`.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_sender_id()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_sender_id>`.
"""

HTTP_CONTENT_TYPE = "solace.messaging.message.http-content"
"""Property constant defining the key for configuring HTTP content type header.  When published messages are consumed
 by HTTP clients, such as a clients using a REST API, the HTTP content type may need to be set.

 The accepted values are defined in RFC 2616, section-14-14.
 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_http_content_header()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_http_content_header>`.
 """

HTTP_CONTENT_ENCODING = "solace.messaging.message.http-encoding"
"""Property constant defining the key for configuring HTTP content-type encoding header.
 When published messages are consumed
 by HTTP clients, such as a clients using a REST API, the HTTP content encoding may need to be set.

 The accepted values are defined in RFC 2616, section-14.11.
 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_http_content_header()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_http_content_header()>`.
"""

CORRELATION_ID = "solace.messaging.message.correlation-id"
"""Property constant defining the key for configuring correlation ID.
 The correlation ID may be used by applications that need an end-to-end identifier for correlation. Such
 applications may be implementing their own proprietary request-reply pattern.

 When use :py:class:`solace.messaging.publisher.request_reply_message_publisher.RequestReplyMessagePublisher`
 the correlation ID is set by the API and any value set by the application is overwritten.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_correlation_id()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_correlation_id>`.
 """

PERSISTENT_TIME_TO_LIVE = "solace.messaging.message.persistent.time-to-live"
"""Property constant defining the key for configuring number of milliseconds before the message is discarded or moved to a
Dead Message Queue.

The value of 0 means the message never expires. The default value is 0.
This property is only valid for persistent messages.
"""

PERSISTENT_EXPIRATION = "solace.messaging.message.persistent.expiration"
"""Property constant defining the key for configuring the UTC time (Epoch time in milliseconds)
 when the message is considered expired. Setting this property has no effect if the TimeToLive
 is set in the same message.

 The expiration time is carried to clients that receive the message, unmodified and
 does not effect the life cycle of the message.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_expiration()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_expiration>`.
 """

PERSISTENT_DMQ_ELIGIBLE = "solace.messaging.message.persistent.dmq-eligible"
"""Property constant defining the key for configuring if message is eligible to be moved to a Dead Message Queue.
 The default value is ``True``.

 This property is only valid for persistent messages."""

PERSISTENT_ACK_IMMEDIATELY = "solace.messaging.message.persistent.ack-immediately"
"""Property constant defining the key to set the ack-immediately property.
 The broker should ACK this message immediately upon receipt when this is ''True''.

 The default value is ``False``.

 This property is only valid for persistent messages."""

SEQUENCE_NUMBER = "solace.messaging.message.persistent.sequence-number"
"""Property constant defining the key to set the message sequence number.
 If not set no sequence number is set on the message. The default value is not set.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_sequence_number()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_sequence_number>`.
 """

APPLICATION_MESSAGE_ID = "solace.messaging.message.application-message-id"
"""Property constant defining the key to set the message application id.
 If not set no application message id is set on the message.  The default value is not set.

 This property can also be set by building a message with
 :py:meth:`OutboundMessageBuilder.with_application_message_id()<solace.messaging.publisher.outbound_message.OutboundMessageBuilder.with_application_message_id>`.
 """
