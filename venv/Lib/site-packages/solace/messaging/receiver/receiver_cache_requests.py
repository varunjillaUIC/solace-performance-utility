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
This module contains an abstract class that is inherited by the
:py:class:`DirectMessageReceiver<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver>`
so that this type of receiver may send cache requests.
"""

from abc import ABC, abstractmethod

class ReceiverCacheRequests(ABC):
    """
    This abstract class provides the interface for requesting cached messages from a Solace Cache instance.
    """

    #  pylint: disable=line-too-long
    @abstractmethod
    def request_cached(self,
                       cached_message_subscription_request: 'CachedMessageSubscriptionRequest',
                       cache_request_id: int,
                       completion_listener: 'CacheRequestOutcomeListener'):
        """
        Requests messages from a broker which were previously cached using Solace Cache. Responses to this request are
        processed by the given :py:class:`CacheRequestOutcomeListener<solace.messaging.utils.cache_request_outcome_listener.CacheRequestOutcomeListener>`.
        The `cache_request_id` parameter is used for correlating requests with responses. It is the application's
        responsibility to guarantee that only unique integers are provided to this field, so as to avoid collisions.

        Args:
            cached_message_subscription_request(CachedMessageSubscriptionRequest): Request
                for cached messages matching specified subscription and other fulfillment
                criteria.
            cache_request_id(int): request identifier which can be used for response
                callback correlation purposes, this value needs to be unique for the time
                of the application execution. A valid cache_request_id is within the range of 0 to Unsigned 64 int max.
                This value will be returned on a
                :py:meth:`on_completion()<solace.messaging.utils.correlating_completion_listener.CacheRequestOutcomeListener.on_completion>`
                callback of the
                :py:class:`CacheRequestOutcomeListener<solace.messaging.utils.correlating_completion_listener.CacheRequestOutcomeListener>`.
                The same value will be returned.
            completion_listener(CacheRequestOutcomeListener): Request completion listener
                to be notified when cache request is completed.

        Raises:
            PubSubPlusClientException: If the operation could not be performed.
            IllegalStateException: If the service is not connected or the receiver is not running.
        """
