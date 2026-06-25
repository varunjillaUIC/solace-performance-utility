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


"""This module contains dictionary keys for
:py:class:`solace.messaging.messaging_service.TransactionalMessagingService`
properties. """  # pylint: disable=line-too-long

TRANSACTIONAL_SERVICE_REQUEST_TIMEOUT = "solace.messaging.transactional.request-timeout"
"""
    Property constant defining the key for configuring the transactional messaging service
    request timeout that affects operation attempts for connect, disconnect, rollback and commit.
    This key may be used in the
    :py:class:`solace.messaging.messaging_service.TransactionalMessagingService` properties
    when configured from a dictionary.
"""
