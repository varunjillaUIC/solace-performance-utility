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

# pylint: disable=no-else-return

"""
The `MessagingService` (:py:class:`solace.messaging.messaging_service`) is an abstract class that
represents the Solace messaging service.

The ``MessagingService`` is used to:

- connect the service
- disconnect the service
- create a ``MessagePublisherBuilder``
- create a ``MessageReceiverBuilder``


The builder for the `MessagingService contains` the configuration to identify:

- a Solace event broker
- the client to the Solace Event Broker
- messaging service characteristics such as flow control
"""

# pylint: disable= missing-function-docstring,protected-access,too-many-lines,inconsistent-return-statements

import concurrent
import ctypes
import datetime
import enum
import json
import logging
import threading
import weakref
from abc import ABC, abstractmethod
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union, Any
from ctypes import c_void_p, cast, POINTER, c_char_p, byref, create_string_buffer

import solace
from solace.messaging import _SolaceServiceAdapter
from solace.messaging._messaging_service_utility import get_transmitted_statistic, get_received_statistic, \
    reset_statistics, get_transmitted_statistics, get_received_statistics, get_aggregate_statistics
from solace.messaging._solace_logging._core_api_log import set_log_file, set_core_api_log_level
from solace.messaging.builder._impl._direct_message_publisher_builder import _DirectMessagePublisherBuilder
from solace.messaging.builder._impl._direct_message_receiver_builder import _DirectMessageReceiverBuilder
from solace.messaging.builder._impl._transactional_message_receiver_builder import _TransactionalMessageReceiverBuilder
from solace.messaging.builder._impl._transactional_message_publisher_builder import  \
    _TransactionalMessagePublisherBuilder
from solace.messaging.builder._impl._message_publisher_builder import PublisherBackPressure
from solace.messaging.builder._impl._persistent_message_publisher_builder import _PersistentMessagePublisherBuilder
from solace.messaging.builder._impl._persistent_message_receiver_builder import _PersistentMessageReceiverBuilder
from solace.messaging.builder._impl._message_queue_browser_builder import _MessageQueueBrowserBuilder
from solace.messaging.builder._impl._request_reply_message_publisher_builder import _RequestReplyMessagePublisherBuilder
from solace.messaging.builder._impl._request_reply_message_receiver_builder import _RequestReplyMessageReceiverBuilder
from solace.messaging.builder.direct_message_publisher_builder import DirectMessagePublisherBuilder
from solace.messaging.builder.direct_message_receiver_builder import DirectMessageReceiverBuilder
from solace.messaging.builder.persistent_message_publisher_builder import PersistentMessagePublisherBuilder
from solace.messaging.builder.persistent_message_receiver_builder import PersistentMessageReceiverBuilder
from solace.messaging.builder.message_queue_browser_builder import MessageQueueBrowserBuilder
from solace.messaging.builder.transactional_message_receiver_builder import TransactionalMessageReceiverBuilder
from solace.messaging.builder.transactional_message_publisher_builder import TransactionalMessagePublisherBuilder
from solace.messaging.config._ccsmp_property_mapping import DEFAULT_PROP, REQUIRED_PROPS, EXCLUDED_PROPS, \
    rectifiable_service_props
from solace.messaging.config._sol_constants import SOLCLIENT_SESSION_PROP_DEFAULT_COMPRESSION_LEVEL, \
    _SOLCLIENTSTATSRX, _SOLCLIENTSTATSTX, SOLCLIENT_SENT_STATS, SOLCLIENT_RECEIVED_STATS, SOLCLIENT_OK, \
    INTERNAL_PYTHON_STATS, SOLCLIENT_SESSION_PROP_USER_ID, SOLCLIENT_SESSION_PROP_CLIENT_NAME, \
    SOLCLIENT_ROLLBACK, SOLCLIENT_TRANSACTEDSESSION_PROP_CREATE_MESSAGE_DISPATCHER, SOLCLIENT_PROP_ENABLE_VAL, \
    SOLCLIENT_SUB_CODE_OK, _CCSMP_AGGREGATE_STATS
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, CCSMP_INFO_SUB_CODE, \
    TRANSACTIONAL_MESSAGE_SERVICE_NOT_ATTEMPTED_TO_CONNECT, \
    CANNOT_UPDATE_SERVICE_PROPERTY_FOR_DISCONNECTED_OR_DISCONNECTING_SERVICE, CANNOT_UPDATE_INVALID_SERVICE_PROPERTY, \
    CANNOT_UPDATE_SERVICE_PROPERTY_WITH_INVALID_VALUE
from solace.messaging.config._solace_message_constants import RECONNECTION_LISTENER_SHOULD_BE_TYPE_OF, \
    RECONNECTION_ATTEMPT_LISTENER_SHOULD_BE_TYPE_OF, STATS_ERROR, INTERRUPTION_LISTENER_SHOULD_BE_TYPE_OF, \
    UNSUPPORTED_METRIC_TYPE, ERROR_WHILE_RETRIEVING_METRIC, BROKER_MANDATORY_KEY_MISSING_ERROR_MESSAGE, \
    BROKER_MANDATORY_MINIMUM_ONE_KEY_MISSING_ERROR_MESSAGE, DISPATCH_FAILED, \
    UNABLE_TO_CONNECT_ALREADY_DISCONNECTED_SERVICE, MESSAGE_SERVICE_CONNECTION_IN_PROGRESS, \
    MESSAGE_SERVICE_DISCONNECT_ALREADY, RECONNECTION_ATTEMPT_LISTENER_NOT_EXISTS, RECONNECTION_LISTENER_NOT_EXISTS, \
    MESSAGE_SERVICE_NOT_ATTEMPTED_TO_CONNECT, BROKER_EXCLUDED_PROPERTY, TRANSACTIONAL_MESSAGE_SERVICE_NOT_CONNECTED, \
    MESSAGE_SERVICE_NOT_CONNECTED, TRANSACTIIONAL_OPERATION_UNDERWAY, CCSMP_CALLER_DESC, CCSMP_RETURN_CODE, \
    CCSMP_SUB_CODE_OK, CCSMP_INFO_CONTENTS
from solace.messaging.config.authentication_strategy import AuthenticationStrategy, AuthenticationConfiguration
from solace.messaging.config.property_based_configuration import PropertyBasedConfiguration
from solace.messaging.config.retry_strategy import RetryConfigurationProvider, RetryStrategy
from solace.messaging.config.solace_properties import client_properties
from solace.messaging.config.solace_properties.authentication_properties import SCHEME, \
    SCHEME_OAUTH2_ACCESS_TOKEN, SCHEME_OAUTH2_OIDC_ID_TOKEN
from solace.messaging.config.solace_properties.transport_layer_properties import COMPRESSION_LEVEL
from solace.messaging.config.solace_properties.transactional_service_properties import \
    TRANSACTIONAL_SERVICE_REQUEST_TIMEOUT
from solace.messaging.config.transport_protocol_configuration import TransportProtocolConfiguration
from solace.messaging.config.transport_security_strategy import TransportSecurityStrategy

from solace.messaging.connections.async_connectable import AsyncConnectable
from solace.messaging.connections.connectable import Connectable
from solace.messaging.core import _solace_session
from solace.messaging.core._publish import _BasicSolacePublisher, _SerializedSolacePublisher
from solace.messaging.core._receive import _BasicSolaceReceiver
from solace.messaging.errors.pubsubplus_client_error import InvalidDataTypeError, \
    IllegalStateError, PubSubPlusClientError, PubSubPlusCoreClientError, \
    UnknownTransactionStateError, TransactionRollbackError, TransactionError, IllegalArgumentError
from solace.messaging.core._solace_transport import _SolaceTransportEvent
from solace.messaging.publisher._impl._outbound_message import _OutboundMessageBuilder
from solace.messaging.publisher.outbound_message import OutboundMessageBuilder
from solace.messaging.utils._solace_utilities import get_last_error_info, handle_none_for_str, is_type_matches, \
    executor_shutdown, COMPLETED_FUTURE, _SolaceThread, Holder, _PubSubPlusQueue, QueueShutdown, _Released, \
    convert_config
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.utils.error_monitoring import ErrorMonitoring
from solace.messaging.utils.manageable import Metric, ApiMetrics, Manageable, ApiInfo, TransactionalServiceInfo
from solace.messaging.core._core_api_utility import prepare_array
from solace.messaging.config._ccsmp_property_mapping import CCSMP_SESSION_PROP_MAPPING
from solace.messaging.config.sub_code import SolClientSubCode as SC
from solace.messaging._impl._transactional_error_subcodes import transactional_subcode_list
from solace.messaging.core._solace_transport import _SolaceTransportEventInfo

logger = logging.getLogger('solace.messaging.connections')

__all__ = ['MessagingServiceClientBuilder', 'ServiceEvent', 'MessagingService', 'ServiceInterruptionListener',
           'ReconnectionListener', 'ReconnectionAttemptListener', 'RequestReplyMessagingService',
           'TransactionalMessagingService', 'TransactionalMessagingServiceBuilder']


