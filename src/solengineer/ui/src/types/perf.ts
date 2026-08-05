export interface PerfResult {
  target: string;
  target_type: string;
  publish_topic: string;
  queue_type: string | null;
  consumer_count: number;
  delivery_mode: string;
  rate_limit: number;
  window_size: number | null;
  message_count: number;
  message_size_bytes: number;
  warmup_count: number;
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
  warmup_avg_ms: number | null;
  warmup_max_ms: number | null;
  ingress_samples: number[];
  throughput_samples: number[];
}

export interface PerfConfig {
  target: string;
  targetType: "topic" | "queue";
  publishTopic: string;
  deliveryMode: "direct" | "persistent";
  queueType: "exclusive" | "non_exclusive";
  messageCount: number;
  messageSize: number;
  messageTemplate: string;
  rateLimit: number;
  windowSize: number;
  warmupCount: number;
  consumerCount: number;
}

export type LiveStats = {
  tps: number;
  ingress: number;
  elapsed: number;
};