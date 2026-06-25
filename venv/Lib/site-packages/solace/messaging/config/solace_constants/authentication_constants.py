# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# pylint: disable=trailing-whitespace, line-too-long

"""
This module contains the acceptable dictionary values for the keys found in
:py:mod:`solace.messaging.config.solace_properties.authentication_properties`.
These keys are used to configure the properties of
:py:class:`solace.messaging.config.authentication_strategy.AuthenticationStrategy`."""

from solace.messaging.config._sol_constants import SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_BASIC, \
    SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE, \
    SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_GSS_KRB, \
    SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_OAUTH2

AUTHENTICATION_SCHEME_BASIC = SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_BASIC
"""
This is an acceptable value for the authentication strategy property
:py:const:`SCHEME<solace.messaging.config.solace_properties.authentication_properties.SCHEME>`.
"""

AUTHENTICATION_SCHEME_CLIENT_CERT = SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE
"""
This is an acceptable value for the authentication strategy property
:py:const:`SCHEME<solace.messaging.config.solace_properties.authentication_properties.SCHEME>`.
"""

AUTHENTICATION_SCHEME_KERBEROS = SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_GSS_KRB
"""
This is an acceptable value for the authentication strategy property. This scheme indicates Kerberos authentication.
:py:const:`SCHEME<solace.messaging.config.solace_properties.authentication_properties.SCHEME>`.
"""

AUTHENTICATION_SCHEME_OAUTH2 = SOLCLIENT_SESSION_PROP_AUTHENTICATION_SCHEME_OAUTH2
"""
This is an acceptable value for the authentication strategy property
:py:const:`SCHEME<solace.messaging.config.solace_properties.authentication_properties.SCHEME>`.
This scheme indicates OAuth2 authentication.
"""
