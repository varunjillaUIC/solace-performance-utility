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


# contains return codes for underlying c api
# pylint: disable=missing-module-docstring, trailing-whitespace

import enum

MAX_UNSIGNED_SIXTY_FOUR_BIT_INT = 2**64 - 1
MAX_SIGNED_SIXTY_FOUR_BIT_INT = 2**63 - 1
MAX_UNSIGNED_THIRTY_TWO_BIT_INT = 2**32 - 1
MAX_SIGNED_THIRTY_TWO_BIT_INT = 2**31 - 1

### Begin Distributed Tracing
class TracingContextType(enum.Enum):
    """
    This class represents the kinds of context type which can be stored in a Solace message.
    """
    TRANSPORT_CONTEXT = 0
    CREATION_CONTEXT = 1

class TracingInjectionStandardType(enum.Enum):
    """
    This class represents the kinds of injection standards which can be used when injecting context data into a Solace
    message.
    """
    INJECTION_STANDARD_SMF = 0
    INJECTION_STANDARD_W3C = 1

TRACE_ID_SIZE = 16
SPAN_ID_SIZE = 8
### End Distributed Tracing

SOLCLIENT_NOT_SET_PRIORITY_VALUE = -1
# The default log filter
SOLCLIENT_LOG_DEFAULT_FILTER = 5

# Normal return - the message is destroyed by the API upon return.
SOLCLIENT_CALLBACK_OK = 0

# The API call was successful.
SOLCLIENT_SUB_CODE_OK = 0

# The API call was successful.
SOLCLIENT_OK = 0

# The API call would block but non-blocking was requested.
SOLCLIENT_WOULD_BLOCK = 1

# An API call is in progress (non-blocking mode).
SOLCLIENT_IN_PROGRESS = 2

# The API could not complete as an object is not ready
SOLCLIENT_NOT_READY = 3

# (for example the Session is not connected).
# A getNext on a structured container returned End-of-Stream.
SOLCLIENT_EOS = 4

# A get for a named field in a MAP was not found in the MAP.
SOLCLIENT_NOT_FOUND = 5

# solClient_context_processEventsWait returns this if wait
SOLCLIENT_NOEVENT = 6

# The API call completed some but not all of the requested function.
SOLCLIENT_INCOMPLETE = 7

# solClient_transactedSession_commit returns this when the
SOLCLIENT_ROLLBACK = 8

# The API call failed.
SOLCLIENT_FAIL = -1

# Delivery Mode Types
SOLCLIENT_DELIVERY_MODE_DIRECT = 0  # Send a Direct message (0x00).
SOLCLIENT_DELIVERY_MODE_PERSISTENT = 16  # Send a Persistent message (0x10).
SOLCLIENT_DELIVERY_MODE_NONPERSISTENT = 32  # Send a Non-Persistent message (0x20).

SOLCLIENT_NULL_DESTINATION = -1
SOLCLIENT_TOPIC_DESTINATION = 0
SOLCLIENT_QUEUE_DESTINATION = 1
SOLCLIENT_TOPIC_TEMP_DESTINATION = 2
SOLCLIENT_QUEUE_TEMP_DESTINATION = 3

# Callback on the dispatch function immediately when a message arrives
SOLCLIENT_DISPATCH_TYPE_CALLBACK = 1

# The subscribe/unsubscribe call blocks until a confirmation is received.
SOLCLIENT_SUBSCRIBE_FLAGS_WAITFORCONFIRM = 0x02

# This flag indicates the subscription should only be added to
SOLCLIENT_SUBSCRIBE_FLAGS_LOCAL_DISPATCH_ONLY = 0x08

# Requests a confirmation for the subscribe/unsubscribe operation.
SOLCLIENT_SUBSCRIBE_FLAGS_REQUEST_CONFIRM = 0x10

# The application is keeping the rxMsg and it must not be released or reused by the API
SOLCLIENT_CALLBACK_TAKE_MSG = 1

MAX_SESSION_PROPS = 60
MAX_RETRY_INTERVAL_MS = 60000
DEFAULT_RECONNECT_RETRIES = "3"  # must be string value
DEFAULT_RECONNECT_RETRY_INTERVAL_TIMER_MS = 3000

# Authentication Scheme
SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE = "AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE"
SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_BASIC = "AUTHENTICATION_SCHEME_BASIC"
SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_GSS_KRB = "AUTHENTICATION_SCHEME_GSS_KRB"
SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_OAUTH2 = "AUTHENTICATION_SCHEME_OAUTH2"

SOLCLIENT_SESSION_PROP_DEFAULT_COMPRESSION_LEVEL = 0  # The default compression level (no compression)

# The Session client name that is used during client login to create a unique Session.
SOLCLIENT_SESSION_PROP_CLIENT_NAME = "SESSION_CLIENT_NAME"

# A read-only informational string providing information about the application,
# such as the name of operating system user that is running the application,
# the hostname, and the PID of the application.
SOLCLIENT_SESSION_PROP_USER_ID = "SESSION_USER_ID"

# The maximum number of bytes that the length of a CCSMP session property can be.
SOLCLIENT_SESSION_PROP_MAX_SIZE = 255

NATIVE_ENCODING = 'utf-8'

# The value used to enable the property
SOLCLIENT_PROP_ENABLE_VAL = "1"

# The value used to disable the property
SOLCLIENT_PROP_DISABLE_VAL = "0"
ENCODING_TYPE = "utf-8"

# The Session is established.
SOLCLIENT_SESSION_EVENT_UP_NOTICE = 0

# The Session was established and then went down.
SOLCLIENT_SESSION_EVENT_DOWN_ERROR = 1

# The Session attempted to connect but was unsuccessful.
SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR = 2

# The appliance rejected a published message.
SOLCLIENT_SESSION_EVENT_REJECTED_MSG_ERROR = 3

