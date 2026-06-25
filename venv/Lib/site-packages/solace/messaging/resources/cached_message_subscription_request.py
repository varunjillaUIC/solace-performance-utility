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

#  pylint: disable=line-too-long
"""
This module contains the factory and reader interfaces for
:py:class:`CachedMessageSubscriptionRequests<solace.messaging.resources.cached_message_subscription_request.CachedMessageSubscriptionRequest>`,
which are required for sending cache requests through a
:py:class:`DirectMessageReceiver<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver>`
by using the
:py:class:`ReceiverCacheRequests<solace.messaging.receiver.receiver_cache_requests.ReceiverCacheRequests>` interface.
"""

from abc import ABC, abstractmethod

from solace.messaging.config._sol_constants import SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FULFILL, \
    SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_QUEUE, SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU, \
    SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY, SOLCLIENT_SUBSCRIBE_FLAGS_REQUEST_CONFIRM, \
    SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY, MAX_SIGNED_THIRTY_TWO_BIT_INT
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._solace_utilities import is_value_out_of_range

class CachedMessageSubscriptionRequest(ABC):
    """
    This class provides constructors used to create cache request configurations.
    """

    @staticmethod
    def as_available(cache_name: str,
                     subscription: TopicSubscription,
                     cache_access_timeout: int,
                     max_cached_messages: int = 0,
                     cached_message_age: int = 0) -> 'CachedMessageSubscriptionRequest':
        """
            A factory method to create instances of a
            :py:class:`CachedMessageSubscriptionRequest<solace.messaging.resources.CachedMessageSubscriptionRequest>`
            to subscribe for a mix of live and cached messages matching specified topic
            subscription.

            Args:
                cache_name(str):          name of the Solace cache to retrieve from.
                subscription(TopicSubscription):        matching topic subscription.
                cache_access_timeout(int): Solace cache request timeout (in milliseconds). A valid cache_access_timeout
                    value ranges between 3000, and signed int 32 max. This value specifies a timer for the internal
                    requests that occur between this API and a Solace cache instance. A single call to
                    :py:meth:`request_cached()<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver.request_cached>`
                    can lead to one or more of these internal requests. As long as each of these internal requests
                    complete before the specified time-out, the timeout value is satisfied.
                max_cached_messages(int): The max number of messages expected to be received
                    from a Solace cache. A valid max_cached_messages value range between 0
                    and signed int 32 max, with 0 as an indicator for NO restrictions on a number of
                    messages. The default value is 0.
                cached_message_age(int): The maximum age (in seconds) of the messages to be
                    retrieved from a Solace cache. A valid cached_message_age value range
                    between 0 and signed int 32 max, with 0 as an indicator for NO restriction on a
                    message age. 0 is the default value

            Returns:
                CachedMessageSubscriptionRequest: an instance of a cached topic subscription used
                to subscribe for a mix of live and cached messages.
        """
        return _CachedMessageSubscriptionRequest(cache_name,
                                                 subscription,
                                                 max_cached_messages,
                                                 cached_message_age,
                                                 SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU | SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY,
                                                 SOLCLIENT_SUBSCRIBE_FLAGS_REQUEST_CONFIRM,
                                                 cache_access_timeout)

    #  pylint: disable=line-too-long
    @staticmethod
    def live_cancels_cached(cache_name: str,
                            subscription: TopicSubscription,
                            cache_access_timeout: int,
                            max_cached_messages: int = 0,
                            cached_message_age: int = 0) -> 'CachedMessageSubscriptionRequest':
        """
        A factory method to create instances of a
        :py:class:`CachedMessageSubscriptionRequest<solace.messaging.resources.cached_message_subscription_request.CachedMessageSubscriptionRequest>`
        to subscribe for latest messages.
        When no live messages are available, cached messages matching specified topic
        subscription considered latest, live messages otherwise.

        Args:
            cache_name(str): name of the Solace cache to retrieve from.
            subscription(TopicSubscription): matching topic subscription.
            cache_access_timeout(int): Solace cache request timeout (in milliseconds). A valid cache_access_timeout
                value ranges between 3000, and signed int 32 max. This value specifies a timer for the internal
                requests that occur between this API and a Solace cache instance. A single call to
                :py:meth:`request_cached()<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver.request_cached>`
                can lead to one or more of these internal requests. As long as each of these internal requests
                complete before the specified time-out, the timeout value is satisfied.
            max_cached_messages(int): The max number of messages expected to be received
                from a Solace cache. A valid max_cached_messages value range between 0
                and signed int 32 max, with 0 as an indicator for NO restrictions on a number
                of messages. The default value is 0.
            cached_message_age(int): The max age in seconds of the messages to be retrieved
                from a Solace cache. A valid cached_message_age value range between 0 and
                signed int 32 max, with 0 as an indicator for NO restrictions on message age. The
                default value is 0.

        Returns:
            CachedMessageSubscriptionRequest: an instance of a cached topic subscription used to subscribe for a latest messages.
        """
        return _CachedMessageSubscriptionRequest(cache_name,
                                                 subscription,
                                                 max_cached_messages,
                                                 cached_message_age,
                                                 SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FULFILL | SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY,
                                                 SOLCLIENT_SUBSCRIBE_FLAGS_REQUEST_CONFIRM,
                                                 cache_access_timeout)

    @staticmethod
    def cached_first(cache_name: str,
                     subscription: TopicSubscription,
                     cache_access_timeout: int,
                     max_cached_messages: int = 0,
                     cached_message_age: int = 0) -> 'CachedMessageSubscriptionRequest':
        """
        A factory method to create instances of a
        :py:class:`CachedMessageSubscriptionRequest<solace.messaging.resources.CachedMessageSubscriptionRequest>`
        to subscribe for cached messages when available, followed by live messages.
        Additional cached message filter properties such as max number of cached messages
        and age of a message from cache can be specified. Live messages will be queues
        until the Solace cache response is received. Queued live messages are delivered
        to the application after the cached messages are delivered.

        Args:
            cache_name(str): Name of the Solace cache to retrieve from.
            subscription(TopicSubscription): matching topic subscription.
            cache_access_timeout(int): Solace cache request timeout, in milliseconds. A valid cache_access_timeout
                value ranges between 3000, and signed int 32 max. This value specifies a timer for the internal
                requests that occur between this API and a Solace cache instance. A single call to
                :py:meth:`request_cached()<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver.request_cached>`
                can lead to one or more of these internal requests. As long as each of these internal requests
                complete before the specified time-out, the timeout value is satisfied.
            max_cached_messages(int): The max number of messages expected to be received from
                a Solace cache. A valid max_cached_messages value range between 0 and signed int 32 max,
                with 0 as an indicator for NO restrictions on a number of messages. The
                default value is 0.
            cached_message_age(int): The maximum age, in seconds, of the messages to be retrieved
                from a Solace cache. A valid cached_message_age value range between 0 and signed int 32 max,
                with 0 as an indicator for NO restriction on a message age. The default value is 0.

        Returns:
            CachedMessageSubscriptionRequest: An instance of a cached topic subscription used to
            subscribe for messages delivered from a cache, followed by live messages.
        """
        return _CachedMessageSubscriptionRequest(cache_name,
                                                 subscription,
                                                 max_cached_messages,
                                                 cached_message_age,
                                                 SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_QUEUE | SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY,
                                                 SOLCLIENT_SUBSCRIBE_FLAGS_REQUEST_CONFIRM,
                                                 cache_access_timeout)

    #  pylint: disable=line-too-long
    @staticmethod
    def cached_only(cache_name: str,
                    subscription: TopicSubscription,
                    cache_access_timeout: int,
                    max_cached_messages: int = 0,
                    cached_message_age: int = 0) -> 'CachedMessageSubscriptionRequest':
        """
        A factory method to create instances of a
        :py:class:`CachedMessageSubscriptionRequest<solace.messaging.resources.cached_message_subscription_request.CachedMessageSubscriptionRequest>`
        to subscribe for cached messages when available, no live messages are expected to be
        received. Additional cached message filter properties such as max number of cached
        messages and age of a message from cache can be specified.

        Note cache_only requests are limited to be used with subscribers without live data
        subscriptions. When used with matching live data subscriptions, cached message will be
        delivered for both the cache outcome and live subscription leading to duplicate
        message delivery. When needing cache data when live data subscriptions are already
        present use other CachedMessageSubscriptionRequest request types such as
        cached_first or as_available.

        Args:
            cache_name(str): Name of Solace cache to retrieve from.
            subscription(TopicSubscription): Matching Topic Subscription.
            cache_access_timeout(int): Solace cache request timeout, in milliseconds. A valid cache_access_timeout
                value ranges between 3000, and signed int 32 max. This value specifies a timer for the internal
                requests that occur between this API and a Solace cache instance. A single call to
                :py:meth:`request_cached()<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver.request_cached>`
                can lead to one or more of these internal requests. As long as each of these internal requests
                complete before the specified time-out, the timeout value is satisfied.
            max_cached_messages(int): The max number of messages expected to be received
                from a Solace cache. A valid max_cached_messages value range between 0
                and signed int 32 max, with 0 as an indicator for NO restrictions on number of
                messages. The default value is 0.
            cached_message_age(int): The maximum age, in seconds, of the messages to be
                retrieved from a Solace cache. A valid cached_message_age value range
                between 0 and signed int 32 max, with 0 as an indicator for NO restrictions on
                age of message. The default value is 0.

        Returns:
            CachedMessageSubscriptionRequest: An instance of a cached topic subscription used to
            subscribe for messages delivered from a cache.
        """
        return _CachedMessageSubscriptionRequest(cache_name,
                                                 subscription,
                                                 max_cached_messages,
                                                 cached_message_age,
                                                 SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY | SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU,
                                                 SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY,
                                                 cache_access_timeout)

    @abstractmethod
    def get_cache_name(self) -> str:
        """
        Retrieves the name of the cache.

        Returns:
            (str): The name of the cache.
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Retrieves the name of the topic subscription.

        Returns:
            (str): The name of the topic subscription.
        """