class ServiceEvent(ABC):
    """
    This class represents an event that can occur asynchronously on a
    :py:class:`solace.messaging.messaging_service.MessagingService` object.
    Applications that are interested in ``ServiceEvent`` objects must register a listener for the one of interest.

    The available listeners for service events are listed below.

        - :py:class:`ReconnectionListener`: Handle service events. These events indicate that the service reconnected.

        - :py:class:`ReconnectionAttemptListener`: Handles events indicating service disconnected, reconnection status.

    """

    @abstractmethod
    def get_time_stamp(self) -> float:
        """
        Retrieves the timestamp of the event.

        Returns:
            float: The time the event occurred.
        """

    @abstractmethod
    def get_message(self) -> str:
        """
        Retrieves the message contents.

        Returns:
            str: An informational string that describes in further detail the cause of the event.
        """

    @abstractmethod
    def get_cause(self) -> 'PubSubPlusClientError':
        """
        Retrieves the cause of the client exception
        (:py:class:`solace.messaging.errors.pubsubplus_client_error.PubSubPlusClientError`).

        Returns:
            PubSubPlusClientError: The client error for the event.
        """

    @abstractmethod
    def get_broker_uri(self) -> str:
        """
        Retrieves the URI of the event broker.

        Returns:
            str: The event broker URI associated with the Messaging Service.
        """


class _ServiceEvent(ServiceEvent):  # pylint: disable=missing-class-docstring
    # implementation of service event abstract class

    def __init__(self, broker_uri: str, original_exception: PubSubPlusClientError, message: str,
                 time_stamp: float = datetime.datetime.now(datetime.timezone.utc)):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self.time_stamp = time_stamp
        self.broker_uri = broker_uri
        self.cause = original_exception
        self.message = message

    def get_time_stamp(self) -> float:
        # :returns: timestamp
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Get timestamp: [%f]', self.time_stamp)
        return self.time_stamp

    def get_message(self) -> str:
        #  :returns: message

        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Get message: [%s]', self.message)
        return self.message

    def get_broker_uri(self) -> str:
        #  :returns: broker uri
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Get broker uri: [%s]', self.broker_uri)
        return self.broker_uri

    def get_cause(self) -> 'PubSubPlusClientError':
        #  Returns: cause
        if self.cause:
            cause = self.cause.args[0]
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Get cause: [%s]', cause)
            return PubSubPlusClientError(cause)
        return None


class ReconnectionListener(ABC):
    """A class interface definition for a ``ReconnectionListener``
    Applications interested in ``Reconnection`` events must instantiate
    an object implementing the ``ReconnectionListener`` class and register
    the listener with ``MessagingService.add_reconnection_listener()``.
    """

    @abstractmethod
    def on_reconnected(self, service_event: ServiceEvent):
        """
        Callback invoked by ``MessagingService`` (:py:class:`solace.messaging.messaging_service.MessagingService`)
        object when it is successfully reconnected.

        Args:
            service_event (ServiceEvent):  The detailed information for the event.

        """


class ListenerThread(_SolaceThread):  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Thread used to dispatch received messages on a receiver.

    def __init__(self,
                 owner_info: str, owner_logger: 'logging.Logger', listener_queue: '_PubSubPlusQueue', *args, **kwargs):
        super().__init__(owner_info, owner_logger, *args, **kwargs)
        self._queue = listener_queue

    def _on_join(self):
        self._queue.shutdown()

    def run(self):

        def dispatch_event(event_handler, service_event):
            try:
                event_handler(service_event)
            except Exception as exception:  # pylint: disable=broad-except
                self.adapter.warning("%s %s", DISPATCH_FAILED, str(exception))

        # Start running thread
        self.adapter.debug('THREAD: [%s] started', type(self).__name__)
        while self._is_running.is_set():
            try:
                # This will block until there is a listener callback on the queue or until the queue is shutdown
                event_handler, service_event = self._queue.get()
            except QueueShutdown as error:
                self.adapter.debug(f"Listener queue was shutdown with the following messge: {str(error)}. "\
                                   f"Executing remaining listener callbacks now.")
                break
            dispatch_event(event_handler, service_event)

        # We need to drain the queue and execute the listener callbacks in case the queue was shutdown before all
        # the callbacks were executed for some reason.
        drained_queue_contents = self._queue.drain()
        for event_handler, service_event in drained_queue_contents:
            dispatch_event(event_handler, service_event)
        self.adapter.debug('THREAD: [%s] exited', type(self).__name__)


class ReconnectionAttemptListener(ABC):
    """
       A class interface definition for a reconnection attempt event listener.
       Applications that are interested in ``ReconnectionAttempt`` events must instantiate
       an object implementing the ReconnectionAttemptListener class and register
       the listener with ``MessagingService.add_reconnection_attempt_listener``.
    """

    @abstractmethod
    def on_reconnecting(self, event: 'ServiceEvent'):
        """
        Callback executed for the ``MessagingService`` connection fails and reconnection attempts begin.

        Args:
            event (ServiceEvent): The Reconnection event with detailed information for each reconnection attempt.

        """


class ServiceInterruptionListener(ABC):
    """An interface that abstracts notification about non recoverable service interruption."""

    @abstractmethod
    def on_service_interrupted(self, event: ServiceEvent):
        """Callback executed in situation when connection goes down and cannot be successfully restored.

        Args:
            event: The service interruption event describing nature of the failure.
        """

class _TransactionalServiceInfo(TransactionalServiceInfo):
    def __init__(self, name):
        self._name = name
    def get_transactional_service_id(self) -> Union[str, None]:
        return self._name

class TransactionalSupport(ABC):
    """ An interface for the high-level requirements for transactional support. """

    def commit(self):
        """
          Commits all messages based on this following:
            - For all messages published to the broker within given transaction, 'commit' allows the Solace Event
              Broker to deliver them.
            - For all messages received in a given transaction 'commit' allows broker to delete them on a broker.
          After commit is called, a 'new' transactions are automatically started for publisher and receiver
            if any associated.

          Raises:
              TransactionRollbackError: can be thrown if commit fails and broker indicates rollback.
                This starts a new transaction.
              UnknownTransactionStateError: can be thrown when transaction state is lost
                and can not be recovered between the remote broker and client service.
                In this case it is unknown whether the borker completed the transaction or not.
              PubSubPlusClientError: can be thrown if the service has an error on commit

        """
    def rollback(self):
        """
          Forces a broker to redeliver all messages and/or remove messages that were published as part
          of a rolled-back transaction.

          Raises:
            PubSubPlusClientError: can be thrown if the service has an error on rollback

        """


class TransactionalMessagingService(TransactionalSupport, Connectable, ABC):
    """
      An interface for transactional (non-XA, broker transacted session) use case of a Solace event broker.
      Transactions are feature of the Solace event broker, client just enables broker-side transactional support.
    """
    def create_transactional_message_receiver_builder(self) -> 'TransactionalMessageReceiverBuilder':
        """
          Creates a transactional message receiver builder instance.
        """
    def create_transactional_message_publisher_builder(self) -> 'TransactionalMessagePublisherBuilder':
        """
          Creates a transactional message publisher builder instance.
        """
    def transactional_service_info(self) -> TransactionalServiceInfo:
        """
          Provides access to the advanced information about transactional service at runtime.

          Returns:
            TransactionalServiceInfo: to access advanced information about the
              transactional messaging service.

        """

