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
# pylint: disable=missing-module-docstring,missing-function-docstring,inconsistent-return-statements
# pylint: disable=missing-class-docstring

import ctypes
import logging
from enum import Enum
from typing import Union, List, Dict, Tuple

import solace
from solace.messaging._impl._interoperability_support import _RestInteroperabilitySupport
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._sol_constants import SOLCLIENT_NOT_FOUND, SOLCLIENT_OK, SOLCLIENT_EOS, \
    SOLCLIENT_FAIL, SOLCLIENT_NOT_SET_PRIORITY_VALUE, SOLCLIENT_NULL_DESTINATION, TRACE_ID_SIZE, SPAN_ID_SIZE
from solace.messaging.config._solace_message_constants import FAILED_TO_RETRIEVE, FAILED_TO_GET_APPLICATION_TYPE, \
    FAILED_TO_GET_APPLICATION_ID
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, PubSubPlusCoreClientError, \
    SolaceSDTError, InvalidDataTypeError, IllegalArgumentError
from solace.messaging.message import Message
from solace.messaging.publisher._outbound_message_utility import get_next_field
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.utils._solace_utilities import get_last_error_info, is_type_matches

logger = logging.getLogger('solace.messaging.core')


class _SolClientDestination(ctypes.Structure):  # pylint: disable=too-few-public-methods,missing-class-docstring
    #   Conforms to solClient_destination . A data structure to represent the message destination. A publisher can
    #   send messages to topics or queues and solClient_destination specifies
    #   the details.
    _fields_ = [
        ("destType", ctypes.c_int),  # The type of destination
        ("dest", ctypes.c_char_p)  # The name of the destination (as a NULL-terminated UTF-8 string)
    ]


class _SolClientFieldType(Enum):  # pylint: disable=too-few-public-methods
    #  Conforms to solClient_fieldType . Data types that can be transmitted by the machine-independent read and write
    #   functions.
    SOLCLIENT_BOOL = 0  # Boolean.
    SOLCLIENT_UINT8 = 1  # 8-bit unsigned integer.
    SOLCLIENT_INT8 = 2  # 8-bit signed integer.
    SOLCLIENT_UINT16 = 3  # 16-bit unsigned integer.
    SOLCLIENT_INT16 = 4  # 16-bit signed integer.
    SOLCLIENT_UINT32 = 5  # 32-bit unsigned integer.
    SOLCLIENT_INT32 = 6  # 32-bit signed integer.
    SOLCLIENT_UINT64 = 7  # 64-bit unsigned integer.
    SOLCLIENT_INT64 = 8  # 64-bit signed integer.
    SOLCLIENT_WCHAR = 9  # 16-bit unicode character.
    SOLCLIENT_STRING = 10  # Null terminated string (ASCII or UTF-8).
    SOLCLIENT_BYTEARRAY = 11  # Byte array.
    SOLCLIENT_FLOAT = 12  # 32-bit floating point number.
    SOLCLIENT_DOUBLE = 13  # 64-bit floating point number.
    SOLCLIENT_MAP = 14  # Solace Map (container class).
    SOLCLIENT_STREAM = 15  # Solace Stream (container class).
    SOLCLIENT_NULL = 16  # NULL field.
    SOLCLIENT_DESTINATION = 17  # Destination field.
    SOLCLIENT_SMF = 18  # A complete Solace Message Format (SMF) message is encapsulated in the container.
    SOLCLIENT_UNKNOWN = -1  # A validly formatted but unrecognized data type was received.


class _SolClientValue(ctypes.Union):  # pylint: disable=too-few-public-methods
    # this class is relevant to c union (Conforms to solClient_field)  for creating solclient values
    _fields_ = [('boolean', ctypes.c_bool),
                ('uint8', ctypes.c_uint8),
                ('int8', ctypes.c_int8),
                ('uint16', ctypes.c_uint16),
                ('int16', ctypes.c_int16),
                ('uint32', ctypes.c_uint32),
                ('int32', ctypes.c_int32),
                ('uint64', ctypes.c_uint64),
                ('int64', ctypes.c_int64),
                ('wchar', ctypes.c_wchar),
                ('float32', ctypes.c_float),
                ('float64', ctypes.c_double),
                ('string', ctypes.c_char_p),
                ('bytearray', ctypes.c_char_p),
                ('map', ctypes.c_uint64),
                ('stream', ctypes.c_uint64),
                ('dest', _SolClientDestination),
                ('smf', ctypes.POINTER(ctypes.c_ubyte)),
                ('unknownField', ctypes.POINTER(ctypes.c_ubyte))

                ]


