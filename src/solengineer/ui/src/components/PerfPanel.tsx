
import { useState, useRef } from "react";
import { PerfResult } from "../types";
import { IconPerf, IconStop, IconExport } from "./Icons";

const TEMPLATES = [
  { label: "Raw payload", value: "" },
  { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
  { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
  { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
  { label: "Custom", value: "custom" },
];

export default function PerfPanel() {
  const [target, setTarget] = useState("perf/test");
  const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
  const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
  const [count, setCount] = useState(1000);
  const [size, setSize] = useState(256);
  const [rateLimit, setRateLimit] = useState(0);
  const [windowSize, setWindowSize] = useState(50);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [customTemplate, setCustomTemplate] = useState("");
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [liveStats, setLiveStats] = useState<{ tps: number; elapsed: number } | null>(null);
  const [result, setResult] = useState<PerfResult | null>(null);
  const [error, setError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

  const handleRun = () => {
    if (wsRef.current) wsRef.current.close();
    setRunning(true);
    setError("");
    setResult(null);
    setProgress(0);
    setLiveStats(null);

    const ws = new WebSocket("ws://localhost:8000/ws/perf");
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        target, target_type: targetType,
        message_count: count, message_size: size,
        message_template: effectiveTemplate,
        delivery_mode: deliveryMode,
        rate_limit: rateLimit,
        window_size: windowSize
      }));
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "progress") {
        setProgress(data.percent);
        setLiveStats({ tps: data.tps, elapsed: data.elapsed });
      } else if (data.type === "complete") {
        setResult(data.results);
        setRunning(false);
        setProgress(100);
      } else if (data.error) {
        setError(data.error);
        setRunning(false);
      }
    };

    ws.onclose = () => setRunning(false);
  };

  const handleStop = () => {
    wsRef.current?.close();
    setRunning(false);
    setProgress(0);
    setLiveStats(null);
  };

  const handleExport = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `solengineer-perf-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={s.page}>
      <div style={s.topbar}>
        <div style={s.topbarLeft}>
          <span style={s.pageTitle}>SDK Performance Test</span>
          {running && <span style={s.tagAmber}>● Running</span>}
          {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
        </div>
        <div style={s.topbarRight}>
          {result && (
            <button style={s.btnGhost} onClick={handleExport}>
              <IconExport color="#5a6675" /> Export JSON
            </button>
          )}
        </div>
      </div>

      <div style={s.body}>
        <div style={s.card}>
          <div style={s.cardTitle}>Configuration</div>

          <div style={s.grid2}>
            <div style={s.fieldGroup}>
              <div style={s.label}>Target Type</div>
              <div style={s.toggleRow}>
                {(["topic", "queue"] as const).map((t) => (
                  <button key={t} onClick={() => setTargetType(t)}
                    style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
                    {t === "topic" ? "📡 Topic" : "📦 Queue"}
                  </button>
                ))}
              </div>
            </div>
            <div style={s.fieldGroup}>
              <div style={s.label}>Delivery Mode</div>
              <div style={s.toggleRow}>
                {(["direct", "persistent"] as const).map((m) => (
                  <button key={m} onClick={() => setDeliveryMode(m)}
                    style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
                    {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div style={s.grid2}>
            <div style={s.fieldGroup}>
              <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
              <input style={s.input} value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
            </div>
            <div style={s.fieldGroup}>
              <div style={s.label}>Message Template</div>
              <select style={s.select} value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}>
                {TEMPLATES.map((t) => (
                  <option key={t.label} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={s.grid2}>
            <div style={s.fieldGroup}>
              <div style={s.label}>Message Count</div>
              <input style={s.input} type="number" value={count}
                onChange={(e) => setCount(Number(e.target.value))} />
            </div>
            <div style={s.fieldGroup}>
              <div style={s.label}>Message Size (bytes)</div>
              <input style={s.input} type="number" value={size}
                onChange={(e) => setSize(Number(e.target.value))} />
            </div>
          </div>

          <div style={s.grid2}>
            <div style={s.fieldGroup}>
              <div style={s.label}>Rate Limit (msg/sec)</div>
              <input style={s.input} type="number" value={rateLimit}
                onChange={(e) => setRateLimit(Number(e.target.value))}
                placeholder="0 = unlimited" />
              <div style={s.hint}>0 = send as fast as possible</div>
            </div>
            <div style={s.fieldGroup}>
              <div style={s.label}>
                Window Size {deliveryMode === "direct" && <span style={s.disabledTag}>(persistent only)</span>}
              </div>
              <input
                style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
                type="number"
                value={windowSize}
                disabled={deliveryMode === "direct"}
                onChange={(e) => setWindowSize(Number(e.target.value))}
              />
              <div style={s.hint}>Max unacknowledged messages in-flight</div>
            </div>
          </div>

          {selectedTemplate === "custom" && (
            <div style={s.fieldGroup}>
              <div style={s.label}>
                 Custom Message Content {/*— use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"} */}
              </div>
              <input style={s.input} value={customTemplate}
                onChange={(e) => setCustomTemplate(e.target.value)}
                placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
            </div>
          )}

          {selectedTemplate !== "" && selectedTemplate !== "custom" && (
            <div style={s.preview}>
              <span style={s.previewLabel}>Preview: </span>
              <span style={s.previewValue}>
                {selectedTemplate
                  .replace("{{index}}", "42")
                  .replace("{{timestamp}}", "1741234567890")
                  .replace("{{random}}", "xKpQmRnL")}
              </span>
            </div>
          )}

          {error && <div style={s.errorBox}>{error}</div>}

          <div>
            {!running
              ? (
                <button style={s.btnPrimary} onClick={handleRun}>
                  <IconPerf color="#fff" size={13} /> Run Perf Test
                </button>
              ) : (
                <button style={s.btnDanger} onClick={handleStop}>
                  <IconStop color="#fff" size={13} /> Stop Test
                </button>
              )
            }
          </div>
        </div>

        {running && (
          <div style={s.card}>
            <div style={s.progressHeader}>
              <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
              {liveStats && (
                <span style={s.liveStatText}>
                  {liveStats.tps} msg/s · {liveStats.elapsed}s elapsed
                </span>
              )}
            </div>
            <div style={s.progressTrack}>
              <div style={{ ...s.progressFill, width: `${progress}%` }} />
            </div>
          </div>
        )}

        {result && (
          <div style={s.card}>
            <div style={s.cardTitle}>Results</div>
            <div style={s.badgeRow}>
              <span style={s.resultBadge}>
                {result.target_type === "topic" ? "📡" : "📦"} {result.target}
              </span>
              <span style={s.resultBadge}>
                {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
              </span>
              {result.rate_limit > 0 && (
                <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
              )}
              {result.window_size && (
                <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
              )}
            </div>
            <div style={s.statsGrid}>
              <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
              <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
              <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
              <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
              <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
              <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
              <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
              <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
              <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
              <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
            </div>

            {result.throughput_samples && result.throughput_samples.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div style={s.label}>Throughput over time (msg/s)</div>
                <ThroughputChart samples={result.throughput_samples} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, highlight }: {
  label: string; value: string; unit: string; highlight?: boolean;
}) {
  return (
    <div style={{
      background: "#f5f7fa",
      border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
      borderRadius: 8, padding: "12px 14px"
    }}>
      <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
      <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
        {value}
        <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>{unit}</span>
      </div>
    </div>
  );
}

function ThroughputChart({ samples }: { samples: number[] }) {
  const max = Math.max(...samples, 1);
  const W = 600;
  const H = 80;
  const pts = samples.map((v, i) => {
    const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
    const y = H - (v / max) * (H - 8);
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`}
      style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 8 }}>
      <polyline points={pts} fill="none" stroke="#1a73e8" strokeWidth="2" />
      {samples.map((v, i) => (
        <circle key={i}
          cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
          cy={H - (v / max) * (H - 8)}
          r="3" fill="#1a73e8" />
      ))}
    </svg>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
  topbar: {
    height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
    display: "flex", alignItems: "center", padding: "0 20px",
    justifyContent: "space-between", flexShrink: 0
  },
  topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
  topbarRight: { display: "flex", alignItems: "center", gap: 8 },
  pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
  tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
  tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
  btnGhost: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    color: "#5a6675", padding: "4px 10px", fontSize: 12,
    cursor: "pointer", display: "flex", alignItems: "center", gap: 5
  },
  body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14 },
  card: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 10, padding: 16,
    display: "flex", flexDirection: "column", gap: 14
  },
  cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
  fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
  label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
  disabledTag: { fontSize: 10, color: "#b0b8c0", textTransform: "none", fontWeight: 400, marginLeft: 4 },
  hint: { fontSize: 11, color: "#b0b8c0" },
  input: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
  },
  inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
  select: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none", cursor: "pointer"
  },
  toggleRow: { display: "flex", gap: 8 },
  toggleBtn: {
    background: "#fff", border: "1px solid #d4dae0",
    color: "#5a6675", borderRadius: 6, padding: "7px 14px",
    fontSize: 13, cursor: "pointer", flex: 1
  },
  toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
  preview: {
    background: "#f5f7fa", border: "1px solid #e1e6eb",
    borderRadius: 6, padding: "8px 12px"
  },
  previewLabel: { fontSize: 12, color: "#8a96a3" },
  previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
  errorBox: {
    background: "#fce8e6", border: "1px solid #f5b9b3",
    borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
  },
  btnPrimary: {
    background: "#1a73e8", color: "#fff", border: "none",
    borderRadius: 6, padding: "9px 20px", fontSize: 13,
    fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
  },
  btnDanger: {
    background: "#d93025", color: "#fff", border: "none",
    borderRadius: 6, padding: "9px 20px", fontSize: 13,
    fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
  },
  progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  liveStatText: { fontSize: 12, color: "#1a73e8" },
  progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
  progressFill: { height: "100%", background: "#1a73e8", borderRadius: 4, transition: "width 0.3s ease" },
  badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
  resultBadge: {
    display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
    color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
  },
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
};