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


""" This modules abstracts different aspects of API manageability"""

import enum
from abc import ABC, abstractmethod
from typing import Union

from solace.messaging.config._sol_constants import _SOLCLIENTSTATSRX, _SOLCLIENTSTATSTX


class Metric(enum.Enum):  # pylint: disable=too-few-public-methods
    """
    A class that is an enumeration of available statistics that may be retrieved from any class with
    the py:class:`solace.messaging.utils.manageable.Manageable` interface.

    These metrics are a composite of native library metrics and Python API metrics.  They will not
    always reflect the application experience.  For example an application may publish some number of
    messages and not see that number in TOTAL_MESSAGES_SENT because this reflects messages sent to the
    broker and not messages that may still be queued within the Python API for sending.

    When analyzing metrics therefore the developer should be aware of all the places messages and or
    event may be counted.

    """

    # Note : Don't name python's internal Metric.value  to starts with  SOLCLIENT_* since
    # ApiMetrics private method _set_internal_stat relies on this naming convention
    # to differentiate internal from broker's metrics for example
    # for RECEIVED_MESSAGES_TERMINATION_DISCARDED = 'RECEIVED_MESSAGES_TERMINATION_DISCARDED' don't name like
    # RECEIVED_MESSAGES_TERMINATION_DISCARDED = 'SOLCLIENT_RECEIVED_MESSAGES_TERMINATION_DISCARDED

    DIRECT_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DIRECT_BYTES.name
    """The number of bytes received."""
    DIRECT_MESSAGES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DIRECT_MSGS.name
    """The number of messages received."""
    BROKER_DISCARD_NOTIFICATIONS_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_IND.name
    """ The number of receive messages with discard indication set."""
    UNKNOWN_PARAMETER_MESSAGES_DISCARDED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_SMF_UNKNOWN_ELEMENT.name
    """The number of messages discarded due to the presence of an unknown element or unknown protocol in the
    Solace Message Format (SMF) header."""
    TOO_BIG_MESSAGES_DISCARDED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_MSG_TOO_BIG.name
    """ The number of messages discarded due to msg too large. """
    PERSISTENT_ACKNOWLEDGE_SENT = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_ACKED.name
    """The number of acknowledgments sent for Guaranteed messages."""
    PERSISTENT_DUPLICATE_MESSAGES_DISCARDED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_DUPLICATE.name
    """The number of Guaranteed messages dropped for being duplicates. """
    PERSISTENT_NO_MATCHING_FLOW_MESSAGES_DISCARDED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_NO_MATCHING_FLOW.name
    """The number of Guaranteed messages discarded due to no match on the flowId."""
    PERSISTENT_OUT_OF_ORDER_MESSAGES_DISCARDED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_DISCARD_OUTOFORDER.name
    """The number of Guaranteed messages discarded for being received out of order."""
    PERSISTENT_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_PERSISTENT_BYTES.name
    """The number of Persistent bytes received on the ``MessageReceiver``. On the ``MessageService``, it is the total
    number of Persistent bytes received across all ``MessageReceiver``."""
    PERSISTENT_MESSAGES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_PERSISTENT_MSGS.name
    """ The number of Persistent messages received on the ``MessageReceiver``. On the ``MessageService``, it is the
    total number of Persistent messages received across all ``MessageReceiver``."""
    NONPERSISTENT_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_NONPERSISTENT_BYTES.name
    """
    The number of Non-persistent bytes received on the ``MessageReceiver``. On the ``MessageService``, it is the total
    number of Non-persistent bytes received across all ``MessageReceiver``."""
    NONPERSISTENT_MESSAGES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_NONPERSISTENT_MSGS.name
    """ The number of Non-persistent messages received on the ``MessageReceiver``. On the ``MessageService``, it is the
    total number of Non-persistent messages received across all ``MessageReceiver``."""
    CONTROL_MESSAGES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_CTL_MSGS.name
    """The number of control (non-data) messages received."""
    CONTROL_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_CTL_BYTES.name
    """The number of bytes received in control (non-data) messages."""
    TOTAL_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_TOTAL_DATA_BYTES.name
    """ The total number of data bytes received. """
    TOTAL_MESSAGES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_TOTAL_DATA_MSGS.name
    """The total number of data messages received."""
    COMPRESSED_BYTES_RECEIVED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_COMPRESSED_BYTES.name
    """The number of bytes received before decompression. """

    TOTAL_BYTES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_TOTAL_DATA_BYTES.name
    """The number of data bytes transmitted in total."""
    TOTAL_MESSAGES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_TOTAL_DATA_MSGS.name
    """The number of data messages transmitted in total. """
    PUBLISHER_WOULD_BLOCK = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_WOULD_BLOCK.name
    """The number of messages not accepted due to would block (non-blocking only)."""
    DIRECT_BYTES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_DIRECT_BYTES.name
    """The number of bytes transmitted in direct messages."""
    DIRECT_MESSAGES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_DIRECT_MSGS.name
    """The number of Direct messages transmitted."""
    PERSISTENT_BYTES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_PERSISTENT_BYTES.name
    """The number of bytes transmitted in persistent messages. """
    NONPERSISTENT_BYTES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_NONPERSISTENT_BYTES.name
    """The number of bytes transmitted in non-persistent messages. """
    PERSISTENT_MESSAGES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_PERSISTENT_MSGS.name
    """The number of persistent messages transmitted. """
    NONPERSISTENT_MESSAGES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_NONPERSISTENT_MSGS.name
    """The number of non-persistent messages transmitted."""
    PERSISTENT_MESSAGES_REDELIVERED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_PERSISTENT_REDELIVERED.name
    """The number of persistent messages redelivered."""
    NONPERSISTENT_MESSAGES_REDELIVERED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_NONPERSISTENT_REDELIVERED.name
    """The number of non-persistent messages redelivered."""
    PERSISTENT_BYTES_REDELIVERED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_PERSISTENT_BYTES_REDELIVERED.name
    """The number of bytes redelivered in persistent messages."""
    NONPERSISTENT_BYTES_REDELIVERED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_NONPERSISTENT_BYTES_REDELIVERED.name
    """The number of bytes redelivered in non-persistent messages."""
    PUBLISHER_ACKNOWLEDGEMENT_RECEIVED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_ACKS_RXED.name
    """The number of acknowledgments received."""
    PUBLISHER_WINDOW_CLOSED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_WINDOW_CLOSE.name
    """The number of times the transmit window closed."""
    PUBLISHER_ACKNOWLEDGEMENT_TIMEOUTS = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_ACK_TIMEOUT.name
    """The number of times the acknowledgment timer expired."""
    CONTROL_MESSAGES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_CTL_MSGS.name
    """The number of control (non-data) messages transmitted. """
    CONTROL_BYTES_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_CTL_BYTES.name
    """The number of bytes transmitted in control (non-data) messages."""
    CONNECTION_ATTEMPTS = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_TOTAL_CONNECTION_ATTEMPTS.name
    """The total number of TCP connections attempted by this ``MessageService``."""
    PUBLISHED_MESSAGES_ACKNOWLEDGED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_GUARANTEED_MSGS_SENT_CONFIRMED.name
    """Guaranteed messages (Persistent/Non-Persistent) published that have been acknowledged."""
    PUBLISH_MESSAGES_DISCARDED = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_DISCARD_CHANNEL_ERROR.name
    """Messages discarded due to channel failure."""

    PUBLISH_MESSAGES_TERMINATION_DISCARDED = 'PUBLISH_MESSAGES_TERMINATION_DISCARDED'
    """Internally buffered published messages count, those which are discarded due to termination event failures
    and also during application initiated termination."""

    RECEIVED_MESSAGES_TERMINATION_DISCARDED = 'RECEIVED_MESSAGES_TERMINATION_DISCARDED'
    """Internally buffered received messages count, those which are discarded due to termination event failures and also
    during application initiated termination. """

    RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED = 'RECEIVED_MESSAGES_BACKPRESSURE_DISCARDED'
    """Received messages discarded by the Python API due to back pressure."""

    INTERNAL_DISCARD_NOTIFICATIONS = 'INTERNAL_DISCARD_NOTIFICATIONS'
    """Received messages with discard notifications."""

    CACHE_REQUESTS_SENT = _SOLCLIENTSTATSTX.SOLCLIENT_STATS_TX_CACHEREQUEST_SENT.name
    """The total number of cache requests that have been sent."""

    CACHE_REQUESTS_SUCCEEDED = "CACHE_REQUESTS_SUCCEEDED"
    """The total number of successful cache request/response paris."""

    CACHE_REQUESTS_FAILED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_CACHEREQUEST_ERROR_RESPONSE.name
    """The total number of failed cache requests"""

    PERSISTENT_MESSSAGES_ACCEPTED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_SETTLE_ACCEPTED.name
    """ Number of messages settled with "ACCEPTED" outcome."""

    PERSISTENT_MESSSAGES_FAILED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_SETTLE_FAILED.name
    """ Number of messages settled with "FAILED" outcome."""

    PERSISTENT_MESSSAGES_REJECTED = _SOLCLIENTSTATSRX.SOLCLIENT_STATS_RX_SETTLE_REJECTED.name
    """ Number of messages settled with "REJECTED" outcome."""