# The appliance rejected a subscription (add or remove).
SOLCLIENT_SESSION_EVENT_SUBSCRIPTION_ERROR = 4

# The API discarded a received message that exceeded the Session buffer size.
SOLCLIENT_SESSION_EVENT_RX_MSG_TOO_BIG_ERROR = 5

# The oldest transmitted Persistent/Non-Persistent message that has been acknowledged.
SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT = 6

# Deprecated
# solClient_session_startAssuredPublishing. The AD Handshake (that is Guaranteed Delivery handshake) has completed
# for the publisher and Guaranteed messages can be sent.
SOLCLIENT_SESSION_EVENT_ASSURED_PUBLISHING_UP = 7

# Deprecated
# solClient_session_startAssuredPublishing. The appliance rejected the AD Handshake to start Guaranteed publishing.
# Use SOLCLIENT_SESSION_EVENT_ASSURED_DELIVERY_DOWN instead.
SOLCLIENT_SESSION_EVENT_ASSURED_CONNECT_FAILED = 8

# Guaranteed Delivery publishing is not available.
# The guaranteed delivery capability on the session has been disabled by some action on the appliance.
SOLCLIENT_SESSION_EVENT_ASSURED_DELIVERY_DOWN = 8

# The Topic Endpoint unsubscribe command failed.
SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_ERROR = 9

# Deprecated name: SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_ERROR is preferred
SOLCLIENT_SESSION_EVENT_DTE_UNSUBSCRIBE_ERROR = SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_ERROR

# The Topic Endpoint unsubscribe completed.
SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_OK = 10

# Deprecated name: SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_OK is preferred
SOLCLIENT_SESSION_EVENT_DTE_UNSUBSCRIBE_OK = SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_OK

# The send is no longer blocked.
SOLCLIENT_SESSION_EVENT_CAN_SEND = 11

# The Session has gone down and an automatic reconnect attempt is in progress.
SOLCLIENT_SESSION_EVENT_RECONNECTING_NOTICE = 12

# The automatic reconnect of the Session was successful and the Session was established again.
SOLCLIENT_SESSION_EVENT_RECONNECTED_NOTICE = 13

# The endpoint create/delete command failed.
SOLCLIENT_SESSION_EVENT_PROVISION_ERROR = 14

# The endpoint create/delete command completed.
SOLCLIENT_SESSION_EVENT_PROVISION_OK = 15

# The subscribe or unsubscribe operation has succeeded.
SOLCLIENT_SESSION_EVENT_SUBSCRIPTION_OK = 16

# The appliance's Virtual Router Name changed during a reconnect operation.
# This could render existing queues or temporary topics invalid.
SOLCLIENT_SESSION_EVENT_VIRTUAL_ROUTER_NAME_CHANGED = 17

# The session property modification completed.
SOLCLIENT_SESSION_EVENT_MODIFYPROP_OK = 18

# The session property modification failed.
SOLCLIENT_SESSION_EVENT_MODIFYPROP_FAIL = 19

# After successfully reconnecting a disconnected
# session the SDK received an unknown publisher flow name response when reconnecting the GD publisher flow.
# If configured to auto-retry (See SOLCLIENT_SESSION_PROP_GD_RECONNECT_FAIL_ACTION.) this event is generated
# to indicate how many unacknowledged messages are retransmitted on success. As the publisher state has been lost
# on failover receiving this event may indicate that some messages have been duplicated in the system.
SOLCLIENT_SESSION_EVENT_REPUBLISH_UNACKED_MESSAGES = 20

SOLCLIENT_SENT_STATS = 'SOLCLIENT_STATS_TX_NUM_STATS'
SOLCLIENT_RECEIVED_STATS = 'SOLCLIENT_STATS_RX_NUM_STATS'

# solClient_msg_dumpExt mode flags
SOLCLIENT_MSGDUMP_FULL = 1  # Display the entire message
SOLCLIENT_MSGDUMP_BRIEF = 0  # Display only the length of the binary attachment, XML attachment, and user property map

DEFAULT_BUFFER_SIZE = 10000
DEFAULT_BUFFER_MULTIPLIER = 3

CTYPES_UINT32_MAX = 2**32 - 1

INTERNAL_PYTHON_STATS = ['RECEIVED_MESSAGES_TERMINATION_DISCARDED',
                         'PUBLISH_MESSAGES_TERMINATION_DISCARDED',
                         'RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED',
                         'INTERNAL_DISCARD_NOTIFICATIONS']  # Added for Internal Python metrics

