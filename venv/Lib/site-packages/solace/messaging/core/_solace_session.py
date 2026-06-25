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


# Module contains classes to interact with underlying c api

# pylint: disable=missing-module-docstring,too-many-statements,no-else-raise,inconsistent-return-statements
# pylint:disable=too-many-public-methods,too-many-branches,broad-except,missing-function-docstring
# pylint: disable=missing-class-docstring,too-many-instance-attributes,too-many-lines

import copy
import ctypes
import datetime
import logging
import os
import platform
import threading
import weakref
from ctypes import Structure, pointer, byref, sizeof, POINTER, util
from ctypes import cdll, py_object, c_void_p, c_char_p, c_int
from os.path import dirname
from struct import calcsize
from typing import Callable, Union

import solace
from solace.messaging import _SolaceServiceAdapter
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._ccsmp_property_mapping import CCSMP_SESSION_PROP_MAPPING, \
    LEGACY_TO_CURRENT_CCSMP_SESSION_PROP_MAPPING
from solace.messaging.config._default_session_props import default_props
from solace.messaging.config._sol_constants import SOLCLIENT_CALLBACK_OK, SOLCLIENT_LOG_DEFAULT_FILTER, \
    SOLCLIENT_OK, SOLCLIENT_SESSION_EVENT_RECONNECTING_NOTICE, SOLCLIENT_FAIL, \
    SOLCLIENT_SESSION_EVENT_RECONNECTED_NOTICE, SOLCLIENT_SESSION_EVENT_CAN_SEND, SOLCLIENT_SESSION_EVENT_DOWN_ERROR, \
    SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR, SOLCLIENT_SESSION_EVENT_UP_NOTICE, \
    SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT, SOLCLIENT_SESSION_EVENT_REJECTED_MSG_ERROR, \
    SOLCLIENT_SESSION_PROP_MAX_SIZE, SOLCLIENT_SUB_CODE_OK
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, UNABLE_TO_LOAD_SOLCLIENT_LIBRARY, \
    CCSMP_SUB_CODE_OK, SESSION_FORCE_DISCONNECT, \
    ESTABLISH_SESSION_ON_HOST, CCSMP_SUB_CODE_FAILED_TO_LOAD_TRUST_STORE, \
    FAILED_TO_LOAD_TRUST_STORE, CCSMP_SUB_CODE_UNRESOLVED_HOST, UNRESOLVED_SESSION, \
    FAILED_TO_LOADING_CERTIFICATE_AND_KEY, CCSMP_SUB_CODE_FAILED_LOADING_CERTIFICATE_AND_KEY, \
    CCSMP_INFO_SUB_CODE, \
    UNABLE_TO_FORCE_DISCONNECT, UNABLE_TO_DESTROY_SESSION, FAILURE_CODE, CCSMP_INFO_CONTENTS, \
    CCSMP_CALLER_DESC, CCSMP_RETURN_CODE
from solace.messaging.config.solace_properties import transport_layer_security_properties, transport_layer_properties
from solace.messaging.config.sub_code import SolClientSubCode
from solace.messaging.core._core_api_utility import context_destroy, session_disconnect, session_force_failure, \
    session_destroy, session_connect, session_create, prepare_array
from solace.messaging.core._publish import _SolacePublisherEvent, _SolacePublisherEventEmitter, \
    _SolacePublisherAcknowledgementEmitter, _SolaceCorrelationManager
from solace.messaging.core._receive import _SolaceReceiverEvent, _SolaceReceiverEventEmitter
from solace.messaging.core._solace_transport import _SolaceTransportState, _SolaceTransportEvent, _SolaceTransport, \
    _SolaceTransportEventEmitter, _SolaceTransportEventInfo
import solace.messaging.core._version as core_version
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError, ServiceUnreachableError, \
    MessageRejectedByBrokerError, \
    MessageDestinationDoesNotExistError, PubSubPlusCoreClientError
from solace.messaging.publisher._impl._publisher_utilities import _PublisherUtilities
from solace.messaging.utils._solace_utilities import get_last_error_info

logger = logging.getLogger('solace.messaging.core')


