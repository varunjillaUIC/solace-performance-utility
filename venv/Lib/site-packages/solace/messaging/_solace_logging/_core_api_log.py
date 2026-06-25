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


"""
This module contains classes and functions for accessing the API logs.
"""
# pylint: disable = missing-function-docstring
import ctypes
import enum
import logging
from ctypes import c_char_p, c_int
from typing import Dict, Any

import solace
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, CCSMP_INFO_SUB_CODE, \
    CCSMP_INFO_CONTENTS, CCSMP_CALLER_DESC, CCSMP_RETURN_CODE

logger = logging.getLogger('solace.messaging.core.api')


class SolClientLogLevel(enum.Enum):  # pylint: disable=missing-class-docstring
    # enum class to define the SolClient log levels for mapping with the python layers
    SOLCLIENT_LOG_EMERGENCY = 0
    SOLCLIENT_LOG_ALERT = 1
    SOLCLIENT_LOG_CRITICAL = 2
    SOLCLIENT_LOG_ERROR = 3
    SOLCLIENT_LOG_WARNING = 4
    SOLCLIENT_LOG_NOTICE = 5
    SOLCLIENT_LOG_INFO = 6
    SOLCLIENT_LOG_DEBUG = 7


log_level = {"DEBUG": SolClientLogLevel.SOLCLIENT_LOG_DEBUG.value, "INFO": SolClientLogLevel.SOLCLIENT_LOG_INFO.value,
             "WARNING": SolClientLogLevel.SOLCLIENT_LOG_WARNING.value,
             "ERROR": SolClientLogLevel.SOLCLIENT_LOG_ERROR.value,
             "CRITICAL": SolClientLogLevel.SOLCLIENT_LOG_CRITICAL.value}


def set_core_api_log_level(level):
    # Allows the log level filter to be set. Any logs of lower severity
    #   than the filter level specified are not emitted by the API. For example, if the
    #   filter level is set to solClient_LOG_ERROR, then only logs of this severity or
    #   higher (for example, solClient_LOG_CRITICAL) are emitted. Less severe logs are filtered
    #   out. The log filter level is applied globally to ALL API Sessions.
    # Args:
    #     level: str value, holds the log level
    #
    level = log_level.get(level.upper(), SolClientLogLevel.SOLCLIENT_LOG_WARNING.value)
    solace.CORE_LIB.solClient_log_setFilterLevel(0, level)


def set_log_file(log_file):
    # Allows the log file, which defaults to stderr, to be changed to a file specified
    #   by the caller. This file is only used if a log callback has not been set through
    #   solClient_log_setCallback(). Setting the file name to NULL or a zero-length string
    #   reverts the file back to stderr. If an error is encountered when
    #   writing a log message to the specified file, the log file is automatically reverted
    #   back to stderr.
    #   Note that solClient_log_setFile() can be called before solClient_initialize().
    # Args:
    #  log_file_name_p The new file name to use, or use the default (stderr) if NULL or zero length.
    # Returns:
    #  SOLCLIENT_OK or SOLCLIENT_FAIL

    if log_file is None:
        log_file_name_p = ctypes.c_char_p(None)
    else:
        log_file_name_p = ctypes.c_char_p(log_file.encode())
    solace.CORE_LIB.solClient_log_setFile(log_file_name_p)


def last_error_info(status_code: int = None, caller_desc: str = None) -> Dict[str, Any]:
    # Fetch the last C core API error and format an exception.
    # :param status_code: core api response code
    # :param caller_desc: description about the caller of this log
    # :return: KVP of core api error details
    #
    solace.CORE_LIB.solClient_returnCodeToString.restype = c_char_p
    solace.CORE_LIB.solClient_returnCodeToString.argtypes = [c_int]
    solace.CORE_LIB.solClient_subCodeToString.restype = c_char_p
    solace.CORE_LIB.solClient_subCodeToString.argtypes = [c_int]
    solace.CORE_LIB.solClient_getLastErrorInfo.restype = ctypes.POINTER(SolClientErrorInfo)
    #   Returns a pointer to a SolClient_errorInfo structure, which contains the last captured
    #   error information for the calling thread. This information is captured on a per-thread
    #   basis. The returned structure is only valid until the thread makes the next API call,
    #   so if the calling thread wants to keep any of the structure fields, it must make a
    #   local copy of the information of interest.
    #
    #   Any API call that returns SOLCLIENT_FAIL or SOLCLIENT_NOT_READY also updates the per-thread
    #   error information.  Applications that wish extra information on the error, should retrieve the
    #   SolClient_errorInfo structure.
    #
    #   The API always sets the SolClient_errorInfo information before invoking any application callback.
    #   Therefore application may always call solClient_getLastErrorInfo() while handling event callbacks.#
    err_info = solace.CORE_LIB.solClient_getLastErrorInfo()
    return_code_str = solace.CORE_LIB.solClient_returnCodeToString(
        status_code).decode() if status_code is not None else ''
    sub_code_str = solace.CORE_LIB.solClient_subCodeToString(err_info.contents.subCode)
    core_api_error = {CCSMP_CALLER_DESC: caller_desc, CCSMP_RETURN_CODE: return_code_str,
                      CCSMP_SUB_CODE: sub_code_str.decode(),
                      CCSMP_INFO_SUB_CODE: err_info.contents.subCode,
                      CCSMP_INFO_CONTENTS: ' '.join(err_info.contents.errorInfo.decode().split())}
    return core_api_error


class SolClientErrorInfo(ctypes.Structure):  # pylint: disable=too-few-public-methods, missing-class-docstring
    # Conforms to solClient_errorInfo_t
    # The structure used to record more detailed error information for a failed API call.
    _fields_ = [
        ("subCode", c_int),  # A subcode indicating the type of error
        ("response_code", c_int),  # A response code that is returned for some subcodes; otherwise zero
        ("errorInfo", ctypes.c_char * 256)  # An information string
        # for certain types of subcodes (empty string, if not used)
    ]
