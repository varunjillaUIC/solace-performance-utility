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


# module contains the class and functions which actually make the call to ccsmp #pylint:disable=missing-module-docstring
# this is an internal utility module, used by implementors of the API. # pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import ctypes
from ctypes import c_char_p, sizeof, byref, POINTER
from functools import reduce

import solace
from solace.messaging.config._sol_constants import MAX_SESSION_PROPS


def session_create(arr, context_p, session_p, session_func_info):
    #  Creates a new Session within a specified Context. The session properties
    #  are supplied as an array of name/value pointer pairs, where the name and value are both strings.
    #  Only configuration property names starting with "SESSION_" are processed; other property names
    #  are ignored. Any values not supplied are set to default values.
    #  When the Session is created, an opaque Session pointer is returned to the caller, and this value
    #  is then used for any Session-level operations (for example, sending a message).
    #  The passed-in structure functInfo_p provides information on the message receive callback
    #  function and the Session event function which the application has provided for this Session.
    #  Both of these callbacks are mandatory. The message receive callback is invoked for each
    #  received message on this Session. The Session event callback is invoked when Session events
    #  occur, such as the Session going up or down. Both callbacks are invoked in the context
    #  of the Context thread to which this Session belongs.
    #  Note that the property values are stored internally in the API and the caller does not have to maintain
    #  the props array or the strings that are pointed to after this call completes.
    # When processing the property list, the API
    #  will not modify any of the strings pointed to by props.
    # Args:
    #     arr:  An array of name/value string pair pointers to configure session properties.
    #     context_p: The Context in which the Session is to be created.
    #     session_p: An opaque Session pointer is returned that refers to the created Session.
    #     session_func_info:  A pointer to a structure that provides information on callback
    #     functions for events and received messages.
    # Returns:
    # SOLCLIENT_OK, SOLCLIENT_FAIL
    return solace.CORE_LIB.solClient_session_create(ctypes.cast(arr, POINTER(c_char_p)), context_p, byref(session_p),
                                                    byref(session_func_info), sizeof(session_func_info))


def session_connect(session_p):
    # Connects the specified Session. A Session connection can be carried out in a blocking or
    #  non-blocking mode, depending upon the Session property
    #  SOLCLIENT_SESSION_PROP_CONNECT_BLOCKING.
    #  In blocking mode, the calling thread is blocked until either the Session connection attempt
    #  succeeds or is determined to have failed. If the connection succeeds, SOLCLIENT_OK is
    #  returned. If the Session could not connect, SOLCLIENT_NOT_READY is returned.
    #  In non-blocking mode, SOLCLIENT_IN_PROGRESS is returned upon a successful Session connect
    #  request, and the connection attempt proceeds in the background.
    #  In both non-blocking and blocking mode, a Session event is generated for the Session:
    #  SOLCLIENT_SESSION_EVENT_UP_NOTICE, if the Session was connected successfully; or
    #  SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR, if the Session failed to connect.
    #  For blocking mode, the Session event is issued before the call to
    #  solClient_session_connect() returns. For non-blocking mode, the timing is undefined (that is,
    #  it could occur before or after the call returns, but it will typically be after).
    #  A Session connection timer, controlled by the Session property
    #  SOLCLIENT_SESSION_PROP_CONNECT_TIMEOUT_MS, controls the maximum amount of
    #  time a Session connect attempt lasts for. If this amount time is exceeded,
    #  a SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR event is issued for the Session.
    #  If there is an error when solClient_session_connect() is invoked, SOLCLIENT_FAIL
    #  is returned, and a Session event is not subsequently issued. Therefore, the caller must
    #  check for a return code of SOLCLIENT_FAIL if it has logic that depends upon a subsequent
    #  Session event to be issued.
    #  For a non-blocking Session connect invocation, if the Session connect attempt eventually
    #  fails, the last error information to indicate the reason for the failure cannot be
    #  determined by the calling thread, rather it must be discovered through the Session event
    #  callback (and solClient_getLastErrorInfo can be called in the Session event callback
    #  to get further information).
    #  For a blocking Session connect invocation, if the Session connect attempt does not
    #  return SOLCLIENT_OK, then the calling thread can determine the failure reason by immediately
    #  calling solClient_getLastErrorInfo.
    # Args:
    #     session_p:  The opaque Session that was returned when Session was created
    # Returns:
    # SOLCLIENT_OK (blocking mode only), SOLCLIENT_NOT_READY (blocking mode only),
    # SOLCLIENT_IN_PROGRESS (non-blocking mode only) or SOLCLIENT_FAIL.

    return solace.CORE_LIB.solClient_session_connect(session_p)