class _SolaceApiLibrary:
    # Singleton class to load dll
    _core_lib = None  # it is a protected member, and is used for holding the C Library
    _instance = None  # it is a protected member, and it holds the instance of the _SolaceApiLibrary super class
    _global_config = None

    def __new__(cls, *args, **kwargs):
        """
        return: instance of Solace Library
        """
        if cls._instance is None:
            cls._instance = super(_SolaceApiLibrary, cls).__new__(cls, *args, **kwargs)
            cls._core_lib = cls.__load_core_library()
            cls.__init_api()
        return cls._instance

    @staticmethod
    def _get_shared_lib_default_path() -> str:
        # used to find shared_lib_config_default path based on platform
        # returns the default native library path or None if no matching
        # platform is found
        platform_os = platform.system()
        # can be "x86-64" or "aarch64" on linux.
        platform_machine = platform.machine()

        # glibc based linux distros return "glibc", musl returns "".
        # Add better logic here when a third libc shows up on linux.
        if hasattr(platform, "libc_ver"):
            platform_libc = platform.libc_ver()[0]
        else:
            platform_libc = ""

        if platform_os == "Linux" and platform_libc != "glibc":
            libc_suffix = "-musl"
        else:
            libc_suffix = ""

        void_pointer_struct_char = 'P'
        is32bit = (calcsize(void_pointer_struct_char) * 8) == 32
        # get relative path of package installed library
        path_default_base = os.path.join(dirname(dirname(__file__)), "lib")
        lib_arch_32bit = {"Windows": "32"}
        lib_arch_64bit = {"Linux": "-"+platform_machine+libc_suffix, "Darwin": "-universal2", "Windows": "-amd64"}
        lib_platform_name = {"Linux": "linux", "Darwin": "macosx", "Windows": "win"}
        lib_arch = lib_arch_32bit if is32bit else lib_arch_64bit
        arch = lib_arch.get(platform_os, None)
        platform_name = lib_platform_name.get(platform_os, None)
        if arch is not None and platform_name is not None:
            return os.path.join(path_default_base, "%s%s" % (platform_name, arch))  # pylint: disable=consider-using-f-string

        return None  # pragma: no cover # Due to core error scenario

    @staticmethod
    def __load_core_library():
        # method to load dll based on OS
        #     Raises:
        #         PubSubPlusClientError: if library is missing
        # shared_lib_config_optional holds the key:value pairs for the the names
        # of shared libraries that can be used for accessing shared libraries in
        # user-customized locations. shared_lib_config_optional is different
        # from shared_lib_config_default because of different methods are used
        # to find the shared library in each case. util.find_library is required
        # to find custom installations of a shared library since it uses the
        # PATH on Windows or the LD_LIBRARY_PATH on Linux to find the custom
        # installation, and in Linux the shared library name passed to the
        # find_library() function must not have the 'lib' prefix or '.so'
        # suffix. In contrast, the default installation of the shared library
        # is within this package so it is always in the same place. Therefore,
        # the relative path from this file to the location of the default
        # installation of the shared library can be used to find it and load
        # it.

        shared_lib_config_optional = {"Linux": 'solclient', "Windows": 'libsolclient.dll',
                                      "Darwin": 'libsolclient.dylib'}

        # get the shared library name for this platform
        shared_lib_name_optional = shared_lib_config_optional.get(platform.system(), None)
        if shared_lib_name_optional:
            # search the PATH variable on Windows and the LD_LIBRARY_PATH on
            # Linux for a custom installation of a Solace CCSMP shared library
            shared_lib_path_optional = util.find_library(shared_lib_name_optional)
            if shared_lib_path_optional is not None:
                # if the custom shared library was found, load and return it
                try:
                    return cdll.LoadLibrary(shared_lib_path_optional)  # pragma: no cover
                except Exception as exception:  # pragma: no cover # Due to core error scenario
                    logger.info('%s from custom location [%s]. Exception: %s', UNABLE_TO_LOAD_SOLCLIENT_LIBRARY,
                                shared_lib_path_optional, str(exception))
                # if a custom installation of a CCSMP shared library was not
                # found, assume that the default shared library included in the
                # distribution should be loaded
            shared_lib_config_default = {"Linux": 'libsolclient.so', "Windows": 'libsolclient.dll',
                                         "Darwin": 'libsolclient.dylib'}
            # get the shared library name for this platform
            shared_lib_name_default = shared_lib_config_default.get(platform.system(), None)
            if shared_lib_name_default:  # pragma: no cover
                # join the relative path from this file to the shared
                # library file
                # prepend the current directory path to the relative path
                # from the this file to the shared library file
                shared_lib_path_default = _SolaceApiLibrary._get_shared_lib_default_path()
                if shared_lib_path_default is not None:
                    shared_lib_path_default = os.path.join(shared_lib_path_default, shared_lib_name_default)
                    if shared_lib_path_default is not None:
                        try:
                            # if the default installation was found, load and return it
                            return cdll.LoadLibrary(shared_lib_path_default)
                        except Exception as exception:  # pragma: no cover # Due to core error scenario
                            logger.error('%s from [%s]. Exception: %s', UNABLE_TO_LOAD_SOLCLIENT_LIBRARY,
                                         shared_lib_path_default, str(exception))
                            raise PubSubPlusClientError(message=f'{UNABLE_TO_LOAD_SOLCLIENT_LIBRARY} '
                                                                f'from [{shared_lib_path_default}]. '
                                                                f'Exception: {exception}') from exception
        # if neither the custom nor default location of the shared library
        # contain the required shared library, throw the relevant error and
        logger.error(UNABLE_TO_LOAD_SOLCLIENT_LIBRARY)  # pragma: no cover # Due to core error scenario
        raise PubSubPlusClientError(
            message=UNABLE_TO_LOAD_SOLCLIENT_LIBRARY)  # pragma: no cover # Due to core error scenario

    @classmethod
    def __init_api(cls):
        # ssl & crypt config begins
        # log setup begins
        cls._core_lib.solClient_log_setFile(ctypes.c_char_p(None))
        _global_arr = _SolaceApiLibrary.__prepare_global_props()
        if _global_arr is not None:
            cls._global_config = ctypes.cast(_global_arr, POINTER(c_char_p))
        return_code = cls._core_lib.solClient_initialize(SOLCLIENT_LOG_DEFAULT_FILTER, cls._global_config)
        if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenario
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='SolaceApi->init_api',
                                    exception_message='Unable to Initialize values')
            logger.exception("%s", str(exception))
            raise exception
        cls.__set_version(cls._core_lib)
        cls._core_lib.solClient_log_setFilterLevel(0, 1)

    @property
    def solclient_core_library(self):
        # property to return the dll
        # return: Returns loaded dll
        return self._core_lib

    @property
    def client_version(self):
        return self.__get_version()

    def __get_version(self) -> dict:
        return core_version.solclient_get_version_info(self._core_lib)

    @property
    def client_config(self):
        return self.__get_config()

    def __get_config(self) -> dict:  # pylint: disable=no-self-use
        return core_version.CONFIG_INFO

    @staticmethod
    def __set_version(core_lib):  # pylint: disable=too-many-locals, invalid-name
        # Get and Set version using Core lib """
        cv = core_version  # pylint: disable=invalid-name
        core_info = cv.solclient_get_version_info(core_lib)
        # alias core_version for covenience
        if core_info:
            core_api_name = 'C API'
            sol_props = cv.CONFIG_INFO.get(cv.CONFIG_INFO_SOLACE_PROP_SECTION, None)
            app_name = sol_props.get(cv.CONFIG_INFO_APP_KEY, None) if sol_props else None

            core_api_version = core_info[cv.VERSION_KEY]
            core_api_date = core_info[cv.DATETIME_KEY]
            core_api_variant = core_info[cv.VARIANT_KEY]

            py_version = cv.VERSION_INFO.get(cv.PY_VERSION_KEY, '0.0.0')
            py_api_date = cv.VERSION_INFO.get(cv.PY_DATETIME_KEY, datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))

            new_version = f'{app_name} {py_version} / {core_api_name} {core_api_version}'
            new_date = f'{app_name} {py_api_date} / {core_api_name} {core_api_date}'
            new_variant = f'{app_name} / {core_api_variant}'

            updated_info = {
                cv.VERSION_KEY: new_version,
                cv.DATETIME_KEY: new_date,
                cv.VARIANT_KEY: new_variant
            }
            return_code = cv.solclient_set_version_from_info(core_lib, updated_info) # pylint: disable=protected-access
            if return_code != SOLCLIENT_OK:
                exception: PubSubPlusCoreClientError = \
                    get_last_error_info(return_code=return_code,
                                        caller_description='SolaceApiLibrary->set_version',
                                        exception_message='Unable to set version')
                logger.warning(str(exception))
        else: # pragma: no cover # Due to core error scenario
            logger.warning('Unable to set version')


    @staticmethod
    def __prepare_global_props() -> ctypes.Array:
        default_lib_keys = ['GLOBAL_GSS_KRB_LIB', 'GLOBAL_CRYPTO_LIB', 'GLOBAL_SSL_LIB',
                            'SOLCLIENT_GLOBAL_PROP_GSS_KRB_LIB', 'SOLCLIENT_GLOBAL_PROP_CRYPTO_LIB',
                            'SOLCLIENT_GLOBAL_PROP_SSL_LIB']
        lib_key_mapping = {
            'SOLCLIENT_GLOBAL_PROP_GSS_KRB_LIB': 'GLOBAL_GSS_KRB_LIB',
            'SOLCLIENT_GLOBAL_PROP_CRYPTO_LIB': 'GLOBAL_CRYPTO_LIB',
            'SOLCLIENT_GLOBAL_PROP_SSL_LIB': 'GLOBAL_SSL_LIB'
        }
        env_dict = {}
        for key in default_lib_keys:
            if not os.environ.get(key) in ('', None):
                mapped_key = key if not key in lib_key_mapping else lib_key_mapping[key]
                env_dict[mapped_key] = os.environ.get(key)
        if not env_dict:
            logger.debug("No KRB, CRYPTO or SSL libraries were passed as environment variables.")
            return None
        logger.info("KRB, CRYPTO or SSL libraries were passed as environment variables.")
        return prepare_array(env_dict)

