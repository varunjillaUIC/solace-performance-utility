from solace.messaging.messaging_service import MessagingService
from solace.messaging.config.transport_security_strategy import TLS


class ConnectionManager:

    def __init__(self, host, vpn, username, password):
        self.host = host
        self.vpn = vpn
        self.username = username
        self.password = password

    def connect(self):
        properties = {
            "solace.messaging.transport.host": self.host,
            "solace.messaging.service.vpn-name": self.vpn,
            "solace.messaging.authentication.basic.username": self.username,
            "solace.messaging.authentication.basic.password": self.password
        }

        tls = TLS.create().without_certificate_validation()

        service = MessagingService.builder() \
            .from_properties(properties) \
            .with_transport_security_strategy(tls) \
            .build()

        service.connect()
        return service