class _TransactionalMessagingService(TransactionalMessagingService):  # pylint: disable=too-many-public-methods

    # pylint: disable=missing-class-docstring,too-many-instance-attributes
    def __init__(self, config: dict, messaging_service: 'MessagingService'):
        # add props received from builder
        self._config = convert_config(config, CCSMP_SESSION_PROP_MAPPING)
        self._config[SOLCLIENT_TRANSACTEDSESSION_PROP_CREATE_MESSAGE_DISPATCHER] = SOLCLIENT_PROP_ENABLE_VAL
        # Supposed to set the window size to 255 and publisher on here, but those are the defaults anyway.
        self._messaging_service = messaging_service
        self._transacted_session_p = c_void_p(None)
        self._connected = False
        self._executor = ThreadPoolExecutor(thread_name_prefix="_TransactionalMessagingService ", max_workers=1)
        self._threadlocal = threading.local()
        # This is how we'll know we are already on the executor's thread:
        def mark_my_thread():
            self._threadlocal.tms_thread = True
        self._executor.submit(mark_my_thread)
        self._id_info = f"{self._messaging_service.logger_id_info} - " \
                        f"[TRANSACTIONAL MESSAGING SERVICE: {str(hex(id(self)))}]"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        self._session_name = None
        # does this need to be non-local? Does the scoping help with the lifecycle maybe?
        self._props_arr = None
        self._shutdown_callbacks = []
        self._service_down_id = None
        # This is for SOL-77361.
        # The purpose of this lock is to call out unsupported concurrent access patterns:
        # It is held for the duration of the message dispatch callback and every transacted operation.
        # Only the message dispatch blocks to acquire it, user-triggered operations throw an exception instead.
        self._commit_lock = threading.RLock()

    def _on_executor_thread(self) -> bool:
        return getattr(self._threadlocal, "tms_thread", False)
    def _on_dispatch_thread(self) -> bool:
        return getattr(self._threadlocal, "dispatch_thread", False)
    def _mark_dispatch_thread(self):
        self._threadlocal.dispatch_thread = True

    # Could be a decorator, but let's not push it :-)
    def _run(self, job, *args, **kwargs):
        if self._on_executor_thread() or self._on_dispatch_thread():
            return job(*args, **kwargs)
        else:
            return self._executor.submit(job, *args, **kwargs).result()

    def _run_later(self, *args, **kwargs) -> concurrent.futures.Future:
        return self._executor.submit(*args, **kwargs)

    @property
    def logger_id_info(self):
        return self._id_info

    def connect(self) -> TransactionalMessagingService: # pylint: disable=protected-access
        return self._run(self._connect_job)

    def _connect_job(self) -> TransactionalMessagingService: # pylint: disable=protected-access
        # Method to start transactional session.
        # Automatically starts the first transaction.

        if self._config:
            self._props_arr = prepare_array(self._config)
        ret = solace.CORE_LIB.solClient_session_createTransactedSession(
            cast(self._props_arr, POINTER(c_char_p)),
            self._messaging_service.session_pointer,
            byref(self._transacted_session_p),
            None)
        if ret in [SOLCLIENT_OK]:
            buff_size = 255
            session_name_buffer = create_string_buffer(buff_size)
            solace.CORE_LIB.solClient_transactedSession_getSessionName(self._transacted_session_p,
                                                                       session_name_buffer,
                                                                       buff_size)
            self._session_name = session_name_buffer.value.decode("utf-8")
            logger.debug('Underlying transacted session SessionName: %s', self._session_name)
            self._connected = True

            self._service_down_id = self._messaging_service._transport_event_emitter \
                .register_transport_event_handler(_SolaceTransportEvent.TRANSPORT_DOWN, self._service_down_callback)

            return self

        core_exception_msg = last_error_info(status_code=ret,
                                             caller_desc='On TRANSACTIONAL SESSION CONNECT')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Unsuccessful transactional session creation (connect()).'
                         ' Return code:%s \nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         ret,
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        raise PubSubPlusClientError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                    message=core_exception_msg["error_info_contents"])

    def _add_shutdown_callback(self, callback):
        self._shutdown_callbacks.append(callback)

    def _remove_shutdown_callback(self, callback):
        try:
            self._shutdown_callbacks.remove(callback)
        except ValueError:
            pass

    # This method does everthig BUT the transactedSession_destroy call.
    def _shutdown(self, event=None):
        self._connected = False
        self._messaging_service._transport_event_emitter.unregister_transport_event_handler(self._service_down_id)
        callbacks = self._shutdown_callbacks.copy()
        for callback in callbacks:
            callback(event)

    def _service_down_callback(self, event: '_SolaceTransportEventInfo'):
        logger.debug('Service shutdown event: %s', event)
        self._shutdown(event)

    def disconnect(self):  # pylint: disable=protected-access
        return self._run(self._disconnect_job)

    def _disconnect_job(self):  # pylint: disable=protected-access
        # Method to stop transactional session.
        if not self._connected:
            raise IllegalStateError(TRANSACTIONAL_MESSAGE_SERVICE_NOT_ATTEMPTED_TO_CONNECT)
        ret = solace.CORE_LIB.solClient_transactedSession_destroy(byref(self._transacted_session_p))
        # create _SolaceTransportEventInfo and pass it to shutdown():

        event_message = {CCSMP_CALLER_DESC: 'SolaceApi->disconnect',
                         CCSMP_RETURN_CODE: SOLCLIENT_OK,
                         CCSMP_SUB_CODE: CCSMP_SUB_CODE_OK,
                         CCSMP_INFO_SUB_CODE: SOLCLIENT_SUB_CODE_OK,
                         CCSMP_INFO_CONTENTS: "The application disconnected the transactional messaging service."}
        self._shutdown(_SolaceTransportEventInfo(self.adapter, "", "", event_message))
        if ret in [SOLCLIENT_OK]:
            return ret

        core_exception_msg = last_error_info(status_code=ret,
                                             caller_desc='On COMMIT')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Unsuccessful transactional session disconnect.'
                         ' Return code:%s \nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         ret,
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        raise PubSubPlusClientError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                    message=core_exception_msg["error_info_contents"])

    @property
    def is_connected(self) -> bool:
        return self._connected

    def create_transactional_message_receiver_builder(self) -> TransactionalMessageReceiverBuilder:
        return _TransactionalMessageReceiverBuilder(self._config, self)

    def create_transactional_message_publisher_builder(self) -> TransactionalMessagePublisherBuilder:
        return _TransactionalMessagePublisherBuilder(self._config, self)

    def commit(self):
        return self._run(self._commit_job)

    def _commit_job(self):
        if not self.is_connected:
            raise IllegalStateError(TRANSACTIONAL_MESSAGE_SERVICE_NOT_CONNECTED)
        if not self.is_connected:
            raise IllegalStateError(MESSAGE_SERVICE_NOT_CONNECTED)

        if self._commit_lock.acquire(blocking=False):  # pylint: disable=consider-using-with
                                                       # We don't use `with` because we need the `if` statement
            try:
                ret = solace.CORE_LIB.solClient_transactedSession_commit(self._transacted_session_p)
            finally:
                self._commit_lock.release()
        else:
            raise TransactionError(TRANSACTIIONAL_OPERATION_UNDERWAY)

        if ret in [SOLCLIENT_OK]:
            return None

        core_exception_msg = last_error_info(status_code=ret,
                                             caller_desc='On COMMIT')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Unsuccessful commit. Return code:%s \nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         ret,
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        if ret == SOLCLIENT_ROLLBACK:
            raise TransactionRollbackError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                           message=core_exception_msg["error_info_contents"])
        if SC.SOLCLIENT_SUBCODE_COMMIT_STATUS_UNKNOWN.name == core_exception_msg[CCSMP_SUB_CODE]:
            raise UnknownTransactionStateError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                               message=core_exception_msg["error_info_contents"])
        if core_exception_msg[CCSMP_SUB_CODE] in transactional_subcode_list:
            raise TransactionError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                   message=core_exception_msg["error_info_contents"])
        raise PubSubPlusClientError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                    message=core_exception_msg["error_info_contents"])


    def rollback(self):
        return self._run(self._rollback_job)

    def _rollback_job(self):
        if not self.is_connected:
            raise IllegalStateError(TRANSACTIONAL_MESSAGE_SERVICE_NOT_CONNECTED)
        if not self.is_connected:
            raise IllegalStateError(MESSAGE_SERVICE_NOT_CONNECTED)

        if self._commit_lock.acquire(blocking=False):  # pylint: disable=consider-using-with
                                                       # We don't use `with` here because we need the `if` statement
            try:
                ret = solace.CORE_LIB.solClient_transactedSession_rollback(self._transacted_session_p)
            finally:
                self._commit_lock.release()
        else:
            raise TransactionError(TRANSACTIIONAL_OPERATION_UNDERWAY)

        if ret in [SOLCLIENT_OK]:
            return None

        core_exception_msg = last_error_info(status_code=ret,
                                             caller_desc='On ROLLBACK')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Unsuccessful rollback. Return code:%s \n'
                         'Sub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         ret,
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])

        if SC.SOLCLIENT_SUBCODE_COMMIT_STATUS_UNKNOWN.name == core_exception_msg[CCSMP_SUB_CODE]:
            raise UnknownTransactionStateError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                               message=core_exception_msg["error_info_contents"])
        if core_exception_msg[CCSMP_SUB_CODE] in transactional_subcode_list:
            raise TransactionError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                   message=core_exception_msg["error_info_contents"])
        raise PubSubPlusClientError(sub_code=core_exception_msg[CCSMP_SUB_CODE],
                                    message=core_exception_msg["error_info_contents"])

    def add_reconnection_attempt_listener(self,
                                          listener: 'ReconnectionAttemptListener') -> TransactionalMessagingService:
        self._messaging_service.add_reconnection_attempt_listener(listener)
        return self

    def add_reconnection_listener(self, listener: 'ReconnectionListener') -> TransactionalMessagingService:
        self._messaging_service.add_reconnection_listener(listener)
        return self

    def remove_reconnection_attempt_listener(self,
                                             listener: 'ReconnectionAttemptListener') -> TransactionalMessagingService:
        self._messaging_service.remove_reconnection_attempt_listener(listener)
        return self

    def remove_reconnection_listener(self, listener: 'ReconnectionListener') -> TransactionalMessagingService:
        self._messaging_service.remove_reconnection_listener(listener)
        return self

    def get_session_name(self) -> str:
        return self._session_name

    def transactional_service_info(self) -> TransactionalServiceInfo:
        return _TransactionalServiceInfo(self._session_name)

class TransactionalMessagingServiceBuilder(PropertyBasedConfiguration):
    """
        An interface to create transactional (non-XA) messaging service with a Solace event broker.
        Transactions are feature of the Solace event broker, client just enables broker-side
        transactional support.
    """
    #def __init__(self, messaging_service: MessagingService):
    def __init__(self, messaging_service):
        # MessagingServiceClient builder
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._messaging_service = messaging_service
        self._stored_config = {}

    def from_properties(self, configuration: dict) -> 'TransactionalMessagingServiceBuilder':
        """
        Passes a configuration dictionary for configuration information.

        Args:
             configuration(dict): Pass a configuration dictionary.

        Returns:
            TransactionalMessagingServiceBuilder: An object for method chaining.
        """
        if isinstance(configuration, dict):
            self._stored_config = {**self._stored_config, **configuration}
        return self

    def set_transaction_request_timeout(self, timeout: int = 10000) -> 'TransactionalMessagingServiceBuilder':
        """
            Timeout (in milliseconds) to wait for a response. Default is 10000.
            This is used for service requests like connect, disconnect, commit and rollback.
            Args:
                timeout(int): time in milliseconds, the minimum configuration value is 1000.
        """
        is_type_matches(timeout, int, ignore_none=True, logger=logger)
        if timeout is not None and timeout > 1000:
            self._stored_config[TRANSACTIONAL_SERVICE_REQUEST_TIMEOUT] = timeout
        return self

    def build(self) -> 'TransactionalMessagingService':
        """
            Creates a new instance of transactional messaging service using the configuration provided by
            self instance of a builder.

            Returns:
                TransactionalMessagingService: a new immutable instance
                of a TransactionalMessagingService to be used for
                transactional message publishing or receive purposes
        """
        return _TransactionalMessagingService(config=self._stored_config, messaging_service=self._messaging_service)