CORE_API = _SolaceApiLibrary()

def context_cleanup(context_pointer):
    # Function for cleaning up the context
    try:
        if context_pointer and context_pointer.value is not None:
            context_destroy(context_pointer)
    except PubSubPlusClientError as exception:  # pragma: no cover # Due to core error scenario
        logger.error(exception)


class _SolaceApiContext:
    # Class to create context

    def __init__(self):
        # return: instance of Solace context
        self.__context_p = c_void_p(None)  # it is a protected member, which holds the context pointer of
        # type (ctypes)
        return_code = self._create_context()
        self._finalizer = weakref.finalize(self, context_cleanup, self.__context_p)
        self._id_info = f"SolaceApiContext Id: {str(hex(id(self)))}"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenario
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='SolaceApiContext->init',
                                    exception_message='Failed to create solace context')
            self.adapter.warning(str(exception))
            raise exception

    def _create_context(self):
        # Method to create context

        class SolClientContextCreateRegisterFdFuncInfo \
                    (Structure):  # pylint: disable=too-few-public-methods,trailing-whitespace
            # Conforms to solClient_context_createRegisterFdFuncInfo_t
            #  .. _class solClient_context_createRegisterFdFuncInfo:
            #
            #  Function is set on a per-Context basis. Providing these functions is optional. If provided, both
            #  function information for file descriptor registration and file descriptor un-registration functions.
            #  Tht be non-NULL, and if not provided, both must be NULL.
            #
            # These functions are used when the application wants to own event generation, and they supply file
            # descriptor events to the API. Such applications typically want to poll several different devices,
            # of which the API is only one. When these functions are provided, the API does not manage its own
            # devices. Instead, when a device is created, the provided 'register' function is called to register the
            # device file descriptor for read and/or write events. It is the responsibility of the application to
            # call back into API when the appropriate event occurs on the device file descriptor. The API callback is
            # provided to the register function (see SolClient_context_registerFdFunc_t). If this interface is
            # chosen, the application <b>must</b> also call solClient_context_timerTick() at regular intervals.
            #
            #  Normally these are not used, and the API owns event registrations. If an internal Context thread is used
            #  by enabling SOLCLIENT_CONTEXT_PROP_CREATE_THREAD
            #  (see also SOLCLIENT_CONTEXT_PROPS_DEFAULT_WITH_CREATE_THREAD),
            #  the API takes care of all devices and timers and no action is required by the application.
            #  If the internal thread is
            #  not enabled, the application must call solClient_context_processEvents() to provide scheduling time to
            #   the API.
            #
            # When the API owns event registrations, it also provides file descriptor register/unregister service to
            # the application. solClient_context_registerForFdEvents() and solClient_context_unregisterForFdEvents()
            # can be used by applications to pass file descriptors to the API for managing, keeping event generation
            # localized to the internal thread or the thread that calls solClient_context_processEvents(). """
            _fields_ = [
                ("reg_fd_func_p", c_void_p),
                ("unreg_fd_func_p", c_void_p),
                ("user_p", c_void_p)
            ]

        class SolClientContextCreateFuncInfo(Structure):  # pylint: disable=too-few-public-methods
            # Conforms to solClient_context_createFuncInfo_t
            _fields_ = [
                ("reg_fd_info", SolClientContextCreateRegisterFdFuncInfo)
            ]

        # create native context
        context_props = pointer(c_char_p.in_dll(self.solclient_core_library,
                                                "_solClient_contextPropsDefaultWithCreateThread"))
        context_func_info = SolClientContextCreateFuncInfo()
        context_func_info.reg_fd_info = \
            SolClientContextCreateRegisterFdFuncInfo(None, None, None)  # pylint: disable=attribute-defined-outside-init
        return_code = self.solclient_core_library.solClient_context_create(context_props, byref(self.__context_p),
                                                                           byref(context_func_info),
                                                                           sizeof(context_func_info))
        return return_code

    @property
    def context_p(self):
        #     Get underlying c api pointer
        #     return:Returns contexts pointer
        return self.__context_p

    @property
    def solclient_core_library(self):
        # property to return the dll
        # return: Returns loaded dll
        return CORE_API.solclient_core_library


class SolClientServiceEventCallbackInfo(Structure):  # pylint: disable=too-few-public-methods
    # Conforms to solClient_session_eventCallbackInfo_t
    # this is a C structure incorporated using c-types module for providing the session event callback info
    _fields_ = [
        ("session_event", ctypes.c_int32),
        ("response_code", ctypes.c_uint32),
        ("info_p", c_char_p),
        ("correlation_p", c_void_p)
    ]

def _session_cleanup(adapter, session_pointer):
    try:
        if session_pointer:
            session_destroy(session_pointer)
    except PubSubPlusClientError as exception:  # pragma: no cover # Due to core error scenario
        adapter.error(exception)

def _service_event_cleanup(can_send_event):
    # set to open for finalizer to unblock threads
    can_send_event.set()

#  SOLCLIENT_SESSION_EVENT_CALLBACK_INFO_PT ia an public member which is used for holding
#  the pointer object of SolClientServiceEventCallbackInfo
SOLCLIENT_SESSION_EVENT_CALLBACK_INFO_PT = POINTER(SolClientServiceEventCallbackInfo)
# protected member, holds c-type event callback function type
_EVENT_CALLBACK_FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, c_void_p,
                                             SOLCLIENT_SESSION_EVENT_CALLBACK_INFO_PT,
                                             py_object)
# it is a protected member, holds the message callback function type of c-types
_MSG_CALLBACK_FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, c_void_p, c_void_p, py_object)

class SolClientServiceCreateRxCallbackFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    # Conforms to solClient_session_createRxMsgCallbackFuncInfo_t
    # Applications should use solClient_session_createRxMsgCallbackFuncInfo.
    # Callback information for Session message receive callback. This is set on a per-Session basis.
    _fields_ = [
        ("callback_p", c_void_p),
        ("user_p", c_void_p)
    ]

class SolClientServiceCreateEventCallbackFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    # Conforms to solClient_session_createEventCallbackFuncInfo_t.
    # Callback information for Session event callback. This is set on a per-Session basis.
    _fields_ = [
        ("callback_p", _EVENT_CALLBACK_FUNC_TYPE),
        ("user_p", py_object)
    ]

class SolClientServiceCreateRxMsgCallbackFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    # Conforms to solClient_session_createRxMsgCallbackFuncInfo_t
    # Applications should use solClient_session_createRxMsgCallbackFuncInfo.
    # Callback information for Session message receive callback. This is set on a per-Session basis
    _fields_ = [
        ("callback_p", _MSG_CALLBACK_FUNC_TYPE),
        ("user_p", py_object)
    ]