#  pylint: disable=missing-function-docstring, missing-class-docstring, too-many-arguments, too-many-instance-attributes
class _CachedMessageSubscriptionRequest(CachedMessageSubscriptionRequest):
    def __init__(self,
                 cache_name: str,
                 topic_subscription: TopicSubscription,
                 max_number_messages: int,
                 message_age: int,
                 cache_flags: int,
                 subscribe_flags: int,
                 cache_access_timeout: int):

        # Validate parameters
        _ = is_value_out_of_range(0, MAX_SIGNED_THIRTY_TWO_BIT_INT, max_number_messages)
        _ = is_value_out_of_range(0, MAX_SIGNED_THIRTY_TWO_BIT_INT, message_age)
        _ = is_value_out_of_range(3000, MAX_SIGNED_THIRTY_TWO_BIT_INT, cache_access_timeout)

        # Note:  for cache_flags the exact type is hexadecimal values
        self.__cache_name = cache_name
        self.__topic_subscription = topic_subscription
        self.__max_number_messages = max_number_messages
        self.__max_message_age = message_age
        self.__cache_flags = cache_flags
        self.__subscribe_flags = subscribe_flags
        self.__cache_access_timeout = cache_access_timeout

    @property
    def cache_name(self):
        return self.__cache_name

    @property
    def topic_subscription(self):
        return self.__topic_subscription

    @property
    def max_number_messages(self):
        return self.__max_number_messages

    @property
    def max_message_age(self):
        return self.__max_message_age

    @property
    def cache_flags(self):
        return self.__cache_flags

    @property
    def cache_access_timeout(self):
        return self.__cache_access_timeout

    @property
    def subscribe_flags(self):
        return self.__subscribe_flags

    def get_cache_name(self) -> str:
        return self.__cache_name

    def get_name(self) -> str:
        return self.topic_subscription.get_name()
