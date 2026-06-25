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

# Module contains the publisher utility methods

# pylint: disable= missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=protected-access

from ctypes import c_void_p, string_at, cast

from solace.messaging.errors.pubsubplus_client_error import InvalidDataTypeError
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.resources.topic import Topic
from solace.messaging.utils._solace_utilities import is_type_matches


class _PublisherUtilities:
    # Publisher utilities

    # correlation tag formatting constants
    # message correlation tags take the form
    # corr_tag[0:1] for type
    # corr_tag[1:9] for pub_id
    # corr_tag[9:17] for message_id
    # for a total length of 17 bytes

    # int value message publisher types
    AWAIT_TYPE = b'\x01'[0]
    ASYNC_TYPE = b'\x02'[0]
    # bytes value message publisher types
    _AWAIT_TYPE_BYTES = b'\x01'
    _ASYNC_TYPE_BYTES = b'\x02'
    # lookup table for int to bytes
    _TYPE_LOOKUP = {
        AWAIT_TYPE: _AWAIT_TYPE_BYTES,
        ASYNC_TYPE: _ASYNC_TYPE_BYTES
    }
    # tag len  len(type) + len(pub_id) + len(message_id)
    _TAG_LEN = 1 + 8 + 8

    # correlation tag utility methods

    @staticmethod
    def decode(encoded_tag: c_void_p) -> bytes:
        return string_at(encoded_tag, _PublisherUtilities._TAG_LEN)

    @staticmethod
    def encode(tag: bytes) -> c_void_p:
        return cast(tag, c_void_p)

    @staticmethod
    def create_publisher_id(publisher) -> bytes:
        # given a publisher object create a unique id in bytes
        # This is implemented specifically for CPython, which returns a representation of the C pointer to the object.
        # It may or may not work for other implementations of Python, such as JPython, or Python implementations.
        # It has been tested on 64 bit Linux, MacOS, Windows, and 32 bit Windows. If other platforms are considered
        # in the future, then this function should be explicitly tested there.
        return id(publisher).to_bytes(8, byteorder="little", signed=True)

    @staticmethod
    def create_message_correlation_tag(pub_id: bytes,
                                       pub_type: int = ASYNC_TYPE,
                                       msg_id: int = 0) -> bytes:
        # given a publisher id, pub_type and msg_id create a correlation of bytes
        bin_tag = _PublisherUtilities._TYPE_LOOKUP[pub_type] + pub_id + msg_id.to_bytes(8, byteorder="little",
                                                                                        signed=True)

        return bin_tag

    @staticmethod
    def get_publisher_id(correlation_tag: bytes) -> bytes:
        # from a given correlation tag return the publisher id
        # if not in the correct format return None
        if correlation_tag:
            tag = correlation_tag
            return None if len(tag) != _PublisherUtilities._TAG_LEN else tag[1:9]
        return None

    @staticmethod
    def get_message_id(correlation_tag: bytes) -> bytes:
        # from a given correlation tag return the message id
        # if not in the correct format return None
        if correlation_tag:
            tag = correlation_tag
            return None if len(tag) != _PublisherUtilities._TAG_LEN else tag[9:17]
        return None

    @staticmethod
    def is_correlation_type(correlation_tag: bytes, pub_type: int) -> bool:
        # test the correlation tag for publish type
        # if not in the correct format return False
        tag = correlation_tag
        return len(tag if tag else b'') == _PublisherUtilities._TAG_LEN and \
                tag[0] == pub_type

    @staticmethod
    def validate_payload_type(message):
        if not isinstance(message,
                          (OutboundMessage, str, bytearray, dict, list, tuple)):
            raise InvalidDataTypeError(f"{type(message)} is unsupported at the "
                                       f"moment to publish a message")


# Global publisher utility functions

def validate_topic_type(destination, logger=None):
    # To validate Topic type
    is_type_matches(destination, Topic, logger=logger)
