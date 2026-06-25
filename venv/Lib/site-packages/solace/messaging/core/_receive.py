# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
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
This module contains the fsm for receivers.
"""

import logging
import enum
from abc import ABC, abstractmethod
from ctypes import c_void_p, POINTER, c_char_p, c_int, Structure, CFUNCTYPE, py_object, c_uint32

logger = logging.getLogger('solace.messaging.core')

class _SolaceReceiverEvent(enum.Enum):
    RECEIVER_DOWN = 0

class _SolaceReceiverEventEmitter(ABC):
    @abstractmethod
    def register_receiver_event_handler(self, event: '_SolaceReceiverEvent', handler) -> int:
        """
        Associates a handler function with a specific event.
        """

    @abstractmethod
    def unregister_receiver_event_handler(self, handler_id: int):
        """
        Dissociates a handler function from its event.
        """

    @abstractmethod
    def emit_receiver_event(self, event: '_SolaceReceiverEvent', event_info: dict):
        """
        Emits a reciever event.
        """

class _SolaceReceiver(ABC):  # pylint: disable=missing-class-docstring
    @property
    @abstractmethod
    def emitter(self) -> '_SolaceReceiverEventEmitter':  # pylint: disable=missing-function-docstring
        pass

class _BasicSolaceReceiver(_SolaceReceiver):
    def __init__(self, messaging_service: 'MessagingService'):
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            logger.debug('[%s] initialized', type(self).__name__)
        self._messaging_service: 'MessagingService' = messaging_service

    @property
    def emitter(self) -> '_SolaceReceiverEventEmitter':
        return self._messaging_service.session

class SolClientFlowEventCallbackInfo(Structure):  # pylint: disable=too-few-public-methods
    """ Conforms to solClient_flow_eventCallbackInfo_t """
    _fields_ = [
        ("flow_event", c_int),
        ("response_code", c_int),
        ("info_p", c_char_p),
    ]

solClient_flow_eventCallbackInfo_pt = POINTER(SolClientFlowEventCallbackInfo)
_event_callback_func_type = CFUNCTYPE(c_int, c_void_p, solClient_flow_eventCallbackInfo_pt, py_object)

_flow_msg_callback_func_type = CFUNCTYPE(c_int, c_void_p, c_void_p, py_object)

class SolClientFlowCreateRxCallbackFuncInfo_deprecated(Structure):  # pylint: disable=too-few-public-methods, invalid-name
    """ Conforms to solClient_flow_createRxCallbackFuncInfo_t (deprecated) """
    _fields_ = [
        ("callback_p", c_void_p),
        ("user_p", c_void_p)
    ]

class SolClientFlowCreateRxCallbackFuncInfo(Structure) \
        :  # pylint: disable=too-few-public-methods, missing-class-docstring
    # Conforms to solClient_flow_rxMsgDispatchFuncInfo_t

    _fields_ = [
        ("dispatch_type", c_uint32),  # The type of dispatch described
        ("callback_p", CFUNCTYPE(c_int, c_void_p, c_void_p, py_object)),  # An application-defined callback
        # function; may be NULL if there is no callback.
        ("user_p", py_object),
        # A user pointer to return with the callback; must be NULL if callback_p is NULL.
        ("rffu", c_void_p)  # Reserved for Future use; must be NULL
    ]

class SolClientFlowCreateEventCallbackFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    """ Conforms to solClient_flow_createEventCallbackFuncInfo_t """
    _fields_ = [
        ("callback_p", _event_callback_func_type),
        ("user_p", py_object)
    ]

class SolClientFlowCreateRxMsgCallbackFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    """ Conforms to solClient_flow_createRxMsgCallbackFuncInfo_t """
    _fields_ = [
        ("callback_p", _flow_msg_callback_func_type),
        ("user_p", py_object)
    ]

class SolClientFlowCreateFuncInfo(Structure):  # pylint: disable=too-few-public-methods
    """ Conforms to solClient_flow_createFuncInfo_t """
    _fields_ = [
        ("rx_info", SolClientFlowCreateRxCallbackFuncInfo_deprecated),  # deprecated
        ("event_info", SolClientFlowCreateEventCallbackFuncInfo),
        ("rx_msg_info", SolClientFlowCreateRxMsgCallbackFuncInfo)
    ]
