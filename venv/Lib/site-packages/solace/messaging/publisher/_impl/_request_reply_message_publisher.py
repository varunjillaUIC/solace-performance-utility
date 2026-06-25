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

# pylint: disable=missing-function-docstring,too-many-ancestors,unused-variable,broad-except,no-else-raise
"""
module contains request reply message publisher

A Request Message Publisher must be created by
:py:class:`solace.messaging.builder.request_reply_message_publisher.RequestReplyMessageReceiverBuilder`.The
RequestReplyMessagePublisher instance is used to publish Messages created by a
:py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder`. Topic (destination)
must be added when the message is a published.
"""

import weakref
import concurrent
import logging
import threading
import time
from collections import namedtuple
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, Union

from solace.messaging.config._sol_constants import SOLCLIENT_DELIVERY_MODE_DIRECT
from solace.messaging.config._solace_message_constants import REQUEST_REPLY_MIN_TIMEOUT, \
    REQUEST_REPLY_MIN_TIMEOUT_ERROR_MESSAGE, REQUEST_REPLY_TIMEOUT_SHOULD_BE_INT, \
    UNSUPPORTED_MESSAGE_TYPE, INVALID_ADDITIONAL_PROPS, INVALID_TYPE_IN_ADDITIONAL_PROPS_VALUE, \
    GRACE_PERIOD_DEFAULT_MS, REQUEST_REPLY_OUTSTANDING_REQUESTS, REQUEST_REPLY_OUTSTANDING_REQUESTS_COUNT, \
    REQUEST_REPLY_PENDING_REQUESTS_COUNT, REQUEST_REPLY_PENDING_REQUESTS, UNABLE_TO_PUBLISH_MESSAGE_PUBLISHER_TERMINATED
from solace.messaging.errors.pubsubplus_client_error import IllegalArgumentError, InvalidDataTypeError, \
    IncompleteMessageDeliveryError, IllegalStateError
from solace.messaging.publisher._impl._direct_message_publisher import PublishFailureNotificationDispatcher
from solace.messaging.publisher._impl._message_publisher import _MessagePublisher, _MessagePublisherUnpublishedState
from solace.messaging.publisher._impl._publisher_utilities import validate_topic_type
from solace.messaging.publisher._publishable import Publishable
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.publisher.request_reply_message_publisher import RequestReplyMessagePublisher
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.resources.topic import Topic
from solace.messaging.utils.manageable import Metric
from solace.messaging.utils._solace_utilities import executor_shutdown

logger = logging.getLogger('solace.messaging.publisher')
Sender = namedtuple('Sender', ['request_message', 'request_destination', 'reply_timeout',
                               'reply_message_handler', 'user_context'])


