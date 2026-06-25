

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

export interface PerfResult {
  target: string;
  target_type: string;
  delivery_mode: string;
  rate_limit: number;
  window_size: number | null;
  message_count: number;
  message_size_bytes: number;
  sent: number;
  received: number;
  errors: number;
  total_time_sec: number;
  throughput_msg_per_sec: number;
  avg_latency_ms: number;
  min_latency_ms: number;
  max_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  throughput_samples: number[];
}