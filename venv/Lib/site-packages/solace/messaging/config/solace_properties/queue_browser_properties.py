# solace-messaging-python-client
#
# Copyright 2025 Solace Corporation. All rights reserved.
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
This module contains dictionary keys for the :py:class:`solace.messaging.receiver.message_receiver.MessageQueueBrowser`
properties.
"""  # pylint: disable=line-too-long


QUEUE_BROWSER_WINDOW_SIZE = "solace.messaging.queue-browser.persistent.transport-window-size"
""" A property key to specify a maximum number of messages that can be pre-fetched by the queue
    browser. The valid range from 1 to 255, defaulting to 255.

    This property-constant mapping can be used in a dictionary
    configuration object to configure the window size for a queue browser
    through the
    :py:meth:`MessageQueueBrowserBuilder.from_properties()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.from_properties>`
    method.

    This method is an alternative to setting the window size of a queue browser by
    :py:meth:`MessageQueueBrowserBuilder.with_message_selector()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.with_queue_browser_window_size>`.
"""


QUEUE_BROWSER_MESSAGE_SELECTOR_QUERY = "solace.messaging.queue-browser.selector-query"
""" Property constant defining the key for configuring a message-selection query for a queue browser.
    When a selector is applied then the receiver receives only
    messages whose headers and properties match the selector. A message selector cannot select
    messages on the basis of the content of the message body.

    An acceptable value for this property is a string formatted according to
    `Solace Selectors <https://docs.solace.com/Solace-JMS-API/Selectors.htm>`_.

    This property-constant mapping can be used in a dictionary
    configuration object to configure the message-selection query for a queue browser
    through the
    :py:meth:`MessageQueueBrowserBuilder.from_properties()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.from_properties>`
    method.

    This method is an alternative to setting the message-selection
    query of a queue browser by
    :py:meth:`MessageQueueBrowserBuilder.with_message_selector()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.with_message_selector>`.
"""

QUEUE_BROWSER_RECONNECTION_ATTEMPTS = "solace.messaging.queue-browser.reconnection-attempts"
""" Property key to specify the number of times to attempt to reconnect to an endpoint after the
    initial bound flow goes down.

    The valid value range is -1 and up. A value of -1 indicates
    the infinite retry. Setting this property is optional. Defaults to -1.

    This property-constant mapping can be used in a dictionary configuration object to configure the reconnect attempts for a queue browser through the     :py:meth:`MessageQueueBrowserBuilder.from_properties()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.from_properties>` method.
"""


QUEUE_BROWSER_RECONNECTION_ATTEMPTS_WAIT_INTERVAL = "solace.messaging.queue-browser.reconnection-attempts-wait-interval"
""" Property key to specify the time (in ms) to wait between each attempt to reconnect from a
    queue browser to an endpoint.

    The valid value range is 50 and up. Default value is 3000.
    Setting this property is optional.

    This property-constant mapping can be used in a dictionary configuration object to configure the reconnect wait time for a queue browser through the :py:meth:`MessageQueueBrowserBuilder.from_properties()<solace.messaging.builder.message_queue_browser_builder.MessageQueueBrowserBuilder.from_properties>` method.
"""