class _SOLCLIENTSTATSTX(enum.Enum):
    #  Transmit statistics (64-bit counters). Index into array of transmit statistics equivalent to solClient_stats_tx.
    SOLCLIENT_STATS_TX_TOTAL_DATA_BYTES = 0  # The number of data bytes transmitted in total.
    SOLCLIENT_STATS_TX_BYTES = SOLCLIENT_STATS_TX_TOTAL_DATA_BYTES  # Deprecated name; ::
    # SOLCLIENT_STATS_TX_TOTAL_DATA_BYTES is preferred
    SOLCLIENT_STATS_TX_TOTAL_DATA_MSGS = 1  # The number of data messages transmitted in total.
    SOLCLIENT_STATS_TX_MSGS = SOLCLIENT_STATS_TX_TOTAL_DATA_MSGS  # Deprecated name; SOLCLIENT_
    # STATS_TX_TOTAL_DATA_MSGS is preferred
    SOLCLIENT_STATS_TX_WOULD_BLOCK = 2  # The number of messages not accepted due to would block (non-blocking only).
    SOLCLIENT_STATS_TX_SOCKET_FULL = 3  # The number of times the socket was full when send done (data buffered).
    SOLCLIENT_STATS_TX_DIRECT_BYTES = 4  # The number of bytes transmitted in Direct messages.
    SOLCLIENT_STATS_TX_DIRECT_MSGS = 5  # The number of Direct messages transmitted.
    SOLCLIENT_STATS_TX_PERSISTENT_BYTES = 6  # The number of bytes transmitted in Persistent messages.
    SOLCLIENT_STATS_TX_NONPERSISTENT_BYTES = 7  # The number of bytes transmitted in Non-Persistent messages.
    SOLCLIENT_STATS_TX_PERSISTENT_MSGS = 8  # The number of Persistent messages transmitted.
    SOLCLIENT_STATS_TX_NONPERSISTENT_MSGS = 9  # The number of Non-Persistent messages transmitted.
    SOLCLIENT_STATS_TX_PERSISTENT_REDELIVERED = 10  # The number of Persistent messages redelivered.
    SOLCLIENT_STATS_TX_NONPERSISTENT_REDELIVERED = 11  # The number of Non-Persistent messages redelivered.
    SOLCLIENT_STATS_TX_PERSISTENT_BYTES_REDELIVERED = 12  # The number of bytes redelivered in Persistent messages.
    SOLCLIENT_STATS_TX_NONPERSISTENT_BYTES_REDELIVERED = 13  # The number of bytes redelivered in
    # Non-Persistent messages.
    SOLCLIENT_STATS_TX_ACKS_RXED = 14  # The number of acknowledgments received.
    SOLCLIENT_STATS_TX_WINDOW_CLOSE = 15  # The number of times the transmit window closed.
    SOLCLIENT_STATS_TX_ACK_TIMEOUT = 16  # The number of times the acknowledgment timer expired.
    SOLCLIENT_STATS_TX_CTL_MSGS = 17  # The number of control (non-data) messages transmitted.
    SOLCLIENT_STATS_TX_CTL_BYTES = 18  # The number of bytes transmitted in control (non-data) messages.
    SOLCLIENT_STATS_TX_COMPRESSED_BYTES = 19  # The number of bytes transmitted after compression.
    SOLCLIENT_STATS_TX_TOTAL_CONNECTION_ATTEMPTS = 20  # The total number of TCP connections attempted by
    # this Session.
    SOLCLIENT_STATS_TX_REQUEST_SENT = 21  # The request messages sent.
    SOLCLIENT_STATS_TX_REQUEST_TIMEOUT = 22  # The request messages sent that did not receive a reply due to timeout.
    SOLCLIENT_STATS_TX_CACHEREQUEST_SENT = 23  # The cache requests sent.
    SOLCLIENT_STATS_TX_GUARANTEED_MSGS_SENT_CONFIRMED = 24  # Guaranteed messages (Persistent/Non-Persistent)
    # published that have been acknowledged.
    SOLCLIENT_STATS_TX_DISCARD_NO_MATCH = 25  # When the IPC add-on is in use  the counter of messages
    # discarded due to no subscription match with connected peers
    SOLCLIENT_STATS_TX_DISCARD_CHANNEL_ERROR = 26  # Messages discarded due to channel failure
    SOLCLIENT_STATS_TX_BLOCKED_ON_SEND = 27  # The number of times Session blocked on socket
    # full (blocking only) occurred.
    SOLCLIENT_STATS_TX_NUM_STATS = 28  # The size of transmit stats array.


