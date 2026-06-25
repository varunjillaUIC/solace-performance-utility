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

# pylint: disable=R0904,missing-function-docstring, too-many-instance-attributes, missing-class-docstring
# pylint: disable=too-many-ancestors,broad-except,protected-access,no-member

"""Module contains the Implementation classes and methods for the DirectMessagePublisher"""

import logging
import time
from typing import Union, Dict

from solace.messaging.config._sol_constants import SOLCLIENT_DELIVERY_MODE_DIRECT
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher._impl._message_publisher import _MessagePublisher, _MessagePublisherUnpublishedState
from solace.messaging.publisher._impl._publisher_utilities import validate_topic_type, _PublisherUtilities
from solace.messaging.publisher._publishable import Publishable
from solace.messaging.publisher.direct_message_publisher import DirectMessagePublisher, FailedPublishEvent, \
    PublishFailureListener
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.publisher._impl._outbound_message import _OutboundMessage
from solace.messaging.resources.topic import Topic
from solace.messaging.utils._solace_utilities import is_type_matches, _ThreadingUtil

logger = logging.getLogger('solace.messaging.publisher')


class _DirectMessagePublisher(_MessagePublisher, DirectMessagePublisher) \
        :

    # class for direct message publisher

    def __init__(self, builder: '_DirectMessagePublisherBuilder'):
        # Args:
        #     messaging_service (MessageService):
        #     publisher_back_pressure_type (PublisherBackPressure):
        #     buffer_capacity (int):
        #     buffer_time_out ():

        super().__init__(builder)
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('[%s] initialized', type(self).__name__)
        self._error_notification_dispatcher: PublishFailureNotificationDispatcher = \
            PublishFailureNotificationDispatcher()

    @property
    def _delivery_mode(self) -> str:
        return SOLCLIENT_DELIVERY_MODE_DIRECT

    def set_publish_failure_listener(self, listener: 'PublishFailureListener') -> None:
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('SET: Direct Publish failure listener')
        is_type_matches(listener, PublishFailureListener)
        self._error_notification_dispatcher.set_publish_failure_listener(listener)

    def publish(self, message: Union[bytearray, str, dict, list, tuple, OutboundMessage], destination: Topic,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple,
                                                               bytearray]] = None):
        validate_topic_type(destination=destination, logger=logger)
        _PublisherUtilities.validate_payload_type(message)
        # if additional_message_properties:
        # is_none_or_empty_exists(additional_message_properties, error_message=INVALID_ADDITIONAL_PROPS,
        #                         logger=logger)
        # props = _SolaceSDTMap(additional_message_properties) if additional_message_properties else dict()
        super().message_publish(message, destination, additional_message_properties=additional_message_properties)

    def notify_publish_error(self, exception: Exception, publishable: Publishable, tag: bytes = None):
        self._error_notification_dispatcher.on_exception(exception, publishable)

    def _cleanup_message_state(self) -> _MessagePublisherUnpublishedState:
        unpub_state = super()._cleanup_message_state()
        # send failure for all messages that did not get published
        error = PubSubPlusClientError('Direct Publisher Terminated')
        for publishable, _ in unpub_state.unpublished_messages:
            self._error_notification_dispatcher.on_exception(error, publishable)
        return unpub_state

    def _on_publisher_down(self, error_info: dict):  # pylint: disable=useless-super-delegation
        # call parent to update state
        super()._on_publisher_down(error_info)

    def _resource_cleanup(self):
        super()._resource_cleanup()
        self._error_notification_dispatcher.shutdown()


class ScheduledFailureNotification:  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Class contains methods for scheduling an failure notification
    def __init__(self, dispatcher,
                 exception: Exception, time_stamp: int, publishable: Publishable = None):
        self._dispatcher = dispatcher
        self._exception = exception
        self._time_stamp = time_stamp
        self._publishable = publishable
        if self._publishable is None:
            self._publishable = Publishable.none()

    def call(self) -> None:
        # This method schedules the notification by calling the on_failed_publish()
        listener: 'PublishFailureListener' = self._dispatcher.publish_failure_listener
        if listener is None:
            # the listener was removed/un-set , skip
            return
        listener.on_failed_publish(FailedPublishEvent(_OutboundMessage(self._publishable.get_message()),
                                                      self._publishable.get_destination(),
                                                      self.map_exception(self._exception),
                                                      self._time_stamp))

    @staticmethod
    def map_exception(exception: Exception) -> PubSubPlusClientError:
        # This method returns the exception map
        if isinstance(exception, PubSubPlusClientError):
            return exception
        return PubSubPlusClientError(exception)


class PublishFailureNotificationDispatcher:  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Dispatcher class for notifying the publish failures
    # failure_notification_executor_service = ThreadPoolExecutor(max_workers=1)
    # publish_failure_listener: 'PublishFailureListener' = None

    def __init__(self):
        self._publish_failure_listener: 'PublishFailureListener' = None
        self._failure_notification_executor_service = None

    @property
    def publish_failure_listener(self):
        return self._publish_failure_listener

    def shutdown(self):
        if self._failure_notification_executor_service:
            self._failure_notification_executor_service.shutdown(wait=True)

    def on_exception(self, exception_occurred: Exception, publishable: Publishable = None,
                     time_stamp: int = None):
        # Method to invoke the listener thread when publish mechanism fails
        #
        # Args:
        #     exception_occurred: occurred exception message
        #     publishable: Publishable object which contains the message and the destination name
        #     time_stamp: current time stamp in Epoch milliseconds.
        listener: 'PublishFailureListener' = self._publish_failure_listener
        if time_stamp is None:
            time_stamp = int(time.time() * 1000)  # in milliseconds
        if listener is None or exception_occurred is None:
            return

        if publishable is None:
            notification: 'ScheduledFailureNotification' = ScheduledFailureNotification(self, exception_occurred,
                                                                                        time_stamp)
        else:
            notification: 'ScheduledFailureNotification' = ScheduledFailureNotification(self, exception_occurred,
                                                                                        time_stamp,
                                                                                        publishable)

        try:
            self._failure_notification_executor_service.submit(notification.call)
        except PubSubPlusClientError as exception:  # pragma: no cover # Due to failure scenario
            logger.exception(exception)
            # if the thread fails to call the notification.call() we explicitly call it to
            # run on same thread when scheduler is full
            try:
                notification.call()
            except PubSubPlusClientError as inner_exception:
                logger.exception(inner_exception)

    def set_publish_failure_listener(self, publish_failure_listener: 'PublishFailureListener') -> None:
        # Method for setting the PublishFailureListener
        #
        # Args:
        #     publish_failure_listener: is of type PublishFailureListener

        # lazy init of executor
        if self._failure_notification_executor_service is None and publish_failure_listener is not None:
            self._failure_notification_executor_service = _ThreadingUtil.create_serialized_executor(
                'PublisherFailureEventNotifier')
        self._publish_failure_listener = publish_failure_listener