class MessagingService(Connectable, AsyncConnectable, Manageable, ErrorMonitoring, ABC):
    """
    This is an abstract class for the messaging service and inherits ``Connectable``, ``AsyncConnect``, ``Manageable``,
    and ``ErrorMonitoring``. It contains abstract methods for connecting, disconnecting a service in both blocking
    and non-blocking mode and also contains the factory methods to create builders for a
    message receiver (:py:class:`solace.messaging.builder.message_receiver_builder.MessageReceiverBuilder`)
    and message publishers (:py:class:`solace.messaging.builder.message_publisher_builder.MessagePublisherBuilder`).
    """

    @abstractmethod
    def create_direct_message_receiver_builder(self) -> DirectMessageReceiverBuilder:
        """
        Defines the interface for a builder to create direct message receiver.

        Returns:
            DirectMessageReceiverBuilder: An DirectMessageReceiverBuilder object.
        """

    @abstractmethod
    def create_direct_message_publisher_builder(self) -> DirectMessagePublisherBuilder:
        """
        Defines the interface for a builder to create a direct message publisher.

        Returns:
            DirectMessagePublisherBuilder: An DirectMessagePublisherBuilder object.
        """

    @abstractmethod
    def create_persistent_message_receiver_builder(self) -> PersistentMessageReceiverBuilder:
        """
        Defines the interface for a builder to create a persistent message receiver.

        Returns:
            PersistentMessageReceiverBuilder: An PersistentMessageReceiverBuilder object.

        """

    @abstractmethod
    def create_persistent_message_publisher_builder(self) -> PersistentMessagePublisherBuilder:
        """
        Defines the interface for a builder to create a persistent message publisher.

        Returns:
            PersistentMessagePublisherBuilder: An PersistentMessagePublisherBuilder object.
        """
    @abstractmethod
    def create_message_queue_browser_builder(self) -> MessageQueueBrowserBuilder:
        """
        Defines the interface for a builder to create a persistent message queue browser.
        Returns:
            MessageQueueBrowserBuilder: An MessageQueueBrowserBuilder object.
        """

    @abstractmethod
    def get_application_id(self) -> str:
        """
        Retrieves the application identifier.

        Returns:
           The application identifier.
        """

    @abstractmethod
    def request_reply(self) -> 'RequestReplyMessagingService':
        """Creates RequestReplyMessagingService that inherits entire configuration from this instance.

        Returns:
            new instance of :py:class:`solace.messaging.messaging_service.RequestReplyMessagingService`"""

    @abstractmethod
    def message_builder(self) -> OutboundMessageBuilder:
        """
        Defines the interface for a builder to create an outbound message.

        Returns:
            OutboundMessageBuilder: An OutboundMessageBuilder object.

        Raises:
            PubSubPlusClientError: If there was an error in creating the message builder.
        """

    @abstractmethod
    def create_transactional_service_builder(self) -> 'TransactionalMessagingServiceBuilder':
        """
            Creates a {@link TransactionalMessagingServiceBuilder} that is used to configure and create
            transactional messaging service instances
            Returns:
                 TransactionalMessagingServiceBuilder: new instance of TransactionalMessagingServiceBuilder
        """

    @staticmethod
    def builder() -> 'MessagingServiceClientBuilder':
        """
        Retrieves a ``MessagingServiceClientBuilder`` object.

        Returns:
            MessagingServiceClientBuilder: A builder object for the message service.
        """
        return MessagingServiceClientBuilder()

    @staticmethod
    def set_core_messaging_log_level(level: str, file=None):
        """
        Sets the core (Native) API log level. The Native API only generates logs at the given level or higher,
        which may be further filtered by Python logging.

        WARNING:
            Don't set the message log level to be too high or you'll impact the
            messaging service performance. For example, though it may seem like a good idea
            to set the core log level to a **DEBUG** level and then rely on Python logging to filter the logs,
            doing so severely affects the  messaging service performance. For this reason, don't do this.
            The core log level must be set lower than **WARNING** as a diagnostic aid.

        Args:
            file(str): The name of the file.
            level(str): A valid string representation of the Python logging level you want using one of the
              following values (ordered from lowest to highest), CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.

        """
        set_log_file(file)
        set_core_api_log_level(level)

    @abstractmethod
    def update_property(self, name: str, value: Any):
        """
        Updates the value of a modifiable service property once the service has been created.
        Modifiable service properties include:

            * :py:const:`SCHEME_OAUTH2_ACCESS_TOKEN<solace.messaging.config.solace_properties.authentication_properties.SCHEME_OAUTH2_ACCESS_TOKEN>`,
              whose update will be applied during the next reconnection attempt.
            * :py:const:`SCHEME_OAUTH2_OIDC_ID_TOKEN<solace.messaging.config.solace_properties.authentication_properties.SCHEME_OAUTH2_OIDC_ID_TOKEN>`,
              whose update will be applied during the next reconnection attempt.

        Modification of a service property may occur instantly, or may occur during the next
        service reconnection.
        Modification of a service property during an ongoing service reconnection may apply
        to the next reconnection attempt.

        Args:
            name(str): The name of the property to modify.
            value(Any): The new value of the property.

        Raises:
            IllegalArgumentError: If the specified property cannot be modified.
            IllegalStateError: If the specified property cannot
                be modified in the current service state.
            PubSubPlusClientError: If other transport or communication related errors occur.
        """  # pylint: disable=line-too-long
        # Although this method is inherited from UpdatableConfiguration, it needs to be redefined
        # here so that we can override the doc string with notes specific to the MessagingService class.


class RequestReplyMessagingService(ABC):
    """
    An interface that abstracts request-reply behavior.
    """

    @abstractmethod
    def create_request_reply_message_receiver_builder(self) -> 'RequestReplyMessageReceiverBuilder':
        """Abstract method to create request reply receiver builder Class

        Returns:
            RequestReplyMessageReceiverBuilder instance
        """

    @abstractmethod
    def create_request_reply_message_publisher_builder(self) -> 'RequestReplyMessagePublisherBuilder':
        """Abstract method to create request reply publisher builder Class

        Returns:
            RequestReplyMessagePublisherBuilder instance
        """

class _RequestReplyMessagingService(RequestReplyMessagingService):
    def __init__(self, messaging_service: "MessagingService"):
        self._messaging_service = messaging_service

    def create_request_reply_message_receiver_builder(self) -> 'RequestReplyMessageReceiverBuilder':
        return _RequestReplyMessageReceiverBuilder(self._messaging_service)

    def create_request_reply_message_publisher_builder(self) -> 'RequestReplyMessagePublisherBuilder':
        return _RequestReplyMessagePublisherBuilder(self._messaging_service)


class _ApiInfo(ApiInfo):  # pylint: disable=missing-class-docstring
    def __init__(self, messaging_service: 'MessagingService'):
        session = messaging_service.session

        parsed_api_info = session.parsed_api_info

        self.__api_build_timestamp = parsed_api_info.api_build_timestamp
        self.__api_vendor = parsed_api_info.api_vendor
        self.__api_version = parsed_api_info.api_version
        self.__api_user_id = session.get_session_property(SOLCLIENT_SESSION_PROP_USER_ID)

    def get_api_build_date(self) -> Union[str, None]:
        # Retrieves the API build date in the form `yyyy-mm-dd HH:mm:ss/yyyy-mm-dd HH:mm:ss`
        # where the first entry is the build date of the wrapper API and the second entry is
        # the build date of the core API.
        return self.__api_build_timestamp

    def get_api_version(self) -> Union[str, None]:
        # Retrieves the API version in the form `<MAJOR.MINOR.PATCH>/<MAJOR.MINOR.PATCH>`
        # where the first entry is the version of the wrapper API and the second entry is
        # the build date of the core API, and where both of these versions follow semantic
        # versioning
        return self.__api_version

    def get_api_user_id(self) -> Union[str, None]:
        # Retrieves the API user identifier that was reported to the event broker
        return self.__api_user_id

    def get_api_implementation_vendor(self) -> Union[str, None]:
        # Retrieves the vendor of the API implementation, i.e. the party selling this API
        return self.__api_vendor


