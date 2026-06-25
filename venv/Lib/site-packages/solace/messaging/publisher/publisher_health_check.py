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
This module provides an interface for readiness checks on
a :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` object.
"""
from abc import ABC, abstractmethod


class PublisherHealthCheck(ABC):
    """
    An abstract class that defines the interfaces for readiness checks on a
    :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher`.
    """

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Checks if a publisher can publish messages.

        Returns:
            bool: True if publisher can publish messages. False if publisher is prevented from sending messages
            including (e.g., full buffer or I/O problems).
        """

    @abstractmethod
    def set_publisher_readiness_listener(self, listener: 'PublisherReadinessListener'):
        """
        Sets a :py:class:`solace.messaging.publisher.publisher_health_check.PublisherReadinessListener`.
        Applications can implement the ``PublisherReadinessListener`` interface and configure objects with this
        interface to receive notifications when the the publisher can send messages.  Typically, after
        a :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` raises a
        :py:class:`solace.messaging.errors.pubsubplus_client_error.PublisherOverflowError`,
        the application will call :py:meth:`PublisherHealthCheck.notify_when_ready()`
        to guarantee that a subsequent :py:meth:`PublisherReadinessListener.ready()` call is seen.

        Args:
            listener(PublisherReadinessListener): A listener to observe the state of the publisher.
        """

    @abstractmethod
    def notify_when_ready(self):
        # pylint: disable=line-too-long
        """
            Makes a request to notify the application when the publisher is ready.

            This method helps to overcome a race condition between the completion of the exception
            processing and the :py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` instance,
            subsequently becoming ready.  While processing
            a :py:class:`solace.messaging.errors.pubsubplus_client_error.PublisherOverflowError`,
            the overflow condition can be resolved by background publishing.  At the end of the business
            logic to handle the ``PublisherOverflowError``, applications can call
            ``notify_when_ready`` to be guaranteed to receive a subsequent
            :py:meth:`PublisherReadinessListener.ready()<solace.messaging.publisher.publisher_health_check.PublisherReadinessListener.ready>`
            callback.
        """


class PublisherReadinessListener(ABC):
    """
    An abstract class that defines the interface for receiving publisher ready notification

    Interested applications can call :py:meth:`PublisherHealthCheck.notify_when_ready()` to
    request a ready notification.  Subsequent to this, when the publisher is ready to publish messages the
    ``ready()`` method is called.

    """

    @abstractmethod
    def ready(self):
        """
        Executes when the publisher is in a state when it can publish.

        After a failure to publish due to
        :py:class:`solace.messaging.errors.pubsubplus_client_error.PublisherOverflowError`. The API
        will always call ``ready()`` when the Publisher Overflow condition has eased.  This can lead to race
        conditions and synchronization issues with the publisher thread, if the publisher thread is still processing
        the exception.

        Consequently, the publisher thread can always use :py:meth:`PublisherHealthCheck.notify_when_ready()`
        to request a ``ready()`` callback that is guaranteed to occur subsequent to the notify request.

        NOTE:
            This ``ready()`` method is executed on a thread separate from the publisher thread.

        """
