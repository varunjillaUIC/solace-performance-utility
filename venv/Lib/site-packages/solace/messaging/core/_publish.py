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


# pylint: disable=missing-module-docstring,missing-function-docstring
# Core Module for Publishing message

import enum
import logging
from abc import ABC, abstractmethod
from ctypes import c_int, c_char_p

from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._sol_constants import SOLCLIENT_TOPIC_DESTINATION, SOLCLIENT_OK, SOLCLIENT_WOULD_BLOCK, \
    SOLCLIENT_FAIL, SOLCLIENT_IN_PROGRESS
from solace.messaging.config._solace_message_constants import SET_DESTINATION_FAILED, UNABLE_TO_PUBLISH_MESSAGE, \
    CCSMP_SUB_CODE, CCSMP_INFO_SUB_CODE, TOPIC_NAME_TOO_LONG, TOPIC_NAME_CANNOT_BE_EMPTY, \
    CCSMP_SUBCODE_PARAM_OUT_OF_RANGE
from solace.messaging.core._message import _SolClientDestination
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.core._solace_transport import _SolaceTransportState
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, IllegalArgumentError
from solace.messaging.utils._solace_utilities import _ThreadingUtil

logger = logging.getLogger('solace.messaging.core')


class _SolacePublisherEvent(enum.Enum):  # pylint: disable=too-few-public-methods, missing-class-docstring
    PUBLISHER_CAN_SEND = 0
    PUBLISHER_WOULD_BLOCK = 1
    PUBLISHER_DOWN = 2


class _SolaceCorrelationManager(ABC):  # pylint: disable=missing-class-docstring
    @abstractmethod
    def register_correlation_tag(self, msg_correlation: bytes) -> bool:
        """
        Registers msg_correlation bytes with the correlation manager.
        This can be done to ensure internal eventing information remains in scope
        event once the publisher is gone.
        """

    def unregister_correlation_tag(self, msg_correlation: bytes) -> bool:
        """
        Removes matching msg_correlation bytes that is already registered.
        """

    def has_correlation_tag(self, msg_correlation: bytes) -> bool:
        """
        Checks is a msg_correlation is already registered
        """


class _SolacePublisherAcknowledgementEmitter(ABC):  # pylint: disable=missing-class-docstring
    @abstractmethod
    def register_acknowledgement_handler(self, handler, publisher_correlation_id: bytes):
        """
        registers handler for acknowledgments with provided publisher
        to see the publisher id component of published messages see _PublisherUtils
        The handler is a function that takes one parameter correlation tag
        the handler is supposed to only get correlation tags with matching publisher ids
        the publisher_correlation_id is used to uniquely match the registered handler
        """

    @abstractmethod
    def unregister_acknowledgement_handler(self, publisher_correlation_id: bytes):
        """ Remove handler using publisher_correlation_id as a key """


class _SolacePublisherEventEmitter(ABC):  # pylint: disable=missing-class-docstring
    @abstractmethod
    def register_publisher_event_handler(self, event: '_SolacePublisherEvent', handler) -> int:
        """ Register publish event """

    @abstractmethod
    def unregister_publisher_event_handler(self, handler_id: int):
        """  Unregister publish event """


class _SolacePublisher(ABC):  # pylint: disable=missing-class-docstring
    @abstractmethod
    def send(self, publishable: 'TopicPublishable') -> int:
        """ sends an api publishable """

    @property
    @abstractmethod
    def emitter(self) -> '_SolacePublisherEventEmitter':
        """ emits an api publishable """

    @property
    @abstractmethod
    def ack_emitter(self) -> '_SolacePublisherAcknowledgementEmitter':
        """ emits ack """

    @property
    @abstractmethod
    def correlation_manager(self) -> '_SolaceCorrelationManager':
        """ returns correlation manager """


class _AsyncWritable(ABC):
    @abstractmethod
    def may_block(self):
        """ may block """

    @property
    @abstractmethod
    def is_writable(self) -> bool:
        """ is writable """

    @abstractmethod
    def wait_for_writable(self):
        """ wait for writable """