class _RequestReplyMessagePublisher(_MessagePublisher, RequestReplyMessagePublisher):  # pylint: disable=too-many-instance-attributes
    """Implementation class for RequestReplyMessagePublisher"""

    def __init__(self, request_reply_publisher: '_RequestReplyMessagePublisherBuilder'):
        self._grace_period: int = GRACE_PERIOD_DEFAULT_MS  # in ms
        self.messaging_service = request_reply_publisher.messaging_service
        super().__init__(request_reply_publisher)
        logger.debug('[%s] initialized', type(self).__name__)
        self._error_notification_dispatcher: PublishFailureNotificationDispatcher = \
            PublishFailureNotificationDispatcher()
        # This is the pending requests attribute which will be used during termination to determine
        # whether any pending requests were discarded due to termination.
        self._pending_requests = 0
        # This is the outstanding requests property which will be used by graceful terminate
        # to determine wether or not there are any outstanding calls at shutdown
        self._outstanding_requests = 0
        # This is a lock to ensure that the updating of the outstanding requests counter is
        # done under mutex protection
        self._outstanding_requests_lock = threading.Lock()
        # This is the condition variable for thread blocking if there are more than 0
        # outstanding requests when graceful terminate is called
        self._zero_outstanding_requests_condition = threading.Condition(self._outstanding_requests_lock)
        self._publisher_executor = ThreadPoolExecutor(thread_name_prefix=type(self).__name__)
        self._rr_finalizer = weakref.finalize(self, executor_shutdown, self._publisher_executor)

    @property
    def _delivery_mode(self) -> str:
        return SOLCLIENT_DELIVERY_MODE_DIRECT

    def notify_publish_error(self, exception: Exception, publishable: Publishable, _tag: bytes = None):
        self._error_notification_dispatcher.on_exception(exception, publishable)

    # async
    def publish(self, request_message: 'OutboundMessage',
                request_destination: Topic, reply_timeout: int,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple, None,
                                                               bytearray]] = None) \
            -> concurrent.futures.Future:
        """Sends a request for reply message; nonblocking

        No especial correlation id is required to be provided, correlation is handled internally by API

        Args:
            additional_message_properties ():
            request_message: request message to be sent
            timeout occurred
            request_destination: destination for request messages
            reply_timeout: wait time in ms to get a reply message,  timeout has to be a positive integer value and will
                not accept None as a parameter"""
        self.validate_input(request_message, request_destination, reply_timeout, additional_message_properties)

        with self._outstanding_requests_lock:
            self._pending_requests += 1

        # Check publisher state in case terminate() was previously called.
        self._check_message_publish(request_message, request_destination)

        # This try block is in place in case terminate() is called while publish is being called, where
        # terminate() will shutdown the executor immediately before the following task is submitted to
        # the executor. This is the only case that this try block is intended for. Any other cases which
        # raise a RuntimeError should be evaluated separately.
        try:
            return self._publisher_executor.submit(self._internal_publish_await_response, request_message,
                                                   request_destination, reply_timeout,
                                                   additional_message_properties, True)
        except RuntimeError as error:
            self.adapter.info("%s", UNABLE_TO_PUBLISH_MESSAGE_PUBLISHER_TERMINATED)
            raise IllegalStateError(UNABLE_TO_PUBLISH_MESSAGE_PUBLISHER_TERMINATED) from error

    # sync
    def publish_await_response(self, request_message: 'OutboundMessage', request_destination: Topic,
                               reply_timeout: int,
                               additional_message_properties: Dict[
                                   str, Union[str, int, float, bool, dict, list, tuple, None,
                                              bytearray]] = None) \
            -> InboundMessage:
        """Sends a request message return response message, blocking until response is received or timeout occurs

        Args:
            additional_message_properties ():
            request_message: request message to be send
            request_destination: destination for request messages
            reply_timeout: wait time in ms to get a reply message, if the timeout is not provided default timeout
            is used

        Returns:
            response message when any received

        Raises:
            PubSubTimeoutError                  if response from a replier does not come on time
            MessageRejectedByBrokerError        if broker is rejecting messages from a publisher(only when service
            interruption listener available , warning log will be emitted)
            PubSubPlusClientError               if some internal error occurs
            IllegalArgumentError                if the value of timeout is negative"""
        self.validate_input(request_message, request_destination, reply_timeout, additional_message_properties)

        return self._internal_publish_await_response(request_message, request_destination, reply_timeout,
                                                     additional_message_properties)

    # pylint: disable=too-many-arguments
    def _internal_publish_await_response(self, request_message: 'OutboundMessage', request_destination: Topic,
                                         reply_timeout: int,
                                         additional_message_properties: Dict[
                                             str, Union[str, int, float, bool, dict, list, tuple, None,
                                                        bytearray]] = None, is_pending=False) \
            -> InboundMessage:

        with self._outstanding_requests_lock:
            # Pre-request update: This updates the outstanding requests property which will be used by graceful
            # terminate to determine wether or not there are outstanding request calls to be completed.

            if is_pending:
                self._pending_requests -= 1
            self._outstanding_requests += 1

        try:

            publish_request_response_message = super().publish_request(request_message,
                                                                       request_destination,
                                                                       reply_timeout,
                                                                       additional_message_properties)
        finally:
            with self._outstanding_requests_lock:
                # Post-request update: This updates the outstanding requests property which will be used by graceful
                # terminate to determine wether or not there are outstanding request calls to be completed.
                self._outstanding_requests -= 1
                # Notify conditional on 0 outstanding requests
                self._zero_outstanding_requests_condition.notify()
        return publish_request_response_message

    # pylint: disable=protected-access
    def _do_metrics(self, unpub_contents: _MessagePublisherUnpublishedState):  # pylint: disable=protected-access
        if self._pending_requests > 0:
            self._int_metrics._increment_internal_stat(Metric.PUBLISH_MESSAGES_TERMINATION_DISCARDED,
                                                       self._pending_requests)

    def _resource_cleanup(self):
        super()._resource_cleanup()
        self._publisher_executor.shutdown(wait=False)

    def _cleanup_message_state(self) -> _MessagePublisherUnpublishedState:
        # We pass this method because there are no queues to drain for RR publisher.
        # Instead, the metrics use internal counters.
        return _MessagePublisherUnpublishedState()

    def _check_unpublished_state(self, unpub_contents: _MessagePublisherUnpublishedState):
        message = ""
        if self._outstanding_requests != 0:
            message += f'{REQUEST_REPLY_OUTSTANDING_REQUESTS} {REQUEST_REPLY_OUTSTANDING_REQUESTS_COUNT} ' \
                                 f'{self._outstanding_requests}'
        if self._pending_requests != 0:
            message += f'{REQUEST_REPLY_PENDING_REQUESTS} {REQUEST_REPLY_PENDING_REQUESTS_COUNT} ' \
                                 f'{self._pending_requests}'
        self._pending_requests = 0
        self._outstanding_requests = 0
        if message != "":
            self.adapter.warning(message)
            raise IncompleteMessageDeliveryError(message)

    def _wait_pending_tasks(self, timeout: float):
        with self._zero_outstanding_requests_condition:
            if timeout is None:
                start_time = time.time()
                while self._outstanding_requests != 0:
                    self._zero_outstanding_requests_condition.wait()
                remaining = time.time() - start_time
            else:
                remaining = timeout
                end_time = time.time() + timeout
                while self._outstanding_requests != 0:
                    remaining = end_time - time.time()
                    if remaining <= 0.0:
                        remaining = 0.0
                        break
                    self._zero_outstanding_requests_condition.wait(remaining)
            return remaining

    @staticmethod
    def validate_input(request_message, request_destination, reply_timeout, additional_message_properties=None):
        if not isinstance(request_message, OutboundMessage):
            raise InvalidDataTypeError(UNSUPPORTED_MESSAGE_TYPE.substitute(message_type=type(request_message)))

        validate_topic_type(destination=request_destination, logger=logger)

        _RequestReplyMessagePublisher.validate_reply_timeout(reply_timeout=reply_timeout)

        if additional_message_properties:
            _RequestReplyMessagePublisher \
                .validate_additional_message_properties(additional_message_properties=additional_message_properties)

    @staticmethod
    def validate_reply_timeout(reply_timeout):
        if not isinstance(reply_timeout, int):
            raise InvalidDataTypeError(REQUEST_REPLY_TIMEOUT_SHOULD_BE_INT)

        if reply_timeout < REQUEST_REPLY_MIN_TIMEOUT:
            logger.warning(REQUEST_REPLY_MIN_TIMEOUT_ERROR_MESSAGE)
            raise IllegalArgumentError(REQUEST_REPLY_MIN_TIMEOUT_ERROR_MESSAGE)

    @staticmethod
    def validate_additional_message_properties(additional_message_properties):
        for key, value in additional_message_properties.items():
            if not isinstance(key, str):
                logger.warning(INVALID_ADDITIONAL_PROPS)
                raise IllegalArgumentError(INVALID_ADDITIONAL_PROPS)
            if not isinstance(value, (str, int, bytearray, float, bool, dict, list, tuple)):
                if value is not None:
                    error_message = INVALID_TYPE_IN_ADDITIONAL_PROPS_VALUE.substitute(value_type=value)
                    logger.warning(error_message)
                    raise IllegalArgumentError(error_message)
