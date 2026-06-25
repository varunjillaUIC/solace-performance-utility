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


"""This module contains dictionary keys for :py:class:`solace.messaging.messaging_service.MessagingService`
transport layer security (TLS) properties."""  # pylint: disable=trailing-whitespace, line-too-long

CERT_VALIDATED = "solace.messaging.tls.cert-validated"
""" Boolean property to enable (default) or disable X.509 certificate validation. When enabled the certificate
received from the Solace event broker is validated by using certificates found in the
TRUST_STORE_PATH.
"""

CERT_REJECT_EXPIRED = "solace.messaging.tls.cert-reject-expired"
"""Boolean property to enable (default) or disable reject of expired certificates. When enabled the certificate
received from the Solace event broker must not be expired.
"""

CERT_VALIDATE_SERVERNAME = "solace.messaging.tls.cert-validate-servername"
"""Boolean property to enable (default) or disable server certificate hostname or IP address validation. When
enabled the certificate received from the Solace event broker must match the host used to connect.
"""

EXCLUDED_PROTOCOLS = "solace.messaging.tls.excluded-protocols"
"""This property is deprecated. Use MINIMUM_PROTOCOL and MAXIMUM_PROTOCOL instead. """

MINIMUM_PROTOCOL = "solace.messaging.tls.minimum-protocol"
"""This property specifies the lowest TLS protocol version to use when connecting to the broker.

Valid protocols are 'TLSv1.1', 'TLSv1.2', and 'TLSv1.3'.
Defaults to TLSv1.2  """

MAXIMUM_PROTOCOL = "solace.messaging.tls.maximum-protocol"
"""This property specifies the highest TLS protocol version to use when connecting to the broker.

Valid protocols are 'TLSv1.1', 'TLSv1.2', and 'TLSv1.3'.
Defaults to empty, meaning highest supported version, safe to leave unset. """

PROTOCOL_DOWNGRADE_TO = "solace.messaging.tls.protocol-downgrade-to"
"""
This property specifies a transport protocol that the SSL connection will be downgradedto after client authentication.

Allowed transport protocol is "PLAIN_TEXT". May be combined with non-zero compression level to achieve compression 
without encryption. """

CIPHER_SUITES = "solace.messaging.tls.cipher-suites"
"""This property specifies a comma separated list of the cipher suites for use with TLSv1.2 and below.
Ignored when TLSv1.3 is negotiated.
Allowed cipher suites are:

+-----------------+-------------------------------+--------------------+
| 'AES256-SHA'    | 'ECDHE-RSA-AES256-SHA'        | 'AES256-GCM-SHA384'| 
+-----------------+-------------------------------+--------------------+
| 'AES256-SHA256' | 'ECDHE-RSA-AES256-GCM-SHA384' | 'AES128-SHA256'    |
+-----------------+-------------------------------+--------------------+
| 'DES-CBC3-SHA'  | 'ECDHE-RSA-DES-CBC3-SHA'      |                    |
+-----------------+-------------------------------+--------------------+
| 'RC4-SHA'       | 'ECDHE-RSA-AES256-SHA384'     | 'AES128            |
+-----------------+-------------------------------+--------------------+
| 'ECDHE-RSA-AES128-SHA256'                       | 'AES128-GCM-SHA256'|
+-----------------+-------------------------------+--------------------+
| 'RC4-MD5'       | 'ECDHE-RSA-AES128-GCM-SHA256' |                    |   
+-----------------+----------------------+--------+--------------------+ 
| 'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384'| 'ECDHE-RSA-AES128-SHA'      |
+----------------------------------------+-----------------------------+    
| 'TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384'|                             |
+----------------------------------------+-----------------------------+ 
| 'TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA'   |                             |
+----------------------------------------+-----------------------------+ 
| 'TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA'  |                             |
+----------------------------------------+-----------------------------+ 
| 'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256'|                             |
+----------------------------------------+-----------------------------+  
| 'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA'   |                             |
+----------------------------------------+-----------------------------+  
| 'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256'|                             |
+-----------------------------------+----+-----------------------------+ 
| 'TLS_RSA_WITH_AES_128_GCM_SHA256' |                                  | 
+-----------------------------------+----------------------------------+ 
| 'TLS_RSA_WITH_AES_128_CBC_SHA256' |'TLS_RSA_WITH_AES_256_GCM_SHA384' |
+-----------------------------------+----------------------------------+ 
| 'TLS_RSA_WITH_AES_256_CBC_SHA256' | 'TLS_RSA_WITH_AES_256_CBC_SHA'   | 
+-----------------------------------+----------------------------------+ 
| 'SSL_RSA_WITH_3DES_EDE_CBC_SHA    | 'TLS_RSA_WITH_AES_128_CBC_SHA'   | 
+-----------------------------------+----------------------------------+ 
| 'SSL_RSA_WITH_RC4_128_SHA'        | 'SSL_RSA_WITH_RC4_128_MD5'       |  
+-----------------------------------+----------------------------------+ 
"""

TRUST_STORE_PATH = "solace.messaging.tls.trust-store-path"
"""This property specifies the directory where the trusted certificates are.
The maximum depth for the certificate chain verification that shall be allowed is 3."""

TRUSTED_COMMON_NAME_LIST = "solace.messaging.tls.trusted-common-name-list"
"""
This property is provided for legacy installations and is not recommended as part of best practices.  The API performs
Subject Alternative Name verification when the Subject Alternative Name is found in the server certificate which 
is generally the best practice for a secure connection.  
 
This property specifies a comma separated list of acceptable common names in certificate validation. The number of
common names specified by an applications is limited to 16. Leading and trailing whitespaces are considered to be
part of the common names and are not ignored. 
If the application does not provide any common names, there is no common name verification."""