class _SOLCLIENTSTATSRX(enum.Enum):
    # Receive statistics (64-bit counters). Index into array of receive statistics equivalent of solClient_stats_rx
    SOLCLIENT_STATS_RX_DIRECT_BYTES = 0  # The number of bytes received.
    SOLCLIENT_STATS_RX_BYTES = SOLCLIENT_STATS_RX_DIRECT_BYTES  # Deprecated name
    # SOLCLIENT_STATS_RX_DIRECT_BYTES is preferred
    SOLCLIENT_STATS_RX_DIRECT_MSGS = 1  # The number of messages received.
    SOLCLIENT_STATS_RX_MSGS = SOLCLIENT_STATS_RX_DIRECT_MSGS  # Deprecated name
    # SOLCLIENT_STATS_RX_DIRECT_MSGS is preferred.
    SOLCLIENT_STATS_RX_READS = 2  # The number of non-empty reads.
    SOLCLIENT_STATS_RX_DISCARD_IND = 3  # The number of receive messages with discard indication set.
    SOLCLIENT_STATS_RX_DISCARD_SMF_UNKNOWN_ELEMENT = 4  # The number of messages discarded due to the presence of
    # an unknown element or unknown protocol in the Solace Message Format (SMF) header.
    SOLCLIENT_STATS_RX_DISCARD_MSG_HDR_ERROR = SOLCLIENT_STATS_RX_DISCARD_SMF_UNKNOWN_ELEMENT  # Deprecated  use
    # the more accurately named SOLCLIENT_STATS_RX_DISCARD_SMF_UNKNOWN_ELEMENT instead.
    SOLCLIENT_STATS_RX_DISCARD_MSG_TOO_BIG = 5  # The number of messages discarded due to msg too large.
    SOLCLIENT_STATS_RX_ACKED = 6  # The number of acknowledgments sent for Guaranteed messages.
    SOLCLIENT_STATS_RX_DISCARD_DUPLICATE = 7  # The number of Guaranteed messages dropped for being duplicates.
    SOLCLIENT_STATS_RX_DISCARD_NO_MATCHING_FLOW = 8  # The number of Guaranteed messages discarded due to no match on
    # the flowId.
    SOLCLIENT_STATS_RX_DISCARD_OUTOFORDER = 9  # The number of Guaranteed messages discarded for
    # being received out of order.
    SOLCLIENT_STATS_RX_PERSISTENT_BYTES = 10  # The number of Persistent bytes received on the Flow. On the Session
    # it is the total number of Persistent bytes received across all Flows.
    SOLCLIENT_STATS_RX_PERSISTENT_MSGS = 11  # The number of Persistent messages received on the Flow.
    # On the Session  it is the total number of Persistent messages received across all Flows.
    SOLCLIENT_STATS_RX_NONPERSISTENT_BYTES = 12  # The number of Persistent bytes received on the Flow.
    # On the Session  it is the total number of Persistent bytes received across all Flows.
    SOLCLIENT_STATS_RX_NONPERSISTENT_MSGS = 13  # The number of Persistent messages received on the Flow.
    # On the Session  it is the total number of Persistent messages received across all Flows.
    SOLCLIENT_STATS_RX_CTL_MSGS = 14  # The number of control (non-data) messages received.
    SOLCLIENT_STATS_RX_CTL_BYTES = 15  # The number of bytes received in control (non-data) messages.
    SOLCLIENT_STATS_RX_TOTAL_DATA_BYTES = 16  # The total number of data bytes received.
    SOLCLIENT_STATS_RX_TOTAL_DATA_MSGS = 17  # The total number of data messages received.
    SOLCLIENT_STATS_RX_COMPRESSED_BYTES = 18  # The number of bytes received before decompression.
    SOLCLIENT_STATS_RX_REPLY_MSG = 19  # The reply messages received.
    SOLCLIENT_STATS_RX_REPLY_MSG_DISCARD = 20  # The reply messages (including cache request response) discarded due
    # to errors in response format or no outstanding request.
    SOLCLIENT_STATS_RX_CACHEREQUEST_OK_RESPONSE = 21  # Cache requests completed OK.
    SOLCLIENT_STATS_RX_CACHEREQUEST_FULFILL_DATA = 22  # Cache requests fulfilled by live data.
    SOLCLIENT_STATS_RX_CACHEREQUEST_ERROR_RESPONSE = 23  # Cache requests failed due to solCache error response.
    SOLCLIENT_STATS_RX_CACHEREQUEST_DISCARD_RESPONSE = 24  # Cache request response discarded due to errors in
    # response format or no outstanding cache request.
    SOLCLIENT_STATS_RX_CACHEMSG = 25  # Cached messages delivered to application.
    SOLCLIENT_STATS_RX_FOUND_CTSYNC = 26  # On a cut-through Flow  the number of times the Flow entered
    # cut-through delivery mode.
    SOLCLIENT_STATS_RX_LOST_CTSYNC = 27  # On a cut-through Flow  the number of times the Flow left cut-through
    # delivery mode to resynchronize with the Guaranteed message storage on the appliance
    SOLCLIENT_STATS_RX_LOST_CTSYNC_GM = 28  # On a cut-through Flow  the number of times the Flow left
    # cut-through delivery mode to resynchronize with the Guaranteed message storage due to receiving a
    # Guaranteed message that was not previously received as Direct.
    SOLCLIENT_STATS_RX_OVERFLOW_CTSYNC_BUFFER = 29  # On a cut-through Flow  the number of times the
    # synchronization buffer overflowed  delaying synchronization.
    SOLCLIENT_STATS_RX_ALREADY_CUT_THROUGH = 30  # On a cut-through Flow  the number of Guaranteed messages
    # discarded because they had already been received on the cut-through Flow.
    SOLCLIENT_STATS_RX_DISCARD_FROM_CTSYNC = 31  # On a cut-through Flow  the number of messages discarded
    # from the synchronization list other than those discarded due to overflow.
    SOLCLIENT_STATS_RX_DISCARD_MSG_FLOW_UNBOUND_PENDING = 32  # On a transacted flow  the number of messages
    # discarded because the flow is in a UNBOUND pending state.
    SOLCLIENT_STATS_RX_DISCARD_MSG_TRANSACTION_ROLLBACK = 33  # On a transacted flow  the number of messages
    # discarded after a transaction rollback and becomes a message comes in with prevMsgId=0.
    SOLCLIENT_STATS_RX_DISCARD_TRANSACTION_RESPONSE = 34  # On a transacted session  the number of transaction
    # responses discarded due to reconnection.
    SOLCLIENT_STATS_RX_SSL_READ_EVENTS = 35
    SOLCLIENT_STATS_RX_SSL_READ_CALLS = 36
    SOLCLIENT_STATS_RX_SETTLE_ACCEPTED = 37 # The number of messages settled with ACCEPTED outcome
    SOLCLIENT_STATS_RX_SETTLE_FAILED = 38 # The number of messages settled with FAILED outcome
    SOLCLIENT_STATS_RX_SETTLE_REJECTED = 39 # The number of messages settled with REJECTED outcome
    SOLCLIENT_STATS_RX_NUM_STATS = 40  # The size of receive stats array.



SOLCLIENT_FLOW_PROP_DEFAULT_ACTIVE_FLOW_IND = SOLCLIENT_PROP_DISABLE_VAL  # The default value for the
# SOLCLIENT_FLOW_PROP_ACTIVE_FLOW_IND property.

# Flow Bind Entities

SOLCLIENT_FLOW_PROP_BIND_ENTITY_SUB = "1"  # A bind target of subscriber
SOLCLIENT_FLOW_PROP_BIND_ENTITY_QUEUE = "2"  # A bind target of Queue
SOLCLIENT_FLOW_PROP_BIND_ENTITY_TE = "3"  # A bind target of Topic Endpoint
SOLCLIENT_FLOW_PROP_BIND_ENTITY_DTE = SOLCLIENT_FLOW_PROP_BIND_ENTITY_TE  # Deprecated name
# ; SOLCLIENT_FLOW_PROP_BIND_ENTITY_TE is preferred

# Flow Acknowledgment Modes

SOLCLIENT_FLOW_PROP_ACKMODE_AUTO = "1"  # Automatic application acknowledgment of all received messages.
# If application calls SolClient_flow_sendAck() in the SOLCLIENT_FLOW_PROP_ACKMODE_AUTO mode,
# a warning is generated.
SOLCLIENT_FLOW_PROP_ACKMODE_CLIENT = "2"  # Client must call solClient_flow_sendAck() to
# acknowledge the msgId specified.


