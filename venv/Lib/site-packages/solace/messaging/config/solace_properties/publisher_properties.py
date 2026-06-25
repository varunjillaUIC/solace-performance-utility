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


# pylint: disable=trailing-whitespace, disable=trailing-whitespace, disable=line-too-long

"""
This module contains dictionary keys for
:py:class:`solace.messaging.publisher.message_publisher.MessagePublisher` properties. """


PUBLISHER_BACK_PRESSURE_STRATEGY = "solace.messaging.publisher.back-pressure.strategy"
"""
    Property-key to define a back pressure strategy. The acceptable values for this key are:

    - :py:const:`solace.messaging.config.solace_constants.publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_ELASTIC`
    - :py:const:`solace.messaging.config.solace_constants.publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_REJECT_WHEN_FULL` 
    - :py:const:`solace.messaging.config.solace_constants.publisher_constants.PUBLISHER_BACK_PRESSURE_STRATEGY_BUFFER_WAIT_WHEN_FULL`
"""

PUBLISHER_BACK_PRESSURE_BUFFER_CAPACITY = "solace.messaging.publisher.back-pressure.buffer-capacity"
"""Property-key to define back pressure buffer capacity measured in messages. 

  This property is ignored when PUBLISHER_BACK_PRESSURE_STRATEGY_ELASTIC is configured.
"""

PUBLISHER_BACK_PRESSURE_BUFFER_WAIT_TIMEOUT = "solace.messaging.publisher.back-pressure.buffer-wait-timeout"
"""Reserved for future use."""
