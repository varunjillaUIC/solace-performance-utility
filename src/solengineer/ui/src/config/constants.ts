const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const WS_URL   = process.env.REACT_APP_WS_URL  || "ws://localhost:8000";

export const API_BASE = `${BASE_URL}/api`;
export const WS_BASE  = WS_URL;

export const APP_NAME    = "SolEngineer";
export const APP_VERSION = "1.0.0";

export const WS_ENDPOINTS = {
  subscribe: (topic: string)     => `${WS_BASE}/ws/subscribe?topic=${encodeURIComponent(topic)}`,
  queue:     (name: string)      => `${WS_BASE}/ws/queue?queue_name=${encodeURIComponent(name)}`,
  perf:                             `${WS_BASE}/ws/perf`,
} as const;

export const MAX_MESSAGES     = 200;
export const MAX_CHART_POINTS = 60;
export const PERF_TIMEOUT_SEC = 90;