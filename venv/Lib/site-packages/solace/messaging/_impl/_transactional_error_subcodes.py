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

"""Module contains the CCSMP subcodes pertaining to transactions."""

from solace.messaging.config.sub_code import SolClientSubCode


transactional_subcode_list = [SolClientSubCode.SOLCLIENT_SUBCODE_INVALID_TRANSACTED_SESSION_ID.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_INVALID_TRANSACTION_ID.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_NO_TRANSACTION_STARTED.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_PUBLISHER_NOT_ESTABLISHED.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_TRANSACTION_FAILURE.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_MESSAGE_CONSUME_FAILURE.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_ENDPOINT_MODIFIED.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_INVALID_CONNECTION_OWNER.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_COMMIT_OR_ROLLBACK_IN_PROGRESS.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_MAX_TRANSACTIONS_EXCEEDED.name,
                              SolClientSubCode.SOLCLIENT_SUBCODE_SYNC_REPLICATION_INELIGIBLE.name]
