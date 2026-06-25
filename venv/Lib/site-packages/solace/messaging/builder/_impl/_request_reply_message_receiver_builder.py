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

# pylint: disable=missing-function-docstring

"""
module contains  request reply message receiver builder.
 Applications that requires request and reply messages must first create a  RequestReplyMessageReceiverBuilder
 using the :py:meth:`MessagingService.create_request_reply_message_receiver_builder(
 )<solace.messaging.messaging_service.MessagingService.create_request_reply_message_receiver_builder>`

 The RequestReplyMessageReceiverBuilder then creates one or more  RequestReplyMessageReceiver as necessary.
"""
import logging

from solace.messaging.builder._impl._message_receiver_builder import _MessageReceiverBuilder
from solace.messaging.builder.request_reply_message_receiver_builder import RequestReplyMessageReceiverBuilder
from solace.messaging.receiver._impl._request_reply_message_receiver import _RequestReplyMessageReceiver
from solace.messaging.resources.share_name import ShareName, _ShareName
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._solace_utilities import is_type_matches

logger = logging.getLogger('solace.messaging.receiver')


class _RequestReplyMessageReceiverBuilder(_MessageReceiverBuilder, RequestReplyMessageReceiverBuilder):
    """Implementation class or the RequestReplyMessageReceiverBuilder"""

    def from_properties(self, configuration: dict) -> 'RequestReplyMessageReceiverBuilder':
        pass

    def __init__(self, messaging_service: 'MessagingService'):
        self._messaging_service = messaging_service
        super().__init__(messaging_service)
        self._topic_dict = {}

    @property
    def messaging_service(self):
        return self._messaging_service

    @property
    def topic_dict(self):
        return self._topic_dict

    def build(self, request_topic_subscription: TopicSubscription,
              share_name: ShareName = None) -> '_RequestReplyMessageReceiver':
        is_type_matches(request_topic_subscription, TopicSubscription, logger=logger)
        self._topic_dict = {'subscriptions': [request_topic_subscription.get_name()]}

        if share_name:
            is_type_matches(share_name, ShareName, logger=logger)
            name = share_name.get_name()
            share_name = _ShareName(name)
            share_name.validate()
            self._topic_dict['group_name'] = name
        return _RequestReplyMessageReceiver(self)
