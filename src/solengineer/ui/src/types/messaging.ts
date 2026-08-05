export interface Profile {
  name: string;
  host: string;
  vpn: string;
  username: string;
  password: string;
}

export interface Message {
  id: string;
  topic?: string;
  queue?: string;
  message: string;
  timestamp: string;
}

export interface HistoryItem {
  topic: string;
  message: string;
  timestamp: string;
}

export interface ConnectPayload {
  host: string;
  vpn: string;
  username: string;
  password: string;
}

export interface BrokerStatus {
  connected: boolean;
}