class _ApiMetrics(ApiMetrics):  # pylint: disable=missing-class-docstring
    def __init__(self, messaging_service):
        self._messaging_service = messaging_service
        self._metrics_lock = threading.Lock()
        self._config = {Metric.RECEIVED_MESSAGES_TERMINATION_DISCARDED.value: 0,
                        Metric.PUBLISH_MESSAGES_TERMINATION_DISCARDED.value: 0,
                        Metric.RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED.value: 0,
                        Metric.INTERNAL_DISCARD_NOTIFICATIONS.value: 0}

    def get_value(self, the_metric: Metric) -> int:
        # Returns the metrics current value/count
        try:
            if the_metric.value in _SOLCLIENTSTATSTX.__members__:
                return get_transmitted_statistic(self._messaging_service.session_pointer,
                                                 _SOLCLIENTSTATSTX[the_metric.value].value)
            if the_metric.value in _SOLCLIENTSTATSRX.__members__:
                stats = get_received_statistic(self._messaging_service.session_pointer,
                                              _SOLCLIENTSTATSRX[the_metric.value].value)
                dup_ack = self._messaging_service.duplicate_ack
                if  dup_ack > 0 and the_metric.value == Metric.PERSISTENT_MESSSAGES_ACCEPTED.value:
                    return stats - dup_ack
                return stats
            if the_metric.value in INTERNAL_PYTHON_STATS:
                return self._config[the_metric.value]
            if the_metric.value in _CCSMP_AGGREGATE_STATS:
                return get_aggregate_statistics(self._messaging_service.session_pointer,
                                                _CCSMP_AGGREGATE_STATS[the_metric.value])

            return None
        except AttributeError as exception:
            logger.warning("%s Exception %s", UNSUPPORTED_METRIC_TYPE, exception)
            raise InvalidDataTypeError(f'{UNSUPPORTED_METRIC_TYPE} {exception}') from exception
        except Exception as exception:
            logger.warning("%s Exception %s", ERROR_WHILE_RETRIEVING_METRIC, exception)
            raise PubSubPlusClientError(f'{ERROR_WHILE_RETRIEVING_METRIC} {exception}') from exception

    def reset(self):
        # Resets ALL stats
        reset_statistics(self._messaging_service.session_pointer)
        with self._metrics_lock:
            self._config = dict((k, 0) for k in self._config)

    @staticmethod
    def __get_stats(arr, stat_info, api_metric) -> dict:
        # Method for getting the statistics
        stats = {}
        arr_list = list(arr)
        api_metrics_values = set(item.value for item in Metric)
        for metric_type, metric_value in enumerate(arr_list):
            stats[stat_info(metric_type).name] = metric_value
            if stat_info(metric_type).name in api_metrics_values:
                for data in Metric:
                    if data.value == stat_info(metric_type).name:
                        api_metric[data.name] = metric_value
                        break
        return stats

    def __get_all_stats(self):
        # Method to get all API metrics for both transmitted and received statistics.
        api_metrics = {}
        transmitted_core_metrics_arr = (ctypes.c_int64 * _SOLCLIENTSTATSTX[SOLCLIENT_SENT_STATS].value)()
        received_core_metrics_arr = (ctypes.c_int64 * _SOLCLIENTSTATSRX[SOLCLIENT_RECEIVED_STATS].value)()

        transmitted_metrics_status = get_transmitted_statistics(
            self._messaging_service.session_pointer,
            transmitted_core_metrics_arr)

        if transmitted_metrics_status != SOLCLIENT_OK:
            logger.warning(STATS_ERROR)
            raise PubSubPlusClientError(STATS_ERROR)

        self.__get_stats(transmitted_core_metrics_arr, _SOLCLIENTSTATSTX, api_metrics)

        received_metrics_status = get_received_statistics(self._messaging_service.session_pointer,
                                                          received_core_metrics_arr)

        if received_metrics_status != SOLCLIENT_OK:
            exception: PubSubPlusCoreClientError = get_last_error_info(return_code=received_metrics_status,
                                                                       caller_description='ApiMetrics->get_all_stats',
                                                                       exception_message=STATS_ERROR)
            logger.warning(str(exception))
            raise exception

        self.__get_stats(received_core_metrics_arr, _SOLCLIENTSTATSRX, api_metrics)

        return {**api_metrics, **self._config}  # also merge the python's internal stats with broker's stats

    def _increment_internal_stat(self, metric: Metric, value: int):
        if not metric.value.startswith('SOLCLIENT'):  # allow only python internal metrics
            with self._metrics_lock:
                self._config[metric.value] += value
        else:
            logger.warning("Attempting modify broker metrics : %s", metric.value)

    def __str__(self):
        # List of all in the API collected metrics
        return_value = handle_none_for_str(input_value=json.dumps(self.__get_all_stats()))
        return return_value


def service_cleanup(serial_publisher, executor):
    if serial_publisher:
        serial_publisher.shutdown()
    executor_shutdown(executor)


def listener_thread_cleanup(listener_thread_holder):
                            # pylint: disable=missing-function-docstring
    listener_thread = listener_thread_holder.value
    if listener_thread is not None and listener_thread.is_alive():
        listener_thread.join()


class _MessagingServiceState(enum.Enum):  # pylint: disable=too-few-public-methods
    NOT_CONNECTED = -1
    CONNECTING = 0
    CONNECTED = 1
    RECONNECTING = 2
    RECONNECTED = 3
    DISCONNECTING = 4
    DISCONNECTED = 5

