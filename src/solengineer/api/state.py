from solengineer.core.connection_manager import ConnectionManager
from solace.messaging.messaging_service import MessagingService
from solace.messaging.config.transport_security_strategy import TLS
import logging

logging.getLogger("solace.messaging.core").setLevel(logging.ERROR)

solace_service = None
_connect_params = {}


def init_service(host: str, vpn: str, username: str, password: str):
    global solace_service, _connect_params
    _connect_params = {
        "host": host, "vpn": vpn,
        "username": username, "password": password
    }
    conn = ConnectionManager(host, vpn, username, password)
    solace_service = conn.connect()


def get_service():
    global solace_service
    if solace_service is None:
        return None
    # Auto-reconnect if session dropped
    try:
        if not solace_service.is_connected:
            _reconnect()
    except Exception:
        _reconnect()
    return solace_service


def _reconnect():
    global solace_service
    if not _connect_params:
        return
    try:
        conn = ConnectionManager(**_connect_params)
        solace_service = conn.connect()
        print("🔄 Reconnected to Solace broker")    
    except Exception as e:
        print(f"❌ Reconnect failed: {e}")
        solace_service = None


def disconnect():
    global solace_service
    if solace_service:
        try:
            solace_service.disconnect()
        except Exception:
            pass
        solace_service = None