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


"""This module contains dictionary keys for the :py:class:`solace.messaging.messaging_service.MessagingService`
transport layer properties."""  # pylint: disable=trailing-whitespace, line-too-long

HOST = "solace.messaging.transport.host"
"""Property constant defining the key for configuring the IPv4 or IPv6 address or host name of the 
  Solace event broker to connect to. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  Multiple entries are allowed, separated by commas.
  The entry for the HOST property should provide a protocol, host, and port.
"""

CONNECTION_ATTEMPTS_TIMEOUT = "solace.messaging.transport.connection-attempts-timeout"
"""Property constant defining the key for configuring timeout period (in milliseconds) 
  for a connect operation to a given host. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
"""

CONNECTION_RETRIES = "solace.messaging.transport.connection-retries"
"""Property constant defining the key for configuring connection retries. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
  
  This property dictates how many times to try to connect to the Solace event broker 
  (or list of Solace event brokers) during connection setup.

  Zero means no automatic connection retries (that is, try once and give up). -1 means try to connect forever. 
  The default valid range is value that is greater than or equal to -1.

  When using a host list, each time the API works through the host list without establishing a connection is
  considered a connect retry. For example, if a CONNECTION_RETRIES value of two is used,
  the API could possibly work through all of the listed hosts without connecting to them three times: one time
  through for the initial connect attempt, and then two times through for connect retries.
  Each connect retry begins with the first host listed. After each unsuccessful attempt to connect to a host,
  the API waits for the amount of time set for RECONNECTION_ATTEMPTS_WAIT_INTERVAL before attempting
  another connection to a host, and the number times to attempt to connect to one host before moving on to the
  next listed host is determined by the value set for CONNECTION_RETRIES_PER_HOST.
"""

CONNECTION_RETRIES_PER_HOST = "solace.messaging.transport.connection.retries-per-host"
"""Property constant defining the key for configuring connection retries per host. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  When using a host list, this property defines how many times to try to connect or reconnect to a
  single host before moving to the next host in the list.
"""

RECONNECTION_ATTEMPTS = "solace.messaging.transport.reconnection-attempts"
"""Property constant defining the key for configuring reconnection attempts after an active session
  has failed. 

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  This property dictates how many times to attempt to reconnect to the Solace event broker
  (or list of Solace event brokers) after a connected``MessagingService`` goes down. 

  Zero means no automatic reconnection attempts. -1 means try to reconnect forever. The default valid range is >= -1.

  When using a host list, each time the API works through the host list without establishing a connection is considered a
  reconnect retry. Each reconnect retry begins with the first host listed. After each unsuccessful attempt to reconnect
  to a host, the API waits for the amount of time set for RECONNECTION_ATTEMPTS_WAIT_INTERVAL before attempting another
  connection to a Solace event broker, and the number times to attempt to connect to one Solace event broker before moving on to the
  next listed host is determined by the value set for CONNECTION_RETRIES_PER_HOST.
"""

RECONNECTION_ATTEMPTS_WAIT_INTERVAL = "solace.messaging.transport.reconnection-attempts-wait-interval"
"""Property constant defining the key for configuring reconnection delay after connect or reconnect attempt fails.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.

  This property dictates how much time (in milliseconds) to wait between each attempt to connect or
  reconnect to the configured HOST.

  If a connect or reconnect attempt to the configured HOST (which may be a list) is not successful, the API waits for
  the amount of time set for RECONNECTION_ATTEMPTS_WAIT_INTERVAL, and then makes another connect or reconnect attempt.
  The valid range is greater than or equal to zero."""

KEEP_ALIVE_INTERVAL = "solace.messaging.transport.keep-alive-interval"
"""Property constant defining the key for configuring keep alive timer in milliseconds.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
"""

KEEP_ALIVE_WITHOUT_RESPONSE_LIMIT = "solace.messaging.transport.keep-alive-without-response-limit"
"""Property constant defining the key for configuring maximum number of consecutive Keep-Alive messages
  that can be sent without receiving a response before the connection is closed by the API.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
"""

SOCKET_OUTPUT_BUFFER_SIZE = "solace.messaging.transport.socket.output-buffer-size"
"""Property constant defining the key for configuring the socket send buffer size (in bytes).

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
  
  When this key is assigned the values 0, it indicates the socket send buffer is not set and left at operating
  system default. Otherwise it must have a value greater than or equal to 1024.
"""

SOCKET_INPUT_BUFFER_SIZE = "solace.messaging.transport.socket.input-buffer-size"
"""Property constant defining the key for configuring the socket receive buffer size (in bytes).

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
  
  When this key is assigned the values 0, it indicates the socket receive buffer is not set and left at operating
  system default. Otherwise it must have a value greater than or equal to 1024.
"""

SOCKET_TCP_OPTION_NO_DELAY = "solace.messaging.transport.socket.tcp-option-no-delay"
"""Property constant defining the key for enabling no delay on the transport socket.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary.
"""

COMPRESSION_LEVEL = "solace.messaging.transport.compression-level"
"""Property constant defining the key for message compression.

  This key may be used in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
  when configured from a dictionary. 
  
  When set the API compresses messages with ZLIB before transmission and decompressed on receive.

  This property should preferably be set by
  :py:meth:`MessagingServiceClientBuilder.with_compression_level()
  <solace.messaging.messaging_service.MessagingServiceClientBuilder.with_message_compression>`

  The valid range is 0 (off) or 1..9, where 1 is less compression (fastest) and 9 is most compression (slowest).

  Note: If no port is specified in the HOST property, the API will automatically connect to either the default 
  non-compressed listen port (55555) or default compressed listen port (55003) based on the specified 
  COMPRESSION_LEVEL. If a port is specified in the HOST property you must specify the non-compressed listen port if not 
  using compression (compression level 0) or the compressed listen port if using compression (compression levels 1 to 
  9).
"""
