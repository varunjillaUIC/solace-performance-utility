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

# pylint: disable=missing-class-docstring, missing-function-docstring

"""Module contains the Implementation class and methods for the OutboundMessageBuilder and OutboundMessage"""

import ctypes
import logging
import weakref
from ctypes import c_char_p
from typing import TypeVar, Dict, Union

from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_FAIL, SOLCLIENT_TOPIC_DESTINATION, \
    SOLCLIENT_QUEUE_DESTINATION
from solace.messaging.config._solace_message_constants import INVALID_ADDITIONAL_PROPS, DICT_KEY_CANNOT_NONE, \
    INVALID_TYPE_IN_ADDITIONAL_PROPS_VALUE
from solace.messaging.core._message import _Message, map_stream_cleanup, _SolClientDestination
from solace.messaging.core._solace_message import _SolaceMessage
from solace.messaging.core._solace_sdt import _SolaceSDTMap, _SolaceSDTStream, valid_sdt_types
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, IllegalArgumentError, \
    InvalidDataTypeError, PubSubPlusCoreClientError
from solace.messaging.publisher._outbound_message_utility import container_add_byte_array, \
    container_add_string, container_add_int64, container_add_boolean, \
    container_add_double, container_open_sub_map, container_open_sub_stream, container_add_null, \
    container_add_destination, container_delete_field, container_add_uint64
from solace.messaging.publisher.outbound_message import OutboundMessageBuilder, OutboundMessage
from solace.messaging.resources.destination import Destination
from solace.messaging.resources.queue import Queue
from solace.messaging.resources.topic import Topic
from solace.messaging.utils._solace_utilities import get_last_error_info, is_type_matches, is_not_negative, \
    handle_none_for_str
from solace.messaging.utils.converter import ObjectToBytes

logger = logging.getLogger('solace.messaging.publisher')


class _SolaceStream:
    def __init__(self, solace_message):
        self._stream_p = ctypes.c_void_p()
        return_code = solace_message.create_binary_attachment_stream(self._stream_p)

        if return_code != SOLCLIENT_OK:  # pragma: no cover # Ignored due to core error scenarios
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='_SolaceStream->init',
                                    exception_message='Unable to set  stream')
            logger.warning(str(exception))
            raise exception
        # by the time weakref.finalize called we might have  already closed the stream while building outbound message
        self._finalizer = weakref.finalize(self, map_stream_cleanup, self._stream_p)

    @property
    def stream_p(self):
        return self._stream_p