class ApiMetrics(ABC):
    """An abstract class the contains the interfaces to retrieve metrics from a Manageable API."""

    @abstractmethod
    def get_value(self, the_metric: Metric) -> int:
        """Retrieves the metrics current value/count.

        Args:
            the_metric(Metric): The metric to retrieve the value/count for.

        Returns:
              int: The value or count for the specified metric.
        """

    @abstractmethod
    def reset(self):
        """Resets all metrics."""

    @abstractmethod
    def __str__(self):
        """List of all the collected metrics provided by this API.

        Returns:
            str: A string of the metrics that are collected.
        """


class ApiInfo(ABC):
    """
    An interface for access to API build, client, environment, and basic broker information.
    """

    @abstractmethod
    def get_api_build_date(self) -> str:
        """
        Retrieves the API build information (date and time) using the pattern
        pubsubplus-python-client mmm dd yyyy HH:mm:ss / C API mmm dd HH:mm:ss.

        Returns:
            str: The API build timestamp.
        """

    @abstractmethod
    def get_api_version(self) -> str:
        """
        Retrieves the API version inforation using the pattern
        pubsubplus-python-client <semantic version> / C API <semantic version>

        Returns:
            str: The API version information.
        """

    @abstractmethod
    def get_api_user_id(self) -> str:
        """
        Retrieves the API user identifier that was reported to the event broker.
        This information includes the OS user ID of the user running the application,
        the computer name of the machine running the application, and the PID of the process
        running the application.

        Returns:
            str: The API user ID.
        """

    @abstractmethod
    def get_api_implementation_vendor(self) -> str:
        """
        Retrieves the implementation venfor of the API.

        Returns:
            str: The implementation vendor of the API.
        """


class Manageable(ABC):
    """A class interface to get API metrics."""

    @abstractmethod
    def metrics(self) -> ApiMetrics:
        """
        Retrieves the API Metrics as a :py:class:`solace.messaging.utils.manageable.ApiMetrics` object.

        Returns:
            ApiMetrics: The metrics transmitted/received data and events on the MessagingService. """

    @abstractmethod
    def info(self) -> ApiInfo:
        """
        Retrieves the API as an py:class:`ApiInfo<solace.messaging.util.manageable.Manageable.ApiInfo>`.

        Returns:
            ApiInfo: The ApiInfo object.
        """

class TransactionalServiceInfo(ABC):
    """An interface that abstracts access to advanced transactional messaging service information at runtime."""

    @abstractmethod
    def get_transactional_service_id(self) -> Union[str, None]:
        """
          Retrieves transactional service identifier assigned to this transactional service instance on a
          Solace Event Broker during connection establishment. This can also be known as the transacted session name.

          Returns:
            str: The transactional service identifier or None when the TransactionalService was not previously
                connected.
        """