class _AsyncSolacePublisher(_SolacePublisher, _AsyncWritable, ABC):
    @abstractmethod
    def start(self):
        """ Start publisher thread """

    @abstractmethod
    def submit(self, handler, send_task):
        """ Submit publisher thread """

    @abstractmethod
    def shutdown(self, wait: bool):
        """ Shutdown publisher thread """


class _BasicSolacePublisher(_SolacePublisher):
    def __init__(self, session: '_SolaceSession'):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._session: '_SolaceSession' = session
        self._solace_publish: '_SolacePublish' = _SolacePublish(self._session)

    @property
    def emitter(self) -> '_SolacePublisherEventEmitter':
        return self._session

    @property
    def ack_emitter(self) -> '_SolacePublisherAcknowledgementEmitter':
        return self._session

    @property
    def correlation_manager(self) -> '_SolaceCorrelationManager':
        return self._session

    def send(self, publishable: 'TopicPublishable') -> int:
        return self._solace_publish.publish(publishable.get_message(), publishable.get_destination())


class _SerializedSolacePublisher(_BasicSolacePublisher, _AsyncSolacePublisher):
    def __init__(self, session: '_SolaceSession'):
        super().__init__(session)
        self._send_executor: 'Executor' = None

    def start(self):
        self._send_executor = \
            _ThreadingUtil.create_serialized_dispatcher(f"send_executor_thread-{str(hex(id(self._session)))}")

    def shutdown(self, wait: bool = True):
        # executors in python 3.9 have a cancel futures parameter on shutdown
        # until only python 3.9 is supported cancel futures manually
        # prevent new futures from being added
        # using a SolaceDisptacher instead does have a thread safe cancel of pending tasks
        executor = self._send_executor
        # shutdown executor
        if executor:
            # should cancel pending send tasks and join serial publish thread if wait is set
            executor.shutdown(wait=wait, cancel=True)

    def may_block(self):
        # this method should only be called from a single executing thread
        # as the underlying publisher can race to unblock

        # This is called as a part of `send()`. We may revisit this access in the future.

        # only allow blocking if the transport is not DOWN

        if self._session.transport_state is not _SolaceTransportState.DOWN:
            self._session.can_send_received.clear()

    def _on_can_write(self):
        # utility function for local unblocking of writable state
        # use the SolaceApi can_send_received
        # can_send_received is typically updated directly on solclient
        # session event CAN_SEND
        self._session.can_send_received.set()

    def send(self, publishable: 'TopicPublishable') -> int:
        # Returns: SOLCLIENT_OK for successful write of publishable
        #          SOLCLIENT_WOULD_BLOCK for recoverable write failure of publishable
        # Throws: PubSubPlusClientError for unrecoverable write failure of publishable
        try:
            # before each send the publisher send channel might be full
            # mark writable state as full to block
            self.may_block()
            # send publishable potentially causing the send channel to block
            # causing a writable signal to be produce on send channel unblock
            return_code = super().send(publishable)
            # return_code is either SOLCLIENT_WOULD_BLOCK or SOLCLIENT_OK
            # should the signal for writable have already occured
            # from a SOLCLIENT_WOULD_BLOCK rc then the writable
            # state has already been updated to a non blockable state
            # should wait_for_writable be callon return otherwise it
            # blocks until _on_can_write or equivalent is called
            #
            # Note updating the blockable state after send can
            # miss the writable signal as it can race with send
            if return_code == SOLCLIENT_OK:
                # unblocks writable state for waiting thread if no write block occurs
                self._on_can_write()
            return return_code
        except:
            # no send occurred so no expect writable signal is coming
            # unblock writable state for any waiting thread
            self._on_can_write()
            raise

    def send_cache_request(self, cache_requester: '_SolaceCacheRequester'):
        try:
            self.may_block()
            return_code = cache_requester.send_cache_request()
            if return_code == SOLCLIENT_IN_PROGRESS:
                self._on_can_write()
            return return_code
        except:
            self._on_can_write()
            raise

    @property
    def is_writable(self) -> bool:
        # gives writable state of the publisher
        # Returns: True when the publisher can write publishables for sending
        #          False when the publisher can not write publishables for sending
        return self._session.can_send_received.is_set()

    def wait_for_writable(self):
        # blocks calling thread for writable signal if one is needed
        self._session.can_send_received.wait()

    def submit(self, handler, send_task):
        if self._send_executor:
            return self._send_executor.submit(handler, send_task)
        return None


