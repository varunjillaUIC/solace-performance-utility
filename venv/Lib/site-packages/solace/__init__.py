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
Solace Messaging API for Python

This package contains a full-featured Python API for developing Python applications. The API follows
the *builder* pattern. Everything begins with a MessagingService.builder() which returns a new
`MessagingServiceClientBuilder` object. With a `MessagingServiceClientBuilder` object, applications can:

- configure a :py:class:`solace.messaging.messaging_service.MessagingService` object
- create a :py:class:`solace.messaging.messaging_service.MessagingService` object

Before the MessagingService is created, global properties can be set by environment variable. The
following environment variables are recognized and handled during API initialization:

- SOLCLIENT_GLOBAL_PROP_GSS_KRB_LIB: GSS (Kerberos) library name. If not set the default value is OS specific

  - Linux/MacOS: libgssapi_krb5.so.2
  - Windows: secur32.dll

- SOLCLIENT_GLOBAL_PROP_SSL_LIB: TLS Protocol libary name. If not set the default value is OS specific:

  - Linux: libssl.so
  - MacOS: libssl.dylib
  - Windows: libssl-1_1.dll

- SOLCLIENT_GLOBAL_PROP_CRYPTO_LIB: TLS Cryptography library name.  If not set the default value is OS specific:

  - Linux: libcrypto.so
  - MacOS: libcrypto.dylib
  - Windows: libcrypto-1_1.dll-

- GLOBAL_GSS_KRB_LIB: Alternate name for SOLCLIENT_GLOBAL_PROP_GSS_KRB_LIB
- GLOBAL_SSL_LIB: Alternate name for SOLCLIENT_GLOBAL_PROP_SSL_LIB
- GLOBAL_CRYPTO_LIB: Alternate name for SOLCLIENT_GLOBAL_PROP_CRYPTO_LIB
"""

import logging.config


def __init():
    from solace.messaging.core._solace_session import CORE_API  # pylint: disable=import-outside-toplevel
    return CORE_API.solclient_core_library

CORE_LIB = __init()
__all__ = ['messaging']
LOG_FILE = "solace_messaging_core_api.log"

SOLACE_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'solace-messaging-formatter': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: [%(filename)s:%(lineno)s]  %(message)s'
        },
        'solace-messaging-core-api-formatter': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: [%(filename)s:%(lineno)s]  %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'NOTSET',  # set to NOTSET to make all level log be handled
            'formatter': 'solace-messaging-formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'core-api': {
            'level': 'NOTSET',  # set to NOTSET to make all level log be handled
            'formatter': 'solace-messaging-core-api-formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        'solace.messaging': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'solace.messaging.publisher': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'solace.messaging.receiver': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'solace.messaging.connections': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'solace.messaging.core': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'solace.messaging.core.api': {
            'handlers': ['core-api'],
            'level': 'WARNING',
            'propagate': False
        }
    }
}

logging.config.dictConfig(SOLACE_LOGGING_CONFIG)