class _BasicMessagingService(MessagingService):  # pylint: disable=too-many-public-methods

    # pylint: disable=missing-class-docstring,too-many-instance-attributes
    #  Class implements all the methods of the MessagingService class and also have implementation for the
    #  reconnection listener and reconnection attempt listener adding and removal
    GENERATED_APP_ID_PREFIX = 'app_'

    MODIFIABLE_SERVICE_PROPERTIES = {SCHEME_OAUTH2_ACCESS_TOKEN: str,
                                     SCHEME_OAUTH2_OIDC_ID_TOKEN: str}

    def __init__(self, **kwargs):  # pylint: disable=too-many-statements
        #
        # Args:
        #    **config (dict): Configuration details for creating messaging service
        #    **application_id (string) : application id value string or none
        #

        self._mutex = threading.Lock()
        with self._mutex:
            self._state = _MessagingServiceState.NOT_CONNECTED

        self._config = kwargs.get('config')  # stores the configuration values

        if self._config.get(client_properties.NAME) is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find client_properties.NAME in messaging service configuration.")
            self._application_id = kwargs.get('application_id')
        else:
            self._application_id = kwargs.get('application_id') or \
                                   self._config[client_properties.NAME]

        if self._application_id is None:
            self._id_info = f"[SERVICE: {str(hex(id(self)))}] - [APP ID: {str(self._application_id)}]"
            self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
            self._session = _solace_session._SolaceSession(self._id_info)  # this holds the instance of the SolaceApi

            self._session.create_session(self._config)  # create the session as part of Messaging Service build process
            self._application_id = self._session.get_session_property(SOLCLIENT_SESSION_PROP_CLIENT_NAME)

            self._id_info = f"[SERVICE: {str(hex(id(self)))}] - [APP ID: {str(self._application_id)}]"
            self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
            self._session.update_id_info(self._id_info)

        else:
            self._id_info = f"[SERVICE: {str(hex(id(self)))}] - [APP ID: {str(self._application_id)}]"
            self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
            self._session = _solace_session._SolaceSession(self._id_info)  # this holds the instance of the SolaceApi

            self._config[client_properties.NAME] = self._application_id
            self._session.create_session(self._config)  # create the session as part of Messaging Service build process

        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('[%s] initialized with application id[%s]', type(self).__name__, self._application_id)

        self._duplicate_ack = 0

        # create publisher wrappers
        self._serial_publisher = _SerializedSolacePublisher(self._session)
        self._basic_publisher = _BasicSolacePublisher(self._session)
        self._basic_receiver = _BasicSolaceReceiver(self)

        self._attempt_listeners = set()
        self._reconnection_listeners = set()
        self._service_interruption_listeners = set()

        self._listener = set()
        self._listener_queue = None
        self.attempt_listener_queue = None
        self.service_interruption_listener_queue = None

        # Register transport event handlers
        self._transport_event_emitter = self._session
        self._transport_event_handlers = {}
        self._register_transport_event_handlers()

        self._listener_thread = None
        self._listener_thread_holder = Holder()
        self._listener_thread_holder.value = self._listener_thread
        self._connect_future = None
        self._disconnect_future = None
        self.__api_metrics = _ApiMetrics(self)
        self.__api_info = _ApiInfo(self)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=type(self).__name__)
        # optin finalizer if the listener thread is made
        # will be run if the self._listener_thread is created
        # must be register before executor finalizer as disconnect_async could cause deadlock otherwise
        self._listener_service_finalizer = weakref.finalize(self, listener_thread_cleanup,
                                                            self._listener_thread_holder)
        # finalizer for known resources on the service
        self._service_finalizer = weakref.finalize(self, service_cleanup, self._serial_publisher, self._executor)

    def _register_transport_event_handlers(self):
        self._transport_event_handlers[_SolaceTransportEvent.TRANSPORT_UP] = \
            self._transport_event_emitter.register_transport_event_handler(_SolaceTransportEvent.TRANSPORT_UP,
                                                                           self._transport_up_event_handler)
        self._transport_event_handlers[_SolaceTransportEvent.TRANSPORT_DOWN] = \
            self._transport_event_emitter.register_transport_event_handler(_SolaceTransportEvent.TRANSPORT_DOWN,
                                                                           self._transport_down_event_handler)

        self._transport_event_handlers[_SolaceTransportEvent.TRANSPORT_RECONNECTING] = \
            self._transport_event_emitter.register_transport_event_handler(_SolaceTransportEvent.TRANSPORT_RECONNECTING,
                                                                           self._transport_reconnecting_event_handler)

        self._transport_event_handlers[_SolaceTransportEvent.TRANSPORT_RECONNECTED] = \
            self._transport_event_emitter.register_transport_event_handler(_SolaceTransportEvent.TRANSPORT_RECONNECTED,
                                                                           self._transport_reconnected_event_handler)

    def _unregister_transport_event_handlers(self):
        for transport_event_handler in self._transport_event_handlers:
            self._transport_event_emitter.unregister_transport_event_handler(transport_event_handler)

    @property
    def logger_id_info(self):
        return self._id_info

    @property
    def state(self) -> '_MessagingServiceState':
        return self._state

    @property
    def session(self):  # pylint: disable=missing-function-docstring
        # this is a property which returns the SolaceApi instance
        return self._session

    @property
    def duplicate_ack(self):
        return self._duplicate_ack

    def _increase_duplicate_ack_count(self):
        self._duplicate_ack += 1

    def _on_service_down(self, ctx=None):  # pylint: disable=unused-argument
        # Unregister transport event handlers
        self._unregister_transport_event_handlers()
        # Callback into the service on underlying transport going unrecoverably down.

        # Calling this finalizer can potentially join the listener thread from the
        # calling thread.
        # Currently only the context thread calls this method only
        # on session down event. Meaning there is no network
        # connectivity for blocking calls to ccsmp so using this
        # context thread should be fine as it will be cleaned up
        # eventually and all waiters are going to be unblocked or failed eventually anyways.
        # This does allow blocked listener threads to block the context thread on session down.
        # However any calls to disconnect from the listener thread will already be unable
        # to race with this listener thread join as the service state is updated before this
        # call and before the service event is pushed to the application.
        # And in the event of an application thread call to disconnect
        # the finalizer is designed to execute only once. So, either the app thread
        # will execute the finalizer and join the listener thread or this soon to be dead context thread
        # will execute the finalizer and join the listener thread.
        #
        # Should this be called by other ccsmp session event that do not halt networking then
        # in the future calling this finalizer must be revisited.
        # However setting the listener event thread stop event must occur here to prevent leaked threads.
        self._listener_service_finalizer()

        self._serial_publisher.shutdown()

    @property
    def serial_publisher(self):
        # There is a separate accessor for serial_publisher since the receiver needs access to it for cache requests,
        # but shouldn't use the existing create_publisher method, since then it would need to use the
        # PublisherBackPressure class. It would not make sense for the receiver to be using
        # PublisherBackPressureStrategies as a filter for configuration on a receiver resource.
        return self._serial_publisher

    def create_publisher(self, back_pressure_type: 'PublisherBackPressure'):
        # provides service publisher specific to underlying service implementation
        # currently the underlying publisher are shared across all api publishers
        # return service instances based on type
        if back_pressure_type == PublisherBackPressure.No:
            return self._basic_publisher
        else:
            return self._serial_publisher

    def create_receiver(self):
        return self._basic_receiver

    def update_property(self, name: str, value: Any):
        # Take the mutex so that the update can complete without the service being disconnected
        # and the context being destroyed
        with self._mutex:
            # Verify that the service is in a valid state to have its properties updated.
            # Once the service is disconnected, its context is destroyed and the session pointer
            # becomes invalid, which prevents this operation from executing, since CCSMP requires
            # a session pointer to modify the properties for that session.
            if self._state in [_MessagingServiceState.DISCONNECTED, _MessagingServiceState.DISCONNECTING]:
                error_message = f"{CANNOT_UPDATE_SERVICE_PROPERTY_FOR_DISCONNECTED_OR_DISCONNECTING_SERVICE}" \
                    f"{self._state}"
                self.adapter.warning(error_message)
                raise IllegalStateError(error_message)

            # Verify that the passed property is a valid property and that it can be modified.
            if name not in self.MODIFIABLE_SERVICE_PROPERTIES.keys():  # pylint: disable=consider-iterating-dictionary
                error_message = f"{CANNOT_UPDATE_INVALID_SERVICE_PROPERTY}{name}"
                self.adapter.warning(error_message)
                raise IllegalArgumentError(error_message)

            # Verify that the passed value is of an appropriate type for the associated property
            if not isinstance(value, self.MODIFIABLE_SERVICE_PROPERTIES[name]):
                error_message = f"{CANNOT_UPDATE_SERVICE_PROPERTY_WITH_INVALID_VALUE}" \
                                f"{self.MODIFIABLE_SERVICE_PROPERTIES[name]}."
                self.adapter.warning(error_message)
                raise IllegalArgumentError(CANNOT_UPDATE_SERVICE_PROPERTY_WITH_INVALID_VALUE)

            # All checks passed, let's modify the property.
            # session_modify_session_properties can raise a PubSubPlusCoreClientError if there
            # is a transport issue, but we just let it be raised since PubSubPlusCoreClientError
            # is a child class of PubSubPlusClientError and we document that this method can raise
            # a PubSubPlusClientError.
            self.session.modify_session_properties({name: value})

    def connect(self) -> '_BasicMessagingService':  # pylint: disable=protected-access
        #
        # Method to establish connection with event broker.
        # Returns:
        #    object: returns MessagingService object.

        # Raise error if message_service is already DISCONNECTING/DISCONNECTED
        self._check_connect_state()

        with self._mutex:
            # Connect message_service, only if it is in INIT(NOT_CONNECTED) state
            if self._state == _MessagingServiceState.NOT_CONNECTED:
                # start listener thread (reconnection_listener/reconnection_attempt_listener/
                # service_interruption_listener, if any. We're starting this thread,
                # because we need this to handle with_connection_retry_strategy scenario
                self.__start_listener_thread()
                self._state = _MessagingServiceState.CONNECTING
                with _Released(self._mutex):
                    connect_status, error = self._session.connect()
                if connect_status != SOLCLIENT_OK or error is not None:
                    self.__stop_listener_thread()
                    self.adapter.warning("Connection failed. Status code: %s", connect_status)
                    raise error
                if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                    self.adapter.debug('[%s] connected', connect_status)

                self._serial_publisher.start()
                return self

            # Return OK if message_service state other than INIT(NOT_CONNECTED),
            # meaning CONNECT method is already invoked
            self.adapter.info('%s %s', MESSAGE_SERVICE_CONNECTION_IN_PROGRESS,
                              self._state.name)
            return self

    def connect_async(self) -> concurrent.futures.Future:
        # See the base class :py:class:`solace.messaging.connections.async_connectable.AsyncConnectable`
        #
        # raise state error if not in correct state
        self._check_connect_state()
        if self.__is_connected():
            return self._connect_future

        with self._mutex:
            # Even after acquiring lock still we have to check the state to avoid spinning up the executor
            self._check_connect_state()
            if self.__is_connected():
                return self._connect_future
            self._connect_future = self._executor.submit(self.connect)
            return self._connect_future

    def disconnect(self):  # pylint: disable=protected-access
        #
        # Method to disconnect message service connection from event broker and stop reconnection
        # listener threads

        # Block message_service disconnect if it is in DISCONNECTING state
        with self._mutex:
            if self.__is_not_connected():
                self.adapter.warning("%s", MESSAGE_SERVICE_NOT_ATTEMPTED_TO_CONNECT)
                raise IllegalStateError(MESSAGE_SERVICE_NOT_ATTEMPTED_TO_CONNECT)
            if self.__is_disconnected():  # Return OK, if it is already DISCONNECTED
                self.adapter.info("%s", MESSAGE_SERVICE_DISCONNECT_ALREADY)
                return None

            # Process disconnect, if it is not disconnected
            # This state assignment will be wrapped by a mutex in a future commit
            self._state = _MessagingServiceState.DISCONNECTING
            self.__stop_listener_thread()
            # Unblock publisher threads
            self._serial_publisher.shutdown(wait=False)
            if self._connect_future is None:
                self._connect_future = COMPLETED_FUTURE
            if self._disconnect_future is None:
                self._disconnect_future = COMPLETED_FUTURE
            # shutdown async executor
            self._executor.shutdown(wait=False)
            # This state assignment will be wrapped in a mutex in a later commit.
            self._state = _MessagingServiceState.DISCONNECTING
            with _Released(self._mutex):
                _, error_info = self._session.disconnect()
            # join serial publisher thread after network resource has unblocked waiters
            self._serial_publisher.shutdown(wait=True)
            # This state assignment will be wrapped by a mutex in a future commit
            self._state = _MessagingServiceState.DISCONNECTED
            self._unregister_transport_event_handlers()
            with _Released(self._mutex):
                self._session.session_cleanup()
            if error_info:
                self.adapter.error(f"Error disconnecting service with error info `{error_info}`")
                raise PubSubPlusClientError(error_info)

    def disconnect_async(self) -> concurrent.futures.Future:
        #
        # Method to asynchronous disconnect message service connection from event broker.
        #
        if self.__is_disconnecting():
            return self._disconnect_future

        with self._mutex:
            if self.__is_disconnecting():
                return self._disconnect_future
            if self.__is_disconnected():
                self.adapter.info("%s", MESSAGE_SERVICE_DISCONNECT_ALREADY)
                return self._disconnect_future
            self._disconnect_future = self._executor.submit(self.disconnect)
            return self._disconnect_future

    # need to remove
    def disconnect_force(self):  # pylint: disable=missing-function-docstring
        #
        # Method to disconnect with event broker.
        # HIGH RISK: We should use this only for testing.
        # In ideal scenario, we won't FORCE DISCONNECT SESSION
        # Returns:
        # object: returns MessagingService object.
        #
        with self._mutex:
            self._state = _MessagingServiceState.DISCONNECTING
        return_code = self._session.session_force_disconnect()
        with self._mutex:
            self._state = _MessagingServiceState.DISCONNECTED
        return return_code

    def create_direct_message_receiver_builder(self) -> DirectMessageReceiverBuilder:
        #
        # Method to create direct message receiver builder class instance
        # Returns:
        #    object: returns DirectMessageReceiverBuilder object.
        #
        return _DirectMessageReceiverBuilder(messaging_service=self)

    def create_direct_message_publisher_builder(self) -> DirectMessagePublisherBuilder:
        # Method to create direct message publisher builder class instance
        # Returns:
        #     object: returns DirectMessagePublisherBuilder object.
        return _DirectMessagePublisherBuilder(messaging_service=self)

    def create_persistent_message_publisher_builder(self) -> PersistentMessagePublisherBuilder:
        # method to create persistent message publisher builder Class
        # Returns:
        #     PersistentMessagePublisherBuilder instance
        return _PersistentMessagePublisherBuilder(messaging_service=self)

    def create_persistent_message_receiver_builder(self) -> PersistentMessageReceiverBuilder:
        # method to create persistent message receiver builder Class
        # Returns:
        #     PersistentMessageReceiverBuilder instance
        return _PersistentMessageReceiverBuilder(self)

    def create_message_queue_browser_builder(self) -> MessageQueueBrowserBuilder:
        # method to create a message queue browser builder instance.
        # Returns:
        #     MessageQueueBrowserBuilder instance
        return _MessageQueueBrowserBuilder(self)

    def message_builder(self) -> OutboundMessageBuilder:
        # Method to return an instance of OutboundMessageBuilder
        return _OutboundMessageBuilder()

    def create_transactional_service_builder(self) -> TransactionalMessagingServiceBuilder:
        """
            Creates a {@link TransactionalMessagingServiceBuilder} that is used to configure and create
            transactional messaging service instances
            Returns:
                 TransactionalMessagingServiceBuilder: new instance of TransactionalMessagingServiceBuilder
        """
        return TransactionalMessagingServiceBuilder(self)

    def request_reply(self) -> 'MessagingService.RequestReplyMessagingService':
        return _RequestReplyMessagingService(self)

    def get_application_id(self) -> str:
        # property to return the application id.
        # Returns:
        #     gives application id
        return self._application_id

    def metrics(self) -> ApiMetrics:
        # Method to get metrics of transmitted/received data
        return self.__api_metrics

    def info(self) -> ApiInfo:
        # Method to get API info like build timestamp, version, etc.
        return self.__api_info

    @property
    def is_connected(self) -> bool:
        # property to know whether we are connected to event broker or not.
        # Returns:
        #     object: returns MessagingService object.
        if self._state in [_MessagingServiceState.CONNECTED,
                           _MessagingServiceState.RECONNECTING,
                           _MessagingServiceState.RECONNECTED]:
            return True
        return False

    @property
    def session_pointer(self):  # pylint: disable=missing-function-docstring
        # returns underlying session pointer
        return self._session.session_pointer

    def add_reconnection_attempt_listener(self, listener: ReconnectionAttemptListener) -> MessagingService:
        # Method for adding the reconnection attempt listener
        #
        # Args:
        #     listener: reconnection attempt notification listener
        if isinstance(listener, ReconnectionAttemptListener):
            self._attempt_listeners.add(listener.on_reconnecting)
            self.__init_listener()
            return self
        self.adapter.warning("%s[%s]", RECONNECTION_ATTEMPT_LISTENER_SHOULD_BE_TYPE_OF,
                             ReconnectionAttemptListener)
        raise InvalidDataTypeError(f"{RECONNECTION_ATTEMPT_LISTENER_SHOULD_BE_TYPE_OF}"
                                   f"[{ReconnectionAttemptListener}]")

    def add_reconnection_listener(self, listener: ReconnectionListener) -> MessagingService:
        # Args:
        #     listener (ReconnectionListener): listener event
        #     args:
        if isinstance(listener, ReconnectionListener):
            self._reconnection_listeners.add(listener.on_reconnected)
            self.__init_listener()
            return self
        self.adapter.warning("%s[%s]", RECONNECTION_LISTENER_SHOULD_BE_TYPE_OF, ReconnectionListener)
        raise InvalidDataTypeError(f"{RECONNECTION_LISTENER_SHOULD_BE_TYPE_OF}[{ReconnectionListener}]")

    def add_service_interruption_listener(self, listener: ServiceInterruptionListener):
        # Method for adding the service interruption listener
        #
        # Args:
        #     listener: listener for identifying service interruptions
        if isinstance(listener, ServiceInterruptionListener):
            self._service_interruption_listeners.add(listener.on_service_interrupted)
            self.__init_listener()
        else:
            self.adapter.warning("%s[%s]", INTERRUPTION_LISTENER_SHOULD_BE_TYPE_OF, ServiceInterruptionListener)
            raise InvalidDataTypeError(f"{INTERRUPTION_LISTENER_SHOULD_BE_TYPE_OF}"
                                       f"[{ServiceInterruptionListener}]")

    def remove_reconnection_listener(self, listener: ReconnectionListener) -> MessagingService:
        # Remove the reconnection listener.
        # Args:
        #    listener (ReconnectionListener): reconnection attempt notification listener
        #
        if isinstance(listener, ReconnectionListener):
            try:
                self._reconnection_listeners.remove(listener.on_reconnected)
                return self
            except KeyError as exception:
                error_message = RECONNECTION_LISTENER_NOT_EXISTS.substitute(listener=listener)
                self.adapter.warning(error_message)
                raise PubSubPlusClientError(error_message) from exception
        self.adapter.warning("%s[%s]", RECONNECTION_LISTENER_SHOULD_BE_TYPE_OF, ReconnectionListener)
        raise InvalidDataTypeError(f"{RECONNECTION_LISTENER_SHOULD_BE_TYPE_OF}[{ReconnectionListener}]")

    def remove_reconnection_attempt_listener(self, listener: ReconnectionAttemptListener) -> MessagingService:
        # method to remove the reconnection attempt listener
        # Args:
        #    listener (ReconnectionAttemptListener): reconnection attempt notification listener
        #
        if isinstance(listener, ReconnectionAttemptListener):
            try:
                self._attempt_listeners.remove(listener.on_reconnecting)
                return self
            except KeyError as exception:
                error_message = RECONNECTION_ATTEMPT_LISTENER_NOT_EXISTS.substitute(listener=listener)
                self.adapter.warning(error_message)
                raise PubSubPlusClientError(error_message) from exception
        self.adapter.warning("%s[%s]", RECONNECTION_ATTEMPT_LISTENER_SHOULD_BE_TYPE_OF,
                             ReconnectionAttemptListener)
        raise InvalidDataTypeError(f"{RECONNECTION_ATTEMPT_LISTENER_SHOULD_BE_TYPE_OF}"
                                   f"[{ReconnectionAttemptListener}]")

    def remove_service_interruption_listener(self, listener: ServiceInterruptionListener) -> bool:
        # method to remove the service interruption listener
        #
        # Args:
        #     listener: instance of the service interruption listener
        if isinstance(listener, ServiceInterruptionListener):
            try:
                self._service_interruption_listeners.remove(listener.on_service_interrupted)
                return True
            except KeyError:
                return False
        self.adapter.warning("%s[%s]", INTERRUPTION_LISTENER_SHOULD_BE_TYPE_OF, ServiceInterruptionListener)
        raise InvalidDataTypeError(f"{INTERRUPTION_LISTENER_SHOULD_BE_TYPE_OF}"
                                   f"[{ServiceInterruptionListener}]")

    def _check_connect_state(self):
        # Raise error if message_service is already DISCONNECTING/DISCONNECTED
        if self._state in [_MessagingServiceState.DISCONNECTING,
                           _MessagingServiceState.DISCONNECTED]:
            error_message = f'{UNABLE_TO_CONNECT_ALREADY_DISCONNECTED_SERVICE}{self._state.name}'
            self.adapter.warning(error_message)
            raise IllegalStateError(error_message)

    def __str__(self) -> str:
        return f"application_id : {self._application_id} connected : {self.is_connected}"

    def _transport_down_event_handler(self, event_info: '_SolaceTransportEventInfo'):
        with self._mutex:
            if self._state == _MessagingServiceState.DISCONNECTING:
                return
            self._state = _MessagingServiceState.DISCONNECTED

        for listener in self._service_interruption_listeners:
            self.__put_service_event(event_info.host, listener, event_info.message, event_info.exception)

        self._on_service_down(event_info.exception)

    def _transport_reconnected_event_handler(self, event_info: '_SolaceTransportEventInfo'):
        with self._mutex:
            self._state = _MessagingServiceState.RECONNECTED

        for listener in self._reconnection_listeners:
            self.__put_service_event(event_info.host, listener, event_info.message, event_info.exception)

    def _transport_reconnecting_event_handler(self, event_info: '_SolaceTransportEventInfo'):
        with self._mutex:
            self._state = _MessagingServiceState.RECONNECTING

        for listener in self._attempt_listeners:
            self.__put_service_event(event_info.host, listener, event_info.message, event_info.exception)

    def _transport_up_event_handler(self, event_info: '_SolaceTransportEventInfo'):  # pylint: disable=unused-argument
        with self._mutex:
            self._state = _MessagingServiceState.CONNECTED

    def __put_service_event(self, host, listener, message, exception):
        # Method for adding service event"""

        obj = _ServiceEvent(host, exception, message, datetime.datetime.now().timestamp())
        try:
            self._listener_queue.put((listener, obj))
        except QueueShutdown:
            logger.info("While trying to buffer transport events, the buffer was shutdown. " \
                        "The following event was dropped: %s. " \
                        "The following listener was dropped: %s.", obj, listener)

    def __init_listener(self):
        if not self._listener_queue:
            self._listener_queue = _PubSubPlusQueue()
        if not self._listener_thread:
            self._listener_thread = ListenerThread(self._id_info, logger, self._listener_queue,
                                                   name=f"ServiceListenerThread[{self._application_id}]")
            # must set the thread holder for the finalizer to get the actual object on finalize
            self._listener_thread_holder.value = self._listener_thread
        if self._state != _MessagingServiceState.NOT_CONNECTED:
            self.__start_listener_thread()

    def __start_listener_thread(self):
        if self._listener_thread is not None and not self._listener_thread.is_alive():
            self._listener_thread.daemon = True
            self._listener_thread.start()

    def __stop_listener_thread(self) -> bool:
        # method for stopping the listener thread
        if self._listener_thread is not None:
            self._reconnection_listeners.clear()
            self._attempt_listeners.clear()
            self._service_interruption_listeners.clear()
            self._listener_service_finalizer()
            self._listener_thread = None

    def __is_not_connected(self) -> bool:
        return self._state == _MessagingServiceState.NOT_CONNECTED

    def __is_connected(self) -> bool:
        # state check for pending connect operation
        # return a condition evaluation of true
        #   when there is a pending connect operation, or an executing connect operation
        return self._connect_future and \
               self._state in [_MessagingServiceState.CONNECTING,
                               _MessagingServiceState.CONNECTED,
                               _MessagingServiceState.RECONNECTING,
                               _MessagingServiceState.RECONNECTED]

    def __is_disconnecting(self) -> bool:
        return self._disconnect_future and \
               self._state == _MessagingServiceState.DISCONNECTING

    def __is_disconnected(self) -> bool:
        return self._state == _MessagingServiceState.DISCONNECTED



