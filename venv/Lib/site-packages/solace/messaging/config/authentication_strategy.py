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
This module contains the AuthenticationStrategy abstract base class and implementation classes for each
available ``AuthenticationStrategy`` instance available.
"""
import logging
from abc import ABC, abstractmethod

from solace.messaging.config._sol_constants import SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_GSS_KRB
from solace.messaging.config.solace_constants import authentication_constants
from solace.messaging.config.solace_properties import authentication_properties
from solace.messaging.utils._solace_utilities import is_type_matches
from solace.messaging.errors.pubsubplus_client_error import IllegalArgumentError
from solace.messaging.config._solace_message_constants import VALUE_CANNOT_BE_EMPTY

logger = logging.getLogger('solace.messaging')

__all_ = ["AuthenticationStrategy", "BasicUserNamePassword", "ClientCertificateAuthentication", "Kerberos"]


class AuthenticationStrategy(ABC):
    """
    An abstract base class for all authentication strategy classes that include:

    - :py:class:`solace.messaging.config.authentication_strategy.BasicUserNamePassword`
    - :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication`
    """

    @property
    @abstractmethod
    def authentication_configuration(self) -> dict:
        """
        Retrieves the authentication strategy.

        Returns:
         dict: A dictionary with the authentication configuration.
        """


class BasicUserNamePassword(AuthenticationStrategy):
    """
    A concrete class implementation of basic username and password for the authentication strategy.
    """

    def __init__(self, username: str, password: str):  # pragma: no cover # Default credentials may get applied
        logger.debug('[%s] initialized', type(self).__name__)

        self._authentication_configuration = {}
        self._authentication_configuration[authentication_properties.SCHEME_BASIC_USER_NAME] = username
        self._authentication_configuration[authentication_properties.SCHEME_BASIC_PASSWORD] = password
        self._authentication_configuration[
            authentication_properties.SCHEME] = authentication_constants.AUTHENTICATION_SCHEME_BASIC

    @property
    def authentication_configuration(self) -> dict:
        """
        The authentication strategy configuration.

        Returns:
         dict: A dictionary with the authentication configuration.
        """
        return self._authentication_configuration

    @staticmethod
    def of(username: str, password: str) -> 'BasicUserNamePassword':  # pylint: disable=invalid-name
        """
        Creates an instance of :py:class:`BasicUserNamePassword` based on the specified from the ``username``
        and ``password``.

        Args:
            username(str): The user name to use to create a BasicUserNamePassword object.
            password(str): The password to use to create a BasicUserNamePassword object.
        Returns:
            BasicUserNamePassword: The created object.
        """
        is_type_matches(username, str, logger=logger)
        is_type_matches(password, str, logger=logger)
        logger.debug('Authentication Strategy with basic username: [%s] and password: [****]', username)
        return BasicUserNamePassword(username, password)


class ClientCertificateAuthentication(AuthenticationStrategy):
    """
    A concrete class implementation of client certificate authentication for the authentication strategy.
    Client certificate authentication can be used when the client connections to
    the Solace event broker are TLS/SSL-encrypted.

    For a client to use a client certificate authentication scheme, the Solace event broker must
    be properly configured for TLS/SSL connections, and the verification of the client certificate must be
    enabled for the particular Message VPN that the client connects to.
    """

    @property
    def authentication_configuration(self) -> dict:
        """
        The authentication strategy configuration.
        """
        return self._authentication_configuration

    def __init__(self, certificate_file: str, key_file: str, key_password: str):
        logger.debug('[%s] initialized', type(self).__name__)
        self._authentication_configuration = {}
        self._authentication_configuration[authentication_properties.SCHEME] = \
            authentication_constants.AUTHENTICATION_SCHEME_CLIENT_CERT
        self._authentication_configuration[authentication_properties.SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD] = \
            key_password
        self._authentication_configuration[authentication_properties.SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE] = key_file
        self._authentication_configuration[authentication_properties.SCHEME_SSL_CLIENT_CERT_FILE] = certificate_file

    @staticmethod
    def of(certificate_file: str, key_file: str, key_password: str) -> \
            'ClientCertificateAuthentication':  # pylint: disable=invalid-name
        """
        Creates an instance of :py:class:`ClientCertificateAuthentication` from
        the given client certificate configuration.

        Args:
            certificate_file(str):  The file that contains the client certificate or the client-certificate chain.
            key_file(str): The file contains the client private key.
            key_password(str): Password if the private key (key_file) is password protected.

        Returns:
            ClientCertificateAuthentication: The instance of the object.
        """
        logger.debug('Authentication Strategy with Client Certificate Authentication. Certificate: '
                     '[%s], Key: [%s] and Keystore password: [****]', certificate_file, key_file)
        return ClientCertificateAuthentication(certificate_file, key_file, key_password)

    def with_certificate_and_key_pem(self, certificate_pem_file: str) \
            -> 'ClientCertificateAuthentication':
        """
        Set the client certificate or the client-certificate chain, and the client private
        key from a single `.PEM` file.

        Args:
            certificate_pem_file(str): The file that contains the client certificate or the client-certificate chain,
                and the client private key. Both must be PEM-encoded.

        Returns:
            ClientCertificateAuthentication: The instance of the object.
        """
        self._authentication_configuration[authentication_properties.SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE] = \
            certificate_pem_file
        self._authentication_configuration[authentication_properties.SCHEME_SSL_CLIENT_CERT_FILE] = certificate_pem_file
        return self

    def with_private_key_password(self, private_key_password: str) \
            -> 'ClientCertificateAuthentication':  # pragma: no cover
        """
        Sets the password needed to use the client-certificate key file.

        Args:
            private_key_password(str): The password if the file is password-protected.

        Returns:
            ClientCertificateAuthentication: The instance of the object.
        """
        self._authentication_configuration[authentication_properties.SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD] = \
            private_key_password
        logger.debug('Set private key password')
        return self

    def with_user_name(self, username: str) -> 'ClientCertificateAuthentication':
        """
        A method to set the client-username. The broker uses the Common Name in the X.509
        certificate as the client-username for authorization. If the Allow API Provided Username
        (not recommended) feature is enabled on the Message VPN as described here,
        https://docs.solace.com/Configuring-and-Managing/Configuring-Client-Authentication.htm#Allow-API,
        then the client-username configured with this method is used for authorization. In all
        cases authentication is still done by verifying the X.509 certificate is valid and
        signed by a know authority.

        Args:
            username (str): The username string to assign as the global username.

        Returns:
            ClientCertificateAuthentication: The instance of the object with the username configured.
                This object can be used for method chaining.
        """
        is_type_matches(username, str)
        self._authentication_configuration[authentication_properties.SCHEME_CLIENT_CERT_USER_NAME] = username
        return self


class OAuth2(AuthenticationStrategy):
    """
    An implementation of OAuth 2.0 with access token and/or ID token authentication.
    """

    @property
    def authentication_configuration(self) -> dict:
        """
        The authentication configuration.
        """
        return self._authentication_configuration

    def __init__(self, oidc_id_token: str = None, access_token: str = None, issuer_identifier: str = None):
        self._authentication_configuration = {}
        self._authentication_configuration[authentication_properties.SCHEME] = \
            authentication_constants.AUTHENTICATION_SCHEME_OAUTH2
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover
            logger.debug('Added OAuth2 authentication scheme to authentication configuration dictionary.')

        if oidc_id_token is not None:
            self._authentication_configuration[authentication_properties.SCHEME_OAUTH2_OIDC_ID_TOKEN] = oidc_id_token
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover
                logger.debug('Added OIDC ID token to authentication configuration dictionary.')

        if access_token is not None:
            self._authentication_configuration[authentication_properties.SCHEME_OAUTH2_ACCESS_TOKEN] = access_token
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover
                logger.debug('Added access token to authentication configuration dictionary.')

        if issuer_identifier is not None:
            self._authentication_configuration[authentication_properties.SCHEME_OAUTH2_ISSUER_IDENTIFIER] = \
                issuer_identifier
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover
                logger.debug('Added issuer identifier to authentication configuration dictionary.')


    @staticmethod
    def of(access_token: str, oidc_id_token: str, issuer_identifier: str = None) -> 'OAuth2':  # pylint: disable=invalid-name
        """
            Creates an instance of
            :py:class:`OAuth2<solace.messaging.config.authentication_strategy.OAuth2>`
            based on the specified access token, and/or the specified OIDC token,
            and/or the specified issuer identifier. The issuer identifier is optional,
            but at least one of either an OIDC ID token or an access token must be provided.

            Args:
                oidc_id_token(str): The OIDC ID token to be used for OAuth2 authentication. To not use
                    an OIDC ID token for OAuth2 authentication, pass None as the value of this parameter.
                access_token(str): The access token to be used for OAuth2 authentication. To not use
                    an access token for OAuth2 authentication, pass None as the value of this parameter.
                issuer_identifier(str): The issuer identifier.

            Raises:
                IllegalArgumentError: If both tokens are None; or, if one or more of the arguments are
                    an empty string; or, if one or more of the arguments is not a string.

            Returns:
                Oauth2: The created object.
        """

        if oidc_id_token is not None:
            if not is_type_matches(actual=oidc_id_token, expected_type=str, raise_exception=False) \
                or len(oidc_id_token) == 0:

                exception_message = f"{VALUE_CANNOT_BE_EMPTY} for oidc_id_token parameter when instantiating OAuth2 " \
                                    f"authentication strategy."
                logger.error("Encountered error while instantiating OAuth2 authentication strategy: " \
                             "%s", exception_message)
                raise IllegalArgumentError(exception_message)

        if access_token is not None:
            if not is_type_matches(actual=access_token, expected_type=str, raise_exception=False) \
                or len(access_token) == 0:

                exception_message = f"{VALUE_CANNOT_BE_EMPTY} for access_token parameter when instantiating " \
                                    f"OAuth2 authentication strategy."
                logger.error("Encountered error while instantiating OAuth2 authentication strategy: " \
                             "%s", exception_message)
                raise IllegalArgumentError(exception_message)

        if issuer_identifier is not None:
            if not is_type_matches(actual=issuer_identifier, expected_type=str, raise_exception=False) \
                or len(issuer_identifier) == 0:

                exception_message = f"{VALUE_CANNOT_BE_EMPTY} for issuer_identifier parameter when instantiating " \
                                    f"OAuth2 authentication strategy."
                logger.error("Encountered error while instantiating OAuth2 authentication strategy: " \
                             "%s", exception_message)
                raise IllegalArgumentError(exception_message)


        if oidc_id_token is None and access_token is None:
            exception_message = f"{VALUE_CANNOT_BE_EMPTY} for both oidc_id_token and access_token parameters. " \
                                f"At least one must be provided."
            logger.error("Encountered error while instantiating OAuth2 authentication strategy: %s", exception_message)
            raise IllegalArgumentError(exception_message)

        return OAuth2(oidc_id_token=oidc_id_token, access_token=access_token, issuer_identifier=issuer_identifier)

    def with_issuer_identifier(self, issuer_identifier: str) -> 'OAuth2':
        """
        Sets the optional issuer identifier.

        Args:
            issuer_identifier(str): The issuer identifier.

        Raises:
            IllegalArgumentError(Exception): If the issuer identifier is None, is an empty string, or is not a string.

        Returns:
            OAuth2: The instance of the object.
        """
        if issuer_identifier is not None:
            if not is_type_matches(actual=issuer_identifier, expected_type=str, raise_exception=False) \
                or len(issuer_identifier) == 0:

                exception_message = f"{VALUE_CANNOT_BE_EMPTY} for issuer_identifier parameter when instantiating " \
                                    f"OAuth2 authentication strategy."
                logger.error("Encountered error while instantiating OAuth2 authentication strategy: " \
                             "%s", exception_message)
                raise IllegalArgumentError(exception_message)

            self._authentication_configuration[authentication_properties.SCHEME_OAUTH2_ISSUER_IDENTIFIER] = \
                issuer_identifier
            if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover
                logger.debug('Added issuer identifier to authentication configuration dictionary.')
        else:
            exception_message = f"{VALUE_CANNOT_BE_EMPTY} for issuer_identifier parameter when instantiating " \
                                f"OAuth2 authentication strategy."
            logger.error("Encountered error while instantiating OAuth2 authentication strategy: " \
                         "%s", exception_message)
            raise IllegalArgumentError(exception_message)


class AuthenticationConfiguration(ABC):
    """
    An abstract base class that provides the `with_authentication_strategy()` interface for
    the :py:meth:`solace.messaging.message_service.MessagingServiceClientBuilder.build` method.
    """

    @abstractmethod
    def with_authentication_strategy(self, authentication_strategy: AuthenticationStrategy) \
            -> 'AuthenticationConfiguration':
        """
        Specifies the authentication strategy to configure.

        Args:
            authentication_strategy(AuthenticationStrategy): The authentication strategy to use  for connections
                to the Solace event broker.

        Returns:
            AuthenticationConfiguration: The authentication configuration instance that can be used for method chaining.
        """


class Kerberos(ABC):
    """
    A concrete class implementation of Kerberos Authentication for the authentication strategy.
    Kerberos is a protocol for authentication between nodes in a computer network over non-secure lines.
    This protocol relies on a combination of private key encryption and access tickets to safely
    verify user identities.

    To implement Kerberos authentication for clients connecting to a Solace event broker, the following
    configurations are required on an event broker:

    - A Kerberos Keytab must be loaded on the event broker. See Event Broker File Management.
    - Kerberos authentication must be configured and enabled for any Message VPNs that
      Kerberos-authenticated clients will connect to.
    - Optional: On an appliance, a Kerberos Service Principal Name (SPN) can be assigned to the IP address
      for the message backbone VRF Kerberos‑authenticated clients will use.

    Further reference can be found at
        https://docs.solace.com/Configuring-and-Managing/Configuring-Client-Authentication.htm#Config-Kerberos
      """

    @staticmethod
    def of(service_name: str):  # pylint: disable=invalid-name
        """
            Creates an instance of :py:class:`Kerberos` from
            the given client Kerberos service name configuration.

            Args:
                service_name: A Valid Kerberos service name

            Returns:
                Kerberos: The instance of the object.
        """
        is_type_matches(service_name, str, logger=logger)
        return _Kerberos(service_name)

    @staticmethod
    def default():
        """
           Returns:
                Kerberos: The instance of the object with a default Kerberos service.
        """
        return _Kerberos()

    @abstractmethod
    def with_user_name(self, username: str) -> 'Kerberos':
        """
        A method to set the client-username. The broker uses the Kerberos Principal as the
        client-username for authorization. If the Allow API Provided Username (not recommended)
        feature is enabled on the Message VPN as described here,
        https://docs.solace.com/Configuring-and-Managing/Configuring-Client-Authentication.htm#Allow-API-Username,
        then the client-username configured with this method is used for authorization. In all
        cases, authentication is still done by verifying the kerberos token.

        Args:
            username (str): The username string to assign as the global username.

        Returns:
            Kerberos: The instance of the object with the username configured. This object can be used for
            method chaining.
        """


class _Kerberos(AuthenticationStrategy, Kerberos):

    def __init__(self, service_name: str = None):
        self._authentication_configuration = {
            authentication_properties.SCHEME: SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_GSS_KRB}
        if service_name:
            self._authentication_configuration[authentication_properties.KRB_SERVICE_NAME] = service_name

    @property
    def authentication_configuration(self) -> dict:
        return self._authentication_configuration

    def with_user_name(self, username: str) -> 'Kerberos':
        is_type_matches(username, str)
        self._authentication_configuration[authentication_properties.SCHEME_KERBEROS_USER_NAME] = username
        return self
