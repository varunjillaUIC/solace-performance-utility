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
    This module contains the abstract base class for transport configuration.
    The methods available in the ``TransportProtocolConfiguration`` class must be
    derived classes to permit applications to configure the underlying transport.

 """

from abc import ABC, abstractmethod


class TransportProtocolConfiguration(ABC):
    """An abstract class that provides the configuration for the transport protocol layer configuration.
       The methods in this class must be  derived classes to permit applications to configure
       the underlying transport.
    """

    @abstractmethod
    def with_message_compression(self, compression_factor: int) -> 'TransportProtocolConfiguration':
        """
        Sets the compression level for all messages sent as a messaging service.

        Args:
            compression_factor (int): Enables messages to be compressed with ZLIB before transmission
                and decompressed on receive. The valid  values to use are 0 (off) or 1..9, where 1 is
                least amount of compression (fastest) and 9 is the most amount of compression (slowest).

        Returns:
            TransportProtocolConfiguration: Instance of the transport configuration that
            can be used for method chaining.
        """

    @abstractmethod
    def with_reconnection_retry_strategy(self, strategy: 'RetryStrategy') -> 'TransportProtocolConfiguration':
        """
        Applies the retry strategy related to a reconnection. Reconnection strategy applies when an established
        ``MessagingService`` connection fails and needs to  be reconnected.  If an initial connection fails,
        see :py:meth:`with_connection_retry_strategy`

        Args:
            strategy (RetryStrategy): The retry strategy configuration.

        Returns:
            TransportProtocolConfiguration: Instance of the transport configuration
            that can be used for method chaining.
        """

    @abstractmethod
    def with_connection_retry_strategy(self, strategy: 'RetryStrategy') -> 'TransportProtocolConfiguration':
        """
        Apply strategy related to connection.

        Connection retry strategy applies when initially establishing a MessagingService connection and the
        connection attempt fails.  If an established connection fails,
        see :py:meth:`TransportProtocolConfiguration.with_reconnection_retry_strategy`.

        Args:
            strategy(RetryStrategy): The retry configuration.

        Returns:
            TransportProtocolConfiguration: Instance of the transport configuration
            that can be used for method chaining.
        """

    @abstractmethod
    def with_transport_security_strategy(self, transport_layer_security_strategy: 'TransportSecurityStrategy') \
            -> 'TransportProtocolConfiguration':
        """
        Set the Transport Layer Security (TLS) configuration on the messaging service.

        Args:
            transport_layer_security_strategy (TransportSecurityStrategy): The configuration for the transport
                layer security.

        Returns:
            TransportProtocolConfiguration: Instance of the transport configuration
            that can be used for method chaining.
        """
