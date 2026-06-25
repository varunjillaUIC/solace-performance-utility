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
This module contains the object models required for basic termination notification.
"""

import datetime
import time
from typing import Union

from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.utils.life_cycle_control import TerminationNotificationListener, TerminationEvent
from solace.messaging.utils._solace_utilities import _ThreadingUtil

class ScheduledFailureNotification:  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Class contains methods for scheduling an failure notification
    def __init__(self, dispatcher, exception: Exception, time_stamp: int):
        self._dispatcher = dispatcher
        self._exception = exception
        self._time_stamp = time_stamp

    def call(self) -> None:
        # This method schedules the notification by calling the on_termination()
        listener: TerminationNotificationListener = self._dispatcher.termination_notification_listener
        if listener is None:
            # the listener was removed/un-set , skip
            return
        listener.on_termination(TerminationNotificationEvent(self.map_exception(self._exception),
                                                             self._time_stamp))

    @staticmethod
    def map_exception(exception: Exception) -> PubSubPlusClientError:
        # This method returns the exception map
        if isinstance(exception, PubSubPlusClientError):
            return exception
        return PubSubPlusClientError(exception)


class TerminationNotificationDispatcher:  # pylint: disable=missing-class-docstring, missing-function-docstring
    # Dispatcher class for notifying the receive failures

    def __init__(self, adapter):
        self._termination_notification_listener: TerminationNotificationListener = None
        self._failure_notification_executor_service = None
        self._adapter = adapter

    @property
    def termination_notification_listener(self):
        return self._termination_notification_listener

    def shutdown(self):
        if self._failure_notification_executor_service:
            self._failure_notification_executor_service.shutdown(wait=True)

    # pylint: disable=broad-except
    def on_termination(self, pending_receive_queue, error: PubSubPlusClientError, time_stamp: int):
        # get listener
        listener: TerminationNotificationListener = self._termination_notification_listener
        # only dispatch failures there is a listener, an error and a pending queue
        if listener is None or error is None or pending_receive_queue is None:
            return None
        # submit event to executor
        # receiver down error typically occur from the native api thread
        try:
            return self._failure_notification_executor_service.submit(self.on_exception, error, time_stamp)
        # We are okay with catching a broad exception here because we just log it and don't conduct any
        # operations based on the type of exception
        except Exception as exception:  # pragma: no cover # Due to failure scenario
            self._adapter.exception(exception)
            return None

    def on_exception(self, exception_occurred: Exception, time_stamp: int = None):
        # Method to invoke the listener thread when receive mechanism fails
        #
        # Args:
        #     exception_occurred: occurred exception message
        #     time_stamp: current time stamp in Epoch milliseconds.
        if time_stamp is None:
            time_stamp = int(time.time() * 1000)
        listener: TerminationNotificationListener = self._termination_notification_listener
        if listener is None or exception_occurred is None:
            return
        notification: ScheduledFailureNotification = ScheduledFailureNotification(self, exception_occurred,
                                                                                  time_stamp)
        try:
            self._failure_notification_executor_service.submit(notification.call)
        except PubSubPlusClientError as exception:  # pragma: no cover # Due to failure scenario
            self._adapter.exception(exception)
            # if the thread fails to call the notification.call() we explicitly call it to
            # run on same thread when scheduler is full
            try:
                notification.call()
            except PubSubPlusClientError as inner_exception:
                self._adapter.exception(inner_exception)

    def set_termination_notification_listener(self,
                                              termination_notification_listener:
                                              TerminationNotificationListener) -> None:
        # Method for setting the TerminationNotificationListener
        #
        # Args:
        #     receive_failure_listener: is of type TerminationNotificationListener

        # lazy init of executor
        if self._failure_notification_executor_service is None and \
                termination_notification_listener is not None:
            self._failure_notification_executor_service = \
                _ThreadingUtil.create_serialized_executor('TerminationEventNotifier')
        self._termination_notification_listener = termination_notification_listener

    @property
    def failure_notification_executor_service(self):
        return self._failure_notification_executor_service


class TerminationNotificationEvent(TerminationEvent):
    """Encapsulates details of a failed attempt to receive, used for failure notification processing
    such as timestamp, exception"""

    def __init__(self, exception: PubSubPlusClientError, timestamp: Union[float, None]):
        self._exception = exception
        self._timestamp = timestamp if timestamp is not None else datetime.datetime.now().microsecond

    @property
    def timestamp(self):
        """Retrieves the timestamp of the event, number of milliseconds from the epoch of 1970-01-01T00:00:00Z

        Returns:
            long value of the timestamp
        """
        return self._timestamp

    @property
    def cause(self):
        """Retrieves exception associated with a given event

        Returns:
            exception for the event
        """
        return self._exception

    @property
    def message(self):
        return f"{type(self).__name__}  timestamp: {self._timestamp}  cause : {self._exception}"
