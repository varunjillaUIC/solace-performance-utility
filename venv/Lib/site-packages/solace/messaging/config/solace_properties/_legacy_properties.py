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

# pylint: disable=trailing-whitespace, line-too-long, invalid-name
"""This module contains dictionary keys for legacy properties."""

# The pattern is to append to the name of the property the latest
# version of the API before the property was deprecated

_GENERATE_RECEIVE_TIMESTAMPS_v1_0_0 = "solclient.session.prop.generate-rcv-timestamps"  # pylint: disable=invalid-name
"""_GENERATE_RECEIVE_TIMESTAMPS_v1_0_0 may be used as a legacy version of the
:py:const:`GENERATE_RECEIVE_TIMESTAMPS<solace.messaging.config.solace_properties.service_properties.GENERATE_RECEIVE_TIMESTAMPS>` key."""

_GENERATE_SEND_TIMESTAMPS_v1_0_0 = "solclient.session.prop.generate-send-timestamps"  # pylint: disable=invalid-name
"""_GENERATE_SEND_TIMESTAMPS_v1_0_0 may be used as a legacy version of the
:py:const:`GENERATE_SEND_TIMESTAMPS<solace.messaging.config.solace_properties.service_properties.GENERATE_SEND_TIMESTAMPS` key."""

_PERSISTENT_NO_LOCAL_PUBLISHED_MESSAGES_v1_0_0 = "solace.messaging.receiver.persistent.no-local-published-messages"  # pylint: disable=invalid-name
"""_PERSISTENT_NO_LOCAL_PUPLISHED_MESSAGES_v1_0_0 may be used as a legacy version of the
:py:const:`PERSISTENT_NO_LOCAL_PUBLISHED_MESSAGES<solace.messaging.config.solace_properties.receiver_properties.PERSISTENT_NO_LOCAL_PUBLISHED_MESSAGES>`
key."""

_SEQUENCE_NUMBER_v1_0_0 = "solace.messaging.message.sequence-number"  # pylint: disable=invalid-name
"""_SEQUENCE_NUMBER_v1_0_0 can be used as a legacy version of the
:py:const:`SEQUENCE_NUMBER<solace.messaging.config.solace_properties.message_properties.SEQUENCE_NUMBER>` key."""

_CORRELATION_ID_v1_2_0 = "solace.messaging.message.correlationId"
""" _CORRELATION_ID_v1_2_0 can be used as a legacy version of the
:py:const:`CORRELATION_ID<solace.messaging.config.solace_properties.message_properties.CORRELATION_ID>`"""

_SCHEME_BASIC_USER_NAME_v1_2_1 = "solace.messaging.authentication.scheme.basic.username"
"""_SCHEME_BASIC_USER_NAME_v1_2_1 can be used as a legacy version of the
:py:const:`SCHEME_BASIC_USER_NAME<solace.messaging.config.solace_properties.authentication_properties.SCHEME_BASIC_USERNAME>`
"""

_SCHEME_BASIC_PASSWORD_v1_2_1 = "solace.messaging.authentication.scheme.basic.password"
"""_SCHEME_BASIC_PASSWORD_v1_2_1 can be used as a legacy version of the
:py:const`SCHEME_BASIC_PASSWORD<solace.messaging.config.solace_properties.authentication_properties.SCHEME_BASIC_PASSWORD>`
"""

_SCHEME_SSL_CLIENT_CERT_FILE_v1_2_1 = "solace.messaging.authentication.scheme.client-cert-file"
"""_SCHEME_SSL_CLIENT_CERT_FILE_v1_2_1 can be used as a legacy version of the
:py:const`SCHEME_SSL_CLIENT_CERT_FILE<solace.messaging.config.solace_properties.authentication_properties.SCHEME_SSL_CLIENT_CERT_FILE>`
"""

_SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE_v1_2_1 = "solace.messaging.authentication.scheme.client-cert.private-key-file"
"""_SCHEME_SSL_CLIENT_PRIVATE_KEY_FILE_v1_2_1 can be used as a legacy version of the
:py:const`SCHEME_SSL_CLIENT_CERT_PRIVATE_KEY_FILE<solace.messaging.config.solace_properties.authentication_properties.SCHEME_SSL_CLIENT_CERT_PRIVATE_KEY>`
"""

_SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD_v1_2_1 = "solace.messaging.authentication.scheme.client-cert.private-key-password"
"""SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD_v1_2_1 may be used as a legacy version of the
:py:const`SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD<solace.messaging.config.solace_properties.authentication_properties.SCHEME_CLIENT_PRIVATE_KEY_FILE_PASSWORD>`
"""
