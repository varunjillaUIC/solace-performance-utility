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

"""This module contains the enum classes related to SolaceTransportState"""

import enum
import logging

from abc import ABC, abstractmethod
from typing import Union, Callable
from solace.messaging.config._solace_message_constants import CCSMP_SUB_CODE, CCSMP_INFO_SUB_CODE, \
    CCSMP_SUBCODE_UNTRUSTED_CERTIFICATE, UNTRUSTED_CERTIFICATE_MESSAGE, \
    CCSMP_SUB_CODE_FAILED_LOADING_CERTIFICATE_AND_KEY, FAILED_TO_LOADING_CERTIFICATE_AND_KEY, \
    CCSMP_SUB_CODE_LOGIN_FAILURE, BAD_CREDENTIALS, CCSMP_SUB_CODE_OK
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusCoreClientError, AuthenticationError

class _SolaceTransportState(enum.Enum):
    # In the future the model for live state and other useful states like connecting, reconnecting, etc,
    # can be revisited as needed.
    LIVE = 1
    DOWN = -1

class _SolaceTransportEvent(enum.Enum):
    """
    Enumeration of different transport events, add more when necessary.
    """

    TRANSPORT_DOWN = 0
    TRANSPORT_UP = 1
    TRANSPORT_RECONNECTING = 2
    TRANSPORT_RECONNECTED = 3

class _SolaceTransport(ABC):
    """
    Interface for internal transport used by services.
    """

    @property
    @abstractmethod
    def event_emitter(self) -> '_SolaceTransportEventEmitter':  # pylint: disable=missing-function-docstring
        ...

    @abstractmethod
    def connect(self) -> (int, Union[Exception, None]):  # pylint: disable=missing-function-docstring
        ...

    @abstractmethod
    def disconnect(self) -> (int, Union[Exception, None]):  # pylint: disable=missing-function-docstring
        ...

class _SolaceTransportEventInfo:
    def __init__(self, adapter, host, message, event_info: dict, exception=None):  # pylint: disable=too-many-arguments
        self._host = host
        self._message = message
        self._event_info: dict = event_info
        self._adapter = adapter
        if exception is None:
            if self.subcode_str == CCSMP_SUBCODE_UNTRUSTED_CERTIFICATE:
                self.adapter.warning(' %s %s', UNTRUSTED_CERTIFICATE_MESSAGE, self._event_info)
                self._exception = PubSubPlusCoreClientError(message=f'{UNTRUSTED_CERTIFICATE_MESSAGE} ' \
                                                                    f'{self._event_info}',
                                                            sub_code=self.subcode)
            elif self.subcode_str == CCSMP_SUB_CODE_FAILED_LOADING_CERTIFICATE_AND_KEY:
                self.adapter.warning(' %s %s', FAILED_TO_LOADING_CERTIFICATE_AND_KEY, self._event_info)
                self._exception = PubSubPlusCoreClientError(message=f'{FAILED_TO_LOADING_CERTIFICATE_AND_KEY} ' \
                                                                    f'{self._event_info}',
                                                            sub_code=self.subcode)
            elif self.subcode_str == CCSMP_SUB_CODE_LOGIN_FAILURE:
                self.adapter.warning('%s %s', BAD_CREDENTIALS, self._event_info)
                self._exception = AuthenticationError(message=f'{BAD_CREDENTIALS} {self._event_info}')
            elif self.subcode_str == CCSMP_SUB_CODE_OK:
                if self.adapter.isEnabledFor(logging.DEBUG):
                    self.adapter.debug('%s', self._event_info)
                self._exception = None
            else:
                self.adapter.warning('%s', self._event_info)
                self._exception = PubSubPlusCoreClientError(message=self._event_info, sub_code=self.subcode)
        else:
            self._exception = exception

    @property
    def adapter(self):  # pylint: disable=missing-function-docstring
        return self._adapter

    @property
    def host(self):  # pylint: disable=missing-function-docstring
        return self._host

    @property
    def message(self):  # pylint: disable=missing-function-docstring
        return self._message

    @property
    def subcode(self) -> int:  # pylint: disable=missing-function-docstring
        return self._event_info[CCSMP_INFO_SUB_CODE]

    @property
    def subcode_str(self) -> str:  # pylint: disable=missing-function-docstring
        return self._event_info[CCSMP_SUB_CODE]

    @property
    def exception(self):  # pylint: disable=missing-function-docstring
        return self._exception

    def __str__(self):
        error = self.exception
        if error:
            return f"{type(self).__name__}:[host:'{self._host}', message:'{self._message}', " \
                   f"error_info: [{self._event_info}], exception: '{error}']"
        return f"{type(self).__name__}:[host:'{self._host}', message:'{self._message}', " \
               f"error_info: [{self._event_info}]]"

class _SolaceTransportEventEmitter(ABC):
    @abstractmethod
    def register_transport_event_handler(self, event: '_SolaceTransportEvent', handler: Callable[[dict], None]) -> int:
        """
        Registers transport event handlers, when used with a _SolaceTransport event should be register before calls
        to connect. Note only one handler can be registered at a time and replaces the previous handler.
        """

    @abstractmethod
    def unregister_transport_event_handler(self, handler_id: int):
        """
        Unregisters transport event handlers so that they can no longer be called. This is useful to ensure that no
        event handlers are called after the transport has disconnected.
        """

    @abstractmethod
    def _emit_transport_event(self, event: '_SolaceTransportEvent', event_info: '_SolaceTransportEventInfo'):
        """
        Emits a transport event along with the variable arguments needed for the event handler.
        """