class _SolacePublish:  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Class for publishing the message

    def __init__(self, session: '_SolaceSession'):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._session: '_SolaceSession' = session

    def publish(self, solace_message: _SolaceMessage, topic: 'Topic') -> int:
        #
        # Args:
        #     topic (str): topic endpoint name
        #     solace_message (SolaceMessage): SolaceMessage instance
        #
        # Returns:
        #     an integer value stating message sent (i.e. SOLCLIENT_OK) or would block (i.e. SOLCLIENT_WOULD_BLOCK)
        # Raises:
        #     PubSubPlusClientError: when status_code is not 0 (i.e. SOLCLIENT_OK) or 1 (i.e. SOLCLIENT_WOULD_BLOCK)
        #
        self.__set_topic(solace_message, topic)
        publish_message_status_code = solace_message.send_msg(self._session)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug("Message publish on [%s] status: [%d]", topic.get_name(), publish_message_status_code)
        if publish_message_status_code in [SOLCLIENT_OK, SOLCLIENT_WOULD_BLOCK]:
            return publish_message_status_code

        core_exception_msg = last_error_info(status_code=publish_message_status_code,
                                             caller_desc='On PUBLISH')
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('\nSub code: %s. Error: %s. Sub code: %s. Return code: %s',
                         core_exception_msg[CCSMP_INFO_SUB_CODE],
                         core_exception_msg["error_info_contents"],
                         core_exception_msg[CCSMP_SUB_CODE],
                         core_exception_msg["return_code"])
        raise PubSubPlusClientError(message=UNABLE_TO_PUBLISH_MESSAGE)

    def publish_request(self, reply_msg_p, solace_message, topic,
                        reply_timeout: int) -> int:
        # """
        # Args:
        #     topic (str): topic endpoint name
        #     solace_message (SolaceMessage): SolaceMessage instance
        #
        # Returns:
        #     an integer value stating message sent (i.e. SOLCLIENT_OK) or would block (i.e. SOLCLIENT_WOULD_BLOCK)
        # Raises:
        #     PubSubPlusClientException: when status_code is not 0 (i.e. SOLCLIENT_OK) or 1 (i.e. SOLCLIENT_WOULD_BLOCK)
        # """
        self.__set_topic(solace_message, topic)
        return solace_message.send_request(self._session, reply_msg_p, reply_timeout)

    @staticmethod
    def __set_topic(solace_message: _SolaceMessage, topic: 'Topic'):
        #
        # Set the topic for a message
        # Args:
        #     solace_message (SolaceMessage): Message object with pointer to the message
        #     topic (Topic): topic endpoint
        # Raises:
        #     PubSubPlusClientError : if the return_code is not 0
        #
        topic_name = topic.get_name()
        destination = _SolClientDestination(destType=c_int(SOLCLIENT_TOPIC_DESTINATION),
                                            dest=c_char_p(topic_name.encode('utf-8')))
        msg_set_destination_status = solace_message.message_set_destination(destination)
        if msg_set_destination_status != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenarios
            core_exception_msg = last_error_info(status_code=msg_set_destination_status,
                                                 caller_desc='On SET destination')
            if msg_set_destination_status == SOLCLIENT_FAIL and \
                    core_exception_msg[CCSMP_SUB_CODE] == CCSMP_SUBCODE_PARAM_OUT_OF_RANGE:
                error_message = 'Invalid topic name'
                if 'Empty string dest pointer' in core_exception_msg["error_info_contents"]:
                    error_message = TOPIC_NAME_CANNOT_BE_EMPTY
                elif 'exceeds maximum of 250' in core_exception_msg["error_info_contents"]:
                    error_message = TOPIC_NAME_TOO_LONG
                logger.warning(error_message)
                raise IllegalArgumentError(error_message)
            logger.warning(SET_DESTINATION_FAILED)
            raise PubSubPlusClientError(message=SET_DESTINATION_FAILED)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Destination [%s] is successfully set', topic_name)
