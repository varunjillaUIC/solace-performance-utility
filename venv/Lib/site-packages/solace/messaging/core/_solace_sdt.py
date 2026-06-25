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

"""This Module contains the implementation classes and methods for SolaceSDTMap and SolaceSDTStream"""

import logging
from typing import Union

from solace.messaging.config._solace_message_constants import SDT_STREAM_ERROR, SDT_KEY_MAP_ERROR, SDT_VALUE_MAP_ERROR
from solace.messaging.errors.pubsubplus_client_error import SolaceSDTError
from solace.messaging.resources.destination import Destination

logger = logging.getLogger('solace.messaging.core')

valid_sdt_types = (int, str, bytearray, float, bool, tuple, list, dict, type(None), Destination)


def set_sdt_value(value: valid_sdt_types) \
        -> Union[int, float, str, bool, bytes, bytearray, 'SolaceSDTMap', 'SolaceSDTStream']:
    """
    Verifies if the list, tuple or dictionary input matches the SolaceSDTMap, SolaceSDTStream or any other valid
    Solace supported Data types
    Returns:
        SolaceSDTMap: SolaceSDTMap object.
        SolaceSDTStream: SolaceSDTStream object Int, Float, String, Bool, Bytes, Bytearray
    """
    if isinstance(value, dict):
        return _SolaceSDTMap(value)
    elif isinstance(value, (tuple, list)):
        return _SolaceSDTStream(value)
    return value


class _SolaceSDTMap(dict):
    """
    A class for creating the SolaceSDTMap from the dictionary input.
    User provided dictionary will be converted to the SolaceSDTMap if it matches the required data types.
    Accepted data types:
    Key : String
    Values: Integer, Float, String, Bool, Bytearray, None, SolaceSDTMap, SolaceSDTStream, Destination
    """

    def __init__(self, item: dict):
        super().__init__()
        for key, value in item.items():
            _SolaceSDTMap._validate_key_type(key)
            _SolaceSDTMap._validate_value_type(value)
            self[key] = value if value is None else set_sdt_value(value)

    @staticmethod
    def _validate_key_type(key):
        if not isinstance(key, str):
            raise SolaceSDTError(SDT_KEY_MAP_ERROR.substitute(key=str(key), type=str(type(key))))

    @staticmethod
    def _validate_value_type(value):
        if not isinstance(value, valid_sdt_types):
            raise SolaceSDTError(SDT_VALUE_MAP_ERROR.substitute(value=str(value), type=str(type(value))))


class _SolaceSDTStream(list):
    """
    A class for creating the SolaceSDTStream from the list or tuple input.
    User provided list or tuple will be converted to the SolaceSDTStream if it matches the required data types.
    Accepted data types:
    Values: Integer, Float, String, Bool, Bytes, Bytearray, None, SolaceSDTMap, SolaceSDTStream, Destination
    """

    def __init__(self, item: Union[list, tuple]):

        super().__init__()
        if not isinstance(item, (list, tuple)):
            raise SolaceSDTError(SDT_STREAM_ERROR.substitute(value=str(item), type=str(type(item))))
        for value in item:
            if isinstance(value, valid_sdt_types):
                self.append(set_sdt_value(value))
            else:
                if value is None:
                    self.append(value)
                else:
                    raise SolaceSDTError(SDT_STREAM_ERROR.substitute(value=str(value), type=str(type(value))))