class SolClientServiceCreateFuncInfo(Structure):  # pylint: disable=too-few-public-methods

    # Conforms to solClient_session_createFuncInfo_t and
    #   Function information for Session creation. This is set on a per-Session basis.
    #   The application must set the eventInfo callback information. All Sessions must have an
    # event callback registered.
    #   The application must set one, and only one, message callback information.
    # The <i>rxInfo</i> message callback interface is
    #  <b>deprecated</b> and should be set to NULL. All applications should prefer to use
    # the <i>rxMsgInfo</i> callback interface.
    #  The application has available to it a SolClient_opaqueMsg_pt, which can be kept for
    # later processing and provides a
    #  structured interface for accessing elements of the received message. The application
    # callback routine then has the signature
    #  (see SolClient_session_rxMsgCallbackFunc_t) :

    _fields_ = [
        ("rx_info", SolClientServiceCreateRxCallbackFuncInfo),  # deprecated
        ("event_info", SolClientServiceCreateEventCallbackFuncInfo),
        ("rx_msg_info", SolClientServiceCreateRxMsgCallbackFuncInfo)
    ]

class _SolaceSession(_SolacePublisherEventEmitter, _SolacePublisherAcknowledgementEmitter,
                     _SolaceCorrelationManager, _SolaceReceiverEventEmitter,
                     _SolaceTransport, _SolaceTransportEventEmitter):
    # class to interact with underlying C core functionality
    _event_callback = None  # this is an protected member, and is used for event callback
    _msg_callback = None  # this is an protected member, and is used for message callback
    # _log_callback = None
    _msg_callback_func_type = _MSG_CALLBACK_FUNC_TYPE
    _event_callback_func_type = _EVENT_CALLBACK_FUNC_TYPE

    def __init__(self, id_info: str):
        # This method is used to initialize _SolaceApiContext() for creating context
        self._id_info = id_info
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        self._core_lib = solace.CORE_LIB
        self._core_lib.solClient_returnCodeToString.restype = c_char_p
        self._core_lib.solClient_returnCodeToString.argtypes = [c_int]
        self._core_lib.solClient_msg_isRedelivered.restype = ctypes.c_int8
        self._core_lib.solClient_msg_isDiscardIndication.restype = ctypes.c_int8
        self._session_func_info = None
        self._context = _SolaceApiContext()
        self._context_p = self._context.context_p
        self._host = None  # it holds the host value
        self._can_send_received = threading.Event()  # this sets the threading event based on the can send received
        self._transport_state = None
        # this is a private member & is used for holding session pointer which is of c-types
        self.__session_p = c_void_p(None)
        self._event_finalizer = weakref.finalize(self, _service_event_cleanup, self._can_send_received)
        self._finalizer = weakref.finalize(self, _session_cleanup, self.adapter, self.__session_p)
        self._pub_handler_id_gen = 0
        self._pub_event_handlers = {}
        self._pub_ack_handlers = {}
        for pub_event in _SolacePublisherEvent:
            self._pub_event_handlers[pub_event] = {}
        # used to unblock direct/persistent receiver queue during blocking receive_message call
        self._correlation_mutex = threading.Lock()
        self._correlation_data = set()
        self._rec_handler_id_gen = 0
        self._rec_event_handlers = {}
        for rec_event in _SolaceReceiverEvent:
            self._rec_event_handlers[rec_event] = {}

        self._transport_event_handler_id_gen = 0
        self._transport_event_handlers = {}
        for transport_event in _SolaceTransportEvent:
            self._transport_event_handlers[transport_event] = {}

        self._mutex = threading.Lock()

    @property
    def event_emitter(self) -> '_SolaceTransportEventEmitter':
        return self

    def connect(self) -> (int, Union[Exception, None]):
        return self.__do_connect()

    def register_transport_event_handler(self, event: '_SolaceTransport', handler: Callable[[dict], None]) -> int:
        with self._mutex:
            handler_id = self._transport_event_handler_id_gen
            self._transport_event_handler_id_gen += 1
            event = self._transport_event_handlers[event]
            event[handler_id] = handler
        return handler_id

    def _emit_transport_event(self, event: '_SolaceTransportEvent', event_info: '_SolaceTransportEventInfo'):
        event_handlers = self._transport_event_handlers[event]
        if event == _SolaceTransportEvent.TRANSPORT_DOWN:
            with self._mutex:
                event_handlers = list(event_handlers.values())
        else:
            event_handlers = event_handlers.values()
        for handler in event_handlers:
            handler(event_info)

    def unregister_transport_event_handler(self, handler_id: int):
        with self._mutex:
            for event_handlers in self._transport_event_handlers.values():
                if event_handlers.get(handler_id) is not None:
                    event_handlers.pop(handler_id)
                    break

    def register_receiver_event_handler(self, event: '_SolaceReceiverEvent', handler) -> int:
        handler_id = self._rec_handler_id_gen
        self._rec_handler_id_gen += 1
        event_dict = self._rec_event_handlers[event]
        event_dict[handler_id] = handler
        return handler_id

    def emit_receiver_event(self, event: '_SolaceReceiverEvent', event_info: dict):
        handlers = []
        with self._mutex:
            for value in self._rec_event_handlers[event].values():
                handlers.append(copy.deepcopy(value))

        for handler in handlers:
            handler(event_info)

    def unregister_receiver_event_handler(self, handler_id: int):
        with self._mutex:
            for event_handlers in self._rec_event_handlers.values():
                if event_handlers.get(handler_id) is not None:
                    event_handlers.pop(handler_id)
                    break

    def update_id_info(self, id_info: str):
        # Updates the id_info of the SolaceApi object
        # Is only intended to be used if the application ID is updated
        # Refer to application ID assignment in _BasicMessagingService.__init__() for an example.
        self._id_info = id_info

        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})

    def get_session_property(self, property_name: str):
        #Gets the value of the specified Session property for the Session.
        #
        #The property value is copied out to buffer provided by the caller. The returned value is a
        #NULL-terminated string.
        #
        #Parameters:
        #opaqueSession_p  An opaque Session returned when the Session was created.
        #propertyName_p   The name of the Session property for which the value is to be returned.
        #buf_p            A pointer to the buffer provided by the caller in which to place the NULL-terminated
        #                     property value string.
        #bufSize          The size (in bytes) of the buffer provided by the caller.
        #
        #Returns:
        #SOLCLIENT_OK, SOLCLIENT_FAIL
        #SubCodes (Unless otherwise noted above, subcodes are only relevant when this function returns SOLCLIENT_FAIL):
        property_name_p = ctypes.c_char_p(property_name.encode("utf-8"))
        prop_val_p = ctypes.create_string_buffer(SOLCLIENT_SESSION_PROP_MAX_SIZE)
        ret = solace.CORE_LIB.solClient_session_getProperty(self.__session_p,
                                                            property_name_p,
                                                            ctypes.byref(prop_val_p),
                                                            SOLCLIENT_SESSION_PROP_MAX_SIZE)
        if ret == SOLCLIENT_OK:
            return prop_val_p.value.decode("utf-8")
        error: PubSubPlusCoreClientError = \
            get_last_error_info(return_code=SOLCLIENT_FAIL,
                                caller_description='_SolaceApi->get_session_property',
                                exception_message=f'Unable to retrieve property {property_name}')
        logger.error(str(error))
        raise error

    def modify_session_properties(self, prop_dict: dict):
        # Allows certain properties of a Session to be modified after the Session has been created.

        # Currently, only the following Session properties can be modified; attempting to specify other Session
        # properties will result in SOLCLIENT_FAIL being returned:

        # SOLCLIENT_SESSION_PROP_APPLICATION_DESCRIPTION (Deprecated -- see Note below)
        # SOLCLIENT_SESSION_PROP_CLIENT_NAME (Deprecated -- see Note below)
        # SOLCLIENT_SESSION_PROP_HOST (may only be modified when Session is disconnected)
        # SOLCLIENT_SESSION_PROP_PORT (may only be modified when Session is disconnected)
        # Note: Applications shall use solClient_session_modifyClientInfo() to modify the following Session properties:

        # SOLCLIENT_SESSION_PROP_APPLICATION_DESCRIPTION
        # SOLCLIENT_SESSION_PROP_CLIENT_NAME
        # Note that the property values are stored internally in the API, and the caller does not have to maintain the
        # props array or the strings that are pointed to after this call completes. The API also will not modify any
        # of the strings pointed to by props when processing the property list.
        # Parameters:
        # opaqueSession_p 	The opaque Session that was returned when Session was created.
        # props 	An array of name/value string pair pointers to modify Session properties.
        # Returns:
        # SOLCLIENT_OK, SOLCLIENT_FAIL, SOLCLIENT_WOULD_BLOCK
        # SubCodes (Unless otherwise noted above, subcodes are only relevant when this function returns
        # SOLCLIENT_FAIL):
        # SOLCLIENT_SUBCODE_CANNOT_MODIFY_WHILE_NOT_IDLE
        # See also:
        # solClient_subCode for a description of all subcodes.

        tmp_dict = {}
        for key, value in prop_dict.items():
            if key in CCSMP_SESSION_PROP_MAPPING:
                if key in LEGACY_TO_CURRENT_CCSMP_SESSION_PROP_MAPPING:
                    if LEGACY_TO_CURRENT_CCSMP_SESSION_PROP_MAPPING[key] in prop_dict:
                        continue
                tmp_dict[CCSMP_SESSION_PROP_MAPPING[key]] = str(int(value)) if isinstance(value, bool) else str(value)

        formatted_props = prepare_array(tmp_dict)
        ret = solace.CORE_LIB.solClient_session_modifyProperties(self.__session_p,
                                                                 formatted_props)
        if ret != SOLCLIENT_OK:
            error: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=ret,
                                    caller_description='_SolaceSession->modify_session_properties',
                                    exception_message=f'Unable to modify properties {prop_dict}')
            logger.error(str(error))
            raise error

    def emit_publisher_event(self, event: '_SolacePublisherEvent', error_info: dict = None):
        handlers = []
        with self._mutex:
            for value in self._pub_event_handlers[event].values():
                handlers.append(copy.deepcopy(value))

        for handler in handlers:
            handler(error_info)

    def register_publisher_event_handler(self, event: '_SolacePublisherEvent', handler) -> int:
        handler_id = self._pub_handler_id_gen
        self._pub_handler_id_gen += 1
        event_dict = self._pub_event_handlers[event]
        event_dict[handler_id] = handler
        return handler_id

    def unregister_publisher_event_handler(self, handler_id: int):
        with self._mutex:
            for event_handlers in self._pub_event_handlers.values():
                if event_handlers.get(handler_id) is not None:
                    event_handlers.pop(handler_id)
                    break

    def register_acknowledgement_handler(self, handler, publisher_correlation_id: bytes):
        self._pub_ack_handlers[publisher_correlation_id] = handler

    def unregister_acknowledgement_handler(self, publisher_correlation_id: bytes):
        if self._pub_ack_handlers.get(publisher_correlation_id) is not None:
            self._pub_ack_handlers.pop(publisher_correlation_id)

    def _add_correlation(self, correlation):
        self._correlation_data.add(correlation)

    def _remove_correlation(self, correlation):
        self._correlation_data.remove(correlation)

    def _has_correlation(self, correlation) -> bool:
        return correlation in self._correlation_data

    def register_correlation_tag(self, msg_correlation: bytes) -> bool:
        with self._correlation_mutex:
            if self._has_correlation(msg_correlation):
                return False
            self._add_correlation(msg_correlation)
        return True

    def unregister_correlation_tag(self, msg_correlation: bytes) -> bool:
        with self._correlation_mutex:
            if self._has_correlation(msg_correlation):
                self._remove_correlation(msg_correlation)
                return True
        return False

    def has_correlation_tag(self, msg_correlation: bytes) -> bool:
        with self._correlation_mutex:
            return self._has_correlation(msg_correlation)

    class __ParsedApiLibInfo:  # pylint: disable=invalid-name
        """
        This class formats the API library information into a field accessible format
        to make accessing those fields easier to implement and easier to read in other modules.
        """
        def __init__(self):
            client_version = CORE_API.client_version
            self.__api_version = client_version[core_version.VERSION_KEY]
            self.__api_build_timestamp = client_version[core_version.DATETIME_KEY]
            self.__api_vendor = CORE_API.client_config[core_version.CONFIG_INFO_SOLACE_PROP_SECTION] \
                                                          [core_version.CONFIG_INFO_VENDOR_KEY]

        @property
        def api_version(self):
            return self.__api_version

        @property
        def api_build_timestamp(self):
            return self.__api_build_timestamp

        @property
        def api_vendor(self):
            return self.__api_vendor


    @property
    def parsed_api_info(self):
        return self.__ParsedApiLibInfo()

    @property
    def can_send_received(self):
        return self._can_send_received

    def session_disconnect(self) -> (int, Union[dict, None]):
        #  Disconnects the specified Session by the help of the C API solClient_session_disconnect,
        #  if the session is disconnected then the return code will be SOLCLIENT_OK else this method
        #  will raise exception.
        # Returns:
        #     int :  returns  0 or -1
        #  Raises:
        #         PubSubPlusClientError: if we didn't receive 0 as return code
        self._core_lib.solClient_session_disconnect.argtypes = [c_void_p]

        error_info = None
        return_code = session_disconnect(self.__session_p)
        if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenario
            error_info = get_last_error_info(return_code=return_code,
                                             caller_description='SolaceApi->session_disconnect',
                                             exception_message='Unable to disconnect session')
            self.adapter.warning("%s", str(error_info))

        # NOTE: Once after successful session disconnect, we're clearing __session_p object since we don't have
        # business of reconnecting the session again, but if we introduce re-connection mechanism inside
        # (actually RetryStrategy are wrapped inside C api) wrapper api then we can't assign None to __session_p
        return return_code, error_info

    def session_force_disconnect(self) -> int:
        # function to disconnect with event broker. HIGH RISK: We should use this only for testing.
        # In ideal scenario, we won't FORCE DISCONNECT SESSION
        # Returns:
        #     int :  returns  0 or -1
        #  Raises:
        #         PubSubPlusClientError: if we didn't receive 1 as return code
        self._core_lib.solClient_session_disconnect.argtypes = [c_void_p]
        return_code = session_force_failure(self.__session_p)
        if return_code != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenario
            failure_message = f'{UNABLE_TO_FORCE_DISCONNECT}{return_code}'
            exception: PubSubPlusCoreClientError = \
                get_last_error_info(return_code=return_code,
                                    caller_description='SolaceApi->session_force_disconnect',
                                    exception_message=failure_message)
            self.adapter.warning(str(exception))
            raise exception
        self.adapter.warning(SESSION_FORCE_DISCONNECT)
        return return_code

    def disconnect(self) -> (int, Union[dict, None]):
        # This method assumes that the service mutex has been acquired by the calling method.
        return_code, error_info = self.session_disconnect()
        if error_info:
            return return_code, error_info

        self._transport_state = _SolaceTransportState.DOWN
        event_message = {CCSMP_CALLER_DESC: 'SolaceApi->disconnect',
                         CCSMP_RETURN_CODE: SOLCLIENT_OK,
                         CCSMP_SUB_CODE: CCSMP_SUB_CODE_OK,
                         CCSMP_INFO_SUB_CODE: SOLCLIENT_SUB_CODE_OK,
                         CCSMP_INFO_CONTENTS: "The application disconnected the messaging service."}

        # emit publisher DOWN event for any lingering publishers
        self.emit_publisher_event(_SolacePublisherEvent.PUBLISHER_DOWN, event_message)
        # emit receiver DOWN event for any lingering receivers
        self.emit_receiver_event(_SolaceReceiverEvent.RECEIVER_DOWN, event_message)
        # run finalizer to release event object to allow for thread exit
        # eg. self._can_send_received.set()
        self._event_finalizer()
        # emit transport DOWN event.
        self._emit_transport_event(
            _SolaceTransportEvent.TRANSPORT_DOWN,
            _SolaceTransportEventInfo(self. adapter, self._host, event_message[CCSMP_INFO_CONTENTS], event_message))
        return return_code, error_info

    def session_cleanup(self):
        # This method assumes that the service mutex has been acquired by the calling method.
        self.session_destroy()
        self._transport_state = _SolaceTransportState.DOWN
        context_cleanup(self._context_p)
        # release correlation memory
        self._correlation_data.clear()

    def session_destroy(self) -> int:  # pragma: no cover
        # Destroys the specified session. On return, the opaque Context pointer
        # is set to NULL. This operation must not be performed in a Context callback
        # for the Context being destroyed. This includes all Sessions on the Context,
        # timers on the Context, and application-supplied register file descriptor
        # functions.
        # Returns:
        #      int :  returns  0 or -1
        # Raises:
        #      PubSubPlusClientError: if we didn't receive 0 as return code
        if self.__session_p:
            self._core_lib.solClient_session_destroy.argtypes = [c_void_p]
            return_code_on_destroy = session_destroy(self.__session_p)
            if return_code_on_destroy != SOLCLIENT_OK:  # pragma: no cover # Due to core error scenario
                error_message = f"{UNABLE_TO_DESTROY_SESSION} {FAILURE_CODE}{return_code_on_destroy}"
                exception: PubSubPlusCoreClientError = \
                    get_last_error_info(return_code=return_code_on_destroy,
                                        caller_description='SolaceApi->session_destroy',
                                        exception_message=error_message)
                self.adapter.warning("%s", str(exception))
                raise exception
            return return_code_on_destroy
        return None

    def create_session(self, config: dict) -> int:
        # When creating the Context, specify that the Context thread be
        # created automatically instead of having the application create its own
        # Context thread.
        # Args:
        #     config (dict):Configuration has been sent in the form of key value pairs.
        # Returns:
        #     int : returns return code from solClient_session_create and value will be '0' for success
        # Raises:
        #         PubSubPlusClientError: if we didn't receive 1 as return code
        arr = self.__prepare_session_props(config)
        self._session_func_info = self.__create_session_func_info()
        return_code = session_create(arr, self._context_p, self.__session_p,
                                     self._session_func_info)
        if transport_layer_properties.HOST in config:
            self.adapter.info('%s [%s]. [%s]', ESTABLISH_SESSION_ON_HOST,
                              config[transport_layer_properties.HOST],
                              "Connected" if return_code == SOLCLIENT_OK else "Not connected")
        if return_code != SOLCLIENT_OK:
            core_exception_msg = last_error_info(status_code=return_code, caller_desc="Session Creation")
            info_sub_code = core_exception_msg[CCSMP_INFO_SUB_CODE]
            exception_message = core_exception_msg[CCSMP_SUB_CODE]
            if f"unspecified property '" \
               f"{CCSMP_SESSION_PROP_MAPPING[transport_layer_security_properties.TRUST_STORE_PATH]}'" \
                    in core_exception_msg:
                self.adapter.warning("HOST: %s is secured, %s param is expected to establish SESSION",
                                     config[transport_layer_properties.HOST],
                                     transport_layer_security_properties.TRUST_STORE_PATH)
                raise PubSubPlusCoreClientError(message=f"HOST: {config[transport_layer_properties.HOST]} is secured, "
                                                        f"{transport_layer_security_properties.TRUST_STORE_PATH} "
                                                        f"param is expected to establish SESSION",
                                                sub_code=info_sub_code)
            self.adapter.warning(core_exception_msg[CCSMP_SUB_CODE])
            if exception_message == CCSMP_SUB_CODE_FAILED_TO_LOAD_TRUST_STORE:
                self.adapter.warning(FAILED_TO_LOAD_TRUST_STORE)
                raise PubSubPlusCoreClientError(message=FAILED_TO_LOAD_TRUST_STORE, sub_code=info_sub_code)
            elif exception_message == CCSMP_SUB_CODE_UNRESOLVED_HOST:
                self.adapter.warning(UNRESOLVED_SESSION)
                raise ServiceUnreachableError(UNRESOLVED_SESSION)
            elif exception_message == CCSMP_SUB_CODE_FAILED_LOADING_CERTIFICATE_AND_KEY:  # pragma: no cover
                # Due to core error scenario
                self.adapter.warning(FAILED_TO_LOADING_CERTIFICATE_AND_KEY)
                raise PubSubPlusCoreClientError(message=FAILED_TO_LOADING_CERTIFICATE_AND_KEY, sub_code=info_sub_code)
            else:
                raise PubSubPlusCoreClientError(message=core_exception_msg, sub_code=info_sub_code)
        return return_code

    def send_message(self, msg_p) -> int:
        # Sends a message on the specified Session. The message is composed of a number of optional
        #  components that are specified by the msg_p. The application should first
        #  allocate a solClient_msg, then use the methods defined in solClientMsg.h to
        #  build the message to send.
        #  solClient_session_sendMsg() returns SOLCLIENT_OK when the message has been successfully
        #  copied to the transmit buffer or underlying transport, this does not guarantee successful
        #  delivery to the Solace messaging appliance. When sending Guaranteed messages (persistent or non-persistent),
        #  the application will receive a subsequent SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT event for all
        #  messages successfully delivered to the Solace messaging appliance.
        # For Guaranteed messages, notifications of
        #  quota, permission, or other delivery problems will be indicated in a
        # SOLCLIENT_SESSION_EVENT_REJECTED_MSG_ERROR
        #  event.
        #  <b>Special Buffering of Guaranteed Messages</b>\n
        #  Guaranteed messages (SOLCLIENT_DELIVERY_MODE_PERSISTENT or SOLCLIENT_DELIVERY_MODE_NONPERSISTENT) are
        #  assured by the protocol between the client and the Solace message router. To make developers' task easier,
        #  guaranteed messages are queued for delivery in many instances:
        #  1. While transport (TCP) flow controlled.
        #  2. While message router flow controlled.
        #  3. While sessions are connecting or reconnecting.
        #  4. While sessions are disconnected or down.
        #  The C-SDK will buffer up to a publishers window size
        # of guaranteed messages before
        #  solClient_session_sendMsg() will either block (when SOLCLIENT_SESSION_PROP_SEND_BLOCKING is enabled)
        # or return SOLCLIENT_WOULD_BLOCK
        #  (on active sessions) or return SOLCLIENT_NOT_READY (on disconnected or reconnecting sessions).
        #  For the most part this is desired behavior. Transient sessions failures do not require special handling
        # in applications. When
        #  SOLCLIENT_SESSION_PROP_RECONNECT_RETRIES is non-zero, the underlying transport will automatically
        # reconnect and the publishing
        #  application does not need to concern itself with special handling for the transient reconnecting state.
        # Args:
        #    session_pointer :  The opaque Session returned when the Session was created.
        #     msg_p:  The opaque message created by solClient_msg_alloc.
        # Returns:
        #     SOLCLIENT_OK, SOLCLIENT_NOT_READY, SOLCLIENT_FAIL, SOLCLIENT_WOULD_BLOCK
        return self._core_lib.solClient_session_sendMsg(self.session_pointer, msg_p)

    def send_request(self, msg_p, reply_msg_p, timeout):
        # """
        #  * Send a Topic Request message. The application expects an end-to-end reply
        #  * from the client that receives the message.
        #  *
        #  * If the Reply-To destination in the Solace header mfap is not set, it is set to the default Session
        #  * replyTo destination. Leaving the replyTo destination unset and allowing the API to
        #  * set the default replyTo destination is the easiest way to set a valid replyTo destination.
        #  *
        #  * When the application needs to do a non-blocking request (that is, the timeout parameter is zero),
        #   the application
        #  * may set any replyTo topic destination.
        #  *
        #  * When the application needs to do a blocking request (that is, the timeout parameter is non-zero),
        #  * the replyTo destination must be a topic that the application has subscribed to for Direct messages.
        #  * If the replyTo destination is set to an unsubscribed topic, a call to solClient_session_sendRequest()
        #  * will block until the amount of time set for the timeout parameter expires and then return
        #  * ::SOLCLIENT_INCOMPLETE with subcode ::SOLCLIENT_SUBCODE_TIMEOUT.
        #  *
        #  * If the timeout parameter is zero, this function returns immediately with ::SOLCLIENT_IN_PROGRESS upon
        #  * successful buffering of the message for transmission. Any response generated by the destination client
        #  * is delivered to the replyTo destination as a receive message callback with the response attribute set -
        #  * solClient_msg_isReplyMsg() returns true. It is entirely within the responsibility of the
        #  * application to manage asynchronous responses.
        #  *
        #  * When the timeout parameter is non-zero, this function waits for the amount of time specified by the timeout
        #   parameter for a
        #  * response before returning ::SOLCLIENT_INCOMPLETE, otherwise this function returns ::SOLCLIENT_OK.
        #  * If replyMsg_p is non-NULL, this functions returns an opaque message pointer (::solClient_opaqueMsg_pt)
        #  in the location
        #  * referenced by reply_msg_p. This message is allocated by the API and contains the received reply.
        #  This function allocates
        #  * the message on behalf of the application and the application <b>must</b>
        #  later release the message by calling
        #  * solClient_msg_free(reply_msg_p).
        #  *
        #  * If this function does not return ::SOLCLIENT_OK, and replyMsg_p is non-NULL,
        #  then the location referenced by
        # * replyMsg_p is set to NULL.
        # Args:
        #     msg_p (): A pointer to a solClient_msgBuffer that contains the
        #                 message to be sent
        #     reply_msg_p (): A reference to a solClient_msgBuffer pointer that will
        #                 receive the reply message pointer. If NULL, then
        #                only status is returned. If non-NULL the application must
        #                 call solClient_msg_free() for the replyMsg when it is
        #                 no longer needed.
        #     timeout (): The maximum time (in milliseconds) to wait for reply.
        #                 If timeout is set to zero then the function will return
        #                 immediately ::SOLCLIENT_IN_PROGRESS after buffering of
        #                 the message for transmission.
        #
        # Returns:SOLCLIENT_OK, ::SOLCLIENT_IN_PROGRESS, ::SOLCLIENT_NOT_READY, ::SOLCLIENT_FAIL,
        # ::SOLCLIENT_WOULD_BLOCK, ::SOLCLIENT_INCOMPLETE
        # """

        return self._core_lib.solClient_session_sendRequest(self.session_pointer, msg_p,
                                                            ctypes.byref(reply_msg_p),
                                                            ctypes.c_int32(timeout))

    def send_reply(self, rxmsg_p, reply_msg_p):
        # """
        # Send a Reply Message. This function constructs a Solace binary
        # message header based on the received message and sends a reply to
        # the correct destination. If rxmsg_p is NULL, the application is responsible for setting
        # a destination and correlationId string in the replyMsg. Otherwise the following fields
        # from the rxmsg are used in the replyMsg
        #  session_pointer: The opaque Session pointer returned when the Session was
        #                created.
        # rxmsg_p:        A pointer to a solClient_msgBuffer that contains the
        #                message to reply to. (optional)
        # reply_msg_p:     A pointer to a solClient_msgBuffer that contains the
        #                message to be sent. (optional)
        # Returns: SOLCLIENT_OK, SOLCLIENT_NOT_READY, SOLCLIENT_FAIL
        # subcodes : SOLCLIENT_SUBCODE_MISSING_REPLY_TO - the rxmsg_p (if not NULL) does not have a
        # reply-to and so a reply cannot be sent.
        # """
        return self._core_lib.solClient_session_sendReply(self.session_pointer, rxmsg_p, reply_msg_p)

    @property
    def transport_state(self) -> _SolaceTransportState:
        return self._transport_state

    @property
    def session_pointer(self):
        # This method will return the underlying  C-api session pointer
        if self._transport_state == _SolaceTransportState.DOWN:
            return c_void_p(None)
        return self.__session_p

    def __do_connect(self) -> int:
        # this method establishes the connection to the service, if the connection is established
        # the return code will be zero stating SOLCLIENT_OK, if the connection is not established properly
        # then the return_code will be anything other than zero, in order to handle exception the return code
        # is sent to the __handle_exception_message() along with the caller description.
        # Returns:
        #     int: returns the return code ranging from (-1 to 8)
        return_code = session_connect(self.__session_p)
        if return_code == SOLCLIENT_OK:
            error = None
        else:
            error_info = last_error_info(status_code=return_code, caller_desc='do_connect')
            error = _SolaceTransportEventInfo(self.adapter, self._host,
                                              "Core library failed to connect.", error_info).exception
        return return_code, error

    def __create_session_func_info(self):
        # Create session function information needed for session creation.

        if not self._event_callback and not self._msg_callback:
            self._event_callback = self._event_callback_func_type(self.__service_event_callback_routine)

            self._msg_callback = self._msg_callback_func_type(self.__service_msg_rx_callback_routine)

        session_func_info = SolClientServiceCreateFuncInfo(
            (c_void_p(None), c_void_p(None)),
            (self._event_callback, py_object),
            (self._msg_callback, py_object))
        return session_func_info

    def __service_event_callback_routine \
                    (self, _opaque_session_p,
                     event_info_p, _pyobject) \
            :  # pylint: disable=too-many-branches  # pragma: no cover # Due to invocation in callbacks
        # conforms to eventCallback
        #     The event callback function is mandatory for session creation.
        # Args:
        #     _opaque_session_p: The Session event that has occurred
        #     event_info_p: A pointer to a NULL-terminated string providing further information about the event,
        #      when available.
        #     _pyobject: Application-supplied correlation pointer where applicable
        # Returns: int
        info = event_info_p
        correlation_tag = b''
        if info.contents.correlation_p:
            correlation_tag = _PublisherUtilities.decode(info.contents.correlation_p)
        event = info.contents.session_event

        if event != SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT:
            message = info.contents.info_p.decode()
        else:
            message = ""
        response_code = info.contents.response_code
        error_info = last_error_info(status_code=response_code,
                                     caller_desc="From service event callback")
        exception = None
        if error_info[CCSMP_SUB_CODE] != CCSMP_SUB_CODE_OK:
            self.adapter.info("%s", error_info)

        if event == SOLCLIENT_SESSION_EVENT_UP_NOTICE:
            self._transport_state = _SolaceTransportState.LIVE
            self._emit_transport_event(
                _SolaceTransportEvent.TRANSPORT_UP,
                _SolaceTransportEventInfo(self.adapter, self._host, message, error_info))

        elif event == SOLCLIENT_SESSION_EVENT_RECONNECTING_NOTICE:
            self._emit_transport_event(
                _SolaceTransportEvent.TRANSPORT_RECONNECTING,
                _SolaceTransportEventInfo(self.adapter, self._host, message, error_info))

        elif event == SOLCLIENT_SESSION_EVENT_RECONNECTED_NOTICE:
            self._emit_transport_event(
                _SolaceTransportEvent.TRANSPORT_RECONNECTED,
                _SolaceTransportEventInfo(self.adapter, self._host, message, error_info))

        elif event == SOLCLIENT_SESSION_EVENT_CAN_SEND:
            self.emit_publisher_event(_SolacePublisherEvent.PUBLISHER_CAN_SEND)
            self.can_send_received.set()

        elif event == SOLCLIENT_SESSION_EVENT_DOWN_ERROR:
            self._transport_state = _SolaceTransportState.DOWN
            self.emit_receiver_event(_SolaceReceiverEvent.RECEIVER_DOWN, error_info)
            self.emit_publisher_event(_SolacePublisherEvent.PUBLISHER_DOWN, error_info)
            self.can_send_received.set()  # wake up blocked publisher listener or worker threads
            # emit the transport event for the subscribers to capture
            self._emit_transport_event(
                _SolaceTransportEvent.TRANSPORT_DOWN,
                _SolaceTransportEventInfo(self.adapter, self._host, message, error_info))

        elif event == SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR:
            self._transport_state = _SolaceTransportState.DOWN
            self._emit_transport_event(
                _SolaceTransportEvent.TRANSPORT_DOWN,
                _SolaceTransportEventInfo(self.adapter, self._host, message, error_info))
        # In the future we should revisit the handling of SOLCLIENT_SESSION_EVENT_RX_MSG_TOO_BIG_ERROR
        # The above event is used for direct and persistent. We have a way of dealing with it for persistent
        # but not for direct.
        # To deal with it in direct, we would need a correlation tag on each message, which would affect performance.
        elif event in [SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT, SOLCLIENT_SESSION_EVENT_REJECTED_MSG_ERROR]:
            # Based on the correlation tag ack is sent to respective publisher's queue
            # self.adapter.warning('Received message acknowledgement with [%s] len [%s] from internal publisher',
            #    correlation_tag, len(correlation_tag))
            # FFC: This should be handled in the publisher not here. However, we
            # can only move this error handling to the publisher if we are willing
            # to rework the error handling for the entire API. This could be very
            # costly, so it is only for future consideradtion.
            if error_info[CCSMP_SUB_CODE] != CCSMP_SUB_CODE_OK:
                exception = PubSubPlusClientError(message=error_info)
                if error_info[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_PUBLISH_ACL_DENIED.value:
                    exception = MessageRejectedByBrokerError(message=error_info)
                elif error_info[CCSMP_INFO_SUB_CODE] == SolClientSubCode.SOLCLIENT_SUBCODE_NO_SUBSCRIPTION_MATCH.value:
                    exception = MessageDestinationDoesNotExistError(message=error_info)

            pub_id = _PublisherUtilities.get_publisher_id(correlation_tag)
            if pub_id:
                ack_handler = self._pub_ack_handlers.get(pub_id)
                if ack_handler:
                    ack_handler(correlation_tag, event, exception)
                else:
                    # no matching publisher
                    self.adapter.info('Received message acknowledgement with [%s] without a publisher',
                                      correlation_tag)
                    # remove correlation tag reference
                    if self.unregister_correlation_tag(correlation_tag) is False:
                        self.adapter.info(
                            'Failed to remove correlation tag [%s] for message acknowledgement without a publisher',
                            correlation_tag)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('Session Event: [%d]', event)
        return SOLCLIENT_CALLBACK_OK

    def __service_msg_rx_callback_routine(self, _opaque_session_p, _msg_p, _pyobject) \
            :  # pylint: disable=no-self-use  # pragma: no cover # Due to invocation in callbacks
        # conforms to messageReceiveCallback
        #  The message receive callback function is mandatory for session creation
        # Args:
        #     _opaque_sess ion_p:The Session event that has occurred
        #     _msg_p : pointer to message
        #     _pyobject : Application-supplied correlation pointer where applicable
        # Returns:
        #     int : return value 0
        return SOLCLIENT_CALLBACK_OK

    def __prepare_session_props(self, config: dict) -> ctypes.Array:
        #     Prepares the session props by comparing their instances and type casting the property value
        #     and finally adding the key value pairs to the dictionary
        #     Args:
        #     config: has key prop_value pairs of session property
        #     Returns:Array of config needed for session creation which got from config argument
        if transport_layer_properties.HOST in config:
            self._host = config[transport_layer_properties.HOST]
        tmp_dict = {}
        for key, value in config.items():
            if key in CCSMP_SESSION_PROP_MAPPING:
                if key in LEGACY_TO_CURRENT_CCSMP_SESSION_PROP_MAPPING:
                    if LEGACY_TO_CURRENT_CCSMP_SESSION_PROP_MAPPING[key] in config:
                        continue
                tmp_dict[CCSMP_SESSION_PROP_MAPPING[key]] = str(int(value)) if isinstance(value, bool) else str(value)
        tmp_dict = {**default_props, **tmp_dict}  # merge the config with default props
        return prepare_array(tmp_dict)
