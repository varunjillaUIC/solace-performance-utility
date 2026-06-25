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

# pylint: disable=invalid-name
""" This module contains abstract base class for strategies for transport security and its concrete implementations.

The following implementations of TransportSecurityStrategy exist:

- :py:class:`TLS`
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum

from solace.messaging.config.solace_properties.transport_layer_security_properties import CERT_VALIDATED, \
    EXCLUDED_PROTOCOLS, MINIMUM_PROTOCOL, MAXIMUM_PROTOCOL, PROTOCOL_DOWNGRADE_TO, TRUST_STORE_PATH, \
    CERT_REJECT_EXPIRED, CERT_VALIDATE_SERVERNAME, \
    TRUSTED_COMMON_NAME_LIST, CIPHER_SUITES
from solace.messaging.errors.pubsubplus_client_error import InvalidDataTypeError

logger = logging.getLogger('solace.messaging')


class TransportSecurityStrategy(ABC):
    """
    An abstract class to represent a transport security strategy.

    This class exists to provide a common interface class for all ``TransportSecurityStrategy`` objects.
    """

    @property
    @abstractmethod
    def security_configuration(self) -> dict:
        """Retrieves the security configuration.

        Returns:
            dict: A dictionary object containing the TLS configuration method to get the security configuration"""


class TLS(TransportSecurityStrategy):
    """A concrete class derived from :py:class:`TransportSecurityStrategy` and extended to support TLS configuration."""

    def __init__(self):
        logger.debug('[%s] initialized', type(self).__name__)
        self._security_configuration = {}
        self._security_configuration[CERT_VALIDATED] = True

    class SecureProtocols(Enum):
        """
        The enumeration of TLS protocol versions.
        """

        SSLv3 = "SSLv3"
        """
        Deprecated, do not use.
        """

        TLSv1 = "TLSv1"
        """
        Deprecated, do not use.
        """

        TLSv1_1 = "TLSv1.1"
        """
        TLS protocol version 1.1. Avoid if possible.
        """

        TLSv1_2 = "TLSv1.2"
        """
        TLS protocol version 1.2.
        """

        TLSv1_3 = "TLSv1.3"
        """
        TLS protocol version 1.3.
        """


    @staticmethod
    def create() -> 'TLS':
        """ Creates a TLS instance.

        Returns:
            TLS: An transport layer security object.
        """
        logger.debug('Create TLS')
        return TLS()

    @property
    def security_configuration(self) -> dict:
        """
        Retrieves the security configuration.

        Returns:
            dict: A dictionary with the security configuration.
        """
        logger.debug('Get [%s] security configuration', type(self).__name__)
        return self._security_configuration

    def with_excluded_protocols(self, *args: SecureProtocols) -> 'TLS':
        """
        Deprecated, use with_minimum_version and with_maximum_version instead.

        Specifies the list of SSL or TLS protocols not to use.

        Args:
            args (SecureProtocols): The SSL or TLS protocols to not use.

        Returns:
            TLS: A transport layer security object with the excluded protocols.
        """
        if all(isinstance(x, TLS.SecureProtocols) for x in args):
            exclude_protocols = ",".join([protocols.value for protocols in args])
            self._security_configuration[EXCLUDED_PROTOCOLS] = exclude_protocols

            logger.debug('Set [%s] with excluded protocols', type(self).__name__)
            return self
        raise InvalidDataTypeError(f"Expected to receive instance of {TLS.SecureProtocols}", )

    def with_minimum_protocol(self, protocol: SecureProtocols) -> 'TLS':
        """

        Specifies the oldest TLS protocol to use.

        Args:
            protocol (SecureProtocols): The lowest TLS protocol version to use.

        Returns:
            TLS: The transport layer security object for method chaining.
        """
        if isinstance(protocol, TLS.SecureProtocols):
            self._security_configuration[MINIMUM_PROTOCOL] = protocol.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Set [%s] with minimum protocol', type(self).__name__)
            return self
        logger.warning("with_minimum_protocol argument not a SecureProtocol: %s", protocol)
        raise InvalidDataTypeError(f"Expected to receive instance of {TLS.SecureProtocols}", )

    def with_maximum_protocol(self, protocol: SecureProtocols) -> 'TLS':
        """

        Specifies the newest TLS protocol to use.

        Args:
            protocol (SecureProtocols): The highest TLS protocol version to use.

        Returns:
            TLS: The transport layer security object for method chaining.
        """
        if isinstance(protocol, TLS.SecureProtocols):
            self._security_configuration[MAXIMUM_PROTOCOL] = protocol.value
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
                logger.debug('Set [%s] with maximum protocol', type(self).__name__)
            return self
        logger.warning("with_minimum_protocol argument not a SecureProtocol: %s", protocol)
        raise InvalidDataTypeError(f"Expected to receive instance of {TLS.SecureProtocols}", )

    def downgradable(self) -> 'TLS':
        """
        Configures TLS so that session connection is downgraded to plain text after client
        authentication.

        WARNING:
            Downgrading SSL to plain-text after after client authentication exposes a client and the data being sent
            to higher security risks.

        Returns:
            TLS: A transport layer security object for method chaining.
        """
        self._security_configuration[PROTOCOL_DOWNGRADE_TO] = "PLAIN_TEXT"

        logger.debug('[%s]: Downgrade protocol to plain text', type(self).__name__)
        return self

    def without_certificate_validation(self) -> 'TLS':
        """
        Configures TLS not to validate server certificates.

        WARNING:
            If you disable certificate validation, it exposes clients and data being sent to
            higher security risks.

        Returns:
           TLS: A transport layer security object for method chaining.
        """
        self._security_configuration[CERT_VALIDATED] = False
        logger.debug('[%s]: Without certificate validation', type(self).__name__)
        return self

    def with_certificate_validation(self, ignore_expiration: bool,
                                    validate_server_name: bool = True,
                                    trust_store_file_path: str = None, trusted_common_name_list: str = None) -> 'TLS':
        """
        Configures TLS validation on certificates. By default validation is performed.

        WARNING:
            If you disable certificate validation, it exposes clients and data being sent to higher security risks.

        Args:
            ignore_expiration (bool): When set to True, then expired certificate will be accepted. It is important
              to note that ignoring expired certificates exposes a client and data being sent to higher security risks.
            validate_server_name(bool): When set to True, then certificates without the matching host will not be
             accepted.
            trust_store_file_path (str): The location of the trust store files.
            trusted_common_name_list: Specifies a comma-delimited list of acceptable common names for matching
              with server certificates.
              The API performs a case-insensitive comparison of the common names provided in this property with
              the common name in the server certificate.
              Note that leading and trailing whitespaces are considered to be part of the common names and are
              not ignored.

        Returns:
            TLS: A transport layer security object for method chaining.
        """
        self._security_configuration[CERT_REJECT_EXPIRED] = not ignore_expiration
        self._security_configuration[CERT_VALIDATE_SERVERNAME] = validate_server_name
        if trust_store_file_path:
            self._security_configuration[TRUST_STORE_PATH] = trust_store_file_path
        if trusted_common_name_list:
            self._security_configuration[TRUSTED_COMMON_NAME_LIST] = trusted_common_name_list
        self._security_configuration[CERT_VALIDATED] = True

        logger.debug('[%s]: With certificate validation. Trust store file path: %s',
                     type(self).__name__, trust_store_file_path)
        return self

    def with_cipher_suites(self, cipher_suites_list: str) -> 'TLS':
        """
        Configures cipher suites. The cipher suites value list must be from the
        :py:meth:`solace.messaging.config.solace_properties.CIPHER_SUITES`.

        Args:
            cipher_suites_list (str): The list of the cipher suites.

        Returns:
            TLS: A transport layer security object for method chaining.
         """
        self._security_configuration[CIPHER_SUITES] = cipher_suites_list
        logger.debug('[%s]: With cipher suites. Cipher suites list: [%s]', type(self).__name__, cipher_suites_list)
        return self
