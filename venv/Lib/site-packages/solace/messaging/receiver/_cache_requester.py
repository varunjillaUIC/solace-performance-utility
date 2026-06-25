# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#  # pylint: disable=missing-module-docstring
# Module implements internal class publishable.  OutboundMessage are carried in
# Publishable objects that contain the message and the destination

"""
This module contains the API object required for the network actor used to send cache requests in the
:py:class:`DirectMessageReceiver<solace.messaging.receiver.direct_message_receiver.DirectMessageReceiver>`.
"""

import ctypes
import logging

from solace.messaging.config._sol_constants import SOLCLIENT_CACHESESSION_PROP_CACHE_NAME, \
    SOLCLIENT_CACHESESSION_PROP_MAX_AGE, SOLCLIENT_CACHESESSION_PROP_MAX_MSGS, \
    SOLCLIENT_CACHESESSION_REQUESTREPLY_TIMEOUT_MS, SOLCLIENT_FAIL, SOLCLIENT_IN_PROGRESS, \
    SOLCLIENT_WOULD_BLOCK, SOLCLIENT_OK, SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY, \
    SOLCLIENT_DISPATCH_TYPE_CALLBACK
from solace.messaging.config._solace_message_constants import CCSMP_INFO_SUB_CODE, CCSMP_SUB_CODE, \
    UNABLE_TO_SEND_CACHE_REQUEST, CACHE_SESSION_DESTROYED, TOPIC_SYNTAX_INVALID, TOPIC_NAME_TOO_LONG, \
    CACHE_ALREADY_IN_PROGRESS
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.core._core_api_utility import prepare_array
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.receiver._impl import _solcache_utility
from solace.messaging.receiver._inbound_message_utility import SUBSCRIPTION_DISPATCH_FILTER_BY_CACHE_REQUEST_ID, \
    SolClientMsgDispatchCacheRequestIdFilterInfo, SolClientNativeRxMsgDispatchFuncInfo, topic_unsubscribe_with_dispatch
from solace.messaging.utils._solace_utilities import get_last_error_info, generate_exception_from_last_error_info

