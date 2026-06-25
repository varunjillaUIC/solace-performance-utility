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

# pylint: disable=line-too-long
""" This module contains the dictionary keys for :py:class:`solace.messaging.messaging_service.MessagingService`
authentication properties """   # pylint: disable=trailing-whitespace

SCHEME = "solace.messaging.authentication.scheme"
"""SCHEME can be used as a key in the :py:class:`solace.messaging.messaging_service.MessagingService` properties 
when configured from a dictionary.  

Although the SCHEME can be set in
:py:meth:`MessagingServiceClientBuilder.from_properties()<solace.messaging.messaging_service.MessagingServiceClientBuilder.from_properties>`
it is preferable to use 
:py:meth:`MessagingServiceClientBuilder.with_authentication_strategy()<solace.messaging.messaging_service.MessagingServiceClientBuilder.with_authentication_strategy>`
to avoid these internal details. 

The value in the dictionary can be one of:

  - :py:const:`AUTHENTICATION_SCHEME_BASIC<solace.messaging.config.solace_constants.authentication_constants.AUTHENTICATION_SCHEME_BASIC>`: 
    Authenticate with username and password, equivalent to
    :py:class:`solace.messaging.config.authentication_strategy.BasicUserNamePassword`

  - :py:const:`AUTHENTICATION_SCHEME_CLIENT_CERT<solace.messaging.config.solace_constants.authentication_constants.AUTHENTICATION_SCHEME_CLIENT_CERT>`:
    Authenticate with a X509 Client Certificate, equivalent to
    :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication`
  
  - :py:const:`AUTHENTICATION_SCHEME_KERBEROS<solace.messaging.config.solace_constants.authentication_constants.AUTHENTICATION_SCHEME_KERBEROS>`:
    Authenticate with Kerberos authentication protocol, equivalent to
    :py:class:`solace.messaging.config.authentication_strategy.Kerberos`

"""

SCHEME_BASIC_USER_NAME = "solace.messaging.authentication.basic.username"
"""SCHEME_BASIC_USER_NAME can be used as a key in the 
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This 
property is only used if :py:class:`solace.messaging.config.authentication_strategy.BasicUserNamePassword` 
strategy is chosen. """

SCHEME_BASIC_PASSWORD = "solace.messaging.authentication.basic.password"
"""SCHEME_BASIC_PASSWORD can be used as a key in the 
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This 
property is only used if :py:class:`solace.messaging.config.authentication_strategy.BasicUserNamePassword` 
strategy is chosen. """

SCHEME_KERBEROS_USER_NAME = "solace.messaging.authentication.kerberos.username"
"""SCHEME_KERBEROS_USER_NAME can be used as a key in the
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This
property is only used if :py:class:`solace.messaging.config.authentication_strategy.Kerberos` strategy is chosen.
This property is ignored by default and only needed if the 'allow-api-provided-username' is enabled in the
configuration of the message-vpn in the broker. This property is not recommended."""

SCHEME_CLIENT_CERT_USER_NAME = "solace.messaging.authentication.client-cert.username"
"""SCHEME_CLIENT_CERT_USER_NAME can be used as a key in the
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This
property is only used if :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication`
strategy is chosen. This property is ignored by default and only needed if the 'allow-api-provided-username'
is enabled in the configuration of the message-vpn in the broker. This property is not recommended."""

SCHEME_SSL_CLIENT_CERT_FILE = "solace.messaging.authentication.client-cert.file"
"""SCHEME_SSL_CLIENT_CERT_FILE can be used as a key in the 
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This 
property is only used if :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication`
strategy is chosen. """

SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE = "solace.messaging.authentication.client-cert.private-key-file"
"""SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE can be used as a key in the 
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This 
property is only used if :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication`
strategy is chosen. """

SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD = "solace.messaging.authentication.client-cert.private-key-password"
"""SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD may be used as a key in the 
:py:class:`solace.messaging.messaging_service.MessagingService` properties when configured from a dictionary. This 
property is only used if :py:class:`solace.messaging.config.authentication_strategy.ClientCertificateAuthentication` 
strategy is chosen. """

SCHEME_OAUTH2_ACCESS_TOKEN = "solace.messaging.authentication.oauth2.access-token"
"""SCHEME_OAUTH2_ACCESS_TOKEN can be used as a key in the
:py:class:`MessagingService<solace.messaging.messaging_service.MessagingService>` properties when configured from a
dictionary. This property is only used if the 
:py:class:`OAuth2<solace.messaging.config.authentication_strategy.OAuth2>`
authentication strategy is chosen."""

SCHEME_OAUTH2_ISSUER_IDENTIFIER = "solace.messaging.authentication.oauth2.issuer-identifier"
"""SCHEME_OAUTH2_ISSUER_IDENTIFIER can be used as a key in the
:py:class:`MessagingService<solace.messaging.messaging_service.MessagingService>` properties when configured from a
dictionary. This property is only used if the
:py:class:`OAuth2<solace.messaging.config.authentication_strategy.OAuth2>`
authentication strategy is chosen."""

SCHEME_OAUTH2_OIDC_ID_TOKEN = "solace.messaging.authentication.oauth2.oidc-id-token"
"""SCHEME_OAUTH2_OIDC_ID_TOKEN can be used as a key in the
:py:class:`MessagingService<solace.messaging.messaging_service.MessagingService>` properties when configured from a
dictionary. This property is only used if the
:py:class:`OAuth2<solace.messaging.config.authentication_strategy.OAuth2>`
authentication strategy is chosen."""

KRB_SERVICE_NAME = "solace.messaging.authentication.kerberos.instance-name"
# pylint: disable=anomalous-backslash-in-string
""" This property specifies the first part of Kerberos Service Principal Name (SPN) of the
 form ServiceName/Hostname\@REALM (for Windows) or Host Based Service of the form 
 ServiceName\@Hostname (for Linux and SunOS).
"""
