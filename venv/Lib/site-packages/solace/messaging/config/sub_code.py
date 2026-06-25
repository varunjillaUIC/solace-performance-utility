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
# pylint: disable=missing-module-docstring, missing-class-docstring

import enum


class SolClientSubCode(enum.Enum):
    """ SolClient sub code enums from underlying protocol engine for additional error information"""
    SOLCLIENT_SUBCODE_OK = 0
    """ No error."""
    SOLCLIENT_SUBCODE_PARAM_OUT_OF_RANGE = 1
    """ An API call was made with an out-of-range parameter."""
    SOLCLIENT_SUBCODE_PARAM_NULL_PTR = 2
    """ An API call was made with a null or invalid pointer parameter."""
    SOLCLIENT_SUBCODE_PARAM_CONFLICT = 3
    """ An API call was made with a parameter combination that is not valid."""
    SOLCLIENT_SUBCODE_INSUFFICIENT_SPACE = 4
    """ An API call failed due to insufficient space to accept more data."""
    SOLCLIENT_SUBCODE_OUT_OF_RESOURCES = 5
    """ An API call failed due to lack of resources (for example, starting a timer when all timers are in use)."""
    SOLCLIENT_SUBCODE_INTERNAL_ERROR = 6
    """ An API call had an internal error (not an application fault)."""
    SOLCLIENT_SUBCODE_OUT_OF_MEMORY = 7
    """ An API call failed due to inability to allocate memory."""
    SOLCLIENT_SUBCODE_PROTOCOL_ERROR = 8
    """ An API call failed due to a protocol error with the appliance (not an
     application fault)."""
    SOLCLIENT_SUBCODE_INIT_NOT_CALLED = 9
    """ An API call failed due to solClient_initialize() not being called first."""
    SOLCLIENT_SUBCODE_TIMEOUT = 10
    """ An API call failed due to a timeout."""
    SOLCLIENT_SUBCODE_KEEP_ALIVE_FAILURE = 11
    """ The Session Keep-Alive detected a failed Session."""
    SOLCLIENT_SUBCODE_SESSION_NOT_ESTABLISHED = 12
    """ An API call failed due to the Session not being established."""
    SOLCLIENT_SUBCODE_OS_ERROR = 13
    """ An API call failed due to a failed operating system call; an error string can
     be retrieved with solClient_getLastErrorInfo()."""
    SOLCLIENT_SUBCODE_COMMUNICATION_ERROR = 14
    """ An API call failed due to a communication error. An error string
     can be retrieved with solClient_getLastErrorInfo()."""
    SOLCLIENT_SUBCODE_USER_DATA_TOO_LARGE = 15
    """ An attempt was made to send a message with user data larger than
     the maximum that is supported."""
    SOLCLIENT_SUBCODE_TOPIC_TOO_LARGE = 16
    """ An attempt was made to use a Topic that is longer than the maximum that
     is supported."""
    SOLCLIENT_SUBCODE_INVALID_TOPIC_SYNTAX = 17
    """ An attempt was made to use a Topic that has a syntax which is not
     supported."""
    SOLCLIENT_SUBCODE_XML_PARSE_ERROR = 18
    """ The appliance could not parse an XML message."""
    SOLCLIENT_SUBCODE_LOGIN_FAILURE = 19
    """ The client could not log into the appliance (bad username or password)."""
    SOLCLIENT_SUBCODE_INVALID_VIRTUAL_ADDRESS = 20
    """ An attempt was made to connect to the wrong IP address on the
     appliance (must use CVRID if configured) or the appliance CVRID has changed and this was detected on reconnect."""
    SOLCLIENT_SUBCODE_CLIENT_DELETE_IN_PROGRESS = 21
    """ The client login not currently possible as previous
     instance of same client still being deleted."""
    SOLCLIENT_SUBCODE_TOO_MANY_CLIENTS = 22
    """ The client login not currently possible because the maximum
     number of active clients on appliance has already been reached."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_ALREADY_PRESENT = 23
    """ The client attempted to add a subscription
     which already exists. This subcode is only returned if the Session property
     SOLCLIENT_SESSION_PROP_IGNORE_DUP_SUBSCRIPTION_ERROR is not enabled."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_NOT_FOUND = 24
    """ The client attempted to remove a subscription
     which did not exist. This subcode is only returned if the Session property
     SOLCLIENT_SESSION_PROP_IGNORE_DUP_SUBSCRIPTION_ERROR is not enabled."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_INVALID = 25
    """ The client attempted to add/remove a subscription that is not valid."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_OTHER = 26
    """ The appliance rejected a subscription add or
     remove request for a reason not separately enumerated."""
    SOLCLIENT_SUBCODE_CONTROL_OTHER = 27
    """ The appliance rejected a control message for another
     reason not separately enumerated."""
    SOLCLIENT_SUBCODE_DATA_OTHER = 28
    """ The appliance rejected a data message for another reason
     not separately enumerated."""
    SOLCLIENT_SUBCODE_LOG_FILE_ERROR = 29
    """ Could not open the log file name specified by the application
     for writing (Deprecated - SOLCLIENT_SUBCODE_OS_ERROR is used)."""
    SOLCLIENT_SUBCODE_MESSAGE_TOO_LARGE = 30
    """ The client attempted to send a message larger than that
     supported by the appliance."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_TOO_MANY = 31
    """ The client attempted to add a subscription
     that exceeded the maximum number allowed."""
    SOLCLIENT_SUBCODE_INVALID_SESSION_OPERATION = 32
    """ An API call failed due to the attempted
     operation not being valid for the Session."""
    SOLCLIENT_SUBCODE_TOPIC_MISSING = 33
    """ A send call was made that did not have a Topic in a
     mode where one is required (for example, client mode)."""
    SOLCLIENT_SUBCODE_ASSURED_MESSAGING_NOT_ESTABLISHED = 34
    """ A send call was made to send a
     Guaranteed message before Guaranteed Delivery is established (Deprecated)."""
    SOLCLIENT_SUBCODE_ASSURED_MESSAGING_STATE_ERROR = 35
    """ An attempt was made to start Guaranteed Delivery when it is already started."""
    SOLCLIENT_SUBCODE_QUEUENAME_TOPIC_CONFLICT = 36
    """ Both Queue Name and Topic are specified in solClient_session_send."""
    SOLCLIENT_SUBCODE_QUEUENAME_TOO_LARGE = 37
    """ An attempt was made to use a Queue name which is longer than the maximum
     supported length."""
    SOLCLIENT_SUBCODE_QUEUENAME_INVALID_MODE = 38
    """ An attempt was made to use a Queue name on a non-Guaranteed message."""
    SOLCLIENT_SUBCODE_MAX_TOTAL_MSGSIZE_EXCEEDED = 39
    """ An attempt was made to send a message with a total size greater than that supported by the protocol."""
    SOLCLIENT_SUBCODE_DBLOCK_ALREADY_EXISTS = 40
    """ An attempt was made to allocate a datablock for a msg element when one already exists."""
    SOLCLIENT_SUBCODE_NO_STRUCTURED_DATA = 41
    """ An attempt was made to create a container to read structured data where none exists."""
    SOLCLIENT_SUBCODE_CONTAINER_BUSY = 42
    """ An attempt was made to add a field to a map or stream while a sub map or stream is being built."""
    SOLCLIENT_SUBCODE_INVALID_DATA_CONVERSION = 43
    """ An attempt was made to retrieve structured data with wrong type."""
    SOLCLIENT_SUBCODE_CANNOT_MODIFY_WHILE_NOT_IDLE = 44
    """ An attempt was made to modify a property that cannot be modified while Session is not idle."""
    SOLCLIENT_SUBCODE_MSG_VPN_NOT_ALLOWED = 45
    """ The Message VPN name set for the Session is not allowed for the Session's username."""
    SOLCLIENT_SUBCODE_CLIENT_NAME_INVALID = 46
    """ The client name chosen has been rejected as invalid by the appliance."""
    SOLCLIENT_SUBCODE_MSG_VPN_UNAVAILABLE = 47
    """The Message VPN name set for the Session (or the default Message VPN, if none was set) is currently shutdown
    on the appliance. """
    SOLCLIENT_SUBCODE_CLIENT_USERNAME_IS_SHUTDOWN = 48
    """ The username for the client is administratively shutdown on the appliance."""
    SOLCLIENT_SUBCODE_DYNAMIC_CLIENTS_NOT_ALLOWED = 49
    """ The username for the Session has not been set and dynamic clients are not allowed."""
    SOLCLIENT_SUBCODE_CLIENT_NAME_ALREADY_IN_USE = 50
    """ The Session is attempting to use a client,
     publisher name, or subscriber name that is in use by another client, publisher, or subscriber,
     and the appliance is configured to reject the new Session. When Message VPNs are in use, the conflicting
     client name must be in the same Message VPN."""
    SOLCLIENT_SUBCODE_CACHE_NO_DATA = 51
    """ When the cache request returns SOLCLIENT_INCOMPLETE,
     this subcode indicates there is no cached data in the designated cache."""
    SOLCLIENT_SUBCODE_CACHE_SUSPECT_DATA = 52
    """When the designated cache responds to a cache request with suspect data the API returns SOLCLIENT_INCOMPLETE
    with this subcode. """
    SOLCLIENT_SUBCODE_CACHE_ERROR_RESPONSE = 53
    """ The cache instance has returned an error response to the request."""
    SOLCLIENT_SUBCODE_CACHE_INVALID_SESSION = 54
    """ The cache session operation failed because the Session has been destroyed."""
    SOLCLIENT_SUBCODE_CACHE_TIMEOUT = 55
    """ The cache session operation failed because the request timeout expired."""
    SOLCLIENT_SUBCODE_CACHE_LIVEDATA_FULFILL = 56
    """ The cache session operation completed when live data arrived on the Topic requested."""
    SOLCLIENT_SUBCODE_CACHE_ALREADY_IN_PROGRESS = 57
    """ A cache request has been made when there is already a cache request outstanding on the
    same Topic and SOLCLIENT_CACHEREQUEST_FLAGS_LIVEDATA_FLOWTHRU was not set."""
    SOLCLIENT_SUBCODE_MISSING_REPLY_TO = 58
    """ A message does not have the required reply-to field."""
    SOLCLIENT_SUBCODE_CANNOT_BIND_TO_QUEUE = 59
    """ Already bound to the queue, or not authorized to bind to the queue."""
    SOLCLIENT_SUBCODE_INVALID_TOPIC_NAME_FOR_TE = 60
    """ An attempt was made to bind to a Topic Endpoint with an invalid topic."""
    SOLCLIENT_SUBCODE_INVALID_TOPIC_NAME_FOR_DTE = SOLCLIENT_SUBCODE_INVALID_TOPIC_NAME_FOR_TE
    """ Deprecated name; SOLCLIENT_SUBCODE_INVALID_TOPIC_NAME_FOR_TE is preferred."""
    SOLCLIENT_SUBCODE_UNKNOWN_QUEUE_NAME = 61
    """ An attempt was made to bind to an unknown Queue name (for example, not configured on appliance)."""
    SOLCLIENT_SUBCODE_UNKNOWN_TE_NAME = 62
    """ An attempt was made to bind to an unknown Topic Endpoint name (for example, not configured on appliance)."""
    SOLCLIENT_SUBCODE_UNKNOWN_DTE_NAME = SOLCLIENT_SUBCODE_UNKNOWN_TE_NAME
    """ Deprecated name; SOLCLIENT_SUBCODE_UNKNOWN_TE_NAME is preferred."""
    SOLCLIENT_SUBCODE_MAX_CLIENTS_FOR_QUEUE = 63
    """ An attempt was made to bind to a Queue that already has a maximum number of clients."""
    SOLCLIENT_SUBCODE_MAX_CLIENTS_FOR_TE = 64
    """ An attempt was made to bind to a Topic Endpoint that already has a maximum number of clients."""
    SOLCLIENT_SUBCODE_MAX_CLIENTS_FOR_DTE = SOLCLIENT_SUBCODE_MAX_CLIENTS_FOR_TE
    """ Deprecated name, SOLCLIENT_SUBCODE_MAX_CLIENTS_FOR_TE is preferred."""
    SOLCLIENT_SUBCODE_UNEXPECTED_UNBIND = 65
    """ An unexpected unbind response was received for a Queue or Topic Endpoint (for example, the Queue
    or Topic Endpoint was deleted from the appliance)."""
    SOLCLIENT_SUBCODE_QUEUE_NOT_FOUND = 66
    """ The specified Queue was not found when publishing a message."""
    SOLCLIENT_SUBCODE_CLIENT_ACL_DENIED = 67
    """ The client login to the appliance was denied because the IP
    address/netmask combination used for the client is designated in the ACL
    (Access Control List) as a deny connection for the given Message VPN and username."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_ACL_DENIED = 68
    """Adding a subscription was denied because it matched a subscription that was defined on the ACL (Access Control
    List). """
    SOLCLIENT_SUBCODE_PUBLISH_ACL_DENIED = 69
    """ A message could not be published because its Topic matched a Topic defined on the ACL (Access Control List)."""
    SOLCLIENT_SUBCODE_DELIVER_TO_ONE_INVALID = 70
    """ An attempt was made to set both Deliver-To-One (DTO)
     and Guaranteed Delivery in the same message. (Deprecated:DTO will be applied to the corresponding
     demoted direct message)"""
    SOLCLIENT_SUBCODE_SPOOL_OVER_QUOTA = 71
    """ Message was not delivered because the Guaranteed message
     spool is over its allotted space quota."""
    SOLCLIENT_SUBCODE_QUEUE_SHUTDOWN = 72
    """ An attempt was made to operate on a shutdown queue."""
    SOLCLIENT_SUBCODE_TE_SHUTDOWN = 73
    """ An attempt was made to bind to a shutdown Topic Endpoint."""
    SOLCLIENT_SUBCODE_NO_MORE_NON_DURABLE_QUEUE_OR_TE = 74
    """ An attempt was made to bind to a non-durable Queue or Topic Endpoint, and the appliance is out of resources."""
    SOLCLIENT_SUBCODE_ENDPOINT_ALREADY_EXISTS = 75
    """ An attempt was made to create a Queue or Topic Endpoint that already exists.
    This subcode is only returned if the provision flag SOLCLIENT_PROVISION_FLAGS_IGNORE_EXIST_ERRORS is not set."""
    SOLCLIENT_SUBCODE_PERMISSION_NOT_ALLOWED = 76
    """ An attempt was made to delete or create a Queue or Topic Endpoint when the Session does not have authorization
     for the action. This subcode is also returned when an attempt is made to remove a message from an endpoint when the
     Session does not have 'consume' authorization, or when an attempt is made to add or remove a Topic
     subscription from a Queue when the Session does not have 'modify-topic' authorization."""
    SOLCLIENT_SUBCODE_INVALID_SELECTOR = 77
    """ An attempt was made to bind to a Queue or Topic Endpoint with an invalid selector."""
    SOLCLIENT_SUBCODE_MAX_MESSAGE_USAGE_EXCEEDED = 78
    """ Publishing of message denied because the maximum spooled message count was exceeded."""
    SOLCLIENT_SUBCODE_ENDPOINT_PROPERTY_MISMATCH = 79
    """ An attempt was made to create a dynamic durable endpoint and it was found to exist with different properties."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_MANAGER_DENIED = 80
    """An attempt was made to add a subscription to another client when Session does not have subscription manager
    privileges. """
    SOLCLIENT_SUBCODE_UNKNOWN_CLIENT_NAME = 81
    """ An attempt was made to add a subscription to another client that is unknown on the appliance."""
    SOLCLIENT_SUBCODE_QUOTA_OUT_OF_RANGE = 82
    """ An attempt was made to provision an endpoint with a quota that is out of range."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_ATTRIBUTES_CONFLICT = 83
    """ The client attempted to add a subscription which already exists but it has different properties"""
    SOLCLIENT_SUBCODE_INVALID_SMF_MESSAGE = 84
    """ The client attempted to send a Solace Message Format (SMF) message
     using solClient_session_sendSmf() or solClient_session_sendMultipleSmf(), but the buffer did not
     contain a Direct message."""
    SOLCLIENT_SUBCODE_NO_LOCAL_NOT_SUPPORTED = 85
    """ The client attempted to establish a Session or
     Flow with No Local enabled and the capability is not supported by the appliance."""
    SOLCLIENT_SUBCODE_UNSUBSCRIBE_NOT_ALLOWED_CLIENTS_BOUND = 86
    """ The client attempted to unsubscribe
     a Topic from a Topic Endpoint while there were still Flows bound to the endpoint."""
    SOLCLIENT_SUBCODE_CANNOT_BLOCK_IN_CONTEXT = 87
    """ An API function was invoked in the
     Context thread that would have blocked otherwise. For an example, a call may have been made to send a message
     when the Session is configured with SOLCLIENT_SESSION_PROP_SEND_BLOCKING enabled and the
     transport (socket or IPC) channel is full. All application callback functions are executed in
     the Context thread."""
    SOLCLIENT_SUBCODE_FLOW_ACTIVE_FLOW_INDICATION_UNSUPPORTED = 88
    """ The client attempted to establish a Flow with Active Flow Indication (SOLCLIENT_FLOW_PROP_ACTIVE_FLOW_IND)
     enabled and the capability is not supported by the appliance"""
    SOLCLIENT_SUBCODE_UNRESOLVED_HOST = 89
    """ The client failed to connect because the host name could not be resolved."""
    SOLCLIENT_SUBCODE_CUT_THROUGH_UNSUPPORTED = 90
    """ An attempt was made to create a 'cut-through' Flow on a Session that does not support this capability"""
    SOLCLIENT_SUBCODE_CUT_THROUGH_ALREADY_BOUND = 91
    """ An attempt was made to create a 'cut-through' Flow on a Session that already has one 'cut-through' Flow"""
    SOLCLIENT_SUBCODE_CUT_THROUGH_INCOMPATIBLE_WITH_SESSION = 92
    """ An attempt was made to create a 'cut-through' Flow on a Session with incompatible Session properties.
    Cut-through may not be enabled on Sessions with SOLCLIENT_SESSION_PROP_TOPIC_DISPATCH enabled."""
    SOLCLIENT_SUBCODE_INVALID_FLOW_OPERATION = 93
    """ An API call failed due to the attempted operation not being valid for the Flow."""
    SOLCLIENT_SUBCODE_UNKNOWN_FLOW_NAME = 94
    """ The session was disconnected due to loss of the publisher flow state.
    All (unacked and unsent) messages held by the API were deleted.
    To connect the session, applications need to call SolClient_session_connect again."""
    SOLCLIENT_SUBCODE_REPLICATION_IS_STANDBY = 95
    """ An attempt to perform an operation using a VPN that is configured to be STANDBY for replication."""
    SOLCLIENT_SUBCODE_LOW_PRIORITY_MSG_CONGESTION = 96
    """The message was rejected by the appliance as one or more matching endpoints exceeded the
    reject-low-priority-msg-limit. """
    SOLCLIENT_SUBCODE_LIBRARY_NOT_LOADED = 97
    """ The client failed to find the library or symbol."""
    SOLCLIENT_SUBCODE_FAILED_LOADING_TRUSTSTORE = 98
    """ The client failed to load the trust store."""
    SOLCLIENT_SUBCODE_UNTRUSTED_CERTIFICATE = 99
    """ The client attempted to connect to an appliance that has a suspect certificate."""
    SOLCLIENT_SUBCODE_UNTRUSTED_COMMONNAME = 100
    """ The client attempted to connect to an appliance that has a suspect common name."""
    SOLCLIENT_SUBCODE_CERTIFICATE_DATE_INVALID = 101
    """ The client attempted to connect to an appliance that does not have a valid certificate date."""
    SOLCLIENT_SUBCODE_FAILED_LOADING_CERTIFICATE_AND_KEY = 102
    """ The client failed to load certificate and/or private key files."""
    SOLCLIENT_SUBCODE_BASIC_AUTHENTICATION_IS_SHUTDOWN = 103
    """ The client attempted to connect to an appliance that has the basic authentication shutdown."""
    SOLCLIENT_SUBCODE_CLIENT_CERTIFICATE_AUTHENTICATION_IS_SHUTDOWN = 104
    """ The client attempted to connect to an appliance that has the client certificate authentication shutdown."""
    SOLCLIENT_SUBCODE_UNTRUSTED_CLIENT_CERTIFICATE = 105
    """ The client failed to connect to an appliance as it has a suspect client certificate."""
    SOLCLIENT_SUBCODE_CLIENT_CERTIFICATE_DATE_INVALID = 106
    """ The client failed to connect to an appliance as it does not have a valid client certificate date."""
    SOLCLIENT_SUBCODE_CACHE_REQUEST_CANCELLED = 107
    """ The cache request has been cancelled by the client."""
    SOLCLIENT_SUBCODE_DELIVERY_MODE_UNSUPPORTED = 108
    """Attempt was made from a Transacted Session to send a message with the delivery mode
    SOLCLIENT_DELIVERY_MODE_DIRECT. """
    SOLCLIENT_SUBCODE_PUBLISHER_NOT_CREATED = 109
    """ Client attempted to send a message from a Transacted Session without creating a default publisher flow."""
    SOLCLIENT_SUBCODE_FLOW_UNBOUND = 110
    """ The client attempted to receive message from an UNBOUND Flow with no queued messages in memory."""
    SOLCLIENT_SUBCODE_INVALID_TRANSACTED_SESSION_ID = 111
    """ The client attempted to commit or rollback a transaction with an invalid Transacted Session Id."""
    SOLCLIENT_SUBCODE_INVALID_TRANSACTION_ID = 112
    """ The client attempted to commit or rollback a transaction with an invalid transaction Id."""
    SOLCLIENT_SUBCODE_MAX_TRANSACTED_SESSIONS_EXCEEDED = 113
    """ The client failed to open a Transacted Session as it exceeded the max Transacted Sessions."""
    SOLCLIENT_SUBCODE_TRANSACTED_SESSION_NAME_IN_USE = 114
    """The client failed to open a Transacted Session as the Transacted Session name provided is being used by
    another opened session. """
    SOLCLIENT_SUBCODE_SERVICE_UNAVAILABLE = 115
    """ Guaranteed Delivery services are not enabled on the appliance."""
    SOLCLIENT_SUBCODE_NO_TRANSACTION_STARTED = 116
    """ The client attempted to commit an unknown transaction."""
    SOLCLIENT_SUBCODE_PUBLISHER_NOT_ESTABLISHED = 117
    """ A send call was made on a transacted session before its publisher is established."""
    SOLCLIENT_SUBCODE_MESSAGE_PUBLISH_FAILURE = 118
    """ The client attempted to commit a transaction with a GD publish failure encountered."""
    SOLCLIENT_SUBCODE_TRANSACTION_FAILURE = 119
    """ The client attempted to commit a transaction with too many transaction steps."""
    SOLCLIENT_SUBCODE_MESSAGE_CONSUME_FAILURE = 120
    """ The client attempted to commit a transaction with a consume failure encountered."""
    SOLCLIENT_SUBCODE_ENDPOINT_MODIFIED = 121
    """ The client attempted to commit a transaction with an Endpoint being shutdown or deleted."""
    SOLCLIENT_SUBCODE_INVALID_CONNECTION_OWNER = 122
    """ The client attempted to commit a transaction with an unknown connection ID."""
    SOLCLIENT_SUBCODE_KERBEROS_AUTHENTICATION_IS_SHUTDOWN = 123
    """ The client attempted to connect to an appliance that has the Kerberos authentication shutdown."""
    SOLCLIENT_SUBCODE_COMMIT_OR_ROLLBACK_IN_PROGRESS = 124
    """The client attempted to send/receive a message or commit/rollback a transaction when a transaction
    commit/rollback is in progress. """
    SOLCLIENT_SUBCODE_UNBIND_RESPONSE_LOST = 125
    """ The application called solClient_flow_destroy() and the unbind-response was not received."""
    SOLCLIENT_SUBCODE_MAX_TRANSACTIONS_EXCEEDED = 126
    """ The client failed to open a Transacted Session as the maximum number of transactions was exceeded."""
    SOLCLIENT_SUBCODE_COMMIT_STATUS_UNKNOWN = 127
    """ The commit response was lost due to a transport layer reconnection to an alternate host in the host list."""
    SOLCLIENT_SUBCODE_PROXY_AUTH_REQUIRED = 128
    """ The host entry did not contain proxy authentication when required by the proxy server."""
    SOLCLIENT_SUBCODE_PROXY_AUTH_FAILURE = 129
    """ The host entry contained invalid proxy authentication when required by the proxy server."""
    SOLCLIENT_SUBCODE_NO_SUBSCRIPTION_MATCH = 130
    """ The client attempted to publish a guaranteed message to a topic that did not have any guaranteed
    subscription matches or only matched a replicated topic."""
    SOLCLIENT_SUBCODE_SUBSCRIPTION_MATCH_ERROR = 131
    """The client attempted to bind to a non-exclusive topic endpoint that is already bound with a different
    subscription. """
    SOLCLIENT_SUBCODE_SELECTOR_MATCH_ERROR = 132
    """The client attempted to bind to a non-exclusive topic endpoint that is already bound with a different ingress
    selector. """
    SOLCLIENT_SUBCODE_REPLAY_NOT_SUPPORTED = 133
    """ Replay is not supported on the Solace Message Router."""
    SOLCLIENT_SUBCODE_REPLAY_DISABLED = 134
    """ Replay is not enabled in the message-vpn."""
    SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_NON_EXCLUSIVE_NOT_ALLOWED = 135
    """ The client attempted to start replay on a flow bound to a non-exclusive endpoint."""
    SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_INACTIVE_FLOW_NOT_ALLOWED = 136
    """ The client attempted to start replay on an inactive flow."""
    SOLCLIENT_SUBCODE_CLIENT_INITIATED_REPLAY_BROWSER_FLOW_NOT_ALLOWED = 137
    """The client attempted to bind with both SOLCLIENT_FLOW_PROP_BROWSER enabled and
    SOLCLIENT_FLOW_PROP_REPLAY_START_LOCATION set. """
    SOLCLIENT_SUBCODE_REPLAY_TEMPORARY_NOT_SUPPORTED = 138
    """ Replay is not supported on temporary endpoints."""
    SOLCLIENT_SUBCODE_UNKNOWN_START_LOCATION_TYPE = 139
    """ The client attempted to start a replay but provided an unknown start location type."""
    SOLCLIENT_SUBCODE_REPLAY_MESSAGE_UNAVAILABLE = 140
    """ A replay in progress on a flow failed because messages to be replayed were trimmed from the replay log."""
    SOLCLIENT_SUBCODE_REPLAY_STARTED = 141
    """A replay was started on the queue/topic endpoint, either by another client or by an administrator on the
    message router. """
    SOLCLIENT_SUBCODE_REPLAY_CANCELLED = 142
    """ A replay in progress on a flow was administratively cancelled, causing the flow to be unbound."""
    SOLCLIENT_SUBCODE_REPLAY_START_TIME_NOT_AVAILABLE = 143
    """ A replay was requested but the requested start time is not available in the replay log."""
    SOLCLIENT_SUBCODE_REPLAY_MESSAGE_REJECTED = 144
    """The Solace Message Router attempted to replay a message, but the queue/topic endpoint rejected the message to
    the sender. """
    SOLCLIENT_SUBCODE_REPLAY_LOG_MODIFIED = 145
    """ A replay in progress on a flow failed because the replay log was modified."""
    SOLCLIENT_SUBCODE_MISMATCHED_ENDPOINT_ERROR_ID = 146
    """ Endpoint error ID in the bind request does not match the endpoint's error ID."""
    SOLCLIENT_SUBCODE_OUT_OF_REPLAY_RESOURCES = 147
    """A replay was requested, but the router does not have sufficient resources to fulfill the request, due to too
    many active replays. """
    SOLCLIENT_SUBCODE_TOPIC_OR_SELECTOR_MODIFIED_ON_DURABLE_TOPIC_ENDPOINT = 148
    """A replay was in progress on a Durable Topic Endpoint (DTE) when its topic or selector was modified,
    causing the replay to fail. """
    SOLCLIENT_SUBCODE_REPLAY_FAILED = 149
    """ A replay in progress on a flow failed."""
    SOLCLIENT_SUBCODE_COMPRESSED_SSL_NOT_SUPPORTED = 150
    """The client attempted to establish a Session or Flow with ssl and compression, but the capability is not
    supported by the appliance. """
    SOLCLIENT_SUBCODE_SHARED_SUBSCRIPTIONS_NOT_SUPPORTED = 151
    """ The client attempted to add a shared subscription, but the capability is not supported by the appliance."""
    SOLCLIENT_SUBCODE_SHARED_SUBSCRIPTIONS_NOT_ALLOWED = 152
    """The client attempted to add a shared subscription on a client that is not permitted to use shared
    subscriptions. """
    SOLCLIENT_SUBCODE_SHARED_SUBSCRIPTIONS_ENDPOINT_NOT_ALLOWED = 153
    """ The client attempted to add a shared subscription to a queue or topic endpoint."""
    SOLCLIENT_SUBCODE_OBJECT_DESTROYED = 154
    """ The operation cannot be completed because the object (context, session, flow) for
    the method has been destroyed in another thread."""
    SOLCLIENT_SUBCODE_DELIVERY_COUNT_NOT_SUPPORTED = 155
    """ The message was received from endpoint that does not support delivery count"""
    SOLCLIENT_SUBCODE_REPLAY_START_MESSAGE_UNAVAILABLE = 156
    """A replay was requested but
    the requested start message is not available in the replay log."""
    SOLCLIENT_SUBCODE_MESSAGE_ID_NOT_COMPARABLE = 157
    """Replication Group Message Id are not
    comparable. Messages must be published to the same broker or HA pair for their Replicaton Group Message Id
    to be comparable. """
    SOLCLIENT_SUBCODE_REPLAY_ANONYMOUS_NOT_SUPPORTED = 158
    """ The client attempted to start replay on a flow bound to an anonymous queue. """
    SOLCLIENT_SUBCODE_BROWSING_NOT_SUPPORTED_ON_PARTITIONED_QUEUE = 159
    """ The client attempted to use a browser flow on a partitioned queue. """
    SOLCLIENT_SUBCODE_SELECTORS_NOT_SUPPORTED_ON_PARTITIONED_QUEUE = 160
    """ The client attempted to use an egress selector when binding to a partitioned queue. """
    SOLCLIENT_SUBCODE_SYNC_REPLICATION_INELIGIBLE = 161
    """ A guaranteed message was rejected because the broker has been configured to reject messages
    when sync replication mode is ineligible. A transaction commit failed because replication
    became ineligible during the transaction. """
    SOLCLIENT_SUBCODE_INVALID_DURABILITY = 164
    """ The application tried to create a receiver using a non-durable queue, but the referenced queue was a durable
    one."""
    SOLCLIENT_SUBCODE_AD_APP_ACK_FAILED_NOT_SUPPORTED = 165
    """
        FAILED and REJECTED message settlement outcomes not supported on the Solace Message Router.
    """
