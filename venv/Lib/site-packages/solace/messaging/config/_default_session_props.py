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

# this module contains the DEFAULT session properties.   # pylint: disable= missing-module-docstring
from solace.messaging.config._ccsmp_property_mapping import CCSMP_SESSION_PROP_MAPPING
from solace.messaging.config._sol_constants import SOLCLIENT_PROP_ENABLE_VAL, SOLCLIENT_PROP_DISABLE_VAL, \
    DEFAULT_RECONNECT_RETRIES
from solace.messaging.config.solace_properties import transport_layer_properties

default_props = {"SESSION_TOPIC_DISPATCH": SOLCLIENT_PROP_ENABLE_VAL,
                 "SESSION_SEND_BLOCKING": SOLCLIENT_PROP_DISABLE_VAL,
                 "SESSION_REAPPLY_SUBSCRIPTIONS": SOLCLIENT_PROP_ENABLE_VAL,
                 "SESSION_IGNORE_DUP_SUBSCRIPTION_ERROR": SOLCLIENT_PROP_ENABLE_VAL,
                 CCSMP_SESSION_PROP_MAPPING[transport_layer_properties.RECONNECTION_ATTEMPTS]:
                     DEFAULT_RECONNECT_RETRIES,
                 "SESSION_GUARANTEED_WITH_WEB_TRANSPORT": SOLCLIENT_PROP_ENABLE_VAL,
                 "SESSION_PUB_WINDOW_SIZE": "255"}
