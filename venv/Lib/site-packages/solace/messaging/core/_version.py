# solace-messaging-python-client
#
# Copyright 2022-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains methods for parsing the core library version and configuration information.
"""

from ctypes import Structure, pointer, byref, c_char_p
import configparser
import logging
import os
from os.path import dirname

from solace.messaging.config._sol_constants import SOLCLIENT_OK, NATIVE_ENCODING
from solace.messaging.utils._solace_utilities import get_last_error_info
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, PubSubPlusCoreClientError

logger = logging.getLogger('solace.messaging.core')

class SolClientVersionInfo(Structure):  # pylint: disable=too-few-public-methods, missing-class-docstring
    # Conforms to SolClient_version_info
    _fields_ = [
        ("version_p", c_char_p),
        ("dateTime_p", c_char_p),
        ("variant_p", c_char_p)
    ]

# config info keys
CONFIG_INFO_SOLACE_PROP_SECTION = 'solace_props'
CONFIG_INFO_APP_KEY = 'solace.messaging.client.app'
CONFIG_INFO_VENDOR_KEY = 'solace.messaging.client.vendor'

# version info keys
VERSION_KEY = 'solace.messaging.client.version'
DATETIME_KEY = 'solace.messaging.client.datetime'
VARIANT_KEY = 'solace.messaging.client.variant'

# version file info keys
PY_VERSION_KEY = 'version'
PY_DATETIME_KEY = 'timestamp'
PY_BUILDREV_KEY = 'build-rev'


def __load_ini_file_info(path):
    try:
        config = configparser.ConfigParser()
        config.read(path)
        config_parser_dict = {s: dict(config.items(s)) for s in config.sections()}
        return config_parser_dict
    except Exception as exception:  # pragma: no cover # Ignored due to unexpected err scenario
        raise PubSubPlusClientError(f'Unable to locate '
                                    f'[{path}] Exception: {exception}') from exception

def __load_version_module_info():
    try:
        from solace.messaging.core import _dynamic_version # pylint: disable=import-outside-toplevel
        return {
            PY_VERSION_KEY: _dynamic_version.SOLACE_PYTHON_CLIENT_VERSION,
            PY_DATETIME_KEY: _dynamic_version.SOLACE_PYTHON_CLIENT_COMMIT_DATE,
            PY_BUILDREV_KEY: _dynamic_version.SOLACE_PYTHON_CLIENT_BUILD_REV
        }
    except Exception as err:
        raise PubSubPlusClientError(f'Error reading version module, Cause: {err}') from err


def __load_file_info():
    base_folder = dirname(dirname(dirname(__file__))) # solace folder

    config_ini_file_name = 'config.ini'
    config_ini_full_path = os.path.join(base_folder, config_ini_file_name)

    config_info = None
    version_info = None
    try:
        config_info = __load_ini_file_info(config_ini_full_path)
    except PubSubPlusClientError:
        pass
    try:
        version_info = __load_version_module_info()
    except PubSubPlusClientError:
        pass
    return version_info, config_info



VERSION_INFO, CONFIG_INFO = __load_file_info()

def solclient_get_version(core_lib) -> SolClientVersionInfo:  # pylint: disable=missing-function-docstring
    info = SolClientVersionInfo()
    version_pointer = pointer(info)
    return_code = core_lib.solClient_version_get(byref(version_pointer))
    if return_code != SOLCLIENT_OK:
        exception: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=return_code,
                                caller_description='solClient_version_get',
                                exception_message='Unable to get version')
        logger.warning(str(exception))
        return None
    return version_pointer.contents

def solclient_get_version_info(core_lib) -> dict:  # pylint: disable=missing-function-docstring
    core_info = solclient_get_version(core_lib)
    if core_info:
        version_info = {
            VERSION_KEY : core_info.version_p.decode(NATIVE_ENCODING),
            DATETIME_KEY : core_info.dateTime_p.decode(NATIVE_ENCODING),
            VARIANT_KEY : core_info.variant_p.decode(NATIVE_ENCODING)
        }
        return version_info
    return None

def solclient_set_version(core_lib, info: SolClientVersionInfo) -> int:  # pylint: disable=missing-function-docstring
    return core_lib._solClient_version_set(byref(info)) # pylint: disable=protected-access

def solclient_set_version_from_info(core_lib, info: dict) -> int:  # pylint: disable=missing-function-docstring
    version_p = c_char_p(info.get(VERSION_KEY, '0.0.0').encode(NATIVE_ENCODING))
    date_p = c_char_p(info.get(DATETIME_KEY, 'Jan 1 1970 00:00:00').encode(NATIVE_ENCODING))
    variant_p = c_char_p(info.get(VARIANT_KEY, 'Unknown').encode(NATIVE_ENCODING))
    core_info = SolClientVersionInfo(version_p, date_p, variant_p)
    return solclient_set_version(core_lib, core_info)
