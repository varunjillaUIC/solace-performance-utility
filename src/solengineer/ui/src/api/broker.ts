import client from "./client";
import { ConnectPayload, BrokerStatus } from "../types/index";

export const checkStatus = () =>
  client.get<BrokerStatus>("/status");

export const connectBroker = (payload: ConnectPayload) =>
  client.post("/connect", payload);

export const disconnectBroker = () =>
  client.post("/disconnect");

// backward compatibility
export const connect = connectBroker;
export const disconnect = disconnectBroker;