# Flow Configuration Properties
SOLCLIENT_FLOW_PROP_BIND_ENTITY_ID = "FLOW_BIND_ENTITY_ID"  # The type of object to which this
# Flow is bound. The valid values are SOLCLIENT_FLOW_PROP_BIND_ENTITY_SUB, SOLCLIENT_FLOW_PROP_BIND_ENTITY_QUEUE,
# and SOLCLIENT_FLOW_PROP_BIND_ENTITY_TE. Default: SOLCLIENT_FLOW_PROP_DEFAULT_BIND_ENTITY_ID

SOLCLIENT_FLOW_PROP_BIND_ENTITY_DURABLE = "FLOW_BIND_ENTITY_DURABLE"  # The durability of the
# object to which this Flow is bound. Default: SOLCLIENT_PROP_ENABLE_VAL, which means the endpoint is durable.
# When set to SOLCLIENT_PROP_DISABLE_VAL, a temporary endpoint is created. 

SOLCLIENT_FLOW_PROP_BIND_NAME = "FLOW_BIND_NAME"  # The name of the Queue or Topic Endpoint that is the target
# of the bind. This property is ignored when the BIND_ENTITY_ID is SOLCLIENT_FLOW_PROP_BIND_ENTITY_SUB.
# The maximum length (not including NULL terminator) is SOLCLIENT_BUFINFO_MAX_QUEUENAME_SIZE except for
# durable queues, which has a limit of SOLCLIENT_BUFINFO_MAX_DURABLE_QUEUENAME_SIZE
# . Default: SOLCLIENT_FLOW_PROP_DEFAULT_BIND_NAME

SOLCLIENT_FLOW_PROP_ACKMODE = "FLOW_ACKMODE"  # Controls how acknowledgments are generated
# for received Guaranteed messages. Possible values are SOLCLIENT_FLOW_PROP_ACKMODE_AUTO
# and SOLCLIENT_FLOW_PROP_ACKMODE_CLIENT. Default SOLCLIENT_FLOW_PROP_ACKMODE_AUTO

SOLCLIENT_FLOW_PROP_ACTIVE_FLOW_IND = "FLOW_ACTIVE_FLOW_IND"  # When a Flow has the Active
# Flow Indication property enabled, the application will receive flow events when the flow becomes
# active, or inactive.  If the underlying session capabilities indicate that the appliance does not
# support active flow indications, then solClient_session_createFlow() will fail immediately (SOLCLIENT_FAIL)
# and set the subCode SOLCLIENT_SUBCODE_FLOW_ACTIVE_FLOW_INDICATION_UNSUPPORTED.
# Default: SOLCLIENT_FLOW_PROP_DEFAULT_ACTIVE_FLOW_IND

SOLCLIENT_FLOW_PROP_BIND_BLOCKING = "FLOW_BIND_BLOCKING"
#This property controls whether or not to block in solClient_session_createFlow().
#Default: SOLCLIENT_FLOW_PROP_DEFAULT_BIND_BLOCKING 

SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_REJECTED = "FLOW_REQUIRED_OUTCOME_REJECTED"
# Create a flow that allows solClient_flow_settleMsg() with SOLCLIENT_OUTCOME_REJECTED.
# Ignored on transacted sessions. Requires SOLCLIENT_SESSION_CAPABILITY_AD_APP_ACK_FAILED.
# Default: SOLCLIENT_FLOW_PROP_DEFAULT_REQUIRED_OUTCOME_REJECTED

SOLCLIENT_FLOW_PROP_REQUIRED_OUTCOME_FAILED = "FLOW_REQUIRED_OUTCOME_FAILED"
# Create a flow that allows solClient_flow_settleMsg() with SOLCLIENT_OUTCOME_FAILED.
# Ignored on transacted sessions. Requires SOLCLIENT_SESSION_CAPABILITY_AD_APP_ACK_FAILED.
# Default: SOLCLIENT_FLOW_PROP_DEFAULT_REQUIRED_OUTCOME_FAILED

SOLCLIENT_FLOW_PROP_BROWSER = "FLOW_BROWSER"
# Set browser mode on flow and signal it is a browser flow to broker on bind.

SOLCLIENT_FLOW_PROP_WINDOWSIZE = "FLOW_WINDOWSIZE"
# The Guaranteed message window size for the Flow.

SOLCLIENT_FLOW_PROP_MAX_RECONNECT_TRIES = "FLOW_MAX_RECONNECT_TRIES"
# When a flow is unbound by the message-broker due to "Replay Started" or "Service Unavailable",
# the API will attempt to reconnect the flow if this property is non-zero.

SOLCLIENT_FLOW_PROP_RECONNECT_RETRY_INTERVAL_MS =  "FLOW_RECONNECT_RETRY_INTERVAL_MS"
# When a flow is reconnecting, the API will attempt to reconnect immediately,
# if that bind attempt fails it will wait for the retry interval before attempting to connect again.

SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_NONEXCLUSIVE = "0"  # A non-exclusive (shared) Queue. Each client to bind
# receives messages in a round robin fashion.
SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE_EXCLUSIVE = "1"  # An exclusive Queue. The first client to bind receives
# the stored messages on the Endpoint.

# Endpoint Naming Entities, used as values for ENDPOINT properties in 
# solClient_session_endpointProvision()/solClient_session_endpointDeprovision(), in solClient_session_createFlow(), and
# in solClient_session_endpointTopicSubscribe() / solClient_session_endpointTopicUnsubscribe().