class MessagingServiceClientBuilder(TransportProtocolConfiguration, AuthenticationConfiguration,
                                    PropertyBasedConfiguration):
    """
     Builder class for messaging service builder
    """

    def __init__(self):
        # MessagingServiceClient builder
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._application_id = None
        self._stored_config = {}

    def from_properties(self, configuration: dict) -> 'MessagingServiceClientBuilder':
        """
        Passes a configuration dictionary for configuration information.

        Args:
             configuration(dict): Pass a configuration dictionary.

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        if isinstance(configuration, dict):
            self._stored_config = {**self._stored_config, **configuration}
        return self

    def with_authentication_strategy(self, authentication_strategy: AuthenticationStrategy) \
            -> 'MessagingServiceClientBuilder':
        """
        Configures the ``MessageService`` instance with the authentication strategy.
        For more information, see the base class
        :py:class:`solace.messaging.config.authentication_strategy.AuthenticationConfiguration`.

        Args:
            authentication_strategy(AuthenticationStrategy): The authentication strategy.

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        is_type_matches(authentication_strategy, AuthenticationStrategy, ignore_none=True)
        if authentication_strategy is not None:
            auth_properties = authentication_strategy.authentication_configuration
            self._stored_config = {**self._stored_config, **auth_properties}
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('[%s] with authentication strategy', MessagingService.__name__)
        return self

    def with_reconnection_retry_strategy(self, strategy: RetryStrategy) -> 'MessagingServiceClientBuilder':
        """
        Configures the ``MessageService`` instance with the reconnection retry strategy.
        For more information, see the base class
        :py:class:`solace.messaging.config.transport_protocol_configuration.TransportProtocolConfiguration`.

        Args:
            strategy(RetryStrategy): The retry strategy.

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        is_type_matches(strategy, RetryStrategy, ignore_none=True, logger=logger)
        if strategy is not None:
            retry_properties = RetryConfigurationProvider.to_reconnection_configuration(strategy)
            self._stored_config = {**self._stored_config, **retry_properties}
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('[%s] with reconnection retry strategy', MessagingService.__name__)
        return self

    def with_connection_retry_strategy(self, strategy: RetryStrategy) -> 'MessagingServiceClientBuilder':
        """
        Configures the ``MessageService`` instance with the connection retry strategy.
        For more information, see the base class
        :py:class:`solace.messaging.config.retry_strategy.RetryStrategy`.

        Args:
            strategy(RetryStrategy): The retry strategy.

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        is_type_matches(strategy, RetryStrategy, ignore_none=True, logger=logger)
        if strategy is not None:
            retry_properties = RetryConfigurationProvider.to_connection_configuration(strategy)  # Re-visit prop
            self._stored_config = {**self._stored_config, **retry_properties}
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('[%s] with connection retry strategy', MessagingService.__name__)
        return self

    def with_transport_security_strategy(self, transport_layer_security_strategy: TransportSecurityStrategy) \
            -> 'MessagingServiceClientBuilder':
        """
        Configures a message with Transport Layer Security configuration.
        For more information, see the base class
        :py:class:`solace.messaging.config.transport_protocol_configuration.TransportProtocolConfiguration`.

        Args:
            transport_layer_security_strategy(TransportSecurityStrategy): The transport security strategy.

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        is_type_matches(transport_layer_security_strategy, TransportSecurityStrategy, ignore_none=True,
                        logger=logger)
        if transport_layer_security_strategy is not None:
            tls_properties = transport_layer_security_strategy.security_configuration
            self._stored_config = {**self._stored_config, **tls_properties}
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('[%s] with TLS strategy', MessagingService.__name__)
        return self

    def with_message_compression(self, compression_factor: int = SOLCLIENT_SESSION_PROP_DEFAULT_COMPRESSION_LEVEL) \
            -> 'MessagingServiceClientBuilder':
        """
        Configures the ``MessageService`` instance with so that messages are compressed with ZLIB
        before transmission and decompressed on receive.

        Args:
            compression_factor (int): Enables messages to be compressed with ZLIB before transmission
                and decompressed on receive. The valid  values to use are 0 (off) or 1..9, where 1 is
                least amount of compression (fastest) and 9 is the most amount of compression (slowest).

        Returns:
            MessagingServiceClientBuilder: An object for method chaining.
        """
        is_type_matches(compression_factor, int, ignore_none=True, logger=logger)
        if compression_factor is not None:
            self._stored_config = {**self._stored_config,
                                   **{COMPRESSION_LEVEL: compression_factor}}
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('[%s] with message compression', MessagingService.__name__)
        return self

    def build(self, application_id: str = None) -> MessagingService:
        """
        Builds a ``MessagingService`` instance.

        Args:
            application_id(str): Application id

        Returns:
            MessagingService: An Messaging Service object.
        """
        is_type_matches(application_id, str, ignore_none=True, logger=logger)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Build [%s]', MessagingService.__name__)
        # Make sure we have received all props to establish connection with broker
        MessagingServiceClientBuilder.__rectify_props(self._stored_config)

        return _BasicMessagingService(config=self._stored_config, application_id=application_id)

    @staticmethod
    def __check_required_props(config: dict):  # pylint: disable=too-many-branches
        if SCHEME in config.keys():
            props = rectifiable_service_props[SCHEME][config[SCHEME]][REQUIRED_PROPS]
        else:
            props = rectifiable_service_props[SCHEME][DEFAULT_PROP][REQUIRED_PROPS]
        for key in props:  # pylint: disable=too-many-nested-blocks
            if isinstance(key, list):
                for minimum_one_prop in key:
                    if minimum_one_prop in config:
                        break
                else:
                    # If the above for loop breaks, this block is not executed
                    # If this block executes, it's beacause the above for loop completed witout breaking,
                    # indicating that none of the properties in list are in the configuration. Therefore,
                    # we raise an error explaining that at least one of the properties in the
                    # 'minimum one required' list are present in the configuration, so the configuration
                    # cannot proceed.
                    missing_keys = ','.join(set(key))
                    error_message = f"{BROKER_MANDATORY_MINIMUM_ONE_KEY_MISSING_ERROR_MESSAGE} {missing_keys}"
                    logger.warning(error_message)
                    raise PubSubPlusClientError(error_message)
            else:
                if key not in config:
                    config_set = set(config.keys())
                    # Because we're using sets to print the series of properties, we need to flatten the list of
                    # properties. Because the internal list is a list of mandatory minimum one properties, we need
                    # to print them separately.
                    # To do this, we extract the single mandatory props, where there are no options like there are
                    # with the internal lists. To print the minimum one required props, we extract each internal
                    # minimum one required list and then create a list of these internal lists. Later on, we
                    # initially print the list of single mandatory props, and then follow it with iterations of the
                    # minimum one required lists. We need to do this so that each list of minimum one required
                    # properties list is clearly distinct from the other properties lists. This helps to prevent
                    # confusion between properties from multiple minimum one required lists.
                    list_of_minimum_required_one = []
                    only_single_mandatory_props = []

                    for item in props:
                        if isinstance(item, list):
                            for entry in item:
                                if entry in config.keys():
                                    break
                            else:
                                list_of_minimum_required_one.append(set(item))
                        else:
                            only_single_mandatory_props.append(item)

                    missing_keys = ','.join(set(only_single_mandatory_props) - config_set)
                    error_message = f"{BROKER_MANDATORY_KEY_MISSING_ERROR_MESSAGE} {missing_keys}."

                    for item in list_of_minimum_required_one:
                        if item:
                            error_message += f" {BROKER_MANDATORY_MINIMUM_ONE_KEY_MISSING_ERROR_MESSAGE} {item}."

                    logger.warning(error_message)
                    raise PubSubPlusClientError(error_message)

    @staticmethod
    def __check_excluded_props(config):
        if SCHEME in config.keys():
            props = rectifiable_service_props[SCHEME][config[SCHEME]][EXCLUDED_PROPS]
        else:
            props = rectifiable_service_props[SCHEME][DEFAULT_PROP][EXCLUDED_PROPS]
        excluded_props = []
        for prop in props:
            if prop in config.keys():
                excluded_props.append(prop)
        if len(excluded_props) > 0:
            warning_message = f"{BROKER_EXCLUDED_PROPERTY} {excluded_props}"
            logger.warning(warning_message)

    @staticmethod
    def __rectify_props(config: dict):
        MessagingServiceClientBuilder.__check_required_props(config)
        MessagingServiceClientBuilder.__check_excluded_props(config)
