import axios from "axios";
import { Profile } from "./types";

const BASE = "http://localhost:8000/api";

export const checkStatus = () => axios.get(`${BASE}/status`);

export const connect = (data: {
  host: string;
  vpn: string;
  username: string;
  password: string;
}) => axios.post(`${BASE}/connect`, data);

export const disconnect = () => axios.post(`${BASE}/disconnect`);

export const publish = (topic: string, message: string) =>
  axios.post(`${BASE}/publish`, { topic, message });
 
export const getHistory = () => axios.get(`${BASE}/history`);

export const clearHistory = () => axios.delete(`${BASE}/history`);

export const getProfiles = () => axios.get(`${BASE}/profiles`);

export const saveProfile = (profile: Profile) =>
  axios.post(`${BASE}/profiles`, profile);

export const deleteProfile = (name: string) =>
  axios.delete(`${BASE}/profiles/${name}`);

export const runPerf = (
  topic: string,
  message_count: number,
  message_size: number
) => axios.post(`${BASE}/perf`, { topic, message_count, message_size });