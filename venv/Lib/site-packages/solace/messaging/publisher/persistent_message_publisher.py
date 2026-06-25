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

# pylint: disable=too-many-arguments

"""
Module that contains Persistent Message Publisher.

A Persistent Message Publisher must be created by
:py:class:`solace.messaging.builder.persistent_message_publisher_builder.PersistentMessagePublisherBuilder`. The
``PersistentMessagePublisher`` instance is used to publish Guaranteed Messages created by a
:py:class:`solace.messaging.publisher.outbound_message.OutboundMessageBuilder`. The
Topic (or destination) can be added once the message is a published.

The persistent message publisher can also be used to publish simple messages containing only a bytearray or
string payload.
"""
from abc import ABC, abstractmethod
from typing import Union, Any, Dict

from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher.message_publisher import MessagePublisher
from solace.messaging.publisher.outbound_message import OutboundMessage
from solace.messaging.resources.topic import Topic


class PersistentMessagePublisher(MessagePublisher, ABC):  # pylint: disable=too-many-ancestors
    """
    A class that defines the interface to a publisher for persistent messages.

    NOTE:
        The ``PublishReceipt`` is available asynchronously via
        :py:class:`solace.messaging.publisher.persistent_message_publisher.MessagePublishReceiptListener`.
        Message correlation tokens are used to PublishReceipt.

        Alternatively, applications can get publish confirmation by publishing with the synchronous method
        :py:meth:`PersistentMessagePublisher.publish_await_acknowledgement()` method that does
        not return until the published message has been acknowledged by the Solace event broker.
    """

    @abstractmethod
    def set_message_publish_receipt_listener(self, listener: 'MessagePublishReceiptListener'):
        """
        Sets the ``MessagePublishReceiptListener`` for the given instance of the publisher. It is used to
        handle broker message acknowledgement or broker message reject for all the messages published.

        Args:
            listener(MessagePublishReceiptListener): A listener that handles message publish confirmations
                or message publish failures.
        """

    @abstractmethod
    def publish(self, message: Union[bytearray, str, OutboundMessage], destination: Topic, user_context: Any = None,
                additional_message_properties: Dict[str, Union[str, int, float, bool, dict, list, tuple, None,
                                                               bytearray]] = None):
        """
        Sends and outbound message to the given destination.

        The :py:class:`solace.messaging.builder.outbound_message.OutboundMessageBuilder` can be used
        to create the ``OutboundMessage`` instance. Alternatively, a bytearray or string payload can be passed
        to this function and the API will create a :py:class:`solace.messaging.core.message.Message` to send.

        Args:
            message:(bytearray, str, OutboundMessage): The message or the or payload to publish.
            destination:(Topic): The destination to add to the message.
            user_context:(Any): the context associated with an action that is performed when the message
                delivery to the broker is confirmed using :py:meth:`MessagePublishReceiptListener.on_publish_receipt`
                When the user-context is not supposed to be available, use the method instead without the
                ``user_context`` parameter.
            additional_message_properties:(Dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The additional message properties to add to the message metadata.Each key can be customer
                provided, or it can be a key from of type
                `solace.messaging.config.solace_properties.message_properties`.
                The key for the configuration is a string, the value  can either be a string or an integer  or a float
                or a bool or a dict or list or a tuple or a None or a bytearray. property_value's int type parameter can
                have minimum value as -9223372036854775808 and maximum value as 18446744073709551615

        Raises:
            PubSubPlusClientError: When message can't be send and retry attempts would not help.
            PublisherOverflowError: When a publisher publishes messages faster then the I/O
                capabilities allow or internal message buffering capabilities are exceeded.
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value
        """

    @abstractmethod
    def publish_await_acknowledgement(self, message: Union[bytearray, str, OutboundMessage], destination: Topic,
                                      time_out: int = None,
                                      additional_message_properties: Dict[str, Union[str, int, float, bool,
                                                                                     dict, list, tuple, None,
                                                                                     bytearray]] = None):
        """
        Sends a persistent message, blocking until publish acknowledgement is received or timeout occurs

        Args:
            message: (bytearray, str, OutboundMessage): The message to send.
            destination: (Topic): The message topic to send to, which is the message destination.
            time_out: (int): The maximum time (in milliseconds) to wait for a message acknowledgement.
            additional_message_properties:(Dict[str, Union[str, int, float, bool, dict, list, tuple, None, bytearray]]):
                The additional message properties to add to the message metadata.Each key can be customer
                provided, or it can be a key from of type `solace.messaging.config.solace_properties.message_properties`
                The key for the configuration is a string, the value  can either be a string or an integer or a float
                or a bool or a dict or list or a tuple or a None or a bytearray. property_value's int type parameter can
                have minimum value as -9223372036854775808 and maximum value as 18446744073709551615

        Raises:
            PubSubTimeoutError: After specified timeout when no-response received.
            MessageRejectedByBrokerError: When a message was rejected from a broker for some reason.
            PublisherOverflowError: When publisher publishes too fast, message can be republished immediately
                                    or after some time
            MessageDestinationDoesNotExistError: When a given message destination does not exist.
            MessageNotAcknowledgedByBrokerError: When a message broker could not acknowledge message
                                                 persistence on an event broker.
            PubSubPlusClientError: When some internal error occurs.
            IllegalArgumentError:  When the value of timeout is negative.
            InvalidDataTypeError : Raised when additional_message_properties's int type value is not in between the
             range of minimum value & maximum value

        """


class MessagePublishReceiptListener(ABC):
    """Message publish listener interface to process broker message publish notifications (success/failure).
    """

    @abstractmethod
    def on_publish_receipt(self, publish_receipt: 'PublishReceipt'):
        """
        On publish, sends the publish receipt.

        Args:
            publish_receipt(PublishReceipt): The object to indicate that publish was done.

        """


class PublishReceipt:
    """
    Encapsulates broker acknowledgement or failed publishing attempt details, used for message
    publish notification processing such as timestamp, correlation token, original message,
    indicator if message was persisted on a broker, exception if any.
    """

    def __init__(self, message: OutboundMessage, exception: PubSubPlusClientError, time_stamp: int,
                 persisted: bool, user_context: object = None):
        self._message: OutboundMessage = message
        self._exception: PubSubPlusClientError = exception
        self._time_stamp: int = time_stamp
        self._persisted: bool = persisted
        self._user_context: object = user_context

    @property
    def user_context(self) -> object:
        """Retrieve the context associated with an action if provided during publishing

        Returns:
            context associated with broker publish confirmation action or None if there is nothing.
        """
        return self._user_context

    @property
    def time_stamp(self) -> int:
        """
        Retrieves the timestamp associated with the Receipt,
        The number of milliseconds from the epoch of 1970-01-01T00:00:00Z

        Returns:
            int value of the timestamp"""
        return self._time_stamp

    @property
    def message(self) -> OutboundMessage:
        """
        Retrieves message associated with a Receipt

        Returns:
            message associated with this instance of the Receipt
        """
        return self._message

    @property
    def exception(self) -> PubSubPlusClientError:
        """
        Gets exception if any, indicating failure case

        Returns:
            not None value indicates failure by publishing to the broker or during persistence on a broker
        """
        return self._exception

    @property
    def is_persisted(self) -> bool:
        """
        Gets the persisted state of the published message.

        Returns:
            true if broker confirmed that message is received and persisted, false otherwise
        """
        return self._persisted

    def __str__(self):
        return f"message : {str(self._message)} time_stamp : {str(self._time_stamp)} " \
               f"exception : {str(self._exception)} persisted : {str(self._persisted)} "
