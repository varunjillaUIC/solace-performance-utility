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

"""
This module contains:
    * all utility tools for interoperating with the core library cache features;
    * additional tooling that is used to process cache requests and responses, such as the _CacheEventThread
"""

import ctypes

import solace
from solace.messaging.config._solace_message_constants import GENERATED_CACHE_CANCELLATION_MESSAGE
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_INCOMPLETE, _SOLCLIENTCACHEEVENT, \
    SOLCLIENT_FAIL
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.utils._solace_utilities import _ThreadingUtil

class CacheRequestReceiverUserContext(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """
    This structure is used to provide a user context(user_p) to CCSMP cache functions.
    """
    _fields_ = [
        ("cache_session_id", ctypes.c_int64) # The id associated with the CacheRequester instance.
                                             # We consider the field to be a int64 because the Python docs say that
                                             # id() returns an int, and we want to to accomodate a 64 bit number,
                                             # although the Python docs do not specify the bit width of the returned
                                             # int. If it is found that this number is larger than a 64 bit int, then
                                             # this would likely need be changed, and the way that the id is
                                             # interpreted from CCSMP when it is returned through the callback
                                             # would need to be changed as well. Currently, the default
                                             # is to read is as an int, so no special reading is required at the
                                             # moment.
    ]

class SolCacheEventCallbackInfo(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """ Conforms to solCache_eventCallbackInfo """
    _fields_ = [
        ("cache_event", ctypes.c_int), # The cache event variant
        ("topic", ctypes.c_char_p), # The topic subscription relevant to this cache event
        ("return_code", ctypes.c_int), # The return code of the operation
        ("sub_code", ctypes.c_int), # The subcode of the operation
        ("cache_request_id", ctypes.c_uint64) # The cache request ID relevant to this cache event
    ]

solCache_eventCallbackInfo_pt = ctypes.POINTER(SolCacheEventCallbackInfo)
_cache_event_callback_func_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p,
                                                   solCache_eventCallbackInfo_pt, ctypes.c_void_p)
_cache_event_callback_func_type.restype = None
_cache_event_callback_func_type.argtypes = [ctypes.c_void_p, solCache_eventCallbackInfo_pt, ctypes.c_void_p]

class _SolCacheEventInfo:
    # pylint: disable=too-many-arguments
    def __init__(self, cache_event, topic, return_code, sub_code, cache_request_id, cache_session_id):
        self.__cache_event = cache_event
        self.__topic = topic
        self.__return_code = return_code
        self.__sub_code = sub_code
        self.__cache_request_id = cache_request_id
        self.__cache_session_id = cache_session_id

    @staticmethod
    def from_solcache_struct(struct: 'SolCacheEventCallbackInfo', user_context):
        """
        This constructor method converts a SolCacheEventCallbackInfo object into a SolCacheEventInfo object. The
        benefit of this conversion is having a purely Python object to use througout the API, instead of using an
        interop object.

        Args:
            struct(SolCacheEventCallbackInfo): The struct to convert.

        Returns:
            SolCacheEventCallbackInfo: The converted event info object.
        """
        return _SolCacheEventInfo(_SOLCLIENTCACHEEVENT(struct.cache_event),
                                  struct.topic.decode(),
                                  struct.return_code,
                                  struct.sub_code,
                                  struct.cache_request_id,
                                  user_context.cache_session_id)

    def as_error_string(self)-> str:
        """
        This method returns a string representation of the _SolCacheEventInfo object.

        Returns:
            str: The error string.
        """
        return_code_str = solace.CORE_LIB.solClient_returnCodeToString(self.__return_code).decode()
        sub_code_str = solace.CORE_LIB.solClient_subCodeToString(self.__sub_code).decode()
        return f"_SolCacheEventInfo:\n" \
               f"Cache Event Type: {self.__cache_event}({self.__cache_event.value})\n" \
               f"Topic: {self.__topic}\n" \
               f"Return Code: {return_code_str}({self.__return_code})\n" \
               f"Sub Code: {sub_code_str}({self.__sub_code})\n" \
               f"Cache Request ID: {self.__cache_request_id}\n" \
               f"Cache Session ID: {self.__cache_session_id}"

    def needs_exception(self) -> bool:
        """
        This method returns a boolean indicating whether or not an exception needs to be generated for this event.

        Returns:
            bool: Whether an exception message needs to be generated.
        """
        return self.__return_code != SOLCLIENT_OK and \
            self.__sub_code != SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_SUSPECT_DATA.value and \
            self.__sub_code != SolClientSubCode.SOLCLIENT_SUBCODE_CACHE_NO_DATA.value

    @property
    def cache_event(self):  # pylint: disable=missing-function-docstring
        return self.__cache_event

    @property
    def topic(self):  # pylint: disable=missing-function-docstring
        return self.__topic

    @property
    def return_code(self):  # pylint: disable=missing-function-docstring
        return self.__return_code

    @property
    def sub_code(self):  # pylint: disable=missing-function-docstring
        return self.__sub_code

    @property
    def cache_request_id(self):  # pylint: disable=missing-function-docstring
        return self.__cache_request_id

    @property
    def cache_session_id(self):  # pylint: disable=missing-function-docstring
        return self.__cache_session_id

class _CacheResponseDispatcher:
    def __init__(self, owner_logger: 'logging.Logger'):
        self.adapter = owner_logger
        self._executor = None
        self._is_running = False

    def start(self):
        """
        This method starts the dispatcher.
        """
        self._executor = \
            _ThreadingUtil.create_serialized_dispatcher(f"cache_response_executor_thread-{str(id(self))}")
        self._is_running = True

    def shutdown(self):
        """
        This method shuts down the dispatcher.
        """
        if self._is_running:
            self._executor.shutdown()
            self._is_running = False

    def submit(self, handler, *args, **kwargs):
        """
        This method submits the given items to the dispatcher executor.
        """
        self._executor.submit(handler, *args, **kwargs)

    @property
    def is_running(self):
        """
        This property accessor allows a state check of whether or not the dispatcher is running.
        """
        return self._is_running

def generate_cancelled_request_tuple(cache_requester: '_SolaceCacheRequester') \
    -> ('_SolCacheEventInfo', 'PubSubPlusClientError'):
    """
    This method generates the event info and exception for a cache request cancelled by the Python API.

    Args:
        cache_requester(_SolaceCacheRequester): The configuration to read from.

    Returns:
        SolCacheEventCallbackInfo: The event info associated with the cancellation.
        PubSubPlusClientError: The exception associated with the cancellation.
    """
    cache_event_info = _SolCacheEventInfo(_SOLCLIENTCACHEEVENT. \
                                             SOLCACHE_EVENT_REQUEST_COMPLETED_NOTICE.value,
                                         cache_requester.topic_subscription.get_name(),
                                         SOLCLIENT_INCOMPLETE,
                                         SolClientSubCode. \
                                             SOLCLIENT_SUBCODE_CACHE_REQUEST_CANCELLED.value,
                                         cache_requester.cache_request_id,
                                         cache_requester.id)

    # We can't pull an exception from the cache event queue because it is generated, but since we are deliberately
    # cancelling the cache request, we can reliably generate the information for the exception message.
    error = PubSubPlusClientError(GENERATED_CACHE_CANCELLATION_MESSAGE)

    return cache_event_info, error


def generate_failed_cache_event(cache_requester: '_SolaceCacheRequester') -> 'SolCacheEventInfo':
    """
    This function returns a cache event formatted for failing to send the cache request from the Python API.

    Args:
        cache_requester(_SolaceCacheRequester): The configuration to read from.

    Returns:
        _SolCacheEventInfo: The formatted cache event info.
    """
    # NOTE:
    # SOL-42602(2023-09-22):
    # Currently, this method is only used when an error is encountered while trying to send a cache request
    # (see _on_publishable_send_error in _direct_message_receiver.py for details). Based on the implementation
    # at this time, the only error that should be picked up on that code path is a PubSubPlusCoreClientError.
    # while that error would contain a stringified version of the error info from the core library, and the
    # error subcode accessible as an attribute, the return code of the error is not accessible through an
    # attribute. The _SolCacheEventInfo that is generated below requires information from the _CacheRequester,
    # as well as an error return code and error subcode. Therefore, if the _SolCacheEventInfo were to be
    # informed by a PubSubPlusCoreClientError, we could copy the subcode, but could not copy the return code.
    # Instead, we would have to generate the return code which could cause confusion since the two codes might
    # not match a possible combination of codes.
    #
    # The alternative, which is currently implemented, is to generate both the return code and subcode, so that
    # the combination is at least guaranteed to be consistent, and since all options require some form of generation
    # anyways. The implemented option is permissible because of several implementation details:
    #
    #
    # 1. As previously stated, this function is called from only one place, which cannot pass the return code
    # without significant change to several interfaces, including the Publishable interface, and would also break
    # the systemic pattern of error handling in the API.
    #
    #
    # 2. The return code and subcode of a _SolCacheEventInfo, in the current implementation and when directly
    # accessed, are only used to determine which CacheRequestOutcome to pass to the application
    # (see process_cache_event in _direct_message_receiver.py for details).
    #
    # 2.a. It is coincidence of the architecture that any of the subcodes and return codes that can be returned as a
    # part of a failure to send a cache request are presented to the application as the same
    # CacheRequestOutcome.FAILED. Without this coincidence, if the API were required to discern between different
    # kinds of send failures, the current implementation would not work.
    #
    # 2.b. Another function in this file, generate_exception_from_cache_event, could hypothetically be used
    # to generate an error from a _SolCacheEventInfo, which itself had been generated from this function. This
    # would be erroneous since the return code and subcode contained within the generated error are presented to the
    # application, and provide useful information. However, currently the generate_exception_from_cache_event function
    # is only used in the _cache_event_callback method (see _direct_message_receiver.py for details) to generate an
    # error from a _SolCacheEventInfo, which itself has been generated from a core library SolCacheEventInfo struct.
    #
    # TL;DR: There isn't really a TL;DR, because you need to read all of the above cases and ensure that either they
    # do not change; or, if any of them do, that this function is reviewed and changed as necessary.

    return _SolCacheEventInfo(_SOLCLIENTCACHEEVENT. \
                                  SOLCACHE_EVENT_REQUEST_COMPLETED_NOTICE.value,
                              cache_requester.topic_subscription.get_name(),
                              SOLCLIENT_FAIL,
                              SolClientSubCode. \
                                  SOLCLIENT_SUBCODE_INTERNAL_ERROR.value,
                              cache_requester.cache_request_id,
                              cache_requester.id)


def generate_exception_from_cache_event(cache_event_info: '_SolCacheEventInfo'):
    """
    This method generates an exception based on the contents of a _SolCacheEventInfo object.

    Args:
        cache_event_info(_SolaceCacheEventInfo): The information object to read from.

    Returns:
        None: If the return code in the cache_event_info argument is SOLCLIENT_OK.
        PubSubPlusClientException: If the return code in the cache_event_info argument is not SOLCLIENT_OK.
    """
    if cache_event_info.needs_exception():
        error = PubSubPlusClientError(cache_event_info.as_error_string(), cache_event_info.sub_code)
        return error
    return None


def create_cache_session(props, session_p, cache_session_p):  # pylint: disable=missing-function-docstring
    # Create a cache session object that is used in subsequent cacheRequests on the
    # Session. Multiple cache session objects may be created on a Session. Each must be
    # destroyed when the application no longer requires the object.
    #
    # @param props                 Array of name/value string pair pointers to configure
    #                              cache session properties.
    # @param opaqueSession_p       Session in which the cache session is to be created.
    # @param opaqueCacheSession_p  Pointer to the location to contain the opaque cache session pointer
    #                              on return.
    # @returns                     ::SOLCLIENT_OK on success. ::SOLCLIENT_FAIL on failure.
    return solace.CORE_LIB.solClient_session_createCacheSession(ctypes.cast(props, ctypes.POINTER(ctypes.c_char_p)),
                                                                session_p, ctypes.byref(cache_session_p))


def cache_session_destroy(cache_session_p):  # pylint: disable=missing-function-docstring
    #  Destroy a cache session object.
    # This function is thread safe and can be called from any thread. When this function is invoked:
    # @li All blocked synchronous cache requests return immediately with SOLCLIENT_INCOMPLETE return code
    # and SOLCLIENT_SUBCODE_PARAM_NULL_PTR subcode.
    # @li Live messages that have been queued (if any) will be delivered.
    #
    # @param opaqueCacheSession_p  Pointer to opaque cache session pointer that was returned
    #                              when the cache session was created.
    # @returns ::SOLCLIENT_OK, ::SOLCLIENT_FAIL
    return solace.CORE_LIB.solClient_cacheSession_destroy(ctypes.byref(cache_session_p))


def cancel_cache_requests(cache_session_p) -> int:
    """
    This method cancels the pending cache requests on the given cache session, using the core library.

    Returns:
        int: The core library return code of the operation.
    """
    # Possible return codes are SOLCLIENT_OK, SOLCLIENT_FAIL
    # * Synchronous cache requests return immediately with SOLCLIENT_INCOMPLETE, and
    #       subcode SOLCLIENT_SUBCODE_CACHE_REQUEST_CANCELLED.
    # * Asynchronous cache requests have associated cache events generated and given to the application callback.
    #       These events will include a SOLCACHE_EVENT_REQUEST_COMPLETED_NOTICE and a subcode of
    #       SOLCLIENT_SUBCODE_CACHE_REQUEST_CANCELLED.
    # * Live messages that have been queued will be delivered
    # * The asoociated cache session is still valid to use.
    return solace.CORE_LIB.solClient_cacheSession_cancelCacheRequests(cache_session_p)



#  pylint: disable=missing-function-docstring,too-many-arguments
def send_cache_request(cache_session_p, topic_subscription: 'TopicSubscription',
                       cache_request_id, event_callback_p, user_context: 'CacheRequestReceiverContext',
                       cache_flags, subscribe_flags,
                       dispatch_info):  # pylint: disable=missing-function-docstring,too-many-arguments
    # Send a cache request message. If the cache request flag
    # ::SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY is set, this function returns ::SOLCLIENT_IN_PROGRESS
    # immediately upon successful buffering of the message for transmission.
    # Otherwise this function waits for the cache response to be fulfilled
    # according to the LIVEDATA handling options. When the function waits for the cache response the
    # cache event callback is not invoked.
    #
    # Irrespective of the cache request flag, ::SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY, cache requests
    # may be flow controlled if the underlying transport is flow controlled. The transport is considered flow
    # controlled if
    # the library is unable to write to the transport device (for example, the TCP socket is full), or if there
    # are more than
    # 1000 session requests (solClient_session_sendRequest() + solClient_cacheSession_sendCacheRequest())
    # outstanding. This causes solClient_cacheSession_sendCacheRequest() to block if the session property,
    # ::SOLCLIENT_SESSION_PROP_SEND_BLOCKING is enabled. If ::SOLCLIENT_SESSION_PROP_SEND_BLOCKING is
    # disabled and it is not possible to write the cache request to the underlying transport,
    # SOLCLIENT_WOULD_BLOCK is returned.
    #
    # Cached messages received in response to the cache request are delivered to the application
    # through the usual receive message callback as the messages arrive. This function returns when all
    # cache responses have been received, or the request is either completed by live data
    # (::SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FULFILL) or by a timeout. If, and only
    # if, ::SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY
    # is set, the cache request callback is invoked when any of these terminating conditions occurs.
    #
    # @param opaqueCacheSession_p An opaque cache session pointer returned when the cache session was
    #                        created.
    # @param topic_p         The string that contains the topic being requested from
    #                        the cache.
    # @param cacheRequestId The 64-bit integer returned to the application in the cache request
    #                        response; it is available in every cached message returned.
    # @param callback_p      A callback pointer for an asynchronous reply to cache requests.
    # @param user_p          A user pointer to return with the callback.
    # @param cacheflags      \ref cacherequestflags "cacheRequest flags" to modify the cache request behavior.
    # @param subscribeFlags  Subscription flags (::SOLCLIENT_SUBSCRIBE_FLAGS_RX_ALL_DELIVER_TO_ONE)
    # @param message_callback_p A callback to handle received cached data messages.
    # @returns ::SOLCLIENT_OK, ::SOLCLIENT_NOT_READY, ::SOLCLIENT_FAIL, ::SOLCLIENT_INCOMPLETE,
    # ::SOLCLIENT_IN_PROGRESS, ::SOLCLIENT_WOULD_BLOCK
    # @subcodes
    # This function can return ::SOLCLIENT_FAIL for any of the following reasons:
    # @li ::SOLCLIENT_SUBCODE_CACHE_INVALID_SESSION - the underlying session in which the cacheSession
    #                        was created has been destroyed.
    # @li ::SOLCLIENT_SUBCODE_INVALID_TOPIC_SYNTAX  - the topic is invalid.
    # @li ::SOLCLIENT_SUBCODE_TOPIC_TOO_LARGE       - the topic exceeds the maximum length.
    #
    # When the ::SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY is set in cacheFlags, the function returns
    # ::SOLCLIENT_IN_PROGRESS and the subsequent callback indicates the
    # final status of the cache request.
    #
    # Otherwise the return code indicates the status of the cache request.
    # ::SOLCLIENT_OK is returned when the cache request completes successfully and valid data is delivered.
    # The ::solClient_subCode is never
    # set when ::SOLCLIENT_OK is returned.
    #
    # ::SOLCLIENT_INCOMPLETE may be returned if the cacheRequest or initial
    # subscription request is sent but not completed successfully.
    # @li ::SOLCLIENT_SUBCODE_CACHE_TIMEOUT         - the timeout specified by
    #     ::SOLCLIENT_CACHESESSION_PROP_REQUESTREPLY_TIMEOUT_MS expired.
    # @li ::SOLCLIENT_SUBCODE_PROTOCOL_ERROR        - the cache response is malformed.
    # @li ::SOLCLIENT_SUBCODE_CACHE_ERROR_RESPONSE  - the cache responded with an error response.
    # @li ::SOLCLIENT_SUBCODE_CACHE_SUSPECT_DATA    - at least one suspect message was received
    #                                                 in response.
    # @li ::SOLCLIENT_SUBCODE_CACHE_NO_DATA         - the cache request completed successfully with no
    #                                                 suspect responses, but no data matching the cache
    #                                                 request was found.
    # @li ::SOLCLIENT_SUBCODE_CACHE_REQUEST_CANCELLED - the cache request has been cancelled.
    # @li ::SOLCLIENT_SUBCODE_PARAM_NULL_PTR          - the cache session has been destroyed.
    # @li ::SOLCLIENT_SUBCODE_CACHE_INVALID_SESSION   - the underlying session in which the cacheSession
    #                        was created has been destroyed.
    return solace.CORE_LIB.solClient_cacheSession_sendCacheRequestWithDispatch(cache_session_p,
                                                                               ctypes.c_char_p(topic_subscription \
                                                                                   .get_name().encode()),
                                                                               ctypes.c_uint64(cache_request_id),
                                                                               event_callback_p,
                                                                               user_context,
                                                                               ctypes.c_uint32(cache_flags),
                                                                               ctypes.c_uint32(subscribe_flags),
                                                                               ctypes.byref(dispatch_info))
