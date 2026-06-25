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
Solace Messaging API for Python

This package contains a full-featured Python API for developing Python applications.  The API follows
the builder pattern.  Everything begins with a ``MessagingService.builder()`` call that returns a new
``MessagingServiceClientBuilder`` object.  When you use a ``MessagingService`` instance, applications can:

- configure the :py:class:`solace.messaging.messaging_service.MessagingService` object
- create a :py:class:`solace.messaging.messaging_service.MessagingService` object

The ``Messaging Service`` in turn can be used to:

- connect the :py:class:`solace.messaging.messaging_service.MessagingService`
- create a :py:class:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder`:
  for building ``MessagePublishers``
- create a :py:class:`solace.messaging.builder.message_receiver_builder.MessageReceiverBuilder`
  for building ``MessageReceivers``
- create a :py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder` for building ``Messages``
  to publish
 """
# pylint: disable=missing-class-docstring
import logging


class _SolaceServiceAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        id_info = kwargs.pop('id_info', self.extra['id_info'])
        return '[%s] %s' % (id_info, msg), kwargs  # pylint: disable=consider-using-f-string
                                                   # We disable consider-using-f-string because
                                                   # this will be used as a part of the
                                                   # logger, and this way will be more performant