SOLCLIENT_ENDPOINT_PROP_QUEUE = "2"  # Request is for a Queue.
SOLCLIENT_ENDPOINT_PROP_TE = "3"  # Request is for a Topic Endpoint.
SOLCLIENT_ENDPOINT_PROP_CLIENT_NAME = "4"  # Request is for a Client name

#  Items that can be configured for a create endpoint operation.
SOLCLIENT_ENDPOINT_PROP_ID = "ENDPOINT_ID"  # The type of endpoint, the valid
# values are SOLCLIENT_ENDPOINT_PROP_QUEUE, SOLCLIENT_ENDPOINT_PROP_TE,
# and SOLCLIENT_ENDPOINT_PROP_CLIENT_NAME. Default: SOLCLIENT_ENDPOINT_PROP_TE
SOLCLIENT_ENDPOINT_PROP_NAME = "ENDPOINT_NAME"  # The name of the Queue or Topic endpoint
# as a NULL-terminated UTF-8 encoded string. 
SOLCLIENT_ENDPOINT_PROP_DURABLE = "ENDPOINT_DURABLE"  # The durability of the endpoint to name.
# Default: SOLCLIENT_PROP_ENABLE_VAL, which means the endpoint is durable.
# Only SOLCLIENT_PROP_ENABLE_VAL is supported in solClient_session_endpointProvision().
# This property is ignored in solClient_session_creatFlow(). 
SOLCLIENT_ENDPOINT_PROP_PERMISSION = "ENDPOINT_PERMISSION"
SOLCLIENT_ENDPOINT_PROP_ACCESSTYPE = "ENDPOINT_ACCESSTYPE"  # Sets the access type for the endpoint.
# This applies to durable Queues only. 
# Provision Flags
# The provision operation may be modified by the use of one or more of the following flags:
SOLCLIENT_PROVISION_FLAGS_WAITFORCONFIRM = 0x01  # The provision operation blocks until it has completed
# successfully on the appliance or failed.
SOLCLIENT_PROVISION_FLAGS_IGNORE_EXIST_ERRORS = 0x02  # When set, it is not considered an error

# Endpoint Permissions

SOLCLIENT_ENDPOINT_PERM_NONE = "n"  # No permissions for other clients
SOLCLIENT_ENDPOINT_PERM_READ_ONLY = "r"  # Read-only permission  other clients may not consume messages.
SOLCLIENT_ENDPOINT_PERM_CONSUME = "c"  # Consumer permission  other clients may read and consume messages.
SOLCLIENT_ENDPOINT_PERM_MODIFY_TOPIC = "m"  # Modify Topic permission  other clients may read and
# consume messages, and modify Topic on a Topic Endpoint.
SOLCLIENT_ENDPOINT_PERM_DELETE = "d"  # Delete permission  other clients may read and consume
SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION = "FLOW_REPLAY_START_LOCATION"  # When a Flow is created, the application
# may request replay of messages from the replay log, even messages that have been previously delivered and removed
# the from topic endpoint or queue.  The replay start location may be
# ::SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION_BEGINNING to indicate that all messages available should be replayed.
# Or the replay start location may be a string that begins with "DATE:" followed by a date in one of two formats. The
# date may be a string representing a long integer, which is the number of seconds since the epoch - 0:00:00 Jan 1,
# 1970.  The date may be a string as specified in RFC3339 - 'YYYY-MM-DDTHH:MM:SS[.1*DIGIT]Z' or 'YYYY-MM-DDTHH:MM:SS[
# .1*DIGIT]("+"/"-")HH:MM' Additionally, the replay start location may be
# a replication-group-message-id string as returned by
# solClient_replicationGroupMessageId_toString().
# Such a string starts with "rmid1:" and is a ::solClient_replicationGroupMessageId_t..
SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION_BEGINNING = "BEGINNING"  # Replay all messages in the replay log


# messages, modify the Topic on a Topic Endpoint, and delete the endpoint.

# solClient_flow_event
# Flow events that can be given to the Flow event callback routine registered for
#  a Flow. The Flow event callback is registered when a Flow is created through 
# solClient_session_createFlow() and has the prototype SolClient_flow_eventCallbackFunc_t.
# A Flow event can be converted to a string value through solClient_flow_eventToString().
class _SolClientFlowEvent(enum.Enum):
    # SolClient Flow event enums
    SOLCLIENT_FLOW_EVENT_UP_NOTICE = 0  # The Flow is established
    SOLCLIENT_FLOW_EVENT_DOWN_ERROR = 1  # The Flow was established and then disconnected by the appliance,
    # likely due to operator intervention. The Flow must be destroyed
    SOLCLIENT_FLOW_EVENT_BIND_FAILED_ERROR = 2  # The Flow attempted to connect but was unsuccessful
    SOLCLIENT_FLOW_EVENT_REJECTED_MSG_ERROR = 3  # This event is deprecated and will never be raised
    SOLCLIENT_FLOW_EVENT_SESSION_DOWN = 4  # The Session for the Flow was disconnected. The Flow will
    # rebound automatically when the Session is reconnected.
    SOLCLIENT_FLOW_EVENT_ACTIVE = 5  # The flow has become active
    SOLCLIENT_FLOW_EVENT_INACTIVE = 6  # The flow has become inactive
    SOLCLIENT_FLOW_EVENT_RECONNECTING = 7  # The Flow was established and then disconnected by the broker,
    # due to operator action, either 'Replay Started' or 'shutdown' on the queue, topic endpoint, or message spool.
    # The API is attempting to reconnect the flow automatically
    SOLCLIENT_FLOW_EVENT_RECONNECTED = 8  # The Flow was successfully reconnected to the broker


# Threshold to pause & resume the flow for persistent receiver
HIGH_THRESHOLD = 50  # pause the flow
LOW_THRESHOLD = 40  # resume the flow

SOLCLIENT_FLOW_PROP_SELECTOR = "FLOW_SELECTOR"  # A Java Message System (JMS) defined selector.