class _SolaceMap:  # pylint: disable=missing-class-docstring, missing-function-docstring
    def __init__(self, solace_message=None, map_p=None, is_user_property_map=True):
        if map_p is not None:
            self._map_p = map_p
        else:
            self._map_p = ctypes.c_void_p()
            if is_user_property_map:
                return_code = solace_message.create_user_property_map(self._map_p)
            else:
                return_code = solace_message.create_binary_attachment_map(self._map_p)
            if return_code != SOLCLIENT_OK:  # pragma: no cover # Ignored due to core error scenarios
                exception: PubSubPlusCoreClientError = \
                    get_last_error_info(return_code=return_code,
                                        caller_description='_SolaceMap->init',
                                        exception_message='Unable to set  map')
                logger.warning(str(exception))
                raise exception
        # by the time weakref.finalize called we might have  already closed the map while building outbound message
        self._finalizer = weakref.finalize(self, map_stream_cleanup, self._map_p)

    @property
    def map_p(self):
        return self._map_p

    @staticmethod
    def get_user_map_from_message(solace_message):
        map_p = ctypes.c_void_p()
        return_code = solace_message.get_user_property_map(map_p)
        if return_code == SOLCLIENT_OK:
            return _SolaceMap(None, map_p)
        return None

    @staticmethod
    def create_int_value(map_p, property_key, property_value):
        _unint64 = {"min": 2 ** 63 - 1, "max": 2 ** 64 - 1}
        _int64 = {"min": -2 ** 63, "max": 2 ** 63 - 1}
        if _int64['min'] <= property_value <= _unint64['max']:
            if _unint64['min'] < property_value <= _unint64['max']:
                return container_add_uint64(map_p, ctypes.c_uint64(property_value), property_key)
            if _int64['min'] <= property_value <= _int64['max']:
                return container_add_int64(map_p, ctypes.c_int64(property_value), property_key)
        raise InvalidDataTypeError(f"The value : {property_value} is out of range of int64/uint64")

    @staticmethod
    def add_props_to_container(map_p, property_key: Union[str, None], property_value: Union[valid_sdt_types]):
        #  Add  properties to the container, common for adding items in a binary map/stream & user map
        # Args:
        #     property_key (str, None): key
        #     property_value (Any):  value
        #
        # Returns:
        # valid_sdt_types = (int, str, bytearray, float, bool, tuple, list, dict, Destination)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Adding user property. Property key: [%s]. Property value: [%s]. '
                         'Type: [%s]', property_key, property_value, str(type(property_value)))

        # property_key must be None for stream
        return_code = SOLCLIENT_OK
        property_key = c_char_p(None) if property_key is None else c_char_p(property_key.encode())
        if not isinstance(property_value, valid_sdt_types):
            error_message = INVALID_TYPE_IN_ADDITIONAL_PROPS_VALUE.substitute(value_type=type(property_value))
            logger.warning(error_message)
            raise InvalidDataTypeError(error_message)

        if isinstance(property_value, bool):
            property_value = ctypes.c_bool(property_value)
            return_code = container_add_boolean(map_p, property_value, property_key)
        elif isinstance(property_value, int):
            return_code = _SolaceMap.create_int_value(map_p, property_key, property_value)
        elif isinstance(property_value, str):
            property_value = c_char_p(property_value.encode())
            return_code = container_add_string(map_p, property_value, property_key)
        elif isinstance(property_value, bytearray):
            char_array = ctypes.c_char * len(property_value)
            property_value = char_array.from_buffer(property_value)
            return_code = container_add_byte_array(map_p, property_value, ctypes.c_uint32(len(property_value)),
                                                   property_key)
        elif isinstance(property_value, float):
            property_value = ctypes.c_double(property_value)
            return_code = container_add_double(map_p, property_value, property_key)
        elif isinstance(property_value, type(None)):
            return_code = container_add_null(map_p, property_key)
        elif isinstance(property_value, Destination):
            return_code = _SolaceMap._add_destination(map_p, property_key, property_value)
        if return_code == SOLCLIENT_FAIL:
            error = get_last_error_info(return_code, "add_props_to_container")
            logger.warning(error)
            raise PubSubPlusClientError(error)

    @staticmethod
    def _add_destination(map_p, property_key, property_value):
        if isinstance(property_value, (Topic, Queue)):
            if isinstance(property_value, Topic):
                destination_type = ctypes.c_int(SOLCLIENT_TOPIC_DESTINATION)
            elif isinstance(property_value, Queue):  # WARNING: Even though queue destination type is
                # sent here python  api receiver will receive as Topic type behaviour may change in future or
                # behaviour might be different in other api/tool for example
                # sdkpref_c currently receive as Queue type when Queue type is sent from python
                destination_type = ctypes.c_int(SOLCLIENT_QUEUE_DESTINATION)
            destination = _SolClientDestination(destType=destination_type,
                                                dest=c_char_p(property_value.get_name().encode()))
            return container_add_destination(map_p, destination, property_key)
        # user may extend Destination create a new type apart of from currently supported Topic & Queue
        error_message = INVALID_TYPE_IN_ADDITIONAL_PROPS_VALUE.substitute(value_type=type(property_value))
        logger.warning(error_message)
        raise InvalidDataTypeError(error_message)


class _SolaceSubMapStream:  # common for creating sub map/stream
    # map_cleanup will be called inside prepare_map/stream
    def __init__(self, container_p, name, is_stream=False):
        self._container_p = ctypes.c_void_p()
        # name is None when sub-map/sub-stream is element of a stream but in a map when we encounter
        # sub-map/sub-stream we have pass that key as name who is having this sub-map/sub-stream as its value
        # example : {"11": [1, 2, 3, {"a": "b", "c": [1, 2, 3]}]}  here the key 11 have value as a stream here
        # we have to pass name as 11 also inside the stream  4th element {"a": "b", "c": [1, 2, 3]} is a dict
        # here we have pass name as None, but for the element "c": [1, 2, 3] value is a  stream here we
        # have to pass c as name when we create a stream containing values 1,2,3.
        self._name = ctypes.c_char_p(name.encode()) if name is not None else ctypes.c_char_p(None)
        if not is_stream:
            return_code = container_open_sub_map(container_p, self._container_p, self._name)
        else:
            return_code = container_open_sub_stream(container_p, self._container_p, self._name)
        if return_code != SOLCLIENT_OK:  # pragma: no cover # Ignored due to core error scenarios
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='SolaceSubMap->init',
                                    exception_message='Unable to set  sub container')
            logger.warning(str(exception))
            raise exception
        # by the time weakref.finalize called we might have  already closed the map while building outbound message
        self._finalizer = weakref.finalize(self, map_stream_cleanup, self._container_p)

    @property
    def container_p(self):
        return self._container_p


