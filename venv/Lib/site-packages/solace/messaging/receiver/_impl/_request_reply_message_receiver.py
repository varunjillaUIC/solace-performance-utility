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

# pylint: disable=missing-module-docstring,missing-function-docstring,protected-access,too-many-instance-attributes
# pylint: disable=too-many-ancestors,arguments-differ,no-else-raise,broad-except,line-too-long
import logging
import queue
import threading
import weakref
from typing import Tuple, Union

from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._sol_constants import SOLCLIENT_OK, SOLCLIENT_NOT_FOUND
from solace.messaging.config._solace_message_constants import GRACE_PERIOD_DEFAULT_MS
from solace.messaging.core._message import _SolClientDestination
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.receiver._impl._message_receiver import _DirectRequestReceiver
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.receiver.request_reply_message_receiver import RequestReplyMessageReceiver, Replier, \
    RequestMessageHandler
from solace.messaging.utils._solace_utilities import is_type_matches, is_not_negative, convert_ms_to_seconds, \
    QueueShutdown

logger = logging.getLogger('solace.messaging.receiver')


class _RequestReplyMessageReceiver(_DirectRequestReceiver, RequestReplyMessageReceiver):
    # """Implementation class for the RequestReplyMessageReceiver"""

    def __init__(self, builder):
        super().__init__(builder)

        self._message_handler = None
        self._inbound_message = None
        self._async_message_handler = None
        self._can_shutdown = threading.Event()
        self._shut_down_initiated = threading.Event()
        self._async_started = False
        self._int_metrics = builder._messaging_service.metrics()
        key = "subscriptions"
        if key in builder.topic_dict:
            subscription = builder.topic_dict[key]
            if isinstance(subscription, str):
                self._topic_dict[subscription] = False  # not applied
            else:
                for topic in subscription:
                    self._topic_dict[topic] = False  # not applied
        key = "group_name"
        if key in builder.topic_dict:
            self._group_name = builder.topic_dict[key]
        def _receiver_cleanup(shut_event, message_queue):
            shut_event.set()
            message_queue.shutdown()
        weakref.finalize(self, _receiver_cleanup, self._can_shutdown, self._message_receiver_queue)

    def _async_receiver(self):
        while not self._can_shutdown.is_set():  # set during terminate()
            try:
                message = self._message_receiver_queue.get()
                if isinstance(message, InboundMessage):
                    return_code = message.solace_message.get_reply_to(_SolClientDestination())

                    if return_code in [SOLCLIENT_OK, SOLCLIENT_NOT_FOUND]:
                        replier = None if return_code == SOLCLIENT_NOT_FOUND else _Replier(
                            self, message)
                        try:
                            self._async_message_handler.on_message(message, replier)
                        except Exception as exception:
                            self.adapter.warning(str(exception))
                    else:
                        self.adapter.warning(last_error_info(return_code, "receive_async")['error_info_contents'])
            except QueueShutdown:
                break
            except Exception as exception:  # pylint: disable=broad-except
                self.adapter.error(str(exception))

    def receive_async(self, message_handler: 'RequestMessageHandler'):
        is_type_matches(actual=message_handler, expected_type=RequestMessageHandler, logger=logger)
        self._can_receive_message()
        self._async_message_handler = message_handler
        if not self._async_started:
            self._executor.submit(self._async_receiver)
            self._async_started = True

    def receive_message(self, timeout=None) -> Tuple[Union[InboundMessage, None],
                                                     Union[Replier, None]]:
        # """Get a message, blocking call"""
        if timeout is not None:
            is_not_negative(input_value=timeout, logger=logger)
        self._can_receive_message()
        # when service goes down so we may receive None as message
        try:
            message = self._message_receiver_queue.get(block=True,
                                                       timeout=convert_ms_to_seconds(
                                                           timeout) if timeout is not None else None)
            if isinstance(message, InboundMessage):
                return_code = message.solace_message.get_reply_to(_SolClientDestination())
                if return_code == SOLCLIENT_OK:
                    return message, _Replier(self, message)
                if return_code == SOLCLIENT_NOT_FOUND:
                    return message, None
                raise PubSubPlusClientError(last_error_info(return_code, "receive_message")['error_info_contents'])  # pragma: no cover # Due to core error scenarios
            else:
                return None, None  # this happens usually when we put None in queue as part of terminate functionality
        except QueueShutdown:
            # unblock waiters on terminate
            return None, None
        except queue.Empty:  # when timeout arg is given just return None on timeout
            return None, None
        except (PubSubPlusClientError, KeyboardInterrupt) as exception:
            raise exception

    def terminate(self, grace_period: int = GRACE_PERIOD_DEFAULT_MS):
        # """
        # Stop the RequestReplyMessageReceiver - put None in the queue which will stop our asynchronous
        # dispatch thread, or the app will get if it asks for another message via sync. """
        self._shut_down_initiated.set()
        super().terminate(grace_period)

    def _halt_messaging(self):
        self._unsubscribe()


class _Replier(Replier):  # pylint: disable=too-few-public-methods
    def __init__(self, request_reply_message_receiver, inbound_message):
        self._messaging_service = request_reply_message_receiver._messaging_service
        self._inbound_message = inbound_message

    def reply(self, response_message: OutboundMessage):
        if isinstance(self._inbound_message, InboundMessage) and isinstance(response_message, OutboundMessage):
            return_code = self._messaging_service.session.send_reply(
                self._inbound_message.solace_message.msg_p,
                response_message.solace_message.msg_p)
            if return_code != SOLCLIENT_OK:
                raise PubSubPlusClientError(last_error_info(return_code, "send reply")['error_info_contents'])
        else:
            raise PubSubPlusClientError(f"Cannot reply due to  either or both args type mismatch "
                                        f"inbound_message: {type(self._inbound_message)}, "
                                        f"response_message: {type(response_message)} ")
