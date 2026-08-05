import { useState, useRef, useCallback } from "react";
import { PerfResult, PerfConfig, LiveStats } from "../types/index";
import { WS_ENDPOINTS, MAX_CHART_POINTS } from "../config/constants";

interface UsePerfTestOptions {
  onResult?: (r: PerfResult) => void;
  onIngressSample?: (v: number) => void;
  onEgressSample?: (v: number) => void;
  onRunning?: (v: boolean) => void;
  onProgressChange?: (v: number) => void;
  onLiveStatsChange?: (v: LiveStats | null) => void;
  onErrorChange?: (v: string) => void;
  savedResult?: PerfResult | null;
  savedProgress?: number;
  savedLiveStats?: LiveStats | null;
  savedError?: string;
}

export function usePerfTest(opts: UsePerfTestOptions = {}) {
  const {
    onResult, onIngressSample, onEgressSample, onRunning,
    onProgressChange, onLiveStatsChange, onErrorChange,
    savedResult, savedProgress, savedLiveStats, savedError,
  } = opts;

  const [running,    setRunning]    = useState(false);
  const [progress,   setProgressState] = useState(savedProgress ?? 0);
  const [liveStats,  setLiveStatsState] = useState<LiveStats | null>(savedLiveStats ?? null);
  const [result,     setResultState] = useState<PerfResult | null>(savedResult ?? null);
  const [error,      setErrorState]  = useState(savedError ?? "");

  const wsRef = useRef<WebSocket | null>(null);

  const setProgress = (v: number) => { setProgressState(v); onProgressChange?.(v); };
  const setLiveStats = (v: LiveStats | null) => { setLiveStatsState(v); onLiveStatsChange?.(v); };
  const setResult = (v: PerfResult | null) => { setResultState(v); };
  const setError = (v: string) => { setErrorState(v); onErrorChange?.(v); };

  const run = useCallback((config: PerfConfig) => {
    if (wsRef.current) wsRef.current.close();
    setRunning(true);
    setError("");
    setResult(null);
    setProgress(0);
    setLiveStats(null);
    onProgressChange?.(0);
    onLiveStatsChange?.(null);
    onErrorChange?.("");
    onRunning?.(true);

    const ws = new WebSocket(WS_ENDPOINTS.perf);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        target:           config.target,
        target_type:      config.targetType,
        publish_topic:    config.publishTopic,
        message_count:    config.messageCount,
        message_size:     config.messageSize,
        message_template: config.messageTemplate,
        delivery_mode:    config.deliveryMode,
        rate_limit:       config.rateLimit,
        window_size:      config.windowSize,
        queue_type:       config.queueType,
        warmup_count:     config.warmupCount,
        consumer_count:   config.consumerCount,
      }));
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "progress") {
        const stats: LiveStats = {
          tps: data.tps,
          ingress: data.ingress_tps ?? 0,
          elapsed: data.elapsed,
        };
        setProgress(data.percent);
        setLiveStats(stats);
        if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
        if (data.tps !== undefined) onEgressSample?.(data.tps);
      } else if (data.type === "complete") {
        setResult(data.results);
        setRunning(false);
        setProgress(100);
        setLiveStats(null);
        onProgressChange?.(100);
        onLiveStatsChange?.(null);
        onResult?.(data.results);
        onRunning?.(false);
      } else if (data.error) {
        setError(data.error);
        setRunning(false);
        onRunning?.(false);
      }
    };

    ws.onclose = () => { setRunning(false); onRunning?.(false); };
  }, []);

  const stop = useCallback(() => {
    wsRef.current?.close();
    setRunning(false);
    setProgress(0);
    setLiveStats(null);
    onProgressChange?.(0);
    onLiveStatsChange?.(null);
    onRunning?.(false);
  }, []);

  return { running, progress, liveStats, result, error, run, stop };
}