class _OutboundMessageBuilder(OutboundMessageBuilder) \
        :  # pylint: disable=missing-class-docstring, missing-function-docstring
    # This builder is used for building outbound messages which can hold any type of messages used for publish message

    T = TypeVar('T', bytearray, str, dict, list, tuple, 'OutboundMessage')

    def __init__(self):
        # message pointer initialization & allocation takes place here
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._solace_message = _SolaceMessage()
        self.priority = None

        return_code = self._solace_message.set_persistent_dmq_eligible(True)
        if return_code != SOLCLIENT_OK:
            exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->__init__',
                                exception_message='Failed to set default value for dmq eligible .')
            logger.error(str(exception))
            raise PubSubPlusClientError(exception)


    def from_properties(self, configuration: Dict[str, Union[str, int, float, bool, dict, list, tuple,
                                                             None, bytearray]]) -> 'OutboundMessageBuilder':
        # This method takes dict and prepare message properties
        # Args:
        # configuration (Dict[str, Union[str, int, bytearray]]): The configuration dictionary, it can have the key
        #                                                        as string and the value can be either a string or
        #                                                        an integer or a bytearray.
        #
        # Returns:
        #
        _OutboundMessageBuilder.add_message_properties(_SolaceSDTMap(configuration), self._solace_message)
        return self

    def with_property(self, property_key: str,
                      property_value: Union[str, int, float, bool, dict, list, tuple, None, bytearray]) \
        -> 'OutboundMessageBuilder':
        #  create user property with the given key & value
        # Args:
        #     property_key (str): key
        #     property_value (str): value
        #
        # Returns:
        #     OutboundMessageBuilder
        if property_key not in ['', None]:
            is_type_matches(property_key, str, logger=logger)
            is_type_matches(property_value, valid_sdt_types, logger=logger)
            _OutboundMessageBuilder.add_message_properties(_SolaceSDTMap({property_key: property_value}),
                                                           self._solace_message)
            return self
        exception_message = DICT_KEY_CANNOT_NONE if property_key in ['', None] else INVALID_ADDITIONAL_PROPS
        raise IllegalArgumentError(exception_message)

    def with_expiration(self, timestamp: int) -> 'OutboundMessageBuilder':
        # set expiration time
        # Args:
        #     timestamp (int): timestamp in ms
        #
        # Returns:
        #     OutboundMessageBuilder
        is_type_matches(timestamp, int, logger=logger)
        is_not_negative(timestamp, logger=logger)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Set message expiration time: [%d]', timestamp)
        return_code = self._solace_message.set_message_expiration(timestamp)

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->with_expiration',
                                exception_message='Unable to set expiration time.')
        logger.warning(str(exception))
        raise exception

    def with_correlation_id(self, correlation_id) -> 'OutboundMessageBuilder':
        # sets the correlation_id
        # Args:
        #     correlation_id (str): The correlation ID to set
        #
        # Returns:
        #     OuboundMessageBuilder: instance used for message building
        is_type_matches(correlation_id, str)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Set message correlation ID: [%s]', correlation_id)
        return_code = self._solace_message.message_set_correlation_id(correlation_id)

        if return_code == SOLCLIENT_OK:
            return self
        error: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->with_correlation_id',
                                exception_message='Unable to set correlation ID.')
        logger.warning(str(error))
        raise InvalidDataTypeError(f"Failed to assign the correlation ID `{correlation_id}` to the message `{self}`.")

    def with_sender_id(self, sender_id: Union[str, None]) -> 'OutboundMessageBuilder':
        # set the sender ID
        # Args:
        #     sender_id (str): The sender ID to assign to the message header.
        #
        # Returns:
        #     OutboundMessageBuilder

        # if this returns true then sender_id is not None, and we need to check the type
        # if this returns false, then sender_id is None and we need to delete the sender_id
        if sender_id is not None:
            is_type_matches(sender_id, str, logger=logger)
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Set message sender ID: [%s]', sender_id)
        else:
            is_type_matches(sender_id, type(None), logger=logger)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Delete message sender ID')
        return_code = self._solace_message.update_message_sender_id(sender_id)

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->with_sender_id',
                                exception_message='Unable to set sender ID.')
        logger.warning(str(exception))
        raise exception

    def with_priority(self, priority: int) -> 'OutboundMessageBuilder':
        # Set the priority (0 to 255), where zero is the lowest  priority
        # Args:
        #     priority (OutboundMessageBuilder.Priority): integer value
        #
        # Returns:
        #     OutboundMessageBuilder
        is_type_matches(priority, int, logger=logger)
        is_not_negative(priority, logger=logger)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('Set message priority: [%d]', priority)
        return_code = self._solace_message.set_message_priority(priority)

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->with_priority',
                                exception_message='Unable to set priority.')
        logger.warning(str(exception))
        raise exception

    def with_sequence_number(self, sequence_number: int) -> 'OutboundMessageBuilder':
        # Set the sequence number for the message
        # Args:
        #     sequence_number (int):  Expecting a integer value
        #
        # Returns:
        #     OutboundMessageBuilder
        is_type_matches(sequence_number, int, logger=logger)
        is_not_negative(sequence_number, logger=logger)
        return_code = self._solace_message.set_message_sequence_number(sequence_number)

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->with_sequence_number',
                                exception_message='Unable to set sequence number.')
        logger.warning(str(exception))
        raise exception

    def with_application_message_id(self, application_message_id: str) -> 'OutboundMessageBuilder':
        # Set the application message id for a message from a str, or None to delete
        # Args:
        #     application_message_id (str):  application message id
        #
        # Returns:
        #     OutboundMessageBuilder
        is_type_matches(application_message_id, str, logger=logger)
        return_code = self._solace_message.set_message_application_message_id(application_message_id) \
            if application_message_id is not None else self._solace_message.delete_message_application_message_id()

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_DirectMessageReceiver->with_application_message_id',
                                exception_message='Unable to set application message id')
        logger.warning(str(exception))
        raise exception

    def with_application_message_type(self, application_message_type: str) -> 'OutboundMessageBuilder':
        # Set the application message type for a message from a string or None to delete
        # Args:
        #     application_message_type (str): application message type
        #
        # Returns:
        #     OutboundMessageBuilder
        is_type_matches(application_message_type, str, logger=logger)
        return_code = self._solace_message.set_message_application_message_type(application_message_type) \
            if application_message_type is not None else self._solace_message.delete_message_application_message_type()

        if return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='_DirectMessageReceiver->with_application_message_type',
                                exception_message='Unable to set application message type.')
        logger.warning(str(exception))
        raise exception

    def with_http_content_header(self, content_type: str, content_encoding: str) -> 'OutboundMessageBuilder':
        # Setting the HTTP content type and encoding for a message from a string
        # Args:
        #     content_type (str):  expecting a valid content type
        #     content_encoding (str):  expecting a valid content  encoding
        # Returns:
        is_type_matches(content_type, str, logger=logger)
        is_type_matches(content_encoding, str, logger=logger)
        content_type_return_code = self._solace_message.set_message_http_content_type(content_type)
        if content_type_return_code != SOLCLIENT_OK:
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=content_type_return_code,
                                    caller_description='_DirectMessageReceiver->with_http_content_header',
                                    exception_message='Unable to set HTTP content type.')
            logger.warning(str(exception))
            raise exception

        content_encoding_return_code = self._solace_message.set_message_http_content_encoding(content_encoding)
        if content_encoding_return_code == SOLCLIENT_OK:
            return self
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=content_encoding_return_code,
                                caller_description='_DirectMessageReceiver->with_http_content_header',
                                exception_message='Unable to set HTTP content header.')
        logger.warning(str(exception))
        raise exception

    def build(self, payload: T, additional_message_properties: Dict[str, Union[str, int, float, bool, dict,
                                                                               list, tuple, None, bytearray]] = None,
              converter: ObjectToBytes[T] = None) -> '_OutboundMessage':
        # Args:
        #     payload (T): payload
        # Kwargs:
        #     additional_message_properties (Any): properties
        #     converter (ObjectToBytes): converter to convert the ``payload`` object to ``bytearray``
        # Returns:

        # Here self.msg_p is a template for all the message's properties
        return_code = SOLCLIENT_FAIL # Fail by default so we require success path from CORE_LIB call to continue.
        msg_p_dup = self._solace_message.message_duplicate()
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('BUILD [%s]', OutboundMessage.__name__)

        if additional_message_properties:
            _OutboundMessageBuilder.add_message_properties(_SolaceSDTMap(additional_message_properties), msg_p_dup)
        if not converter:
            if isinstance(payload, bytearray):
                char_array = ctypes.c_char * len(payload)
                message = char_array.from_buffer(payload)
                return_code = msg_p_dup.message_set_binary_attachment(message)

            elif isinstance(payload, str):
                return_code = msg_p_dup.message_set_binary_attachment_string(payload)
            elif isinstance(payload, dict):
                custom_dict = _SolaceSDTMap(payload)  # modify payload as solace's custom dict
                solace_map = _SolaceMap(solace_message=msg_p_dup, is_user_property_map=False)
                _OutboundMessageBuilder.prepare_map(custom_dict, solace_map.map_p)
                return_code = SOLCLIENT_OK
            elif isinstance(payload, (tuple, list)):
                custom_list = _SolaceSDTStream(payload)  # modify payload as solace's custom list
                solace_stream = _SolaceStream(solace_message=msg_p_dup)
                _OutboundMessageBuilder.prepare_stream(custom_list, solace_stream.stream_p)
                return_code = SOLCLIENT_OK
        elif converter:
            payload_bytes = converter.to_bytes(payload)
            char_array = ctypes.c_char * len(payload_bytes)
            message = char_array.from_buffer_copy(payload_bytes)
            return_code = msg_p_dup.message_set_binary_attachment(msg=message, msg_length=len(payload_bytes))

        if return_code == SOLCLIENT_OK:
            return _OutboundMessage(msg_p_dup)
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='OutboundMessageBuilder->build',
                                exception_message='Failed to create attachment for the message.')
        logger.warning(str(exception))
        raise exception

    @staticmethod
    def prepare_map(custom_dict: _SolaceSDTMap, map_p, close_map_stream=True):
        # check _SolaceSubMapStream's dev comment to understand when to pass second arg as key when to pass key as None
        try:
            for key, value in custom_dict.items():
                if isinstance(value, dict):
                    solace_sub_map_stream = _SolaceSubMapStream(map_p, key)
                    _OutboundMessageBuilder.prepare_map(value, solace_sub_map_stream.container_p)
                elif isinstance(value, (list, tuple)):
                    solace_sub_map_stream = _SolaceSubMapStream(map_p, key, is_stream=True)
                    _OutboundMessageBuilder.prepare_stream(value, solace_sub_map_stream.container_p)

                elif isinstance(value, (int, str, bytes, bytearray, float, type(None), Destination)):
                    _SolaceMap.add_props_to_container(map_p, key, value)
            if close_map_stream:
                map_stream_cleanup(map_p)
        except Exception as exception:
            map_stream_cleanup(map_p)
            raise exception

    @staticmethod
    def prepare_stream(custom_list: _SolaceSDTStream, stream_p, close_map_stream=True):
        #         # check _SolaceSubMapStream's dev comment to understand when to pass second arg
        #         as key when to pass key as None
        try:
            for item in custom_list:
                if isinstance(item, dict):
                    solace_sub_map_stream = _SolaceSubMapStream(stream_p, None)
                    _OutboundMessageBuilder.prepare_map(item, solace_sub_map_stream.container_p)
                elif isinstance(item, (list, tuple)):
                    solace_sub_map_stream = _SolaceSubMapStream(stream_p, None, is_stream=True)
                    _OutboundMessageBuilder.prepare_stream(item, solace_sub_map_stream.container_p)

                elif isinstance(item, (int, str, bytes, bytearray, float, type(None), Destination)):
                    _SolaceMap.add_props_to_container(stream_p, None, item)
            if close_map_stream:
                map_stream_cleanup(stream_p)
        except Exception as exception:
            map_stream_cleanup(stream_p)
            raise exception

    @staticmethod
    def add_message_properties(configuration, solace_message: '_SolaceMessage'):
        # set the solace defined message properties
        solace_message.handle_message_properties(configuration)
        user_props = set(list(configuration.keys())) - set(
            list(solace_message.message_properties_mapping.keys()) + \
            list(solace_message.legacy_to_current_message_properties_mapping.keys()))
        if len(user_props) == 0:
            return
        solace_map_dup = _SolaceMap.get_user_map_from_message(solace_message)
        if solace_map_dup is None:
            solace_map_dup = _SolaceMap(solace_message)
        for key, value in configuration.items():
            # only add user defined props skip the  properties defined by Solace
            if key in [None, '']:
                logger.warning(DICT_KEY_CANNOT_NONE)
                raise IllegalArgumentError(DICT_KEY_CANNOT_NONE)
            if key in user_props:
                # remove any existing field
                container_delete_field(solace_map_dup.map_p, key)
                # add field value
                if isinstance(value, (dict, list)):
                    _OutboundMessageBuilder.prepare_map({key: value}, solace_map_dup.map_p, close_map_stream=False)
                else:
                    _SolaceMap.add_props_to_container(solace_map_dup.map_p, key, value)


class _OutboundMessage(_Message, OutboundMessage):  # pylint: disable=missing-class-docstring
    # Implementation class for OutboundMessage abstract class

    def __init__(self, msg_p):
        # Args: msg_p:  SolaceMessage used to publish the message
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        super().__init__(msg_p)

    def __str__(self):
        return handle_none_for_str(input_value=self._solace_message.get_message_dump())