SOLCLIENT_GLOBAL_PROP_DEFAULT_SSL_LIB_UNIX = "libssl.so"  # The default SSL library name for Unix
# (including Linux and AIX)
SOLCLIENT_GLOBAL_PROP_DEFAULT_SSL_LIB_MACOSX = "libssl.1.1.dylib"  # The default SSL library name for MacOSX
SOLCLIENT_GLOBAL_PROP_DEFAULT_SSL_LIB_VMS = "SSL1$LIBSSL_SHR.EXE"  # The default SSL library name for OpenVMS
SOLCLIENT_GLOBAL_PROP_DEFAULT_SSL_LIB_WINDOWS = "libssl-1_1.dll"  # The default SSL library name for Windows
SOLCLIENT_GLOBAL_PROP_DEFAULT_CRYPTO_LIB_UNIX = "libcrypto.so"  # The default crypto library name for Unix
# (including Linux and AIX).
SOLCLIENT_GLOBAL_PROP_DEFAULT_CRYPTO_LIB_MACOSX = "libcrypto.1.1.dylib"  # The default crypto library name for MacOSX.
SOLCLIENT_GLOBAL_PROP_DEFAULT_CRYPTO_LIB_VMS = "SSL1$LIBCRYPTO_SHR.EXE"  # The default crypto library name for OpenVMS.
SOLCLIENT_GLOBAL_PROP_DEFAULT_CRYPTO_LIB_WINDOWS = "libcrypto-1_1.dll"  # The default crypto library name for Windows.

MAX_RMID_STR_LEN = 64  # used to allocate buffer size for solClient_replicationGroupMessageId_toString
SOLCLIENT_REPLICATION_GROUP_MESSAGE_ID_SIZE = 16

TOPIC_GENERATED_FOR_CANCELLED_CACHE_REQUEST = "This is a topic that was generated for a cancelled cache request."

# CCSMP CACHE SESSION PROPS
SOLCLIENT_CACHESESSION_PROP_CACHE_NAME = "CACHESESSION_CACHE_NAME"
SOLCLIENT_CACHESESSION_PROP_MAX_AGE = "CACHESESSION_MAX_AGE"
SOLCLIENT_CACHESESSION_PROP_MAX_MSGS = "CACHESESSION_MAX_MSGS"
SOLCLIENT_CACHESESSION_REQUESTREPLY_TIMEOUT_MS = "CACHESESSION_RR_TIMEOUT_MS"

SOLCLIENT_CACHEREQUEST_FLAGS_NO_SUBSCRIBE = 0x01  # Do not send a subscription request to the appliance before
# sending the cache request. This flag is used if the client is already subscribed to the cache request topic.*/
SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FULFILL = 0x02  # The cache request completes when the cache response is
# returned or when live data that matches the cache request topic arrives, whichever happens first. In the latter
# case, the cache request completes as soon as live data arrives. The status of the cache response is SOLCLIENT_OK,
# unless part of the response is flagged as suspect, in which case the response is SOLCLIENT_INCOMPLETE. This is a
# typical last value cache mode where only the most recent data is of interest and the application is not interested
# in all data available on the topic. */

SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_QUEUE = 0x04  # The cache request completes when the cache response is
# returned. Live data matching the cache request topic is queued until the cache request completes.  Data from the
# cache-response is delivered before queued live data. The queued live data is delivered to the application before
# the cache request completes. It is possible for queued live data to duplicate data in the cache-response. It is the
# responsibility of the application to handle duplication by some application specific method.  For example,
# by using an end-to-end message-id in the message meta-data.  */

SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU = 0x08  # The cache request completes when the cache response is
# returned. Live data matching the cache request topic is delivered immediately to the application while the cache
# request is outstanding.
# SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU is the only live data action that supports wildcard topic cache
# requests.
SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY = 0x10  # By default, solClient_cacheSession_sendCacheRequest


# blocks until the cache request completes and then returns the cache request status. If the cache request flag
# SOLCLIENT_CACHEREQUEST_FLAGS_NOWAIT_REPLY is set, solClient_cacheSession_sendCacheRequest returns immediately with
# the status SOLCLIENT_IN_PROGRESS, and the cache request status is returned through a callback when it completes.

# CCSMP CACHE ENUMS

class _SOLCLIENTCACHEEVENT(enum.Enum):
    # Assigning naked integers to this enum is fine for when it is used in Python code,
    # but if a variant of this enum were ever to be passed to CCSMP, it would need to be cast
    # to a ctypes.c_int object first.
    SOLCACHE_EVENT_REQUEST_COMPLETED_NOTICE = 0

class _SOLCLIENTCACHESTATUS(enum.Enum):
    # Cache Status of received message, returned by solClient_msg_isCacheMsg()
    SOLCLIENT_CACHE_INVALID_MESSAGE = -1
    SOLCLIENT_CACHE_LIVE_MESSAGE = 0
    SOLCLIENT_CACHE_MESSAGE = 1
    SOLCLIENT_CACHE_SUSPECT_MESSAGE = 2

_CCSMP_AGGREGATE_STATS = {
    "CACHE_REQUESTS_SUCCEEDED": [_SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_CACHEREQUEST_OK_RESPONSE,
                                 _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_CACHEREQUEST_FULFILL_DATA]
}