class _SolClientField(ctypes.Structure):  # pylint: disable=too-few-public-methods
    # Conforms to solClient_field. The general solClient_field structure is returned by generic accessors to
    # the container. The application must first check the fieldType to determine
    # which member of the union to use.
    _fields_ = [
        ("type", ctypes.c_int),
        ("length", ctypes.c_uint32),
        ("value", _SolClientValue)]


def close_map_stream(container_p):
    # Finish a map or stream. This action makes the opaque container pointer invalid and fixes the
    # structured data in memory.
    # Args:
    #   container_p : A pointer to the opaque container pointer. The pointer is
    #                        reset to NULL on return
    # Returns:
    #   SOLCLIENT_OK on success, SOLCLIENT_FAIL on failure.
    return solace.CORE_LIB.solClient_container_closeMapStream(ctypes.byref(container_p))

class _Message(Message):  # pylint: disable=too-many-public-methods
    # We disabled too-many-public-methods because an internal class shouldn't have any, but public methods for tracing
    # are added so the OTel package can access them. This is confirmed through arch.
    # implementation class for Message

    def __init__(self, solace_message: _SolaceMessage):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._solace_message: _SolaceMessage = solace_message
        self._user_properties = {}
        self._get_http_content_type = None
        self._get_http_content_encoding = None
        self.__process_rest_interoperability(self.solace_message)
        self.__rest_interoperability_support = _RestInteroperabilitySupport(self._get_http_content_type,
                                                                            self._get_http_content_encoding)
        self._sdt_stream: Union[List, None] = None
        self._sdt_map: Union[Dict, None] = None

    def get_baggage(self) -> Union[str, None]:
        """
        Retrieves the baggage string associated with the message
        If the content is not accessible, the method returns None

        Returns:
            Union[str, None]: baggage string associated with the message or None if there is no baggage

        Raises:
            PubSubPlusClientError: If an error was encountered during the operation.
        """
        baggage, error = self._solace_message.get_baggage()
        if baggage is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved baggage %s from message %s", baggage, self._solace_message.msg_p)
        elif baggage is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find baggage in message %s", self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)
        return baggage

    def set_baggage(self, baggage: Union[None, str]):
        """
        Sets the baggage string associated with the message.

        Args:
            baggage(Union[None, str]): baggage string to be associated with the message

        Raises:
            PubSubPlusClientError: If an error was encountered during the operation.
        """
        if baggage is not None and not isinstance(baggage, str):
            raise InvalidDataTypeError(f"Was passed baggage {baggage} which must be either None or str, " \
                                       f"but was instead {type(baggage)}.")
        error = self._solace_message.set_baggage(baggage)
        if error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Set baggage %s on message %s.", baggage, self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

    # pylint: disable=too-many-branches
    def set_creation_trace_context(self, trace_id: bytes, span_id: bytes, is_sampled: bool,
                                   trace_state: Union[str, None]):
        """
        Sets creation trace context metadata used for distributed message tracing.
        Creation context considered to be immutable, and should not be set multiple times.
        If the content could not be set into the message, the ok flag will be false.

        Args:
            trace_id(bytes): The ID of the trace that this span belongs to, encoded as 16 raw bytes.
            span_id(bytes): This span's ID, encoded as 8 raw bytes.
            is_sampled(bool): indicates that the trace may have been sampled upstream
            trace_state(Union[str, None]):  vendor-specific trace info formatted as a single string (encoded using
                https://github.com/open-telemetry/opentelemetry-python/blob/4280235f5383cb5034993f76aee22502a631a0b2/exporter/opentelemetry-exporter-otlp-proto-common/src/opentelemetry/exporter/otlp/proto/common/_internal/trace_encoder/__init__.py#L169)

        Raises:
            PubSubPlusClientError: If an error was encountered during the operation.
        """
        if trace_id is not None and not isinstance(trace_id, (bytearray, bytes)):
            msg = f"Passed trace ID {trace_id} must be type None, bytes, or bytearray, but was instead " \
                  f"{type(trace_id)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if trace_id is not None and len(trace_id) != TRACE_ID_SIZE:
            msg = f"Passed trace ID {trace_id} must be of length {TRACE_ID_SIZE}, but instead was of length " \
                  f"{len(trace_id)}."
            logger.warning(msg)
            raise IllegalArgumentError(msg)

        if span_id is not None and not isinstance(span_id, (bytearray, bytes)):
            msg = f"Passed span ID {span_id} must be type None, bytes, or bytearray, but was instead " \
                  f"{type(span_id)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if span_id is not None and len(span_id) != SPAN_ID_SIZE:
            msg = f"Passed span ID {span_id} must be of length {SPAN_ID_SIZE}, but instead was of length " \
                  f"{len(span_id)}."
            logger.warning(msg)
            raise IllegalArgumentError(msg)

        if is_sampled is not None and not isinstance(is_sampled, bool):
            msg = f"Passed is_sampled {is_sampled} must be type None or bool, but was instead {type(is_sampled)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if trace_state is not None and not isinstance(trace_state, str):
            msg = f"Passed trace_state {trace_state} must be type None or str, but was instead {type(trace_state)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)

        error = self._solace_message.set_creation_trace_context_trace_id(trace_id)
        if error is not None:
            logger.warning(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set trace ID %s on creation context for message %s.",
                trace_id, self._solace_message.msg_p)

        error = self._solace_message.set_creation_trace_context_span_id(span_id)
        if error is not None:
            logger.warning(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set span ID %s on creation context for message %s.",
                span_id, self._solace_message.msg_p)

        error = self._solace_message.set_creation_trace_context_sampled(is_sampled)
        if error is not None:
            logger.warning(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set sampled flag %s on creation context for message %s.",
                is_sampled, self._solace_message.msg_p)

        error = self._solace_message.set_creation_trace_context_trace_state(trace_state)
        if error is not None:
            logger.warning(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set trace state %s on creation context for message %s,",
                trace_state, self._solace_message.msg_p)

    def set_transport_trace_context(self, trace_id: bytes, span_id: bytes, is_sampled: bool,
                                    trace_state: Union[str, None]):
        """
        Sets transport trace context metadata used for distributed message tracing.
        Creation context considered to be immutable, and should not be set multiple times.
        If the content could not be set into the message, the ok flag will be false.

        Args:
            trace_id(bytes): The ID of the trace that this span belongs to, encoded as 16 raw bytes.
            span_id(bytes): This span's ID, encoded as 8 raw bytes.
            is_sampled(bool): indicates that the trace may have been sampled upstream
            trace_state(Union[str, None]):  vendor-specific trace info formatted as a single string (encoded using
                https://github.com/open-telemetry/opentelemetry-python/blob/4280235f5383cb5034993f76aee22502a631a0b2/exporter/opentelemetry-exporter-otlp-proto-common/src/opentelemetry/exporter/otlp/proto/common/_internal/trace_encoder/__init__.py#L169)

        Raises:
            PubSubPlusClientError: If an error was encountered during the operation.
        """
        if trace_id is not None and not isinstance(trace_id, (bytearray, bytes)):
            msg = f"Passed trace ID {trace_id} must be type None, bytes, or bytearray, " \
                  f"but was instead {type(trace_id)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if trace_id is not None and len(trace_id) != TRACE_ID_SIZE:
            msg = f"Passed trace ID {trace_id} must be of length {TRACE_ID_SIZE}, but instead was of " \
                  f"length {len(trace_id)}."
            logger.warning(msg)
            raise IllegalArgumentError(msg)

        if span_id is not None and not isinstance(span_id, (bytearray, bytes)):
            msg = f"Passed span ID {span_id} must be type None, bytes, or bytearray, but was instead {type(span_id)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if span_id is not None and len(span_id) != SPAN_ID_SIZE:
            msg = f"Passed span ID {span_id} must be of length {SPAN_ID_SIZE}, but instead was " \
                  f"of length {len(span_id)}."
            logger.warning(msg)
            raise IllegalArgumentError(msg)

        if is_sampled is not None and not isinstance(is_sampled, bool):
            msg = f"Passed is_sampled {is_sampled} must be type None or bool, but was instead {type(is_sampled)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)
        if trace_state is not None and not isinstance(trace_state, str):
            msg = f"Passed trace_state {trace_state} must be type None or str, but was instead {type(trace_state)}."
            logger.warning(msg)
            raise InvalidDataTypeError(msg)

        error = self._solace_message.set_transport_trace_context_trace_id(trace_id)
        if error is not None:
            logger.error(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set trace ID %s on transport context for message %s.",
                trace_id, self._solace_message.msg_p)
        error = self._solace_message.set_transport_trace_context_span_id(span_id)
        if error is not None:
            logger.error(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set span ID %s on transport context for message %s.",
                span_id, self._solace_message.msg_p)
        error = self._solace_message.set_transport_trace_context_sampled(is_sampled)
        if error is not None:
            logger.error(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set sampled flag %s on transport context for message %s.",
                is_sampled, self._solace_message.msg_p)
        error = self._solace_message.set_transport_trace_context_trace_state(trace_state)
        if error is not None:
            logger.error(error)
            raise PubSubPlusClientError(error)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Successfully set trace state %s on transport context for message %s.",
                trace_state, self._solace_message.msg_p)

    def get_creation_trace_context(self) -> Tuple[Union[None, bytes], Union[bytes, None],
                                                  Union[None, bool], Union[str, None]]:
        """
        Gets creation trace context metadata used for distributed message tracing message
        creation context information across service boundaries.
        It allows correlating the producer with the consumers of a message, regardless of intermediary

        Returns:
            Tuple[bytes, bytes, bool, Union[str, None]]: Tuple of trace_id (16 bytes),
                span_id (8 bytes), is_sampled, and trace_state, where trace_state is optional

        Raises:
            PubSubPlusClientError: If an error was encountered during the operation
        """
        trace_id, error = self._solace_message.get_creation_trace_context_trace_id()
        if trace_id is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved trace id %s from creation context of message %s.",
                    trace_id, self._solace_message.msg_p)
        elif trace_id is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find trace ID from creation context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        span_id, error = self._solace_message.get_creation_trace_context_span_id()
        if span_id is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved span id %s from creation context of message %s.",
                    span_id, self._solace_message.msg_p)
        elif span_id is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find span ID from creation context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        sampled_flag, error = self._solace_message.get_creation_trace_context_sampled()
        if sampled_flag is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved sampled_flag %s from creation context of message %s.",
                    sampled_flag, self._solace_message.msg_p)
        elif sampled_flag is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find sampled_flag from creation context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        trace_state, error = self._solace_message.get_creation_trace_context_trace_state()
        if trace_state is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved trace state %s from creation context of message %s.",
                    trace_state, self._solace_message.msg_p)
        elif trace_state is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find trace ID from creation context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        return trace_id, span_id, sampled_flag, trace_state

    def get_transport_trace_context(self) -> Tuple[Union[None, bytes], Union[None, bytes],
                                                   Union[None, bool], Union[str, None]]:
        """
        Gets transport trace context metadata used for distributed message tracing.

        Returns:
            Tuple[bytes, bytes, bool, Union[str, None]]: Tuple of trace_id (16 bytes),
                span_id (8 bytes), is_sampled, trace_state; where trace_state is optional

        Raises:
            PubSubPlusClientError: If there was an internal error during the operation.
        """
        trace_id, error = self._solace_message.get_transport_trace_context_trace_id()
        if trace_id is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved trace id %s from transport context of message %s.",
                    trace_id, self._solace_message.msg_p)
        elif trace_id is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find trace ID from transport context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        span_id, error = self._solace_message.get_transport_trace_context_span_id()
        if span_id is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved span id %s from transport context of message %s.",
                    span_id, self._solace_message.msg_p)
        elif span_id is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find span ID from transport context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        sampled_flag, error = self._solace_message.get_transport_trace_context_sampled()
        if sampled_flag is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved sampled_flag %s from transport context of message %s.",
                    sampled_flag, self._solace_message.msg_p)
        elif sampled_flag is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find sampled_flag from transport context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        trace_state, error = self._solace_message.get_transport_trace_context_trace_state()
        if trace_state is not None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Retrieved trace state %s from transport context of message %s.",
                    trace_state, self._solace_message.msg_p)
        elif trace_state is None and error is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Did not find trace ID from transport context of message %s.",
                    self._solace_message.msg_p)
        else:
            logger.warning(error)
            raise PubSubPlusClientError(error)

        return trace_id, span_id, sampled_flag, trace_state

    def get_rest_interoperability_support(self) -> '_RestInteroperabilitySupport':
        # Get RestInteroperabilitySupport object to invoke it's method
        return self.__rest_interoperability_support

    def __process_rest_interoperability(self, msg_p: _SolaceMessage):
        content_type_p = ctypes.c_char_p()
        encoding_p = ctypes.c_char_p()
        content_type_return_code = msg_p.get_message_http_content_type(content_type_p)
        content_encoding_return_type = msg_p.get_message_http_content_encoding(encoding_p)
        self._get_http_content_type = self.__process_rest_data(content_type_return_code, content_type_p)
        self._get_http_content_encoding = self.__process_rest_data(content_encoding_return_type, encoding_p)

    @staticmethod
    def __process_rest_data(return_code, ptr_value):
        if return_code == SOLCLIENT_OK:
            return ptr_value.value.decode()
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='Message->process_rest_data',
                                exception_message=FAILED_TO_RETRIEVE)
        logger.warning(str(exception))
        raise exception

    @property
    def solace_message(self):
        #  Property holds and returns a Solace Event Broker message.
        return self._solace_message

    # refer the  link https://docs.python.org/3/library/ctypes.html#fundamental-data-types for mapping
    # between ctypes & python's data types . sol_client_field_t.value.* is already a  python data type  when we receive
    # instead of ctypes data type.
    # For example   sol_client_field_t.value.boolean we defined  mapping between c & ctypes as
    # ('boolean', ctypes.c_bool) in _SolClientValue  so  from the table defined in the link the mapping between
    # ctypes, c & python is (c_bool, _Bool, bool (1)) similarly for wchar the mapping is ('wchar', ctypes.c_wchar)
    # and in python it is string (c_wchar_p, wchar_t * (NUL terminated), string or None) so no need to call decode
    # but when its c_char_p the python equivalent is bytes
    # (c_char_p,  char * (NUL terminated), bytes object or None) so we have to decode the value,
    # for all types of uint/int the python equivalent is int
    def _get_data(self, sol_client_field_t):  # pylint: disable=too-many-branches, too-many-return-statements

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_BOOL.value:
            return sol_client_field_t.value.boolean

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_UINT8.value:
            return sol_client_field_t.value.uint8
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_INT8.value:
            return sol_client_field_t.value.int8
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_UINT16.value:
            return sol_client_field_t.value.uint16
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_INT16.value:
            return sol_client_field_t.value.int16
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_UINT32.value:
            return sol_client_field_t.value.uint32
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_INT32.value:
            return sol_client_field_t.value.int32
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_INT64.value:
            return sol_client_field_t.value.int64
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_UINT64.value:
            return sol_client_field_t.value.uint64

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_WCHAR.value:
            return sol_client_field_t.value.wchar
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_STRING.value:
            return sol_client_field_t.value.string.decode()
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_BYTEARRAY.value:
            return _SolaceMessage.get_payload_from_memory(sol_client_field_t.length, sol_client_field_t.value.bytearray)
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_FLOAT.value:
            return sol_client_field_t.value.float32
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_DOUBLE.value:
            return sol_client_field_t.value.float64

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_MAP.value:
            return self._get_map_stream(map_p=sol_client_field_t.value.map, stream_p=None)
        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_STREAM.value:
            return self._get_map_stream(map_p=None, stream_p=sol_client_field_t.value.stream)

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_NULL.value:
            return None

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_DESTINATION.value:
            # WARNING: even though we have destination type like the following:
            # SOLCLIENT_NULL_DESTINATION = -1
            # SOLCLIENT_TOPIC_DESTINATION = 0
            # SOLCLIENT_QUEUE_DESTINATION = 1
            # SOLCLIENT_TOPIC_TEMP_DESTINATION = 2
            # SOLCLIENT_QUEUE_TEMP_DESTINATION = 3
            # we treat everything as SOLCLIENT_TOPIC_DESTINATION
            # discard whatever type we receive except NULL DESTINATION,  behaviour may change in future
            if sol_client_field_t.value.dest.destType != SOLCLIENT_NULL_DESTINATION:
                return TopicSubscription.of(sol_client_field_t.value.dest.dest.decode())
            return None  # return None when we receive SOLCLIENT_NULL_DESTINATION

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_SMF.value:
            return _SolaceMessage.get_payload_from_memory(sol_client_field_t.length, sol_client_field_t.value.bytearray)

        if sol_client_field_t.type == _SolClientFieldType.SOLCLIENT_UNKNOWN.value:
            return _SolaceMessage.get_payload_from_memory(sol_client_field_t.length, sol_client_field_t.value.bytearray)

        # exception thrown when type is not even detected as  SOLCLIENT_UNKNOWN
        logger.warning("Received Unknown data type: %s", sol_client_field_t.type)
        raise SolaceSDTError(f"Received Unknown data type: {sol_client_field_t.type}")  # pragma: no cover
        # Ignored due to core error scenarios

    def _get_map_stream(self, map_p=None, stream_p=None):
        sdt = {} if stream_p is None else []
        address_pointer = map_p if stream_p is None else stream_p
        if isinstance(address_pointer, int):  # this we get from  get_next_field,
            # but from get_binary_attachment_map/steam(outer most map/stream) we get c_void_p instead of int
            address_pointer = ctypes.c_void_p(address_pointer)
        sol_client_field_t = _SolClientField()
        key_p = ctypes.c_char_p()
        while True:

            return_code = get_next_field(address_pointer, sol_client_field_t, key_p)
            if return_code == SOLCLIENT_FAIL:  # pragma: no cover # Ignored due to core error scenarios
                exception: PubSubPlusCoreClientError = \
                    get_last_error_info(return_code=return_code,
                                        caller_description='Message->get_next_field',
                                        exception_message='Unable to get message next field')
                map_stream_cleanup(address_pointer)  # close tha map/stream in the event of exception
                logger.warning(str(exception))
                raise exception
            if return_code == SOLCLIENT_EOS:
                map_stream_cleanup(address_pointer)
                break
            if return_code == SOLCLIENT_OK:
                if stream_p is None:
                    key = key_p.value.decode()  # pylint: disable=no-member
                    sdt[key] = self._get_data(sol_client_field_t)
                else:
                    sdt.append(self._get_data(sol_client_field_t))
        return sdt

    def _prepare_dict(self, is_user_property_map=False) -> Union[Dict, None]:
        # common to retrieve additional_message_properties & payload that contains SDT
        map_p = ctypes.c_void_p(None)
        if is_user_property_map:
            return_code = self._solace_message.get_user_property_map(map_p)
        else:
            return_code = self._solace_message.get_binary_attachment_map(map_p)
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        if return_code == SOLCLIENT_FAIL:
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='Message->get_properties',
                                    exception_message='Unable to get payload user properties')
            logger.warning(str(exception))
            raise exception
        sdt_map = self._get_map_stream(map_p=map_p, stream_p=None)
        return sdt_map

    def _prepare_list(self) -> Union[List, None]:
        stream_p = ctypes.c_void_p(None)
        return_code = self._solace_message.get_binary_attachment_stream(stream_p)
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        if return_code == SOLCLIENT_FAIL:
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='Message->get_properties',
                                    exception_message='Unable to get payload user properties')
            logger.warning(str(exception))
            raise exception
        return self._get_map_stream(map_p=None, stream_p=stream_p)

    def get_properties(self) -> Union[Dict, None]:
        # Return the properties attached to the message
        self._user_properties = self._prepare_dict(True)
        return self._user_properties

    def has_property(self, name: str) -> bool:
        # checks if message has a specific property attached.
        # :param name:
        # :return: boolean value
        is_type_matches(name, str, logger=logger)
        if not self._user_properties:
            self.get_properties()
        if isinstance(self._user_properties, dict):
            has_prop = name in self._user_properties
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug("Is property: [%s] exists? %s", name, has_prop)
            return has_prop
        return False

    def get_property(self, name: str) -> Union[str, int, bytearray, None]:
        # Get the value of a specific property.
        # :param: name the name of the property
        # :return: the value of the property or None if the property was not defined
        is_type_matches(name, str, logger=logger)
        if not self._user_properties:
            self.get_properties()
        if isinstance(self._user_properties, dict):
            user_prop = self._user_properties.get(name, None)
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug("Get Prop:[%s] Values: [%s]", name, user_prop)
            return user_prop
        return None

    def get_payload_as_bytes(self) -> Union[bytearray, None]:
        # Get the raw payload of the message
        # Returns:
        #     bytearray : The byte [] with the message payload.
        #     None : There is no payload
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug("Get [%s] payload as bytes", Message.__name__)
        buffer_p = ctypes.c_void_p(None)
        buffer_size = ctypes.c_uint32(0)
        xml_buffer_p = ctypes.c_void_p(None)
        xml_buffer_size = ctypes.c_uint32(0)
        return_code = self._solace_message.message_get_binary_attachment_ptr(buffer_p, buffer_size)
        xml_return_code = self._solace_message.get_xml_ptr(xml_buffer_p, xml_buffer_size)
        return _SolaceMessage.process_payload(return_code, buffer_p, buffer_size, xml_return_code,
                                              xml_buffer_p, xml_buffer_size, is_str=False)

    def get_binary_attachment(self):
        # This method is used to get the binary attachment from the receiver side
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug("Get [%s] binary attachment", Message.__name__)
        buffer_size, buffer_p = self._solace_message.get_payload_details()
        if buffer_size in [None, 0]:
            return None
        return _SolaceMessage.get_payload_from_memory(buffer_size, buffer_p)

    def get_payload_as_string(self) -> Union[str, None]:
        # Get especially to String decoded payload
        # Returns:
        #     payload (str) : the String representation of a payload
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug("Get [%s] payload as string", Message.__name__)
        binary_p = ctypes.c_char_p()
        xml_buffer_p = ctypes.c_void_p(None)
        xml_buffer_size = ctypes.c_uint32(0)
        str_return_code = self._solace_message.message_get_binary_attachment_string(binary_p)
        xml_return_code = self._solace_message.get_xml_ptr(xml_buffer_p, xml_buffer_size)
        return _SolaceMessage.process_payload(str_return_code, binary_p, None, xml_return_code,
                                              xml_buffer_p, xml_buffer_size, is_str=True)

    def get_payload_as_dictionary(self) -> Union[Dict, None]:
        if self._sdt_map:
            return self._sdt_map
        self._sdt_map = self._prepare_dict(False)
        return self._sdt_map

    def get_payload_as_list(self) -> Union[List, None]:
        if self._sdt_stream:
            return self._sdt_stream
        self._sdt_stream = self._prepare_list()
        return self._sdt_stream

    def get_correlation_id(self) -> Union[str, None]:
        # Get correlation id passed from a message producer
        # Returns:
        #     str or None : the unique identifier for the message set by the producer or None
        return_code = SOLCLIENT_FAIL
        try:
            correlation_p = ctypes.c_char_p()
            return_code = self._solace_message.message_get_correlation_id(correlation_p)
            if return_code == SOLCLIENT_OK:
                correlation_id = correlation_p.value.decode()  # pylint: disable=no-member
                if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                    logger.debug("Get [%s] correlation id: [%s]", Message.__name__, correlation_id)
                return correlation_id
            if return_code == SOLCLIENT_NOT_FOUND:
                return None
            logger.warning("Unable to get correlation id. Status code: %d", return_code)  # pragma: no cover
            # Ignored due to core error scenarios
            raise PubSubPlusClientError(f"Unable to get correlation id. Status code: {return_code}")  # pragma: no cover
            # Ignored due to core error scenarios
        except PubSubPlusClientError as exception:
            logger.warning("Unable to get correlation id. Status code: %d", return_code)  # pragma: no cover
            # Ignored due to core error scenarios
            raise PubSubPlusClientError(
                f"Unable to get correlation id. Status code: {return_code}") from exception  # pragma: no cover
            # Ignored due to core error scenarios

    def get_expiration(self) -> Union[int, None]:
        # The UTC time (in ms, from midnight, January 1, 1970 UTC) when the message is supposed
        # to expire.A value of 0 means the message never expires. The default value is 0.
        # Returns:
        #     int: The UTC time when the message is discarded or moved to a Dead Message Queue
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Get [%s] expiration", Message.__name__)
        timestamp_p = ctypes.c_uint64(0)
        return_code = self._solace_message.get_message_expiration(timestamp_p)
        if return_code == SOLCLIENT_OK:
            expiration_timestamp = timestamp_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug("Get [%s] expiration: [%s]", Message.__name__, expiration_timestamp)
            return expiration_timestamp
        if return_code == SOLCLIENT_NOT_FOUND:  # pragma: no cover # Ignored due to core error scenarios
            return None
        logger.warning("Unable to get expiration time. Status code: %d", return_code)  # pragma: no cover
        # Ignored due to core error scenarios
        raise PubSubPlusClientError(f"Unable to get expiration time. Status code:{return_code}")  # pragma: no cover
        # Ignored due to core error scenarios

    def get_sequence_number(self) -> Union[int, None]:
        # Gets the sequence number
        # Returns:
        #     int : The positive sequence number or -1 if it was not set.
        seq_num_p = ctypes.c_uint64(0)
        return_code = self._solace_message.get_message_sequence_number(seq_num_p)
        if return_code == SOLCLIENT_OK:
            sequence_number = seq_num_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug("Get [%s] sequence number: [%d]", Message.__name__, sequence_number)
            return sequence_number
        if return_code == SOLCLIENT_NOT_FOUND:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("[%s] sequence number NOT FOUND", Message.__name__)
            return None
        logger.warning("Unable to get sequence number. Status code: %d", return_code)  # pragma: no cover
        # Ignored due to core error scenarios
        raise PubSubPlusClientError(f"Unable to get sequence number. Status code: {return_code}")  # pragma: no cover
        # Ignored due to core error scenarios

    def get_priority(self) -> Union[int, None]:
        # Gets priority value in the range of 0–255, or -1 if it is not set
        #
        # Returns:
        #     int: priority value in the range of 0–255, or -1 if it is not set
        priority_p = ctypes.c_int32(0)
        return_code = self._solace_message.get_message_priority(priority_p)

        if return_code == SOLCLIENT_OK:
            if priority_p.value == SOLCLIENT_NOT_SET_PRIORITY_VALUE:
                priority = None
            else:
                priority = priority_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug("Get %s priority: %d", Message.__name__, priority)
            return priority
        logger.warning("Unable to get priority. Status code: %d", return_code)  # pragma: no cover
        # Ignored due to core error scenarios
        raise PubSubPlusClientError(f"Unable to get priority. Status code: {return_code}")  # pragma: no cover
        # Ignored due to core error scenarios

    def get_application_message_type(self) -> Union[str, None]:
        # Gets the application message type. This value is used by applications only, and is passed
        # through the API untouched
        # Returns:
        #     msg_type (str/None) :application message type or null if not set
        app_msg_type = ctypes.c_char_p()
        return_code = self.solace_message.get_application_msg_type(app_msg_type)
        if return_code == SOLCLIENT_OK:
            msg_type = app_msg_type.value.decode()  # type: ignore  # pylint: disable=no-member
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Get application message type: [%s]', msg_type)
            return msg_type
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description=f'{type(self).__name__}->get_application_message_type()',
                                exception_message=FAILED_TO_GET_APPLICATION_TYPE)  # pragma: no cover
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenario
        raise exception  # pragma: no cover # Due to core error scenario

    def get_application_message_id(self) -> Union[str, None]:
        # Gets an optional message identifier when sender application sets one.
        #
        # Returns:
        #    str: Sender application identifier if set by message publisher, or None/empty if not set.
        app_msg_id = ctypes.c_char_p()

        return_code = self.solace_message.get_application_message_id(app_msg_id)
        if return_code == SOLCLIENT_OK:
            msg_id = app_msg_id.value.decode()  # type: ignore  # pylint: disable=no-member
            if logger.isEnabledFor(logging.DEBUG):  # pragma no cover # Ignored due to log level
                logger.debug('Get application message id: [%s]', msg_id)
            return msg_id
        if return_code == SOLCLIENT_NOT_FOUND:
            return None
        exception: PubSubPlusClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description=f'{type(self).__name__}->get_application_message_id()',
                                exception_message=FAILED_TO_GET_APPLICATION_ID)  # pragma: no cover
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenario
        raise exception  # pragma: no cover # Due to core error scenario

    def get_class_of_service(self) -> Union[int, None]:
        # Gets the message class of service
        # Returns:
        #     cos (int): if valid cos is found, or None if not set or in failure cases
        cos_p = ctypes.c_uint32()
        return_code = self.solace_message.get_message_class_of_service(cos_p)
        if return_code == SOLCLIENT_OK:
            cos = cos_p.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Message class of service: %d', cos)
            return cos
        # The CCSMP method for retrieving the CoS returns either SOLCLIENT_OK or SOLCLIENT_FAIL.
        # We only check for SOLCLIENT_OK, because everything else is considered a fail, whether the
        # CCSMP method returns SOLCLIENT_FAIL or not, which makes checking for SOLCLIENT_FAIL a
        # waste of cycles.
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_InboundMessage->get_sender_timestamp',
                                exception_message="Unable to get message send timestamp.")  # pragma: no cover
        # Due to core error scenario
        logger.warning(str(exception))  # pragma: no cover # Due to core error scenarios
        raise exception  # pragma: no cover # Due to core error scenario

def map_stream_cleanup(mapstream_p):
    # function to clean up map & stream
    if mapstream_p.value:
        try:
            return_code = close_map_stream(mapstream_p)
            if return_code != SOLCLIENT_OK:
                logger.warning("%s", last_error_info(return_code, caller_desc="map_stream_cleanup"))
        except PubSubPlusClientError as exception:  # pragma: no cover # Due to core error scenarios
            logger.warning("Failed to free up the map container. Error: %s", str(exception))