class _SolaceCacheRequester:  # pylint: disable=too-many-instance-attributes
    """
    This class contains the methods required for managing cache requests.
    """
    def __init__(self, cache_request: '_CachedMessageSubscriptionRequest', cache_request_id: int,
                 receiver: '_DirectMessageReceiver'):
        """
        Extracts the relevantconfiguration from the given _CachedMessageSubscriptionRequest, and prepares it for
        sending the cache request.

        Args:
            cache_request(_CachedMessageSubscriptionRequest): The cache request configuration to use.
        """
        # Attributes given through the constructor
        self.__cache_request_id = cache_request_id
        self.__event_callback_p = receiver._event_callback_p
        self.__session_p = receiver._messaging_service.session_pointer
        self.__cache_session_id = id(self)
        self.__user_context = \
            ctypes.py_object(_solcache_utility.CacheRequestReceiverUserContext(self.__cache_session_id))
        self.__adapter: '_SolaceServiceAdapter' = receiver.adapter

        # Attributes which are taken from the _CachedMessageSubscriptionRequest configuration
        self.__cache_name = cache_request.cache_name
        self.__topic_subscription = cache_request.topic_subscription
        self.__max_number_messages = cache_request.max_number_messages
        self.__max_message_age = cache_request.max_message_age
        self.__cache_flags = cache_request.cache_flags
        self.__subscribe_flags = cache_request.subscribe_flags
        self.__cache_access_timeout = cache_request.cache_access_timeout

        # disaptch subscription attritbute
        # precalculate if the subscription is local dispatch only
        # this allows for the cache event callback thread to quickly check if it needs to remove subscription on
        # cache complete
        self.__is_local_dispatch = \
            (cache_request.subscribe_flags & SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY) == \
            SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY
        if self.__is_local_dispatch:
            self.__filter_info = SolClientMsgDispatchCacheRequestIdFilterInfo(
                ctypes.c_uint64(self.__cache_request_id),
                (receiver._dispatch_info.dispatch_type, receiver._dispatch_info.callback_p,
                 receiver._dispatch_info.user_p, receiver._dispatch_info.rffu ) )
            self.__dispatch_info = SolClientNativeRxMsgDispatchFuncInfo(
                ctypes.c_uint32(SOLCLIENT_DISPATCH_TYPE_CALLBACK),
                SUBSCRIPTION_DISPATCH_FILTER_BY_CACHE_REQUEST_ID,
                ctypes.cast(ctypes.byref(self.__filter_info), ctypes.c_void_p),
                ctypes.c_void_p(None) )
        else:
            self.__dispatch_info = receiver._dispatch_info

        # Attributes which require further configuration
        self.__cache_session_p = ctypes.c_void_p()

        # Attributes which require formatting
        self.__prepared_cache_session_props = \
            prepare_array({SOLCLIENT_CACHESESSION_PROP_CACHE_NAME: self.__cache_name,
                           SOLCLIENT_CACHESESSION_PROP_MAX_AGE: str(self.__max_message_age),
                           SOLCLIENT_CACHESESSION_PROP_MAX_MSGS: str(self.__max_number_messages),
                           SOLCLIENT_CACHESESSION_REQUESTREPLY_TIMEOUT_MS: str(self.__cache_access_timeout)})

    def setup(self):
        """
        This method creates the cache session for this _CacheRequester instance.

        Raises:
            PubSubPlusCoreClientError: If this instance was unable to create the cache session.
        """
        return_code = _solcache_utility.create_cache_session(self.__prepared_cache_session_props,
                                                             self.__session_p,
                                                             self.__cache_session_p)
        # The associated solClient_session_createCacheSession CCSMP method only returns only SOLCLIENT_OK or
        # SOLCLIENT_FAIL
        if return_code == SOLCLIENT_FAIL:
            error: 'PubSubPlusCoreClientError' = \
                get_last_error_info(return_code=return_code,
                                    caller_description='_CacheRequester->__init__',
                                    exception_message=f"Failed to create the cache session with cache request ID " \
                                                      f"{self.__cache_request_id}.")
            self.__adapter.warning(error)  # pragma: no cover # Due to core error scenario
            raise error  # pragma: no cover # Due to core error scenario

    def cleanup(self):
        """
        This method cleans up the resources for this _CacheRequester instance. This involves:
            * destroying the cache session
            * removing the _CacheRequester entry from the receiver dictionary

        Raises:
            PubSubPlusCoreClientError: If this instance was unable to destroy the cache session.
        """
        return_code = _solcache_utility.cache_session_destroy(self.__cache_session_p)
        if return_code != SOLCLIENT_OK:
            error: 'PubSubPlusCoreClientError' = \
                get_last_error_info(return_code=return_code,
                                    caller_description='_CacheRequester->cleanup',
                                    exception_message=f"Failed to destroy cache session with cache request " \
                                                      f"ID {self.__cache_request_id}")
            self.__adapter.warning(error)  # pragma: no cover # Due to core error scenario
        if self.__is_local_dispatch:
            # when using local dispatch only flags on cache request complete we can remove the subscription
            #
            # FFC: Consider moving to context thread due to performance impact of not calling from context thread
            return_code = topic_unsubscribe_with_dispatch(
                self.__session_p,
                self.__topic_subscription.get_name(),
                self.__dispatch_info,
                self.__subscribe_flags)
            if return_code != SOLCLIENT_OK:
                error: 'PubSubPlusCoreClientError' = \
                    get_last_error_info(return_code=return_code,
                                        caller_description='_CacheRequester->cleanup',
                                        exception_message=f"Failed to unsubscribe from local dispatch the cache " \
                                                          f"session with cache request ID {self.__cache_request_id} " \
                                                          f"and subscription {self.__topic_subscription}.")
                self.__adapter.warning(error)  # pragma: no cover # Due to core error scenario

    def cancel_pending_cache_requests(self):
        """
        This method cancels all pending cache requests submitted by this _CacheRequester instance.

        Raises:
            PubSubPlusCoreClientError: If this instance was unable to cancel the cache requests.
        """
        return_code =_solcache_utility.cancel_cache_requests(self.__cache_session_p)
        if return_code != SOLCLIENT_OK:
            error: 'PubSubPlusCoreClientError' = \
                get_last_error_info(return_code=return_code,
                                   caller_description='_CacheRequester->cancel_pending_cache_requests',
                                   exception_message=f"Failed to cancel cache request with cache request " \
                                                     f"ID {self.__cache_request_id}")
            self.__adapter.warning(error)
            raise error

    def send_cache_request(self) -> int:
        """
        This method sends the cache request that has been configured for this _CacheRequester instance.

        Returns:
            int: The return code of the operation.

        Raises:
            PubSubPlusClientError: If there was an error in sending the cache request.
        """
        return_code = _solcache_utility.send_cache_request(self.__cache_session_p,
                                                           self.__topic_subscription,
                                                           self.__cache_request_id,
                                                           self.__event_callback_p,
                                                           self.__user_context,
                                                           self.__cache_flags,
                                                           self.__subscribe_flags,
                                                           self.__dispatch_info)
        # SOLCLIENT_IN_PROGRESS and SOLCLIENT_WOULD_BLOCK are expected return codes, in the case
        # that CCSMP has sent the async cache request and returned, or in the case that CCSMP is
        # busy and can't send the async cache request right now.
        #
        # SOLCLIENT_OK is not expected in this case, since that return code is expected only when a
        # synchronous cache request is sent. At the time of this design, the Python API intends to only
        # support async cache requests.
        if return_code in [SOLCLIENT_IN_PROGRESS, SOLCLIENT_WOULD_BLOCK]:
            return return_code
        core_exception_msg = last_error_info(status_code=return_code,
                                             caller_desc='On cache request send')
        exception_message = UNABLE_TO_SEND_CACHE_REQUEST
        if core_exception_msg[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_INVALID_SESSION:
            exception_message += CACHE_SESSION_DESTROYED
        elif core_exception_msg[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_INVALID_TOPIC_SYNTAX:
            exception_message += TOPIC_SYNTAX_INVALID
        elif core_exception_msg[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_TOPIC_TOO_LARGE:
            exception_message += TOPIC_NAME_TOO_LONG
        elif core_exception_msg[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_ALREADY_IN_PROGRESS:
            exception_message += CACHE_ALREADY_IN_PROGRESS

        exception: 'PubSubPlusCoreClientError' = \
            generate_exception_from_last_error_info(core_exception_msg, exception_message)
        if self.__adapter.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.__adapter.debug('\nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                                 core_exception_msg[CCSMP_INFO_SUB_CODE],
                                 core_exception_msg["error_info_contents"],
                                 core_exception_msg[CCSMP_SUB_CODE],
                                 core_exception_msg["return_code"])

        raise exception

    @property
    def cache_request_id(self):
        """
        This property accessor allows other parts of the API to access the cache request ID associated with this
        _SolaceCacheRequester instance.
        """
        return self.__cache_request_id

    @property
    def cache_session_p(self):
        """
        This property accessor allows other parts of the API to access the cache session pointer associated
        with this _SolaceCacheRequester instance.
        """
        return self.__cache_session_p

    @property
    def topic_subscription(self):
        """
        This property accessor allows other parts of the API to access the cache topic subscription associated with
        this _SolaceCacheRequester instance.
        """
        return self.__topic_subscription

    @property
    def id(self):  # pylint: disable=invalid-name
        """
        This property accessor allows other parts of the API to access the indexable ID associated with this
        _SolaceCacheRequester instance.
        """
        return self.__cache_session_id
