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
This module contains classes for direct message publishers.

A direct message publisher must be created using
:py:class:`solace.messaging.builder.direct_message_publisher_builder.DirectMessagePublisherBuilder`. The
DirectMessagePublisher instance is used to publish direct messages created by a
:py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder`. The topic (or destination)
can be added when the message is a published.

The direct message publisher may also be use to publish simple messages containing only a bytearray or string payload.
"""

from abc import abstractmethod, ABC
from typing import Union, Dict

from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher.message_publisher import MessagePublisher
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.resources.destination import Destination
from solace.messaging.resources.topic import Topic


class DirectMessagePublisher(MessagePublisher, ABC):
    """ A class that defines the interface to a publisher for direct (non-persisted) messages."""

    @abstractmethod
    def set_publish_failure_listener(self, listener: 'PublishFailureListener'):
        """
        Set the specified ``PublishFailureListener`` to listen for a provided instance of the publisher.

        A :py:class:`solace.messaging.publisher.direct_message_publisher.PublishFailureListener` is notified
        through it's defined callback whenever a publish message attempt fails asynchronously.

        Published messages can be queued for later transmission when the transport is flow-controlled.  If queued
        messages cannot be published, the ``PublishFailureListener`` - if one is registered - is notified.
        The Solace event broker can also reject messages which appear as rejection notices on the
        specified ``PublishFailureListener``.

        Args:
            listener(PublishFailureListener): The specified listener for publisher failures.
        """

    @abstractmethod
    def publish(self, message: Union[bytearray, str, OutboundMessage], destination: Topic,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple, None,
                                                               bytearray]] = None):
        """
        Send outbound messages to the specified ``destination`` using a provided
        :py:class:`solace.messaging.builder.outbound_message.OutboundMessageBuilder` instance.
        Alternatively, a ``bytearray`` or ``str`` payload can be passed
        to this method this API will creates a :py:class:`solace.messaging.core.message.Message` instance to send.

        Args:
            message(bytearray, str, OutboundMessage): The outbound message that can be an
                                                      Outbound object, bytearray, or str.
            destination(Topic): The destination to add to the message.
            additional_message_properties(Dict[str, Union[str, int, float, bool, dict,list, tuple, None, bytearray]]) :
             The additional properties to customize a particular message. Each key can be customer
             provided, or it can be a key from of type
             :py:class:`solace.messaging.config.solace_properties.message_properties`, The value can either be a
             string or an integer or a float or a bool or a dict or list or a tuple or a None or a bytearray.
             additional_message_properties's int type parameter can  have minimum value
             as -9223372036854775808 and maximum value as 18446744073709551615
        Raises:
            PubSubPlusClientError: When the message cannot be send and retry attempts did not help in resolving problem.
            PublisherOverflowError: Raised when the publisher sends messages faster than what
                                    the current I/O capabilities allow for or when internal buffering
                                    capabilities have been exceeded.
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value
        """


class PublishFailureListener(ABC):
    """Interface definition for a listener for publish failures.
    """

    @abstractmethod
    def on_failed_publish(self, failed_publish_event: 'FailedPublishEvent'):
        """
        Callback method executed when publish errors occur asynchronously.

        Args:
            failed_publish_event(FailedPublishEvent): The publish event indicating a failure.
        """


class FailedPublishEvent:
    """
    FailedPublishEvent carries the details of a failed attempt to publish.

    When the application registers a
    :py:class:`solace.messaging.publisher.direct_message_publisher.PublishFailureListener`. the listener
    will be informed of failures with a FailedPublishEvent containing:

    - Message: OutboundMessage that failed.
    - Destination: The topic of the message.
    - Exception:  The exception that occurred on publish
    - Timestamp:  The time of the failure.

    """

    def __init__(self, message: OutboundMessage, destination: Destination, exception: PubSubPlusClientError,
                 timestamp: int = None):
        self._message: OutboundMessage = message
        self._destination: Destination = destination
        self._exception: PubSubPlusClientError = exception
        self._timestamp: float = timestamp

    def get_message(self) -> OutboundMessage:  # pragma: no cover # method executes in callback
        """ Retrieves :py:class:`solace.messaging.publisher.outbound_message.OutboundMessage`

        Returns:
            Message associated with this instance of the FailedPublishEvent
        """
        return self._message

    def get_destination(self) -> Destination:  # pragma: no cover # method executes in callback
        """Retrieves message destination (topic) on the failed message

        Returns:
            Destination associated with this instance of the FailedPublishEvent
        """
        return self._destination

    def get_timestamp(self) -> float:  # pragma: no cover # method executes in callback
        """Retrieves the timestamp of the event

        Returns:
            Timestamp associated with this instance of the FailedPublsihEvent
        """
        return self._timestamp

    def get_exception(self) -> PubSubPlusClientError:  # pragma: no cover # method executes in callback
        """Retrieves exception associated with a given event

        Returns:
            Exception associated with this instance of the FailedPublishEvent
        """
        return self._exception

    def __str__(self):  # pragma: no cover # method executes in callback
        return f"message : {str(self._message)}  timestamp : {self._timestamp} exception : {self._exception}"
