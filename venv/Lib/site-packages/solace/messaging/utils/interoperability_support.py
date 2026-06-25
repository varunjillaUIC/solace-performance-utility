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
This module contains the interface definition for messaging interoperability.

A Solace event broker supports many messaging protocols. When acting as a gateway
from one protocol to another, there may be messaging headers that need to be carried in
the messaging metadata.

One such protocol is REST. When you use the Solace Messaging API for Python to receive messages that were
originally published by a REST publisher, it may be necessary to know the original HTTP content-type
or HTTP content-encoding which that is available for these interfaces.

"""
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger('solace.messaging.receiver')


class RestInteroperabilitySupport(ABC):
    """This class contains the methods to retrieve REST metadata."""

    @abstractmethod
    def get_http_content_type(self) -> str:
        """
        Retrieves the HTTP content type header value from message originally published by a REST client.

        Returns:
            str: The HTTP content-type or None if no content-type is present.
        """

    @abstractmethod
    def get_http_content_encoding(self) -> str:
        """
        Retrieves the HTTP content encoding value from message originally published by a REST client.

        Returns:
            str: HTTP content encoding(str) or None if the encoding is not present.
        """


class InteroperabilitySupport(ABC):
    """
        The base class for providing the methods related to the REST metadata.
    """

    @abstractmethod
    def get_rest_interoperability_support(self) -> 'RestInteroperabilitySupport':
        """
         Retrieves access to the optional metadata used for interoperability with REST messaging clients.

        Returns:
            RestInteroperabilitySupport: The metadata collection or None if not set.
        """