SOLCLIENT_SESSION_PROP_HOST = "SESSION_HOST"
SOLCLIENT_SESSION_PROP_CONNECT_TIMEOUT_MS = "SESSION_CONNECT_TIMEOUT_MS"
SOLCLIENT_SESSION_PROP_CONNECT_RETRIES = "SESSION_CONNECT_RETRIES"
SOLCLIENT_SESSION_PROP_CONNECT_RETRIES_PER_HOST = "SESSION_CONNECT_RETRIES_PER_HOST"
SOLCLIENT_SESSION_PROP_RECONNECT_RETRIES = "SESSION_RECONNECT_RETRIES"
SOLCLIENT_SESSION_PROP_RECONNECT_RETRY_WAIT_MS = "SESSION_RECONNECT_RETRY_WAIT_MS"
SOLCLIENT_SESSION_PROP_KEEP_ALIVE_INT_MS = "SESSION_KEEP_ALIVE_INTERVAL_MS"
SOLCLIENT_SESSION_PROP_KEEP_ALIVE_LIMIT = "SESSION_KEEP_ALIVE_LIMIT"
SOLCLIENT_SESSION_PROP_SOCKET_RCV_BUF_SIZE = "SESSION_SOCKET_RCV_BUF_SIZE"
SOLCLIENT_SESSION_PROP_SOCKET_SEND_BUF_SIZE = "SESSION_SOCKET_SEND_BUF_SIZE"
SOLCLIENT_SESSION_PROP_TCP_NODELAY = "SESSION_TCP_NODELAY"
SOLCLIENT_SESSION_PROP_COMPRESSION_LEVEL = "SESSION_COMPRESSION_LEVEL"
SOLCLIENT_SESSION_PROP_PAYLOAD_COMPRESSION_LEVEL = "SESSION_PAYLOAD_COMPRESSION_LEVEL"
SOLCLIENT_SESSION_PROP_SSL_VALIDATE_CERTIFICATE = "SESSION_SSL_VALIDATE_CERTIFICATE"
SOLCLIENT_SESSION_PROP_SSL_VALIDATE_CERTIFICATE_DATE = "SESSION_SSL_VALIDATE_CERTIFICATE_DATE"
SOLCLIENT_SESSION_PROP_SSL_VALIDATE_CERTIFICATE_HOST = "SESSION_SSL_VALIDATE_CERTIFICATE_HOST"
SOLCLIENT_SESSION_PROP_SSL_EXCLUDED_PROTOCOLS = "SESSION_SSL_EXCLUDED_PROTOCOLS" # Deprecated.
SOLCLIENT_SESSION_PROP_MINIMUM_TLS_PROTOCOL_VERSION = "SESSION_MINIMUM_TLS_PROTOCOL_VERSION"
SOLCLIENT_SESSION_PROP_MAXIMUM_TLS_PROTOCOL_VERSION = "SESSION_MAXIMUM_TLS_PROTOCOL_VERSION"
SOLCLIENT_SESSION_PROP_SSL_CONNECTION_DOWNGRADE_TO = "SESSION_SSL_CONNECTION_DOWNGRADE_TO"
SOLCLIENT_SESSION_PROP_SSL_CIPHER_SUITES = "SESSION_SSL_CIPHER_SUITES"
SOLCLIENT_SESSION_PROP_SSL_TRUST_STORE_DIR = "SESSION_SSL_TRUST_STORE_DIR"
SOLCLIENT_SESSION_PROP_SSL_TRUSTED_COMMON_NAME_LIST = "SESSION_SSL_TRUSTED_COMMON_NAME_LIST"
SOLCLIENT_SESSION_PROP_VPN_NAME = "SESSION_VPN_NAME"
SOLCLIENT_SESSION_PROP_GENERATE_SENDER_ID = "SESSION_SEND_SENDER_ID"
SOLCLIENT_SESSION_PROP_GENERATE_RCV_TIMESTAMPS = "SESSION_RCV_TIMESTAMP"
SOLCLIENT_SESSION_PROP_GENERATE_SEND_TIMESTAMPS = "SESSION_SEND_TIMESTAMP"
SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME = "SESSION_AUTHENTICATION_SCHEME"
SOLCLIENT_SESSION_PROP_USERNAME = "SESSION_USERNAME"
SOLCLIENT_SESSION_PROP_PASSWORD = "SESSION_PASSWORD"
SOLCLIENT_SESSION_PROP_SSL_CLIENT_CERTIFICATE_FILE = "SESSION_SSL_CLIENT_CERTIFICATE_FILE"
SOLCLIENT_SESSION_PROP_SSL_CLIENT_PRIVATE_KEY_FILE = "SESSION_SSL_CLIENT_PRIVATE_KEY_FILE"
SOLCLIENT_SESSION_PROP_SSL_CLIENT_PRIVATE_KEY_FILE_PASSWORD = "SESSION_SSL_CLIENT_PRIVATE_KEY_FILE_PASSWORD"
SOLCLIENT_SESSION_PROP_OAUTH2_ACCESS_TOKEN = "SESSION_OAUTH2_ACCESS_TOKEN"
SOLCLIENT_SESSION_PROP_OIDC_ID_TOKEN = "SESSION_OIDC_ID_TOKEN"
SOLCLIENT_SESSION_PROP_OAUTH2_ISSUER_IDENTIFIER = "SESSION_OAUTH2_ISSUER_IDENTIFIER"
SOLCLIENT_FLOW_PROP_NO_LOCAL = "FLOW_NO_LOCAL"
SOLCLIENT_SESSION_PROP_APPLICATION_DESCRIPTION = "SESSION_APPLICATION_DESCRIPTION"
SOLCLIENT_SESSION_PROP_KRB_SERVICE_NAME = "SESSION_KRB_SERVICE_NAME"
SOLCLIENT_FLOW_PROP_START_STATE = "FLOW_START_STATE"
SOLCLIENT_TRANSACTEDSESSION_PROP_CREATE_MESSAGE_DISPATCHER = "TRANSACTEDSESSION_CREATE_MESSAGE_DISPATCHER"
SOLCLIENT_TRANSACTEDSESSION_PROP_REQUESTREPLY_TIMEOUT_MS = "TRANSACTEDSESSION_REQUESTREPLY_TIMEOUT_MS"
BUFFER_SIZE_LIMIT = 640000