def session_disconnect(session_p):
    # Disconnects the specified Session. Once disconnected, topics/subscriptions
    #  can no longer be added or removed from the Session, messages can no longer be received for
    #  the Session, and messages cannot be sent to the Session. The Session definition remains,
    #  and the Session can be connected again (using solClient_session_connect()).
    #  When solClient_session_disconnect() is called, if there are buffered messages waiting to
    #  be transmitted for the Session (for example, because the send socket is full), the caller is
    #  blocked until all buffered data has been written to the send socket. Note the following: 1) This
    #  is done regardless of whether the Session has been configured for a blocking or non-blocking
    #  send operation (see SOLCLIENT_SESSION_PROP_SEND_BLOCKING).
    #  2) A call to solClient_session_destroy(), solClient_context_destroy(), or solClient_cleanup()
    #  while a Session is connected (without first disconnecting the Session explicitly through a
    #  call to solClient_session_disconnect()) discards any buffered messages.
    # Args:
    #     session_p:The opaque Session returned when Session was created.
    # Returns:
    #     SOLCLIENT_OK, SOLCLIENT_FAIL
    return solace.CORE_LIB.solClient_session_disconnect(session_p)


def session_destroy(session_p):
    # Destroys a previously created Session. Upon return, the opaque Session pointer
    #  is set to NULL. If the Session being destroyed is still in a connected state,
    #  any buffered messages which have not been sent yet are
    #  discarded. If the application wants to ensure that any buffered messages are
    #  first sent, solClient_session_disconnect() must be
    #  called before solClient_sesssion_destroy().
    #
    #  This operation must not be performed in a Session callback
    #  for the Session being destroyed. This includes all Flows on the Session,
    #  as well as the application supplied event and data callback functions (
    #  solClient_session_createFuncInfo) functions.
    # Args:
    #     session_p: An opaque Session that was returned when the Session was created.
    # Returns:
    #     SOLCLIENT_OK, SOLCLIENT_FAIL
    return solace.CORE_LIB.solClient_session_destroy(byref(session_p))


def session_force_failure(session_p):
    # function to force failure the session
    # Args:
    #     session_p: session pointer
    # Returns:
    #     returns the force disconnected status
    return solace.CORE_LIB._solClient_session_forceFailure(session_p, 0)


def context_destroy(context_p):
    # Destroys a previously created Context. On return, the opaque Context pointer
    #  is set to NULL. This operation must not be performed in a Context callback
    #  for the Context being destroyed. This includes all Sessions on the Context, timers on
    #  the Context, and application-supplied register file descriptor (see
    #  SolClient_context_createFuncInfo) functions.
    # Args:
    #     context_p: An opaque Context returned when Context was created.
    # Returns:
    #     SOLCLIENT_OK, SOLCLIENT_FAIL
    return solace.CORE_LIB.solClient_context_destroy(ctypes.byref(context_p))


def prepare_array(config):
    props_list = list(reduce(lambda x, y: x + y, config.items()))
    props_list = [e.encode() for e in props_list]
    props_list.append(c_char_p(None))  # add NULL at the end of array
    return (c_char_p * (2 * MAX_SESSION_PROPS + 1))(*props_list)
