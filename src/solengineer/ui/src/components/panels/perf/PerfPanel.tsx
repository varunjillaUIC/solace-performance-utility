
// // // // import { useState, useRef } from "react";
// // // // import { PerfResult } from "../types";
// // // // import { IconPerf, IconStop, IconExport } from "./Icons";
// // // // import { exportPerfExcel } from "../api";


// // // // const TEMPLATES = [
// // // //   { label: "Raw payload", value: "" },
// // // //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// // // //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// // // //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// // // //   { label: "Custom", value: "custom" },
// // // // ];

// // // // export default function PerfPanel() {
// // // //   const [target, setTarget] = useState("perf/test");
// // // //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// // // //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// // // //   const [count, setCount] = useState(1000);
// // // //   const [size, setSize] = useState(256);
// // // //   const [rateLimit, setRateLimit] = useState(0);
// // // //   const [windowSize, setWindowSize] = useState(50);
// // // //   const [selectedTemplate, setSelectedTemplate] = useState("");
// // // //   const [customTemplate, setCustomTemplate] = useState("");
// // // //   const [running, setRunning] = useState(false);
// // // //   const [progress, setProgress] = useState(0);
// // // //   const [liveStats, setLiveStats] = useState<{ tps: number; elapsed: number } | null>(null);
// // // //   const [result, setResult] = useState<PerfResult | null>(null);
// // // //   const [error, setError] = useState("");
// // // //   const wsRef = useRef<WebSocket | null>(null);

// // // //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// // // //   const handleRun = () => {
// // // //     if (wsRef.current) wsRef.current.close();
// // // //     setRunning(true);
// // // //     setError("");
// // // //     setResult(null);
// // // //     setProgress(0);
// // // //     setLiveStats(null);

// // // //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// // // //     wsRef.current = ws;

// // // //     ws.onopen = () => {
// // // //       ws.send(JSON.stringify({
// // // //         target, target_type: targetType,
// // // //         message_count: count, message_size: size,
// // // //         message_template: effectiveTemplate,
// // // //         delivery_mode: deliveryMode,
// // // //         rate_limit: rateLimit,
// // // //         window_size: windowSize
// // // //       }));
// // // //     };

// // // //     ws.onmessage = (e) => {
// // // //       const data = JSON.parse(e.data);
// // // //       if (data.type === "progress") {
// // // //         setProgress(data.percent);
// // // //         setLiveStats({ tps: data.tps, elapsed: data.elapsed });
// // // //       } else if (data.type === "complete") {
// // // //         setResult(data.results);
// // // //         setRunning(false);
// // // //         setProgress(100);
// // // //       } else if (data.error) {
// // // //         setError(data.error);
// // // //         setRunning(false);
// // // //       }
// // // //     };

// // // //     ws.onclose = () => setRunning(false);
// // // //   };

// // // //   const handleStop = () => {
// // // //     wsRef.current?.close();
// // // //     setRunning(false);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //   };

// // // //   const handleExportJSON = () => {
// // // //     if (!result) return;
// // // //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// // // //     const url = URL.createObjectURL(blob);
// // // //     const a = document.createElement("a");
// // // //     a.href = url;
// // // //     a.download = `solengineer-perf-${Date.now()}.json`;
// // // //     a.click();
// // // //     URL.revokeObjectURL(url);
// // // //   };

// // // //   const handleExportExcel = async () => {
// // // //     if (!result) return;
// // // //     try {
// // // //       const response = await exportPerfExcel(result);
// // // //       const blob = new Blob([response.data], {
// // // //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// // // //       });
// // // //       const url = URL.createObjectURL(blob);
// // // //       const a = document.createElement("a");
// // // //       a.href = url;
// // // //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// // // //       a.click();
// // // //       URL.revokeObjectURL(url);
// // // //     } catch {
// // // //       console.error("Excel export failed");
// // // //     }
// // // //   };
// // // //   return (
// // // //     <div style={s.page}>
// // // //       <div style={s.topbar}>
// // // //         <div style={s.topbarLeft}>
// // // //           <span style={s.pageTitle}>SDK Performance Test</span>
// // // //           {running && <span style={s.tagAmber}>● Running</span>}
// // // //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// // // //         </div>
// // // //         <div style={s.topbarRight}>
// // // //           {result && (
// // // //             <div style={{ display: "flex", gap: 8 }}>
// // // //               <button style={s.btnGhost} onClick={handleExportJSON}>
// // // //                 <IconExport color="#5a6675" /> JSON
// // // //               </button>
// // // //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// // // //                 onClick={handleExportExcel}>
// // // //                 <IconExport color="#00874a" /> Excel
// // // //               </button>
// // // //             </div>
// // // //           )}
// // // //         </div>
// // // //       </div>

// // // //       <div style={s.body}>
// // // //         <div style={s.card}>
// // // //           <div style={s.cardTitle}>Configuration</div>

// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Target Type</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["topic", "queue"] as const).map((t) => (
// // // //                   <button key={t} onClick={() => setTargetType(t)}
// // // //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// // // //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Delivery Mode</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["direct", "persistent"] as const).map((m) => (
// // // //                   <button key={m} onClick={() => setDeliveryMode(m)}
// // // //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// // // //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //           </div>

// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// // // //               <input style={s.input} value={target}
// // // //                 onChange={(e) => setTarget(e.target.value)}
// // // //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Template</div>
// // // //               <select style={s.select} value={selectedTemplate}
// // // //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// // // //                 {TEMPLATES.map((t) => (
// // // //                   <option key={t.label} value={t.value}>{t.label}</option>
// // // //                 ))}
// // // //               </select>
// // // //             </div>
// // // //           </div>

// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Count</div>
// // // //               <input style={s.input} type="number" value={count}
// // // //                 onChange={(e) => setCount(Number(e.target.value))} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Size (bytes)</div>
// // // //               <input style={s.input} type="number" value={size}
// // // //                 onChange={(e) => setSize(Number(e.target.value))} />
// // // //             </div>
// // // //           </div>

// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Rate Limit (msg/sec)</div>
// // // //               <input style={s.input} type="number" value={rateLimit}
// // // //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// // // //                 placeholder="0 = unlimited" />
// // // //               <div style={s.hint}>0 = send as fast as possible</div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Window Size {deliveryMode === "direct" && <span style={s.disabledTag}>(persistent only)</span>}
// // // //               </div>
// // // //               <input
// // // //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// // // //                 type="number"
// // // //                 value={windowSize}
// // // //                 disabled={deliveryMode === "direct"}
// // // //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// // // //               />
// // // //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// // // //             </div>
// // // //           </div>

// // // //           {selectedTemplate === "custom" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Custom Message Content {/*— use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"} */}
// // // //               </div>
// // // //               <input style={s.input} value={customTemplate}
// // // //                 onChange={(e) => setCustomTemplate(e.target.value)}
// // // //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// // // //             </div>
// // // //           )}

// // // //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// // // //             <div style={s.preview}>
// // // //               <span style={s.previewLabel}>Preview: </span>
// // // //               <span style={s.previewValue}>
// // // //                 {selectedTemplate
// // // //                   .replace("{{index}}", "42")
// // // //                   .replace("{{timestamp}}", "1741234567890")
// // // //                   .replace("{{random}}", "xKpQmRnL")}
// // // //               </span>
// // // //             </div>
// // // //           )}

// // // //           {error && <div style={s.errorBox}>{error}</div>}

// // // //           <div>
// // // //             {!running
// // // //               ? (
// // // //                 <button style={s.btnPrimary} onClick={handleRun}>
// // // //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// // // //                 </button>
// // // //               ) : (
// // // //                 <button style={s.btnDanger} onClick={handleStop}>
// // // //                   <IconStop color="#fff" size={13} /> Stop Test
// // // //                 </button>
// // // //               )
// // // //             }
// // // //           </div>
// // // //         </div>

// // // //         {running && (
// // // //           <div style={s.card}>
// // // //             <div style={s.progressHeader}>
// // // //               <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
// // // //               {liveStats && (
// // // //                 <span style={s.liveStatText}>
// // // //                   {liveStats.tps} msg/s · {liveStats.elapsed}s elapsed
// // // //                 </span>
// // // //               )}
// // // //             </div>
// // // //             <div style={s.progressTrack}>
// // // //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// // // //             </div>
// // // //           </div>
// // // //         )}

// // // //         {result && (
// // // //           <div style={s.card}>
// // // //             <div style={s.cardTitle}>Results</div>
// // // //             <div style={s.badgeRow}>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// // // //               </span>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //               </span>
// // // //               {result.rate_limit > 0 && (
// // // //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// // // //               )}
// // // //               {result.window_size && (
// // // //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// // // //               )}
// // // //             </div>
// // // //             <div style={s.statsGrid}>
// // // //               <StatCard label="Throughput" value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// // // //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`} unit="ms" highlight />
// // // //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`} unit="ms" />
// // // //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`} unit="ms" />
// // // //               <StatCard label="Min latency" value={`${result.min_latency_ms}`} unit="ms" />
// // // //               <StatCard label="Max latency" value={`${result.max_latency_ms}`} unit="ms" />
// // // //               <StatCard label="Sent" value={`${result.sent}`} unit="msgs" />
// // // //               <StatCard label="Received" value={`${result.received}`} unit="msgs" />
// // // //               <StatCard label="Errors" value={`${result.errors}`} unit="" />
// // // //               <StatCard label="Total time" value={`${result.total_time_sec}`} unit="sec" />
// // // //             </div>

// // // //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// // // //               <div style={{ marginTop: 16 }}>
// // // //                 <div style={s.label}>Throughput over time (msg/s)</div>
// // // //                 <ThroughputChart samples={result.throughput_samples} />
// // // //               </div>
// // // //             )}
// // // //           </div>
// // // //         )}
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function StatCard({ label, value, unit, highlight }: {
// // // //   label: string; value: string; unit: string; highlight?: boolean;
// // // // }) {
// // // //   return (
// // // //     <div style={{
// // // //       background: "#f5f7fa",
// // // //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// // // //       borderRadius: 8, padding: "12px 14px"
// // // //     }}>
// // // //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// // // //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// // // //         {value}
// // // //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>{unit}</span>
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function ThroughputChart({ samples }: { samples: number[] }) {
// // // //   const max = Math.max(...samples, 1);
// // // //   const W = 600;
// // // //   const H = 80;
// // // //   const pts = samples.map((v, i) => {
// // // //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// // // //     const y = H - (v / max) * (H - 8);
// // // //     return `${x},${y}`;
// // // //   }).join(" ");

// // // //   return (
// // // //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// // // //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 8 }}>
// // // //       <polyline points={pts} fill="none" stroke="#1a73e8" strokeWidth="2" />
// // // //       {samples.map((v, i) => (
// // // //         <circle key={i}
// // // //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// // // //           cy={H - (v / max) * (H - 8)}
// // // //           r="3" fill="#1a73e8" />
// // // //       ))}
// // // //     </svg>
// // // //   );
// // // // }

// // // // const s: Record<string, React.CSSProperties> = {
// // // //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// // // //   topbar: {
// // // //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// // // //     display: "flex", alignItems: "center", padding: "0 20px",
// // // //     justifyContent: "space-between", flexShrink: 0
// // // //   },
// // // //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// // // //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// // // //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// // // //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// // // //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// // // //   btnGhost: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// // // //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// // // //   },
// // // //   body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14 },
// // // //   card: {
// // // //     background: "#fff", border: "1px solid #e1e6eb",
// // // //     borderRadius: 10, padding: 16,
// // // //     display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// // // //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// // // //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// // // //   label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
// // // //   disabledTag: { fontSize: 10, color: "#b0b8c0", textTransform: "none", fontWeight: 400, marginLeft: 4 },
// // // //   hint: { fontSize: 11, color: "#b0b8c0" },
// // // //   input: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// // // //   },
// // // //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// // // //   select: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none", cursor: "pointer"
// // // //   },
// // // //   toggleRow: { display: "flex", gap: 8 },
// // // //   toggleBtn: {
// // // //     background: "#fff", border: "1px solid #d4dae0",
// // // //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// // // //     fontSize: 13, cursor: "pointer", flex: 1
// // // //   },
// // // //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// // // //   preview: {
// // // //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     borderRadius: 6, padding: "8px 12px"
// // // //   },
// // // //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// // // //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// // // //   errorBox: {
// // // //     background: "#fce8e6", border: "1px solid #f5b9b3",
// // // //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// // // //   },
// // // //   btnPrimary: {
// // // //     background: "#1a73e8", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   btnDanger: {
// // // //     background: "#d93025", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// // // //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// // // //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// // // //   progressFill: { height: "100%", background: "#1a73e8", borderRadius: 4, transition: "width 0.3s ease" },
// // // //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// // // //   resultBadge: {
// // // //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// // // //   },
// // // //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
// // // // };


// // // // import { useState, useRef } from "react";
// // // // import { PerfResult } from "../types";
// // // // import { IconPerf, IconStop, IconExport } from "./Icons";
// // // // import { exportPerfExcel } from "../api";

// // // // const TEMPLATES = [
// // // //   { label: "Raw payload", value: "" },
// // // //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// // // //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// // // //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// // // //   { label: "Custom", value: "custom" },
// // // // ];

// // // // export default function PerfPanel() {
// // // //   const [target, setTarget] = useState("perf/test");
// // // //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// // // //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// // // //   const [count, setCount] = useState(1000);
// // // //   const [size, setSize] = useState(256);
// // // //   const [rateLimit, setRateLimit] = useState(0);
// // // //   const [windowSize, setWindowSize] = useState(50);
// // // //   const [selectedTemplate, setSelectedTemplate] = useState("");
// // // //   const [customTemplate, setCustomTemplate] = useState("");
// // // //   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
// // // //   const [warmupCount, setWarmupCount] = useState(50);
// // // //   const [running, setRunning] = useState(false);
// // // //   const [progress, setProgress] = useState(0);
// // // //   const [liveStats, setLiveStats] = useState<{ tps: number; elapsed: number } | null>(null);
// // // //   const [result, setResult] = useState<PerfResult | null>(null);
// // // //   const [error, setError] = useState("");
// // // //   const [consumerCount, setConsumerCount] = useState(1);
// // // //   const wsRef = useRef<WebSocket | null>(null);

// // // //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// // // //   const handleRun = () => {
// // // //     if (wsRef.current) wsRef.current.close();
// // // //     setRunning(true);
// // // //     setError("");
// // // //     setResult(null);
// // // //     setProgress(0);
// // // //     setLiveStats(null);

// // // //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// // // //     wsRef.current = ws;

// // // //     ws.onopen = () => {
// // // //       ws.send(JSON.stringify({
// // // //         target,
// // // //         target_type: targetType,
// // // //         message_count: count,
// // // //         message_size: size,
// // // //         message_template: effectiveTemplate,
// // // //         delivery_mode: deliveryMode,
// // // //         rate_limit: rateLimit,
// // // //         window_size: windowSize,
// // // //         queue_type: queueType,
// // // //         warmup_count: warmupCount,
// // // //         consumer_count: consumerCount,
// // // //       }));
// // // //     };

// // // //     ws.onmessage = (e) => {
// // // //       const data = JSON.parse(e.data);
// // // //       if (data.type === "progress") {
// // // //         setProgress(data.percent);
// // // //         setLiveStats({ tps: data.tps, elapsed: data.elapsed });
// // // //       } else if (data.type === "complete") {
// // // //         setResult(data.results);
// // // //         setRunning(false);
// // // //         setProgress(100);
// // // //       } else if (data.error) {
// // // //         setError(data.error);
// // // //         setRunning(false);
// // // //       }
// // // //     };

// // // //     ws.onclose = () => setRunning(false);
// // // //   };

// // // //   const handleStop = () => {
// // // //     wsRef.current?.close();
// // // //     setRunning(false);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //   };

// // // //   const handleExportJSON = () => {
// // // //     if (!result) return;
// // // //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// // // //     const url = URL.createObjectURL(blob);
// // // //     const a = document.createElement("a");
// // // //     a.href = url;
// // // //     a.download = `solengineer-perf-${Date.now()}.json`;
// // // //     a.click();
// // // //     URL.revokeObjectURL(url);
// // // //   };

// // // //   const handleExportExcel = async () => {
// // // //     if (!result) return;
// // // //     try {
// // // //       const response = await exportPerfExcel(result);
// // // //       const blob = new Blob([response.data], {
// // // //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// // // //       });
// // // //       const url = URL.createObjectURL(blob);
// // // //       const a = document.createElement("a");
// // // //       a.href = url;
// // // //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// // // //       a.click();
// // // //       URL.revokeObjectURL(url);
// // // //     } catch {
// // // //       console.error("Excel export failed");
// // // //     }
// // // //   };

// // // //   const warmupImprovement = () => {
// // // //     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
// // // //     const pct = ((result.warmup_avg_ms - result.avg_latency_ms) / result.warmup_avg_ms * 100).toFixed(0);
// // // //     return `${pct}% faster`;
// // // //   };

// // // //   return (
// // // //     <div style={s.page}>

// // // //       {/* Topbar */}
// // // //       <div style={s.topbar}>
// // // //         <div style={s.topbarLeft}>
// // // //           <span style={s.pageTitle}>SDK Performance Test</span>
// // // //           {running && <span style={s.tagAmber}>● Running</span>}
// // // //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// // // //         </div>
// // // //         <div style={s.topbarRight}>
// // // //           {result && (
// // // //             <div style={{ display: "flex", gap: 8 }}>
// // // //               <button style={s.btnGhost} onClick={handleExportJSON}>
// // // //                 <IconExport color="#5a6675" /> JSON
// // // //               </button>
// // // //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// // // //                 onClick={handleExportExcel}>
// // // //                 <IconExport color="#00874a" /> Excel
// // // //               </button>
// // // //             </div>
// // // //           )}
// // // //         </div>
// // // //       </div>

// // // //       <div style={s.body}>
// // // //         <div style={s.card}>
// // // //           <div style={s.cardTitle}>Configuration</div>

// // // //           {/* Row 1 — Target Type + Delivery Mode */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Target Type</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["topic", "queue"] as const).map((t) => (
// // // //                   <button key={t} onClick={() => setTargetType(t)}
// // // //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// // // //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Delivery Mode</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["direct", "persistent"] as const).map((m) => (
// // // //                   <button key={m} onClick={() => setDeliveryMode(m)}
// // // //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// // // //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Queue Type — only shown when target is queue */}
// // // //          {targetType === "queue" && (
// // // //   <div style={s.fieldGroup}>
// // // //     <div style={s.label}>Queue Type</div>
// // // //     <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
// // // //       {(["exclusive", "non_exclusive"] as const).map((q) => (
// // // //         <button key={q} onClick={() => setQueueType(q)}
// // // //           style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
// // // //           {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //         </button>
// // // //       ))}
// // // //     </div>
// // // //     <div style={s.hint}>
// // // //       {queueType === "exclusive"
// // // //         ? "One active consumer — ordered delivery, automatic failover"
// // // //         : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
// // // //       }
// // // //     </div>

// // // //     {/* Consumer count — only for non-exclusive */}
// // // //     {queueType === "non_exclusive" && (
// // // //       <div style={{ marginTop: 8 }}>
// // // //         <div style={s.label}>
// // // //           Consumer Count
// // // //           <span style={s.disabledTag}>(non-exclusive only)</span>
// // // //         </div>
// // // //         <input
// // // //           style={{ ...s.input, maxWidth: 200 }}
// // // //           type="number"
// // // //           min={1}
// // // //           max={10}
// // // //           value={consumerCount}
// // // //           onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
// // // //         />
// // // //         <div style={s.hint}>
// // // //           Spawns N receiver threads on the same queue — simulates real multi-consumer load.
// // // //           Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
// // // //         </div>
// // // //       </div>
// // // //     )}
// // // //   </div>
// // // // )}

// // // //           {/* Row 2 — Target + Template */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// // // //               <input style={s.input} value={target}
// // // //                 onChange={(e) => setTarget(e.target.value)}
// // // //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Template</div>
// // // //               <select style={s.select} value={selectedTemplate}
// // // //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// // // //                 {TEMPLATES.map((t) => (
// // // //                   <option key={t.label} value={t.value}>{t.label}</option>
// // // //                 ))}
// // // //               </select>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 3 — Count + Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Count</div>
// // // //               <input style={s.input} type="number" value={count}
// // // //                 onChange={(e) => setCount(Number(e.target.value))} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Size (bytes)</div>
// // // //               <input style={s.input} type="number" value={size}
// // // //                 onChange={(e) => setSize(Number(e.target.value))} />
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 4 — Rate Limit + Window Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Rate Limit (msg/sec)</div>
// // // //               <input style={s.input} type="number" value={rateLimit}
// // // //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// // // //                 placeholder="0 = unlimited" />
// // // //               <div style={s.hint}>0 = send as fast as possible</div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Window Size
// // // //                 {deliveryMode === "direct" && (
// // // //                   <span style={s.disabledTag}>(persistent only)</span>
// // // //                 )}
// // // //               </div>
// // // //               <input
// // // //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// // // //                 type="number"
// // // //                 value={windowSize}
// // // //                 disabled={deliveryMode === "direct"}
// // // //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// // // //               />
// // // //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 5 — Warmup Count */}
// // // //           <div style={s.fieldGroup}>
// // // //             <div style={s.label}>Warmup Messages to Skip</div>
// // // //             <input
// // // //               style={{ ...s.input, maxWidth: 280 }}
// // // //               type="number"
// // // //               value={warmupCount}
// // // //               onChange={(e) => setWarmupCount(Number(e.target.value))}
// // // //               placeholder="0"
// // // //             />
// // // //             <div style={s.hint}>
// // // //               First N messages excluded from latency stats — removes TCP slow-start and SDK warmup bias from results.
// // // //               Set to 0 to include all messages.
// // // //             </div>
// // // //           </div>

// // // //           {/* Custom template input */}
// // // //           {selectedTemplate === "custom" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
// // // //               </div>
// // // //               <input style={s.input} value={customTemplate}
// // // //                 onChange={(e) => setCustomTemplate(e.target.value)}
// // // //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// // // //             </div>
// // // //           )}

// // // //           {/* Template preview */}
// // // //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// // // //             <div style={s.preview}>
// // // //               <span style={s.previewLabel}>Preview: </span>
// // // //               <span style={s.previewValue}>
// // // //                 {selectedTemplate
// // // //                   .replace("{{index}}", "42")
// // // //                   .replace("{{timestamp}}", "1741234567890")
// // // //                   .replace("{{random}}", "xKpQmRnL")}
// // // //               </span>
// // // //             </div>
// // // //           )}

// // // //           {error && <div style={s.errorBox}>{error}</div>}

// // // //           {/* Run / Stop */}
// // // //           <div>
// // // //             {!running
// // // //               ? (
// // // //                 <button style={s.btnPrimary} onClick={handleRun}>
// // // //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// // // //                 </button>
// // // //               ) : (
// // // //                 <button style={s.btnDanger} onClick={handleStop}>
// // // //                   <IconStop color="#fff" size={13} /> Stop Test
// // // //                 </button>
// // // //               )
// // // //             }
// // // //           </div>
// // // //         </div>

// // // //         {/* Progress */}
// // // //         {running && (
// // // //           <div style={s.card}>
// // // //             <div style={s.progressHeader}>
// // // //               <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
// // // //               {liveStats && (
// // // //                 <span style={s.liveStatText}>
// // // //                   {liveStats.tps} msg/s · {liveStats.elapsed}s elapsed
// // // //                 </span>
// // // //               )}
// // // //             </div>
// // // //             <div style={s.progressTrack}>
// // // //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// // // //             </div>
// // // //           </div>
// // // //         )}

// // // //         {/* Results */}
// // // //         {result && (
// // // //           <div style={s.card}>
// // // //             <div style={s.cardTitle}>Results</div>

// // // //             {/* Badges */}
// // // //             <div style={s.badgeRow}>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// // // //               </span>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //               </span>
// // // //               {result.queue_type && (
// // // //                 <span style={s.resultBadge}>
// // // //                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
// // // //                 </span>
// // // //               )}
// // // //               {result.rate_limit > 0 && (
// // // //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// // // //               )}
// // // //               {result.window_size && (
// // // //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// // // //               )}
// // // //               {result.warmup_count > 0 && (
// // // //                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
// // // //               )}
// // // //             </div>

// // // //             {/* Main stats grid */}
// // // //             <div style={s.statsGrid}>
// // // //               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// // // //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
// // // //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
// // // //               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
// // // //               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
// // // //               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
// // // //             </div>

// // // //             {/* Warmup analysis box */}
// // // //             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
// // // //               <div style={s.warmupBox}>
// // // //                 <div style={s.warmupTitle}>
// // // //                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
// // // //                 </div>
// // // //                 <div style={s.warmupGrid}>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Avg</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
// // // //                     <div style={s.warmupNote}>cold-start latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Max</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
// // // //                     <div style={s.warmupNote}>TCP slow-start peak</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Steady-State Avg</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
// // // //                       {result.avg_latency_ms} ms
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>true production latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Improvement</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
// // // //                       {warmupImprovement() ?? "—"}
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>warmup vs steady-state</div>
// // // //                   </div>
// // // //                 </div>
// // // //               </div>
// // // //             )}

// // // //             {/* Throughput chart */}
// // // //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// // // //               <div style={{ marginTop: 8 }}>
// // // //                 <div style={s.label}>Throughput over time (msg/s)</div>
// // // //                 <ThroughputChart samples={result.throughput_samples} />
// // // //               </div>
// // // //             )}
// // // //           </div>
// // // //         )}
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function StatCard({ label, value, unit, highlight }: {
// // // //   label: string; value: string; unit: string; highlight?: boolean;
// // // // }) {
// // // //   return (
// // // //     <div style={{
// // // //       background: "#f5f7fa",
// // // //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// // // //       borderRadius: 8, padding: "12px 14px"
// // // //     }}>
// // // //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// // // //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// // // //         {value}
// // // //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
// // // //           {unit}
// // // //         </span>
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function ThroughputChart({ samples }: { samples: number[] }) {
// // // //   const max = Math.max(...samples, 1);
// // // //   const W = 600;
// // // //   const H = 80;
// // // //   const pts = samples.map((v, i) => {
// // // //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// // // //     const y = H - (v / max) * (H - 8);
// // // //     return `${x},${y}`;
// // // //   }).join(" ");

// // // //   return (
// // // //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// // // //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 8 }}>
// // // //       <polyline points={pts} fill="none" stroke="#1a73e8" strokeWidth="2" />
// // // //       {samples.map((v, i) => (
// // // //         <circle key={i}
// // // //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// // // //           cy={H - (v / max) * (H - 8)}
// // // //           r="3" fill="#1a73e8"
// // // //         />
// // // //       ))}
// // // //     </svg>
// // // //   );
// // // // }

// // // // const s: Record<string, React.CSSProperties> = {
// // // //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// // // //   topbar: {
// // // //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// // // //     display: "flex", alignItems: "center", padding: "0 20px",
// // // //     justifyContent: "space-between", flexShrink: 0
// // // //   },
// // // //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// // // //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// // // //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// // // //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// // // //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// // // //   btnGhost: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// // // //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// // // //   },
// // // //   body: {
// // // //     flex: 1, overflowY: "auto", padding: 20,
// // // //     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   card: {
// // // //     background: "#fff", border: "1px solid #e1e6eb",
// // // //     borderRadius: 10, padding: 16,
// // // //     display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// // // //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// // // //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// // // //   label: {
// // // //     fontSize: 11, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   disabledTag: {
// // // //     fontSize: 10, color: "#b0b8c0",
// // // //     textTransform: "none", fontWeight: 400, marginLeft: 4
// // // //   },
// // // //   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
// // // //   input: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// // // //   },
// // // //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// // // //   select: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13,
// // // //     outline: "none", cursor: "pointer"
// // // //   },
// // // //   toggleRow: { display: "flex", gap: 8 },
// // // //   toggleBtn: {
// // // //     background: "#fff", border: "1px solid #d4dae0",
// // // //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// // // //     fontSize: 13, cursor: "pointer", flex: 1
// // // //   },
// // // //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// // // //   preview: {
// // // //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     borderRadius: 6, padding: "8px 12px"
// // // //   },
// // // //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// // // //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// // // //   errorBox: {
// // // //     background: "#fce8e6", border: "1px solid #f5b9b3",
// // // //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// // // //   },
// // // //   btnPrimary: {
// // // //     background: "#1a73e8", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   btnDanger: {
// // // //     background: "#d93025", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// // // //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// // // //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// // // //   progressFill: {
// // // //     height: "100%", background: "#1a73e8",
// // // //     borderRadius: 4, transition: "width 0.3s ease"
// // // //   },
// // // //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// // // //   resultBadge: {
// // // //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// // // //   },
// // // //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },

// // // //   // Warmup analysis styles
// // // //   warmupBox: {
// // // //     background: "#fef9ec", border: "1px solid #fcd9a0",
// // // //     borderRadius: 8, padding: "14px 16px",
// // // //     display: "flex", flexDirection: "column", gap: 12
// // // //   },
// // // //   warmupTitle: {
// // // //     fontSize: 12, fontWeight: 600, color: "#e8710a"
// // // //   },
// // // //   warmupGrid: {
// // // //     display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12
// // // //   },
// // // //   warmupStat: {
// // // //     display: "flex", flexDirection: "column", gap: 3
// // // //   },
// // // //   warmupLabel: {
// // // //     fontSize: 10, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   warmupValue: {
// // // //     fontSize: 18, fontWeight: 600, color: "#1a2733"
// // // //   },
// // // //   warmupNote: {
// // // //     fontSize: 10, color: "#b0b8c0"
// // // //   }
// // // // };



// // // // import { useState, useRef } from "react";
// // // // import { PerfResult } from "../types";
// // // // import { IconPerf, IconStop, IconExport } from "./Icons";
// // // // import { exportPerfExcel } from "../api";

// // // // const TEMPLATES = [
// // // //   { label: "Raw payload", value: "" },
// // // //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// // // //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// // // //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// // // //   { label: "Custom", value: "custom" },
// // // // ];

// // // // interface PerfPanelProps {
// // // //   onResult?: (r: PerfResult) => void;
// // // //   onIngressSample?: (v: number) => void;
// // // //   onEgressSample?: (v: number) => void;
// // // //   onRunning?: (v: boolean) => void;

  
// // // // }

// // // // export default function PerfPanel({
// // // //   onResult, onIngressSample, onEgressSample, onRunning
// // // // }: PerfPanelProps) {

// // // //   const [target, setTarget] = useState("perf/test");
// // // //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// // // //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// // // //   const [count, setCount] = useState(1000);
// // // //   const [size, setSize] = useState(256);
// // // //   const [rateLimit, setRateLimit] = useState(0);
// // // //   const [windowSize, setWindowSize] = useState(50);
// // // //   const [selectedTemplate, setSelectedTemplate] = useState("");
// // // //   const [customTemplate, setCustomTemplate] = useState("");
// // // //   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
// // // //   const [warmupCount, setWarmupCount] = useState(50);
// // // //   const [consumerCount, setConsumerCount] = useState(1);
// // // //   const [running, setRunning] = useState(false);
// // // //   const [progress, setProgress] = useState(0);
// // // //   const [liveStats, setLiveStats] = useState<{ tps: number; ingress: number; elapsed: number } | null>(null);
// // // //   const [result, setResult] = useState<PerfResult | null>(null);
// // // //   const [error, setError] = useState("");
// // // //   const wsRef = useRef<WebSocket | null>(null);

// // // //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// // // //   const handleRun = () => {
// // // //     if (wsRef.current) wsRef.current.close();
// // // //     setRunning(true);
// // // //     setError("");
// // // //     setResult(null);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //     onRunning?.(true);

// // // //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// // // //     wsRef.current = ws;

// // // //     ws.onopen = () => {
// // // //       ws.send(JSON.stringify({
// // // //         target,
// // // //         target_type: targetType,
// // // //         message_count: count,
// // // //         message_size: size,
// // // //         message_template: effectiveTemplate,
// // // //         delivery_mode: deliveryMode,
// // // //         rate_limit: rateLimit,
// // // //         window_size: windowSize,
// // // //         queue_type: queueType,
// // // //         warmup_count: warmupCount,
// // // //         consumer_count: consumerCount,
// // // //       }));
// // // //     };

// // // //     ws.onmessage = (e) => {
// // // //       const data = JSON.parse(e.data);
// // // //       if (data.type === "progress") {
// // // //         setProgress(data.percent);
// // // //         setLiveStats({
// // // //           tps: data.tps,
// // // //           ingress: data.ingress_tps ?? 0,
// // // //           elapsed: data.elapsed
// // // //         });
// // // //         // Fire callbacks to Dashboard for Charts tab
// // // //         if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
// // // //         if (data.tps !== undefined) onEgressSample?.(data.tps);

// // // //       } else if (data.type === "complete") {
// // // //         setResult(data.results);
// // // //         setRunning(false);
// // // //         setProgress(100);
// // // //         onResult?.(data.results);
// // // //         onRunning?.(false);

// // // //       } else if (data.error) {
// // // //         setError(data.error);
// // // //         setRunning(false);
// // // //         onRunning?.(false);
// // // //       }
// // // //     };

// // // //     ws.onclose = () => {
// // // //       setRunning(false);
// // // //       onRunning?.(false);
// // // //     };
// // // //   };

// // // //   const handleStop = () => {
// // // //     wsRef.current?.close();
// // // //     setRunning(false);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //     onRunning?.(false);
// // // //   };

// // // //   const handleExportJSON = () => {
// // // //     if (!result) return;
// // // //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// // // //     const url = URL.createObjectURL(blob);
// // // //     const a = document.createElement("a");
// // // //     a.href = url;
// // // //     a.download = `solengineer-perf-${Date.now()}.json`;
// // // //     a.click();
// // // //     URL.revokeObjectURL(url);
// // // //   };

// // // //   const handleExportExcel = async () => {
// // // //     if (!result) return;
// // // //     try {
// // // //       const response = await exportPerfExcel(result);
// // // //       const blob = new Blob([response.data], {
// // // //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// // // //       });
// // // //       const url = URL.createObjectURL(blob);
// // // //       const a = document.createElement("a");
// // // //       a.href = url;
// // // //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// // // //       a.click();
// // // //       URL.revokeObjectURL(url);
// // // //     } catch {
// // // //       console.error("Excel export failed");
// // // //     }
// // // //   };

// // // //   const warmupImprovement = () => {
// // // //     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
// // // //     const pct = (
// // // //       (result.warmup_avg_ms - result.avg_latency_ms)
// // // //       / result.warmup_avg_ms * 100
// // // //     ).toFixed(0);
// // // //     return `${pct}% faster`;
// // // //   };

// // // //   return (
// // // //     <div style={s.page}>

// // // //       {/* Topbar */}
// // // //       <div style={s.topbar}>
// // // //         <div style={s.topbarLeft}>
// // // //           <span style={s.pageTitle}>SDK Performance Test</span>
// // // //           {running && <span style={s.tagAmber}>● Running</span>}
// // // //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// // // //         </div>
// // // //         <div style={s.topbarRight}>
// // // //           {result && (
// // // //             <div style={{ display: "flex", gap: 8 }}>
// // // //               <button style={s.btnGhost} onClick={handleExportJSON}>
// // // //                 <IconExport color="#5a6675" /> JSON
// // // //               </button>
// // // //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// // // //                 onClick={handleExportExcel}>
// // // //                 <IconExport color="#00874a" /> Excel
// // // //               </button>
// // // //             </div>
// // // //           )}
// // // //         </div>
// // // //       </div>

// // // //       <div style={s.body}>
// // // //         <div style={s.card}>
// // // //           <div style={s.cardTitle}>Configuration</div>

// // // //           {/* Row 1 — Target Type + Delivery Mode */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Target Type</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["topic", "queue"] as const).map((t) => (
// // // //                   <button key={t} onClick={() => setTargetType(t)}
// // // //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// // // //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Delivery Mode</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["direct", "persistent"] as const).map((m) => (
// // // //                   <button key={m} onClick={() => setDeliveryMode(m)}
// // // //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// // // //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Queue Type — only when queue selected */}
// // // //           {targetType === "queue" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Queue Type</div>
// // // //               <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
// // // //                 {(["exclusive", "non_exclusive"] as const).map((q) => (
// // // //                   <button key={q} onClick={() => setQueueType(q)}
// // // //                     style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
// // // //                     {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //               <div style={s.hint}>
// // // //                 {queueType === "exclusive"
// // // //                   ? "One active consumer — ordered delivery, automatic failover"
// // // //                   : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
// // // //                 }
// // // //               </div>

// // // //               {/* Consumer count — non-exclusive only */}
// // // //               {queueType === "non_exclusive" && (
// // // //                 <div style={{ marginTop: 8 }}>
// // // //                   <div style={s.label}>
// // // //                     Consumer Count
// // // //                     <span style={s.disabledTag}>(non-exclusive only)</span>
// // // //                   </div>
// // // //                   <input
// // // //                     style={{ ...s.input, maxWidth: 200 }}
// // // //                     type="number"
// // // //                     min={1}
// // // //                     max={10}
// // // //                     value={consumerCount}
// // // //                     onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
// // // //                   />
// // // //                   <div style={s.hint}>
// // // //                     Spawns N receiver threads — simulates real multi-consumer load.
// // // //                     Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
// // // //                   </div>
// // // //                 </div>
// // // //               )}
// // // //             </div>
// // // //           )}

// // // //           {/* Row 2 — Target + Template */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// // // //               <input style={s.input} value={target}
// // // //                 onChange={(e) => setTarget(e.target.value)}
// // // //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Template</div>
// // // //               <select style={s.select} value={selectedTemplate}
// // // //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// // // //                 {TEMPLATES.map((t) => (
// // // //                   <option key={t.label} value={t.value}>{t.label}</option>
// // // //                 ))}
// // // //               </select>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 3 — Count + Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Count</div>
// // // //               <input style={s.input} type="number" value={count}
// // // //                 onChange={(e) => setCount(Number(e.target.value))} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Size (bytes)</div>
// // // //               <input style={s.input} type="number" value={size}
// // // //                 onChange={(e) => setSize(Number(e.target.value))} />
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 4 — Rate Limit + Window Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Rate Limit (msg/sec)</div>
// // // //               <input style={s.input} type="number" value={rateLimit}
// // // //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// // // //                 placeholder="0 = unlimited" />
// // // //               <div style={s.hint}>0 = send as fast as possible</div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Window Size
// // // //                 {deliveryMode === "direct" && (
// // // //                   <span style={s.disabledTag}>(persistent only)</span>
// // // //                 )}
// // // //               </div>
// // // //               <input
// // // //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// // // //                 type="number"
// // // //                 value={windowSize}
// // // //                 disabled={deliveryMode === "direct"}
// // // //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// // // //               />
// // // //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 5 — Warmup Count */}
// // // //           <div style={s.fieldGroup}>
// // // //             <div style={s.label}>Warmup Messages to Skip</div>
// // // //             <input
// // // //               style={{ ...s.input, maxWidth: 280 }}
// // // //               type="number"
// // // //               value={warmupCount}
// // // //               onChange={(e) => setWarmupCount(Number(e.target.value))}
// // // //               placeholder="0"
// // // //             />
// // // //             <div style={s.hint}>
// // // //               First N messages excluded from latency stats — removes TCP slow-start
// // // //               and SDK warmup bias. Set to 0 to include all messages.
// // // //             </div>
// // // //           </div>

// // // //           {/* Custom template */}
// // // //           {selectedTemplate === "custom" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
// // // //               </div>
// // // //               <input style={s.input} value={customTemplate}
// // // //                 onChange={(e) => setCustomTemplate(e.target.value)}
// // // //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// // // //             </div>
// // // //           )}

// // // //           {/* Template preview */}
// // // //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// // // //             <div style={s.preview}>
// // // //               <span style={s.previewLabel}>Preview: </span>
// // // //               <span style={s.previewValue}>
// // // //                 {selectedTemplate
// // // //                   .replace("{{index}}", "42")
// // // //                   .replace("{{timestamp}}", "1741234567890")
// // // //                   .replace("{{random}}", "xKpQmRnL")}
// // // //               </span>
// // // //             </div>
// // // //           )}

// // // //           {error && <div style={s.errorBox}>{error}</div>}

// // // //           {/* Run / Stop */}
// // // //           <div>
// // // //             {!running
// // // //               ? (
// // // //                 <button style={s.btnPrimary} onClick={handleRun}>
// // // //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// // // //                 </button>
// // // //               ) : (
// // // //                 <button style={s.btnDanger} onClick={handleStop}>
// // // //                   <IconStop color="#fff" size={13} /> Stop Test
// // // //                 </button>
// // // //               )
// // // //             }
// // // //           </div>
// // // //         </div>

// // // //         {/* Progress */}
// // // //         {running && (
// // // //           <div style={s.card}>
// // // //             <div style={s.progressHeader}>
// // // //               <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
// // // //               {liveStats && (
// // // //                 <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
// // // //                   <span style={{ ...s.liveStatText, color: "#1a73e8" }}>
// // // //                     ↑ {liveStats.ingress} msg/s ingress
// // // //                   </span>
// // // //                   <span style={{ ...s.liveStatText, color: "#00874a" }}>
// // // //                     ↓ {liveStats.tps} msg/s egress
// // // //                   </span>
// // // //                   <span style={s.liveStatText}>
// // // //                     {liveStats.elapsed}s elapsed
// // // //                   </span>
// // // //                 </div>
// // // //               )}
// // // //             </div>
// // // //             <div style={s.progressTrack}>
// // // //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// // // //             </div>
// // // //           </div>
// // // //         )}

// // // //         {/* Results */}
// // // //         {result && (
// // // //           <div style={s.card}>
// // // //             <div style={s.cardTitle}>Results</div>

// // // //             {/* Badges */}
// // // //             <div style={s.badgeRow}>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// // // //               </span>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //               </span>
// // // //               {result.queue_type && (
// // // //                 <span style={s.resultBadge}>
// // // //                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
// // // //                 </span>
// // // //               )}
// // // //               {result.rate_limit > 0 && (
// // // //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// // // //               )}
// // // //               {result.window_size && (
// // // //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// // // //               )}
// // // //               {result.warmup_count > 0 && (
// // // //                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
// // // //               )}
// // // //             </div>

// // // //             {/* Stats grid */}
// // // //             <div style={s.statsGrid}>
// // // //               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// // // //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
// // // //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
// // // //               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
// // // //               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
// // // //               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
// // // //             </div>

// // // //             {/* Warmup analysis */}
// // // //             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
// // // //               <div style={s.warmupBox}>
// // // //                 <div style={s.warmupTitle}>
// // // //                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
// // // //                 </div>
// // // //                 <div style={s.warmupGrid}>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Avg</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
// // // //                     <div style={s.warmupNote}>cold-start latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Max</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
// // // //                     <div style={s.warmupNote}>TCP slow-start peak</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Steady-State Avg</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
// // // //                       {result.avg_latency_ms} ms
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>true production latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Improvement</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
// // // //                       {warmupImprovement() ?? "—"}
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>warmup vs steady-state</div>
// // // //                   </div>
// // // //                 </div>
// // // //               </div>
// // // //             )}

// // // //             {/* Egress throughput chart */}
// // // //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// // // //               <div style={{ marginTop: 8 }}>
// // // //                 <div style={s.label}>Egress — Receive rate over time (msg/s)</div>
// // // //                 <ThroughputChart
// // // //                   samples={result.throughput_samples}
// // // //                   color="#00874a"
// // // //                 />
// // // //               </div>
// // // //             )}

// // // //             {/* Ingress throughput chart */}
// // // //             {result.ingress_samples && result.ingress_samples.length > 0 && (
// // // //               <div style={{ marginTop: 8 }}>
// // // //                 <div style={s.label}>Ingress — Publish rate over time (msg/s)</div>
// // // //                 <ThroughputChart
// // // //                   samples={result.ingress_samples}
// // // //                   color="#1a73e8"
// // // //                 />
// // // //               </div>
// // // //             )}
// // // //           </div>
// // // //         )}
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function StatCard({ label, value, unit, highlight }: {
// // // //   label: string; value: string; unit: string; highlight?: boolean;
// // // // }) {
// // // //   return (
// // // //     <div style={{
// // // //       background: "#f5f7fa",
// // // //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// // // //       borderRadius: 8, padding: "12px 14px"
// // // //     }}>
// // // //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// // // //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// // // //         {value}
// // // //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
// // // //           {unit}
// // // //         </span>
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function ThroughputChart({ samples, color }: { samples: number[]; color: string }) {
// // // //   const max = Math.max(...samples, 1);
// // // //   const W = 600;
// // // //   const H = 80;
// // // //   const pts = samples.map((v, i) => {
// // // //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// // // //     const y = H - (v / max) * (H - 8);
// // // //     return `${x},${y}`;
// // // //   }).join(" ");

// // // //   return (
// // // //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// // // //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 6 }}>
// // // //       <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
// // // //       {samples.map((v, i) => (
// // // //         <circle key={i}
// // // //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// // // //           cy={H - (v / max) * (H - 8)}
// // // //           r="3" fill={color}
// // // //         />
// // // //       ))}
// // // //     </svg>
// // // //   );
// // // // }

// // // // const s: Record<string, React.CSSProperties> = {
// // // //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// // // //   topbar: {
// // // //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// // // //     display: "flex", alignItems: "center", padding: "0 20px",
// // // //     justifyContent: "space-between", flexShrink: 0
// // // //   },
// // // //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// // // //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// // // //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// // // //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// // // //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// // // //   btnGhost: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// // // //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// // // //   },
// // // //   body: {
// // // //     flex: 1, overflowY: "auto", padding: 20,
// // // //     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   card: {
// // // //     background: "#fff", border: "1px solid #e1e6eb",
// // // //     borderRadius: 10, padding: 16,
// // // //     display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// // // //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// // // //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// // // //   label: {
// // // //     fontSize: 11, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   disabledTag: {
// // // //     fontSize: 10, color: "#b0b8c0",
// // // //     textTransform: "none", fontWeight: 400, marginLeft: 4
// // // //   },
// // // //   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
// // // //   input: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// // // //   },
// // // //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// // // //   select: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13,
// // // //     outline: "none", cursor: "pointer"
// // // //   },
// // // //   toggleRow: { display: "flex", gap: 8 },
// // // //   toggleBtn: {
// // // //     background: "#fff", border: "1px solid #d4dae0",
// // // //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// // // //     fontSize: 13, cursor: "pointer", flex: 1
// // // //   },
// // // //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// // // //   preview: {
// // // //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     borderRadius: 6, padding: "8px 12px"
// // // //   },
// // // //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// // // //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// // // //   errorBox: {
// // // //     background: "#fce8e6", border: "1px solid #f5b9b3",
// // // //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// // // //   },
// // // //   btnPrimary: {
// // // //     background: "#1a73e8", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   btnDanger: {
// // // //     background: "#d93025", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// // // //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// // // //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// // // //   progressFill: {
// // // //     height: "100%", background: "#1a73e8",
// // // //     borderRadius: 4, transition: "width 0.3s ease"
// // // //   },
// // // //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// // // //   resultBadge: {
// // // //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// // // //   },
// // // //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
// // // //   warmupBox: {
// // // //     background: "#fef9ec", border: "1px solid #fcd9a0",
// // // //     borderRadius: 8, padding: "14px 16px",
// // // //     display: "flex", flexDirection: "column", gap: 12
// // // //   },
// // // //   warmupTitle: { fontSize: 12, fontWeight: 600, color: "#e8710a" },
// // // //   warmupGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
// // // //   warmupStat: { display: "flex", flexDirection: "column", gap: 3 },
// // // //   warmupLabel: {
// // // //     fontSize: 10, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   warmupValue: { fontSize: 18, fontWeight: 600, color: "#1a2733" },
// // // //   warmupNote: { fontSize: 10, color: "#b0b8c0" }
// // // // };


// // // // import { useState, useRef } from "react";
// // // // import { PerfResult } from "../types";
// // // // import { IconPerf, IconStop, IconExport } from "./Icons";
// // // // import { exportPerfExcel } from "../api";

// // // // const TEMPLATES = [
// // // //   { label: "Raw payload", value: "" },
// // // //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// // // //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// // // //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// // // //   { label: "Custom", value: "custom" },
// // // // ];

// // // // interface PerfPanelProps {
// // // //   onResult?: (r: PerfResult) => void;
// // // //   onIngressSample?: (v: number) => void;
// // // //   onEgressSample?: (v: number) => void;
// // // //   onRunning?: (v: boolean) => void;
// // // //   savedResult?: PerfResult | null;
// // // //   savedProgress?: number;
// // // //   savedLiveStats?: { tps: number; ingress: number; elapsed: number } | null;
// // // //   savedError?: string;
// // // //   onProgressChange?: (v: number) => void;
// // // //   onLiveStatsChange?: (v: { tps: number; ingress: number; elapsed: number } | null) => void;
// // // //   onErrorChange?: (v: string) => void;
// // // // }

// // // // export default function PerfPanel({
// // // //   onResult, onIngressSample, onEgressSample, onRunning,
// // // //   savedResult, savedProgress, savedLiveStats, savedError,
// // // //   onProgressChange, onLiveStatsChange, onErrorChange
// // // // }: PerfPanelProps) {

// // // //   const [target, setTarget] = useState("perf/test");
// // // //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// // // //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// // // //   const [count, setCount] = useState(1000);
// // // //   const [size, setSize] = useState(256);
// // // //   const [rateLimit, setRateLimit] = useState(0);
// // // //   const [windowSize, setWindowSize] = useState(50);
// // // //   const [selectedTemplate, setSelectedTemplate] = useState("");
// // // //   const [customTemplate, setCustomTemplate] = useState("");
// // // //   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
// // // //   const [warmupCount, setWarmupCount] = useState(50);
// // // //   const [consumerCount, setConsumerCount] = useState(1);
// // // //   const [running, setRunning] = useState(false);

// // // //   // ── Lifted state — initialized from Dashboard so they survive tab switches ──
// // // //   const [progressState, setProgressState] = useState(savedProgress ?? 0);
// // // //   const [liveStatsState, setLiveStatsState] = useState<{
// // // //     tps: number; ingress: number; elapsed: number
// // // //   } | null>(savedLiveStats ?? null);
// // // //   const [resultState, setResultState] = useState<PerfResult | null>(savedResult ?? null);
// // // //   const [errorState, setErrorState] = useState(savedError ?? "");

// // // //   // Wrapper setters — update local + parent
// // // //   const setProgress = (v: number) => { setProgressState(v); onProgressChange?.(v); };
// // // //   const setLiveStats = (v: { tps: number; ingress: number; elapsed: number } | null) => {
// // // //     setLiveStatsState(v); onLiveStatsChange?.(v);
// // // //   };
// // // //   const setResult = (v: PerfResult | null) => { setResultState(v); };
// // // //   const setError = (v: string) => { setErrorState(v); onErrorChange?.(v); };

// // // //   // Convenience aliases for reading
// // // //   const progress  = progressState;
// // // //   const liveStats = liveStatsState;
// // // //   const result    = resultState;
// // // //   const error     = errorState;

// // // //   const wsRef = useRef<WebSocket | null>(null);
// // // //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// // // //   const handleRun = () => {
// // // //     if (wsRef.current) wsRef.current.close();
// // // //     setRunning(true);
// // // //     setError("");
// // // //     setResult(null);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //     onProgressChange?.(0);
// // // //     onLiveStatsChange?.(null);
// // // //     onErrorChange?.("");
// // // //     onRunning?.(true);

// // // //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// // // //     wsRef.current = ws;

// // // //     ws.onopen = () => {
// // // //       ws.send(JSON.stringify({
// // // //         target,
// // // //         target_type: targetType,
// // // //         message_count: count,
// // // //         message_size: size,
// // // //         message_template: effectiveTemplate,
// // // //         delivery_mode: deliveryMode,
// // // //         rate_limit: rateLimit,
// // // //         window_size: windowSize,
// // // //         queue_type: queueType,
// // // //         warmup_count: warmupCount,
// // // //         consumer_count: consumerCount,
// // // //       }));
// // // //     };

// // // //     ws.onmessage = (e) => {
// // // //       const data = JSON.parse(e.data);

// // // //       if (data.type === "progress") {
// // // //         const stats = {
// // // //           tps: data.tps,
// // // //           ingress: data.ingress_tps ?? 0,
// // // //           elapsed: data.elapsed
// // // //         };
// // // //         setProgress(data.percent);
// // // //         setLiveStats(stats);
// // // //         if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
// // // //         if (data.tps !== undefined) onEgressSample?.(data.tps);

// // // //       } else if (data.type === "complete") {
// // // //         setResult(data.results);
// // // //         setRunning(false);
// // // //         setProgress(100);
// // // //         setLiveStats(null);
// // // //         onProgressChange?.(100);
// // // //         onLiveStatsChange?.(null);
// // // //         onResult?.(data.results);
// // // //         onRunning?.(false);

// // // //       } else if (data.error) {
// // // //         setError(data.error);
// // // //         setRunning(false);
// // // //         onRunning?.(false);
// // // //       }
// // // //     };

// // // //     ws.onclose = () => {
// // // //       setRunning(false);
// // // //       onRunning?.(false);
// // // //     };
// // // //   };

// // // //   const handleStop = () => {
// // // //     wsRef.current?.close();
// // // //     setRunning(false);
// // // //     setProgress(0);
// // // //     setLiveStats(null);
// // // //     onProgressChange?.(0);
// // // //     onLiveStatsChange?.(null);
// // // //     onRunning?.(false);
// // // //   };

// // // //   const handleExportJSON = () => {
// // // //     if (!result) return;
// // // //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// // // //     const url = URL.createObjectURL(blob);
// // // //     const a = document.createElement("a");
// // // //     a.href = url;
// // // //     a.download = `solengineer-perf-${Date.now()}.json`;
// // // //     a.click();
// // // //     URL.revokeObjectURL(url);
// // // //   };

// // // //   const handleExportExcel = async () => {
// // // //     if (!result) return;
// // // //     try {
// // // //       const response = await exportPerfExcel(result);
// // // //       const blob = new Blob([response.data], {
// // // //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// // // //       });
// // // //       const url = URL.createObjectURL(blob);
// // // //       const a = document.createElement("a");
// // // //       a.href = url;
// // // //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// // // //       a.click();
// // // //       URL.revokeObjectURL(url);
// // // //     } catch {
// // // //       console.error("Excel export failed");
// // // //     }
// // // //   };

// // // //   const warmupImprovement = () => {
// // // //     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
// // // //     const pct = (
// // // //       (result.warmup_avg_ms - result.avg_latency_ms)
// // // //       / result.warmup_avg_ms * 100
// // // //     ).toFixed(0);
// // // //     return `${pct}% faster`;
// // // //   };

// // // //   return (
// // // //     <div style={s.page}>

// // // //       {/* Topbar */}
// // // //       <div style={s.topbar}>
// // // //         <div style={s.topbarLeft}>
// // // //           <span style={s.pageTitle}>SDK Performance Test</span>
// // // //           {running && <span style={s.tagAmber}>● Running</span>}
// // // //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// // // //         </div>
// // // //         <div style={s.topbarRight}>
// // // //           {result && (
// // // //             <div style={{ display: "flex", gap: 8 }}>
// // // //               <button style={s.btnGhost} onClick={handleExportJSON}>
// // // //                 <IconExport color="#5a6675" /> JSON
// // // //               </button>
// // // //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// // // //                 onClick={handleExportExcel}>
// // // //                 <IconExport color="#00874a" /> Excel
// // // //               </button>
// // // //             </div>
// // // //           )}
// // // //         </div>
// // // //       </div>

// // // //       <div style={s.body}>
// // // //         <div style={s.card}>
// // // //           <div style={s.cardTitle}>Configuration</div>

// // // //           {/* Row 1 — Target Type + Delivery Mode */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Target Type</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["topic", "queue"] as const).map((t) => (
// // // //                   <button key={t} onClick={() => setTargetType(t)}
// // // //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// // // //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Delivery Mode</div>
// // // //               <div style={s.toggleRow}>
// // // //                 {(["direct", "persistent"] as const).map((m) => (
// // // //                   <button key={m} onClick={() => setDeliveryMode(m)}
// // // //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// // // //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Queue Type — only when queue selected */}
// // // //           {targetType === "queue" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Queue Type</div>
// // // //               <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
// // // //                 {(["exclusive", "non_exclusive"] as const).map((q) => (
// // // //                   <button key={q} onClick={() => setQueueType(q)}
// // // //                     style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
// // // //                     {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //                   </button>
// // // //                 ))}
// // // //               </div>
// // // //               <div style={s.hint}>
// // // //                 {queueType === "exclusive"
// // // //                   ? "One active consumer — ordered delivery, automatic failover"
// // // //                   : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
// // // //                 }
// // // //               </div>

// // // //               {/* Consumer count — non-exclusive only */}
// // // //               {queueType === "non_exclusive" && (
// // // //                 <div style={{ marginTop: 8 }}>
// // // //                   <div style={s.label}>
// // // //                     Consumer Count
// // // //                     <span style={s.disabledTag}>(non-exclusive only)</span>
// // // //                   </div>
// // // //                   <input
// // // //                     style={{ ...s.input, maxWidth: 200 }}
// // // //                     type="number"
// // // //                     min={1}
// // // //                     max={10}
// // // //                     value={consumerCount}
// // // //                     onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
// // // //                   />
// // // //                   <div style={s.hint}>
// // // //                     Spawns N receiver threads — simulates real multi-consumer load.
// // // //                     Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
// // // //                   </div>
// // // //                 </div>
// // // //               )}
// // // //             </div>
// // // //           )}

// // // //           {/* Row 2 — Target + Template */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// // // //               <input style={s.input} value={target}
// // // //                 onChange={(e) => setTarget(e.target.value)}
// // // //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Template</div>
// // // //               <select style={s.select} value={selectedTemplate}
// // // //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// // // //                 {TEMPLATES.map((t) => (
// // // //                   <option key={t.label} value={t.value}>{t.label}</option>
// // // //                 ))}
// // // //               </select>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 3 — Count + Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Count</div>
// // // //               <input style={s.input} type="number" value={count}
// // // //                 onChange={(e) => setCount(Number(e.target.value))} />
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Message Size (bytes)</div>
// // // //               <input style={s.input} type="number" value={size}
// // // //                 onChange={(e) => setSize(Number(e.target.value))} />
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 4 — Rate Limit + Window Size */}
// // // //           <div style={s.grid2}>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>Rate Limit (msg/sec)</div>
// // // //               <input style={s.input} type="number" value={rateLimit}
// // // //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// // // //                 placeholder="0 = unlimited" />
// // // //               <div style={s.hint}>0 = send as fast as possible</div>
// // // //             </div>
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Window Size
// // // //                 {deliveryMode === "direct" && (
// // // //                   <span style={s.disabledTag}>(persistent only)</span>
// // // //                 )}
// // // //               </div>
// // // //               <input
// // // //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// // // //                 type="number"
// // // //                 value={windowSize}
// // // //                 disabled={deliveryMode === "direct"}
// // // //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// // // //               />
// // // //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// // // //             </div>
// // // //           </div>

// // // //           {/* Row 5 — Warmup Count */}
// // // //           <div style={s.fieldGroup}>
// // // //             <div style={s.label}>Warmup Messages to Skip</div>
// // // //             <input
// // // //               style={{ ...s.input, maxWidth: 280 }}
// // // //               type="number"
// // // //               value={warmupCount}
// // // //               onChange={(e) => setWarmupCount(Number(e.target.value))}
// // // //               placeholder="0"
// // // //             />
// // // //             <div style={s.hint}>
// // // //               First N messages excluded from latency stats — removes TCP slow-start
// // // //               and SDK warmup bias. Set to 0 to include all messages.
// // // //             </div>
// // // //           </div>

// // // //           {/* Custom template */}
// // // //           {selectedTemplate === "custom" && (
// // // //             <div style={s.fieldGroup}>
// // // //               <div style={s.label}>
// // // //                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
// // // //               </div>
// // // //               <input style={s.input} value={customTemplate}
// // // //                 onChange={(e) => setCustomTemplate(e.target.value)}
// // // //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// // // //             </div>
// // // //           )}

// // // //           {/* Template preview */}
// // // //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// // // //             <div style={s.preview}>
// // // //               <span style={s.previewLabel}>Preview: </span>
// // // //               <span style={s.previewValue}>
// // // //                 {selectedTemplate
// // // //                   .replace("{{index}}", "42")
// // // //                   .replace("{{timestamp}}", "1741234567890")
// // // //                   .replace("{{random}}", "xKpQmRnL")}
// // // //               </span>
// // // //             </div>
// // // //           )}

// // // //           {error && <div style={s.errorBox}>{error}</div>}

// // // //           {/* Run / Stop */}
// // // //           <div>
// // // //             {!running
// // // //               ? (
// // // //                 <button style={s.btnPrimary} onClick={handleRun}>
// // // //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// // // //                 </button>
// // // //               ) : (
// // // //                 <button style={s.btnDanger} onClick={handleStop}>
// // // //                   <IconStop color="#fff" size={13} /> Stop Test
// // // //                 </button>
// // // //               )
// // // //             }
// // // //           </div>
// // // //         </div>

// // // //         {/* Progress */}
// // // //         {(running || progress > 0) && (
// // // //           <div style={s.card}>
// // // //             <div style={s.progressHeader}>
// // // //               <span style={s.cardTitle}>
// // // //                 {running ? `Running... ${progress.toFixed(1)}%` : `Completed — ${progress.toFixed(1)}%`}
// // // //               </span>
// // // //               {liveStats && (
// // // //                 <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
// // // //                   <span style={{ ...s.liveStatText, color: "#1a73e8" }}>
// // // //                     ↑ {liveStats.ingress} msg/s ingress
// // // //                   </span>
// // // //                   <span style={{ ...s.liveStatText, color: "#00874a" }}>
// // // //                     ↓ {liveStats.tps} msg/s egress
// // // //                   </span>
// // // //                   <span style={s.liveStatText}>
// // // //                     {liveStats.elapsed}s elapsed
// // // //                   </span>
// // // //                 </div>
// // // //               )}
// // // //             </div>
// // // //             <div style={s.progressTrack}>
// // // //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// // // //             </div>
// // // //           </div>
// // // //         )}

// // // //         {/* Results */}
// // // //         {result && (
// // // //           <div style={s.card}>
// // // //             <div style={s.cardTitle}>Results</div>

// // // //             {/* Badges */}
// // // //             <div style={s.badgeRow}>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// // // //               </span>
// // // //               <span style={s.resultBadge}>
// // // //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // // //               </span>
// // // //               {result.queue_type && (
// // // //                 <span style={s.resultBadge}>
// // // //                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // // //                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
// // // //                 </span>
// // // //               )}
// // // //               {result.rate_limit > 0 && (
// // // //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// // // //               )}
// // // //               {result.window_size && (
// // // //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// // // //               )}
// // // //               {result.warmup_count > 0 && (
// // // //                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
// // // //               )}
// // // //             </div>

// // // //             {/* Stats grid */}
// // // //             <div style={s.statsGrid}>
// // // //               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// // // //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
// // // //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
// // // //               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
// // // //               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
// // // //               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
// // // //               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
// // // //             </div>

// // // //             {/* Warmup analysis */}
// // // //             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
// // // //               <div style={s.warmupBox}>
// // // //                 <div style={s.warmupTitle}>
// // // //                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
// // // //                 </div>
// // // //                 <div style={s.warmupGrid}>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Avg</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
// // // //                     <div style={s.warmupNote}>cold-start latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Warmup Max</div>
// // // //                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
// // // //                     <div style={s.warmupNote}>TCP slow-start peak</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Steady-State Avg</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
// // // //                       {result.avg_latency_ms} ms
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>true production latency</div>
// // // //                   </div>
// // // //                   <div style={s.warmupStat}>
// // // //                     <div style={s.warmupLabel}>Improvement</div>
// // // //                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
// // // //                       {warmupImprovement() ?? "—"}
// // // //                     </div>
// // // //                     <div style={s.warmupNote}>warmup vs steady-state</div>
// // // //                   </div>
// // // //                 </div>
// // // //               </div>
// // // //             )}

// // // //             {/* Egress chart */}
// // // //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// // // //               <div style={{ marginTop: 8 }}>
// // // //                 <div style={s.label}>Egress — Receive rate over time (msg/s)</div>
// // // //                 <ThroughputChart samples={result.throughput_samples} color="#00874a" />
// // // //               </div>
// // // //             )}

// // // //             {/* Ingress chart */}
// // // //             {result.ingress_samples && result.ingress_samples.length > 0 && (
// // // //               <div style={{ marginTop: 8 }}>
// // // //                 <div style={s.label}>Ingress — Publish rate over time (msg/s)</div>
// // // //                 <ThroughputChart samples={result.ingress_samples} color="#1a73e8" />
// // // //               </div>
// // // //             )}
// // // //           </div>
// // // //         )}
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function StatCard({ label, value, unit, highlight }: {
// // // //   label: string; value: string; unit: string; highlight?: boolean;
// // // // }) {
// // // //   return (
// // // //     <div style={{
// // // //       background: "#f5f7fa",
// // // //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// // // //       borderRadius: 8, padding: "12px 14px"
// // // //     }}>
// // // //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// // // //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// // // //         {value}
// // // //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
// // // //           {unit}
// // // //         </span>
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }

// // // // function ThroughputChart({ samples, color }: { samples: number[]; color: string }) {
// // // //   const max = Math.max(...samples, 1);
// // // //   const W = 600;
// // // //   const H = 80;
// // // //   const pts = samples.map((v, i) => {
// // // //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// // // //     const y = H - (v / max) * (H - 8);
// // // //     return `${x},${y}`;
// // // //   }).join(" ");

// // // //   return (
// // // //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// // // //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 6 }}>
// // // //       <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
// // // //       {samples.map((v, i) => (
// // // //         <circle key={i}
// // // //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// // // //           cy={H - (v / max) * (H - 8)}
// // // //           r="3" fill={color}
// // // //         />
// // // //       ))}
// // // //     </svg>
// // // //   );
// // // // }

// // // // const s: Record<string, React.CSSProperties> = {
// // // //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// // // //   topbar: {
// // // //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// // // //     display: "flex", alignItems: "center", padding: "0 20px",
// // // //     justifyContent: "space-between", flexShrink: 0
// // // //   },
// // // //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// // // //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// // // //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// // // //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// // // //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// // // //   btnGhost: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// // // //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// // // //   },
// // // //   body: {
// // // //     flex: 1, overflowY: "auto", padding: 20,
// // // //     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   card: {
// // // //     background: "#fff", border: "1px solid #e1e6eb",
// // // //     borderRadius: 10, padding: 16,
// // // //     display: "flex", flexDirection: "column", gap: 14
// // // //   },
// // // //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// // // //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// // // //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// // // //   label: {
// // // //     fontSize: 11, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   disabledTag: {
// // // //     fontSize: 10, color: "#b0b8c0",
// // // //     textTransform: "none", fontWeight: 400, marginLeft: 4
// // // //   },
// // // //   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
// // // //   input: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// // // //   },
// // // //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// // // //   select: {
// // // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // // //     padding: "8px 12px", color: "#1a2733", fontSize: 13,
// // // //     outline: "none", cursor: "pointer"
// // // //   },
// // // //   toggleRow: { display: "flex", gap: 8 },
// // // //   toggleBtn: {
// // // //     background: "#fff", border: "1px solid #d4dae0",
// // // //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// // // //     fontSize: 13, cursor: "pointer", flex: 1
// // // //   },
// // // //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// // // //   preview: {
// // // //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     borderRadius: 6, padding: "8px 12px"
// // // //   },
// // // //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// // // //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// // // //   errorBox: {
// // // //     background: "#fce8e6", border: "1px solid #f5b9b3",
// // // //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// // // //   },
// // // //   btnPrimary: {
// // // //     background: "#1a73e8", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   btnDanger: {
// // // //     background: "#d93025", color: "#fff", border: "none",
// // // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // // //   },
// // // //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// // // //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// // // //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// // // //   progressFill: {
// // // //     height: "100%", background: "#1a73e8",
// // // //     borderRadius: 4, transition: "width 0.3s ease"
// // // //   },
// // // //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// // // //   resultBadge: {
// // // //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// // // //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// // // //   },
// // // //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
// // // //   warmupBox: {
// // // //     background: "#fef9ec", border: "1px solid #fcd9a0",
// // // //     borderRadius: 8, padding: "14px 16px",
// // // //     display: "flex", flexDirection: "column", gap: 12
// // // //   },
// // // //   warmupTitle: { fontSize: 12, fontWeight: 600, color: "#e8710a" },
// // // //   warmupGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
// // // //   warmupStat: { display: "flex", flexDirection: "column", gap: 3 },
// // // //   warmupLabel: {
// // // //     fontSize: 10, fontWeight: 600, color: "#8a96a3",
// // // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // // //   },
// // // //   warmupValue: { fontSize: 18, fontWeight: 600, color: "#1a2733" },
// // // //   warmupNote: { fontSize: 10, color: "#b0b8c0" }
// // // // };










// // // import { useState, useRef } from "react";
// // // import { PerfResult } from "../types";
// // // import { IconPerf, IconStop, IconExport } from "./Icons";
// // // import { exportPerfExcel } from "../api";

// // // const TEMPLATES = [
// // //   { label: "Raw payload", value: "" },
// // //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// // //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// // //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// // //   { label: "Custom", value: "custom" },
// // // ];

// // // interface PerfPanelProps {
// // //   onResult?: (r: PerfResult) => void;
// // //   onIngressSample?: (v: number) => void;
// // //   onEgressSample?: (v: number) => void;
// // //   onRunning?: (v: boolean) => void;
// // // }

// // // export default function PerfPanel({
// // //   onResult, onIngressSample, onEgressSample, onRunning
// // // }: PerfPanelProps) {

// // //   const [target, setTarget] = useState("perf/test");
// // //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// // //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// // //   const [count, setCount] = useState(1000);
// // //   const [size, setSize] = useState(256);
// // //   const [rateLimit, setRateLimit] = useState(0);
// // //   const [windowSize, setWindowSize] = useState(50);
// // //   const [selectedTemplate, setSelectedTemplate] = useState("");
// // //   const [customTemplate, setCustomTemplate] = useState("");
// // //   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
// // //   const [warmupCount, setWarmupCount] = useState(50);
// // //   const [consumerCount, setConsumerCount] = useState(1);
// // //   const [running, setRunning] = useState(false);
// // //   const [progress, setProgress] = useState(0);
// // //   const [liveStats, setLiveStats] = useState<{ tps: number; ingress: number; elapsed: number } | null>(null);
// // //   const [result, setResult] = useState<PerfResult | null>(null);
// // //   const [error, setError] = useState("");
// // //   const wsRef = useRef<WebSocket | null>(null);

// // //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// // //   const handleRun = () => {
// // //     if (wsRef.current) wsRef.current.close();
// // //     setRunning(true);
// // //     setError("");
// // //     setResult(null);
// // //     setProgress(0);
// // //     setLiveStats(null);
// // //     onRunning?.(true);

// // //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// // //     wsRef.current = ws;

// // //     ws.onopen = () => {
// // //       ws.send(JSON.stringify({
// // //         target,
// // //         target_type: targetType,
// // //         message_count: count,
// // //         message_size: size,
// // //         message_template: effectiveTemplate,
// // //         delivery_mode: deliveryMode,
// // //         rate_limit: rateLimit,
// // //         window_size: windowSize,
// // //         queue_type: queueType,
// // //         warmup_count: warmupCount,
// // //         consumer_count: consumerCount,
// // //       }));
// // //     };

// // //     ws.onmessage = (e) => {
// // //       const data = JSON.parse(e.data);
// // //       if (data.type === "progress") {
// // //         setProgress(data.percent);
// // //         setLiveStats({
// // //           tps: data.tps,
// // //           ingress: data.ingress_tps ?? 0,
// // //           elapsed: data.elapsed
// // //         });
// // //         // Fire callbacks to Dashboard for Charts tab
// // //         if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
// // //         if (data.tps !== undefined) onEgressSample?.(data.tps);

// // //       } else if (data.type === "complete") {
// // //         setResult(data.results);
// // //         setRunning(false);
// // //         setProgress(100);
// // //         onResult?.(data.results);
// // //         onRunning?.(false);

// // //       } else if (data.error) {
// // //         setError(data.error);
// // //         setRunning(false);
// // //         onRunning?.(false);
// // //       }
// // //     };

// // //     ws.onclose = () => {
// // //       setRunning(false);
// // //       onRunning?.(false);
// // //     };
// // //   };

// // //   const handleStop = () => {
// // //     wsRef.current?.close();
// // //     setRunning(false);
// // //     setProgress(0);
// // //     setLiveStats(null);
// // //     onRunning?.(false);
// // //   };

// // //   const handleExportJSON = () => {
// // //     if (!result) return;
// // //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// // //     const url = URL.createObjectURL(blob);
// // //     const a = document.createElement("a");
// // //     a.href = url;
// // //     a.download = `solengineer-perf-${Date.now()}.json`;
// // //     a.click();
// // //     URL.revokeObjectURL(url);
// // //   };

// // //   const handleExportExcel = async () => {
// // //     if (!result) return;
// // //     try {
// // //       const response = await exportPerfExcel(result);
// // //       const blob = new Blob([response.data], {
// // //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// // //       });
// // //       const url = URL.createObjectURL(blob);
// // //       const a = document.createElement("a");
// // //       a.href = url;
// // //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// // //       a.click();
// // //       URL.revokeObjectURL(url);
// // //     } catch {
// // //       console.error("Excel export failed");
// // //     }
// // //   };

// // //   const warmupImprovement = () => {
// // //     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
// // //     const pct = (
// // //       (result.warmup_avg_ms - result.avg_latency_ms)
// // //       / result.warmup_avg_ms * 100
// // //     ).toFixed(0);
// // //     return `${pct}% faster`;
// // //   };

// // //   return (
// // //     <div style={s.page}>

// // //       {/* Topbar */}
// // //       <div style={s.topbar}>
// // //         <div style={s.topbarLeft}>
// // //           <span style={s.pageTitle}>SDK Performance Test</span>
// // //           {running && <span style={s.tagAmber}>● Running</span>}
// // //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// // //         </div>
// // //         <div style={s.topbarRight}>
// // //           {result && (
// // //             <div style={{ display: "flex", gap: 8 }}>
// // //               <button style={s.btnGhost} onClick={handleExportJSON}>
// // //                 <IconExport color="#5a6675" /> JSON
// // //               </button>
// // //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// // //                 onClick={handleExportExcel}>
// // //                 <IconExport color="#00874a" /> Excel
// // //               </button>
// // //             </div>
// // //           )}
// // //         </div>
// // //       </div>

// // //       <div style={s.body}>
// // //         <div style={s.card}>
// // //           <div style={s.cardTitle}>Configuration</div>

// // //           {/* Row 1 — Target Type + Delivery Mode */}
// // //           <div style={s.grid2}>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Target Type</div>
// // //               <div style={s.toggleRow}>
// // //                 {(["topic", "queue"] as const).map((t) => (
// // //                   <button key={t} onClick={() => setTargetType(t)}
// // //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// // //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// // //                   </button>
// // //                 ))}
// // //               </div>
// // //             </div>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Delivery Mode</div>
// // //               <div style={s.toggleRow}>
// // //                 {(["direct", "persistent"] as const).map((m) => (
// // //                   <button key={m} onClick={() => setDeliveryMode(m)}
// // //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// // //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // //                   </button>
// // //                 ))}
// // //               </div>
// // //             </div>
// // //           </div>

// // //           {/* Queue Type — only when queue selected */}
// // //           {targetType === "queue" && (
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Queue Type</div>
// // //               <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
// // //                 {(["exclusive", "non_exclusive"] as const).map((q) => (
// // //                   <button key={q} onClick={() => setQueueType(q)}
// // //                     style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
// // //                     {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // //                   </button>
// // //                 ))}
// // //               </div>
// // //               <div style={s.hint}>
// // //                 {queueType === "exclusive"
// // //                   ? "One active consumer — ordered delivery, automatic failover"
// // //                   : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
// // //                 }
// // //               </div>

// // //               {/* Consumer count — non-exclusive only */}
// // //               {queueType === "non_exclusive" && (
// // //                 <div style={{ marginTop: 8 }}>
// // //                   <div style={s.label}>
// // //                     Consumer Count
// // //                     <span style={s.disabledTag}>(non-exclusive only)</span>
// // //                   </div>
// // //                   <input
// // //                     style={{ ...s.input, maxWidth: 200 }}
// // //                     type="number"
// // //                     min={1}
// // //                     max={10}
// // //                     value={consumerCount}
// // //                     onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
// // //                   />
// // //                   <div style={s.hint}>
// // //                     Spawns N receiver threads — simulates real multi-consumer load.
// // //                     Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
// // //                   </div>
// // //                 </div>
// // //               )}
// // //             </div>
// // //           )}

// // //           {/* Row 2 — Target + Template */}
// // //           <div style={s.grid2}>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// // //               <input style={s.input} value={target}
// // //                 onChange={(e) => setTarget(e.target.value)}
// // //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// // //             </div>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Message Template</div>
// // //               <select style={s.select} value={selectedTemplate}
// // //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// // //                 {TEMPLATES.map((t) => (
// // //                   <option key={t.label} value={t.value}>{t.label}</option>
// // //                 ))}
// // //               </select>
// // //             </div>
// // //           </div>

// // //           {/* Row 3 — Count + Size */}
// // //           <div style={s.grid2}>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Message Count</div>
// // //               <input style={s.input} type="number" value={count}
// // //                 onChange={(e) => setCount(Number(e.target.value))} />
// // //             </div>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Message Size (bytes)</div>
// // //               <input style={s.input} type="number" value={size}
// // //                 onChange={(e) => setSize(Number(e.target.value))} />
// // //             </div>
// // //           </div>

// // //           {/* Row 4 — Rate Limit + Window Size */}
// // //           <div style={s.grid2}>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>Rate Limit (msg/sec)</div>
// // //               <input style={s.input} type="number" value={rateLimit}
// // //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// // //                 placeholder="0 = unlimited" />
// // //               <div style={s.hint}>0 = send as fast as possible</div>
// // //             </div>
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>
// // //                 Window Size
// // //                 {deliveryMode === "direct" && (
// // //                   <span style={s.disabledTag}>(persistent only)</span>
// // //                 )}
// // //               </div>
// // //               <input
// // //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// // //                 type="number"
// // //                 value={windowSize}
// // //                 disabled={deliveryMode === "direct"}
// // //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// // //               />
// // //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// // //             </div>
// // //           </div>

// // //           {/* Row 5 — Warmup Count */}
// // //           <div style={s.fieldGroup}>
// // //             <div style={s.label}>Warmup Messages to Skip</div>
// // //             <input
// // //               style={{ ...s.input, maxWidth: 280 }}
// // //               type="number"
// // //               value={warmupCount}
// // //               onChange={(e) => setWarmupCount(Number(e.target.value))}
// // //               placeholder="0"
// // //             />
// // //             <div style={s.hint}>
// // //               First N messages excluded from latency stats — removes TCP slow-start
// // //               and SDK warmup bias. Set to 0 to include all messages.
// // //             </div>
// // //           </div>

// // //           {/* Custom template */}
// // //           {selectedTemplate === "custom" && (
// // //             <div style={s.fieldGroup}>
// // //               <div style={s.label}>
// // //                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
// // //               </div>
// // //               <input style={s.input} value={customTemplate}
// // //                 onChange={(e) => setCustomTemplate(e.target.value)}
// // //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// // //             </div>
// // //           )}

// // //           {/* Template preview */}
// // //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// // //             <div style={s.preview}>
// // //               <span style={s.previewLabel}>Preview: </span>
// // //               <span style={s.previewValue}>
// // //                 {selectedTemplate
// // //                   .replace("{{index}}", "42")
// // //                   .replace("{{timestamp}}", "1741234567890")
// // //                   .replace("{{random}}", "xKpQmRnL")}
// // //               </span>
// // //             </div>
// // //           )}

// // //           {error && <div style={s.errorBox}>{error}</div>}

// // //           {/* Run / Stop */}
// // //           <div>
// // //             {!running
// // //               ? (
// // //                 <button style={s.btnPrimary} onClick={handleRun}>
// // //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// // //                 </button>
// // //               ) : (
// // //                 <button style={s.btnDanger} onClick={handleStop}>
// // //                   <IconStop color="#fff" size={13} /> Stop Test
// // //                 </button>
// // //               )
// // //             }
// // //           </div>
// // //         </div>

// // //         {/* Progress */}
// // //         {running && (
// // //           <div style={s.card}>
// // //             <div style={s.progressHeader}>
// // //               <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
// // //               {liveStats && (
// // //                 <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
// // //                   <span style={{ ...s.liveStatText, color: "#1a73e8" }}>
// // //                     ↑ {liveStats.ingress} msg/s ingress
// // //                   </span>
// // //                   <span style={{ ...s.liveStatText, color: "#00874a" }}>
// // //                     ↓ {liveStats.tps} msg/s egress
// // //                   </span>
// // //                   <span style={s.liveStatText}>
// // //                     {liveStats.elapsed}s elapsed
// // //                   </span>
// // //                 </div>
// // //               )}
// // //             </div>
// // //             <div style={s.progressTrack}>
// // //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// // //             </div>
// // //           </div>
// // //         )}

// // //         {/* Results */}
// // //         {result && (
// // //           <div style={s.card}>
// // //             <div style={s.cardTitle}>Results</div>

// // //             {/* Badges */}
// // //             <div style={s.badgeRow}>
// // //               <span style={s.resultBadge}>
// // //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// // //               </span>
// // //               <span style={s.resultBadge}>
// // //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// // //               </span>
// // //               {result.queue_type && (
// // //                 <span style={s.resultBadge}>
// // //                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// // //                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
// // //                 </span>
// // //               )}
// // //               {result.rate_limit > 0 && (
// // //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// // //               )}
// // //               {result.window_size && (
// // //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// // //               )}
// // //               {result.warmup_count > 0 && (
// // //                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
// // //               )}
// // //             </div>

// // //             {/* Stats grid */}
// // //             <div style={s.statsGrid}>
// // //               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// // //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
// // //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
// // //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
// // //               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
// // //               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
// // //               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
// // //               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
// // //               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
// // //               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
// // //             </div>

// // //             {/* Warmup analysis */}
// // //             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
// // //               <div style={s.warmupBox}>
// // //                 <div style={s.warmupTitle}>
// // //                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
// // //                 </div>
// // //                 <div style={s.warmupGrid}>
// // //                   <div style={s.warmupStat}>
// // //                     <div style={s.warmupLabel}>Warmup Avg</div>
// // //                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
// // //                     <div style={s.warmupNote}>cold-start latency</div>
// // //                   </div>
// // //                   <div style={s.warmupStat}>
// // //                     <div style={s.warmupLabel}>Warmup Max</div>
// // //                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
// // //                     <div style={s.warmupNote}>TCP slow-start peak</div>
// // //                   </div>
// // //                   <div style={s.warmupStat}>
// // //                     <div style={s.warmupLabel}>Steady-State Avg</div>
// // //                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
// // //                       {result.avg_latency_ms} ms
// // //                     </div>
// // //                     <div style={s.warmupNote}>true production latency</div>
// // //                   </div>
// // //                   <div style={s.warmupStat}>
// // //                     <div style={s.warmupLabel}>Improvement</div>
// // //                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
// // //                       {warmupImprovement() ?? "—"}
// // //                     </div>
// // //                     <div style={s.warmupNote}>warmup vs steady-state</div>
// // //                   </div>
// // //                 </div>
// // //               </div>
// // //             )}

// // //             {/* Egress throughput chart */}
// // //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// // //               <div style={{ marginTop: 8 }}>
// // //                 <div style={s.label}>Egress — Receive rate over time (msg/s)</div>
// // //                 <ThroughputChart
// // //                   samples={result.throughput_samples}
// // //                   color="#00874a"
// // //                 />
// // //               </div>
// // //             )}

// // //             {/* Ingress throughput chart */}
// // //             {result.ingress_samples && result.ingress_samples.length > 0 && (
// // //               <div style={{ marginTop: 8 }}>
// // //                 <div style={s.label}>Ingress — Publish rate over time (msg/s)</div>
// // //                 <ThroughputChart
// // //                   samples={result.ingress_samples}
// // //                   color="#1a73e8"
// // //                 />
// // //               </div>
// // //             )}
// // //           </div>
// // //         )}
// // //       </div>
// // //     </div>
// // //   );
// // // }

// // // function StatCard({ label, value, unit, highlight }: {
// // //   label: string; value: string; unit: string; highlight?: boolean;
// // // }) {
// // //   return (
// // //     <div style={{
// // //       background: "#f5f7fa",
// // //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// // //       borderRadius: 8, padding: "12px 14px"
// // //     }}>
// // //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// // //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// // //         {value}
// // //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
// // //           {unit}
// // //         </span>
// // //       </div>
// // //     </div>
// // //   );
// // // }

// // // function ThroughputChart({ samples, color }: { samples: number[]; color: string }) {
// // //   const max = Math.max(...samples, 1);
// // //   const W = 600;
// // //   const H = 80;
// // //   const pts = samples.map((v, i) => {
// // //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// // //     const y = H - (v / max) * (H - 8);
// // //     return `${x},${y}`;
// // //   }).join(" ");

// // //   return (
// // //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// // //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 6 }}>
// // //       <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
// // //       {samples.map((v, i) => (
// // //         <circle key={i}
// // //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// // //           cy={H - (v / max) * (H - 8)}
// // //           r="3" fill={color}
// // //         />
// // //       ))}
// // //     </svg>
// // //   );
// // // }

// // // const s: Record<string, React.CSSProperties> = {
// // //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// // //   topbar: {
// // //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// // //     display: "flex", alignItems: "center", padding: "0 20px",
// // //     justifyContent: "space-between", flexShrink: 0
// // //   },
// // //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// // //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// // //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// // //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// // //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// // //   btnGhost: {
// // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// // //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// // //   },
// // //   body: {
// // //     flex: 1, overflowY: "auto", padding: 20,
// // //     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
// // //   },
// // //   card: {
// // //     background: "#fff", border: "1px solid #e1e6eb",
// // //     borderRadius: 10, padding: 16,
// // //     display: "flex", flexDirection: "column", gap: 14
// // //   },
// // //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// // //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// // //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// // //   label: {
// // //     fontSize: 11, fontWeight: 600, color: "#8a96a3",
// // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // //   },
// // //   disabledTag: {
// // //     fontSize: 10, color: "#b0b8c0",
// // //     textTransform: "none", fontWeight: 400, marginLeft: 4
// // //   },
// // //   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
// // //   input: {
// // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// // //   },
// // //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// // //   select: {
// // //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// // //     padding: "8px 12px", color: "#1a2733", fontSize: 13,
// // //     outline: "none", cursor: "pointer"
// // //   },
// // //   toggleRow: { display: "flex", gap: 8 },
// // //   toggleBtn: {
// // //     background: "#fff", border: "1px solid #d4dae0",
// // //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// // //     fontSize: 13, cursor: "pointer", flex: 1
// // //   },
// // //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// // //   preview: {
// // //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// // //     borderRadius: 6, padding: "8px 12px"
// // //   },
// // //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// // //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// // //   errorBox: {
// // //     background: "#fce8e6", border: "1px solid #f5b9b3",
// // //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// // //   },
// // //   btnPrimary: {
// // //     background: "#1a73e8", color: "#fff", border: "none",
// // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // //   },
// // //   btnDanger: {
// // //     background: "#d93025", color: "#fff", border: "none",
// // //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// // //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// // //   },
// // //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// // //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// // //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// // //   progressFill: {
// // //     height: "100%", background: "#1a73e8",
// // //     borderRadius: 4, transition: "width 0.3s ease"
// // //   },
// // //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// // //   resultBadge: {
// // //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// // //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// // //   },
// // //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
// // //   warmupBox: {
// // //     background: "#fef9ec", border: "1px solid #fcd9a0",
// // //     borderRadius: 8, padding: "14px 16px",
// // //     display: "flex", flexDirection: "column", gap: 12
// // //   },
// // //   warmupTitle: { fontSize: 12, fontWeight: 600, color: "#e8710a" },
// // //   warmupGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
// // //   warmupStat: { display: "flex", flexDirection: "column", gap: 3 },
// // //   warmupLabel: {
// // //     fontSize: 10, fontWeight: 600, color: "#8a96a3",
// // //     textTransform: "uppercase", letterSpacing: "0.6px"
// // //   },
// // //   warmupValue: { fontSize: 18, fontWeight: 600, color: "#1a2733" },
// // //   warmupNote: { fontSize: 10, color: "#b0b8c0" }
// // // };




// // import { useState, useRef } from "react";
// // import { PerfResult } from "../types";
// // import { IconPerf, IconStop, IconExport } from "./Icons";
// // import { exportPerfExcel } from "../api";

// // const TEMPLATES = [
// //   { label: "Raw payload", value: "" },
// //   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
// //   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
// //   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
// //   { label: "Custom", value: "custom" },
// // ];
// // interface PerfPanelProps {
// //   onResult?: (r: PerfResult) => void;
// //   onIngressSample?: (v: number) => void;
// //   onEgressSample?: (v: number) => void;
// //   onRunning?: (v: boolean) => void;
// //   // Lifted state — survives tab switches
// //   savedResult?: PerfResult | null;
// //   savedProgress?: number;
// //   savedLiveStats?: { tps: number; ingress: number; elapsed: number } | null;
// //   savedError?: string;
// //   onProgressChange?: (v: number) => void;
// //   onLiveStatsChange?: (v: { tps: number; ingress: number; elapsed: number } | null) => void;
// //   onErrorChange?: (v: string) => void;
// // }

// // export default function PerfPanel({
// //   onResult, onIngressSample, onEgressSample, onRunning,
// //   savedResult, savedProgress, savedLiveStats, savedError,
// //   onProgressChange, onLiveStatsChange, onErrorChange
// // }: PerfPanelProps) {
// //   const [target, setTarget] = useState("perf/test");
// //   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
// //   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
// //   const [count, setCount] = useState(1000);
// //   const [size, setSize] = useState(256);
// //   const [rateLimit, setRateLimit] = useState(0);
// //   const [windowSize, setWindowSize] = useState(50);
// //   const [selectedTemplate, setSelectedTemplate] = useState("");
// //   const [customTemplate, setCustomTemplate] = useState("");
// //   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
// //   const [warmupCount, setWarmupCount] = useState(50);
// //   const [consumerCount, setConsumerCount] = useState(1);
// //   const [running, setRunning] = useState(false);
// //   const [progress, setProgress] = useState(0);
// //   const [liveStats, setLiveStats] = useState<{ tps: number; ingress: number; elapsed: number } | null>(null);
// //   const [result, setResult] = useState<PerfResult | null>(null);
// //   const [error, setError] = useState("");
// //   const wsRef = useRef<WebSocket | null>(null);

// //   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

// //   const handleRun = () => {
// //     if (wsRef.current) wsRef.current.close();
// //     setRunning(true);
// //     setError("");
// //     setResult(null);
// //     setProgress(0);
// //     setLiveStats(null);
// //     onRunning?.(true);

// //     const ws = new WebSocket("ws://localhost:8000/ws/perf");
// //     wsRef.current = ws;

// //     ws.onopen = () => {
// //       ws.send(JSON.stringify({
// //         target,
// //         target_type: targetType,
// //         message_count: count,
// //         message_size: size,
// //         message_template: effectiveTemplate,
// //         delivery_mode: deliveryMode,
// //         rate_limit: rateLimit,
// //         window_size: windowSize,
// //         queue_type: queueType,
// //         warmup_count: warmupCount,
// //         consumer_count: consumerCount,
// //       }));
// //     };

// //     ws.onmessage = (e) => {
// //       const data = JSON.parse(e.data);
// //       if (data.type === "progress") {
// //         setProgress(data.percent);
// //         setLiveStats({
// //           tps: data.tps,
// //           ingress: data.ingress_tps ?? 0,
// //           elapsed: data.elapsed
// //         });
// //         // Fire callbacks to Dashboard for Charts tab
// //         if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
// //         if (data.tps !== undefined) onEgressSample?.(data.tps);

// //       } else if (data.type === "complete") {
// //         setResult(data.results);
// //         setRunning(false);
// //         setProgress(100);
// //         onResult?.(data.results);
// //         onRunning?.(false);

// //       } else if (data.error) {
// //         setError(data.error);
// //         setRunning(false);
// //         onRunning?.(false);
// //       }
// //     };

// //     ws.onclose = () => {
// //       setRunning(false);
// //       onRunning?.(false);
// //     };
// //   };

// //   const handleStop = () => {
// //     wsRef.current?.close();
// //     setRunning(false);
// //     setProgress(0);
// //     setLiveStats(null);
// //     onRunning?.(false);
// //   };

// //   const handleExportJSON = () => {
// //     if (!result) return;
// //     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
// //     const url = URL.createObjectURL(blob);
// //     const a = document.createElement("a");
// //     a.href = url;
// //     a.download = `solengineer-perf-${Date.now()}.json`;
// //     a.click();
// //     URL.revokeObjectURL(url);
// //   };

// //   const handleExportExcel = async () => {
// //     if (!result) return;
// //     try {
// //       const response = await exportPerfExcel(result);
// //       const blob = new Blob([response.data], {
// //         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
// //       });
// //       const url = URL.createObjectURL(blob);
// //       const a = document.createElement("a");
// //       a.href = url;
// //       a.download = `solengineer-perf-${Date.now()}.xlsx`;
// //       a.click();
// //       URL.revokeObjectURL(url);
// //     } catch {
// //       console.error("Excel export failed");
// //     }
// //   };

// //   const warmupImprovement = () => {
// //     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
// //     const pct = (
// //       (result.warmup_avg_ms - result.avg_latency_ms)
// //       / result.warmup_avg_ms * 100
// //     ).toFixed(0);
// //     return `${pct}% faster`;
// //   };

// //   return (
// //     <div style={s.page}>

// //       {/* Topbar */}
// //       <div style={s.topbar}>
// //         <div style={s.topbarLeft}>
// //           <span style={s.pageTitle}>SDK Performance Test</span>
// //           {running && <span style={s.tagAmber}>● Running</span>}
// //           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
// //         </div>
// //         <div style={s.topbarRight}>
// //           {result && (
// //             <div style={{ display: "flex", gap: 8 }}>
// //               <button style={s.btnGhost} onClick={handleExportJSON}>
// //                 <IconExport color="#5a6675" /> JSON
// //               </button>
// //               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
// //                 onClick={handleExportExcel}>
// //                 <IconExport color="#00874a" /> Excel
// //               </button>
// //             </div>
// //           )}
// //         </div>
// //       </div>

// //       <div style={s.body}>
// //         <div style={s.card}>
// //           <div style={s.cardTitle}>Configuration</div>

// //           {/* Row 1 — Target Type + Delivery Mode */}
// //           <div style={s.grid2}>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Target Type</div>
// //               <div style={s.toggleRow}>
// //                 {(["topic", "queue"] as const).map((t) => (
// //                   <button key={t} onClick={() => setTargetType(t)}
// //                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
// //                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
// //                   </button>
// //                 ))}
// //               </div>
// //             </div>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Delivery Mode</div>
// //               <div style={s.toggleRow}>
// //                 {(["direct", "persistent"] as const).map((m) => (
// //                   <button key={m} onClick={() => setDeliveryMode(m)}
// //                     style={{ ...s.toggleBtn, ...(deliveryMode === m ? s.toggleActive : {}) }}>
// //                     {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// //                   </button>
// //                 ))}
// //               </div>
// //             </div>
// //           </div>

// //           {/* Queue Type — only when queue selected */}
// //           {targetType === "queue" && (
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Queue Type</div>
// //               <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
// //                 {(["exclusive", "non_exclusive"] as const).map((q) => (
// //                   <button key={q} onClick={() => setQueueType(q)}
// //                     style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
// //                     {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// //                   </button>
// //                 ))}
// //               </div>
// //               <div style={s.hint}>
// //                 {queueType === "exclusive"
// //                   ? "One active consumer — ordered delivery, automatic failover"
// //                   : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
// //                 }
// //               </div>

// //               {/* Consumer count — non-exclusive only */}
// //               {queueType === "non_exclusive" && (
// //                 <div style={{ marginTop: 8 }}>
// //                   <div style={s.label}>
// //                     Consumer Count
// //                     <span style={s.disabledTag}>(non-exclusive only)</span>
// //                   </div>
// //                   <input
// //                     style={{ ...s.input, maxWidth: 200 }}
// //                     type="number"
// //                     min={1}
// //                     max={10}
// //                     value={consumerCount}
// //                     onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
// //                   />
// //                   <div style={s.hint}>
// //                     Spawns N receiver threads — simulates real multi-consumer load.
// //                     Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
// //                   </div>
// //                 </div>
// //               )}
// //             </div>
// //           )}

// //           {/* Row 2 — Target + Template */}
// //           <div style={s.grid2}>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
// //               <input style={s.input} value={target}
// //                 onChange={(e) => setTarget(e.target.value)}
// //                 placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
// //             </div>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Message Template</div>
// //               <select style={s.select} value={selectedTemplate}
// //                 onChange={(e) => setSelectedTemplate(e.target.value)}>
// //                 {TEMPLATES.map((t) => (
// //                   <option key={t.label} value={t.value}>{t.label}</option>
// //                 ))}
// //               </select>
// //             </div>
// //           </div>

// //           {/* Row 3 — Count + Size */}
// //           <div style={s.grid2}>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Message Count</div>
// //               <input style={s.input} type="number" value={count}
// //                 onChange={(e) => setCount(Number(e.target.value))} />
// //             </div>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Message Size (bytes)</div>
// //               <input style={s.input} type="number" value={size}
// //                 onChange={(e) => setSize(Number(e.target.value))} />
// //             </div>
// //           </div>

// //           {/* Row 4 — Rate Limit + Window Size */}
// //           <div style={s.grid2}>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>Rate Limit (msg/sec)</div>
// //               <input style={s.input} type="number" value={rateLimit}
// //                 onChange={(e) => setRateLimit(Number(e.target.value))}
// //                 placeholder="0 = unlimited" />
// //               <div style={s.hint}>0 = send as fast as possible</div>
// //             </div>
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>
// //                 Window Size
// //                 {deliveryMode === "direct" && (
// //                   <span style={s.disabledTag}>(persistent only)</span>
// //                 )}
// //               </div>
// //               <input
// //                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
// //                 type="number"
// //                 value={windowSize}
// //                 disabled={deliveryMode === "direct"}
// //                 onChange={(e) => setWindowSize(Number(e.target.value))}
// //               />
// //               <div style={s.hint}>Max unacknowledged messages in-flight</div>
// //             </div>
// //           </div>

// //           {/* Row 5 — Warmup Count */}
// //           <div style={s.fieldGroup}>
// //             <div style={s.label}>Warmup Messages to Skip</div>
// //             <input
// //               style={{ ...s.input, maxWidth: 280 }}
// //               type="number"
// //               value={warmupCount}
// //               onChange={(e) => setWarmupCount(Number(e.target.value))}
// //               placeholder="0"
// //             />
// //             <div style={s.hint}>
// //               First N messages excluded from latency stats — removes TCP slow-start
// //               and SDK warmup bias. Set to 0 to include all messages.
// //             </div>
// //           </div>

// //           {/* Custom template */}
// //           {selectedTemplate === "custom" && (
// //             <div style={s.fieldGroup}>
// //               <div style={s.label}>
// //                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
// //               </div>
// //               <input style={s.input} value={customTemplate}
// //                 onChange={(e) => setCustomTemplate(e.target.value)}
// //                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
// //             </div>
// //           )}

// //           {/* Template preview */}
// //           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
// //             <div style={s.preview}>
// //               <span style={s.previewLabel}>Preview: </span>
// //               <span style={s.previewValue}>
// //                 {selectedTemplate
// //                   .replace("{{index}}", "42")
// //                   .replace("{{timestamp}}", "1741234567890")
// //                   .replace("{{random}}", "xKpQmRnL")}
// //               </span>
// //             </div>
// //           )}

// //           {error && <div style={s.errorBox}>{error}</div>}

// //           {/* Run / Stop */}
// //           <div>
// //             {!running
// //               ? (
// //                 <button style={s.btnPrimary} onClick={handleRun}>
// //                   <IconPerf color="#fff" size={13} /> Run Perf Test
// //                 </button>
// //               ) : (
// //                 <button style={s.btnDanger} onClick={handleStop}>
// //                   <IconStop color="#fff" size={13} /> Stop Test
// //                 </button>
// //               )
// //             }
// //           </div>
// //         </div>

// //         {/* Progress */}
// //         {running && (
// //           <div style={s.card}>
// //             <div style={s.progressHeader}>
// //               <span style={s.cardTitle}>Running... {progress.toFixed(1)}%</span>
// //               {liveStats && (
// //                 <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
// //                   <span style={{ ...s.liveStatText, color: "#1a73e8" }}>
// //                     ↑ {liveStats.ingress} msg/s ingress
// //                   </span>
// //                   <span style={{ ...s.liveStatText, color: "#00874a" }}>
// //                     ↓ {liveStats.tps} msg/s egress
// //                   </span>
// //                   <span style={s.liveStatText}>
// //                     {liveStats.elapsed}s elapsed
// //                   </span>
// //                 </div>
// //               )}
// //             </div>
// //             <div style={s.progressTrack}>
// //               <div style={{ ...s.progressFill, width: `${progress}%` }} />
// //             </div>
// //           </div>
// //         )}

// //         {/* Results */}
// //         {result && (
// //           <div style={s.card}>
// //             <div style={s.cardTitle}>Results</div>

// //             {/* Badges */}
// //             <div style={s.badgeRow}>
// //               <span style={s.resultBadge}>
// //                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
// //               </span>
// //               <span style={s.resultBadge}>
// //                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
// //               </span>
// //               {result.queue_type && (
// //                 <span style={s.resultBadge}>
// //                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
// //                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
// //                 </span>
// //               )}
// //               {result.rate_limit > 0 && (
// //                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
// //               )}
// //               {result.window_size && (
// //                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
// //               )}
// //               {result.warmup_count > 0 && (
// //                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
// //               )}
// //             </div>

// //             {/* Stats grid */}
// //             <div style={s.statsGrid}>
// //               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
// //               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
// //               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
// //               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
// //               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
// //               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
// //               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
// //               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
// //               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
// //               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
// //             </div>

// //             {/* Warmup analysis */}
// //             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
// //               <div style={s.warmupBox}>
// //                 <div style={s.warmupTitle}>
// //                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
// //                 </div>
// //                 <div style={s.warmupGrid}>
// //                   <div style={s.warmupStat}>
// //                     <div style={s.warmupLabel}>Warmup Avg</div>
// //                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
// //                     <div style={s.warmupNote}>cold-start latency</div>
// //                   </div>
// //                   <div style={s.warmupStat}>
// //                     <div style={s.warmupLabel}>Warmup Max</div>
// //                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
// //                     <div style={s.warmupNote}>TCP slow-start peak</div>
// //                   </div>
// //                   <div style={s.warmupStat}>
// //                     <div style={s.warmupLabel}>Steady-State Avg</div>
// //                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
// //                       {result.avg_latency_ms} ms
// //                     </div>
// //                     <div style={s.warmupNote}>true production latency</div>
// //                   </div>
// //                   <div style={s.warmupStat}>
// //                     <div style={s.warmupLabel}>Improvement</div>
// //                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
// //                       {warmupImprovement() ?? "—"}
// //                     </div>
// //                     <div style={s.warmupNote}>warmup vs steady-state</div>
// //                   </div>
// //                 </div>
// //               </div>
// //             )}

// //             {/* Egress throughput chart */}
// //             {result.throughput_samples && result.throughput_samples.length > 0 && (
// //               <div style={{ marginTop: 8 }}>
// //                 <div style={s.label}>Egress — Receive rate over time (msg/s)</div>
// //                 <ThroughputChart
// //                   samples={result.throughput_samples}
// //                   color="#00874a"
// //                 />
// //               </div>
// //             )}

// //             {/* Ingress throughput chart */}
// //             {result.ingress_samples && result.ingress_samples.length > 0 && (
// //               <div style={{ marginTop: 8 }}>
// //                 <div style={s.label}>Ingress — Publish rate over time (msg/s)</div>
// //                 <ThroughputChart
// //                   samples={result.ingress_samples}
// //                   color="#1a73e8"
// //                 />
// //               </div>
// //             )}
// //           </div>
// //         )}
// //       </div>
// //     </div>
// //   );
// // }

// // function StatCard({ label, value, unit, highlight }: {
// //   label: string; value: string; unit: string; highlight?: boolean;
// // }) {
// //   return (
// //     <div style={{
// //       background: "#f5f7fa",
// //       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
// //       borderRadius: 8, padding: "12px 14px"
// //     }}>
// //       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
// //       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
// //         {value}
// //         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
// //           {unit}
// //         </span>
// //       </div>
// //     </div>
// //   );
// // }

// // function ThroughputChart({ samples, color }: { samples: number[]; color: string }) {
// //   const max = Math.max(...samples, 1);
// //   const W = 600;
// //   const H = 80;
// //   const pts = samples.map((v, i) => {
// //     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
// //     const y = H - (v / max) * (H - 8);
// //     return `${x},${y}`;
// //   }).join(" ");

// //   return (
// //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
// //       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 6 }}>
// //       <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
// //       {samples.map((v, i) => (
// //         <circle key={i}
// //           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
// //           cy={H - (v / max) * (H - 8)}
// //           r="3" fill={color}
// //         />
// //       ))}
// //     </svg>
// //   );
// // }

// // const s: Record<string, React.CSSProperties> = {
// //   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
// //   topbar: {
// //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
// //     display: "flex", alignItems: "center", padding: "0 20px",
// //     justifyContent: "space-between", flexShrink: 0
// //   },
// //   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
// //   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// //   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
// //   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
// //   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
// //   btnGhost: {
// //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// //     color: "#5a6675", padding: "4px 10px", fontSize: 12,
// //     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
// //   },
// //   body: {
// //     flex: 1, overflowY: "auto", padding: 20,
// //     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
// //   },
// //   card: {
// //     background: "#fff", border: "1px solid #e1e6eb",
// //     borderRadius: 10, padding: 16,
// //     display: "flex", flexDirection: "column", gap: 14
// //   },
// //   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
// //   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
// //   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
// //   label: {
// //     fontSize: 11, fontWeight: 600, color: "#8a96a3",
// //     textTransform: "uppercase", letterSpacing: "0.6px"
// //   },
// //   disabledTag: {
// //     fontSize: 10, color: "#b0b8c0",
// //     textTransform: "none", fontWeight: 400, marginLeft: 4
// //   },
// //   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
// //   input: {
// //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// //     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
// //   },
// //   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
// //   select: {
// //     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
// //     padding: "8px 12px", color: "#1a2733", fontSize: 13,
// //     outline: "none", cursor: "pointer"
// //   },
// //   toggleRow: { display: "flex", gap: 8 },
// //   toggleBtn: {
// //     background: "#fff", border: "1px solid #d4dae0",
// //     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
// //     fontSize: 13, cursor: "pointer", flex: 1
// //   },
// //   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
// //   preview: {
// //     background: "#f5f7fa", border: "1px solid #e1e6eb",
// //     borderRadius: 6, padding: "8px 12px"
// //   },
// //   previewLabel: { fontSize: 12, color: "#8a96a3" },
// //   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
// //   errorBox: {
// //     background: "#fce8e6", border: "1px solid #f5b9b3",
// //     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
// //   },
// //   btnPrimary: {
// //     background: "#1a73e8", color: "#fff", border: "none",
// //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// //   },
// //   btnDanger: {
// //     background: "#d93025", color: "#fff", border: "none",
// //     borderRadius: 6, padding: "9px 20px", fontSize: 13,
// //     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
// //   },
// //   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
// //   liveStatText: { fontSize: 12, color: "#1a73e8" },
// //   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
// //   progressFill: {
// //     height: "100%", background: "#1a73e8",
// //     borderRadius: 4, transition: "width 0.3s ease"
// //   },
// //   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
// //   resultBadge: {
// //     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
// //     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
// //   },
// //   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
// //   warmupBox: {
// //     background: "#fef9ec", border: "1px solid #fcd9a0",
// //     borderRadius: 8, padding: "14px 16px",
// //     display: "flex", flexDirection: "column", gap: 12
// //   },
// //   warmupTitle: { fontSize: 12, fontWeight: 600, color: "#e8710a" },
// //   warmupGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
// //   warmupStat: { display: "flex", flexDirection: "column", gap: 3 },
// //   warmupLabel: {
// //     fontSize: 10, fontWeight: 600, color: "#8a96a3",
// //     textTransform: "uppercase", letterSpacing: "0.6px"
// //   },
// //   warmupValue: { fontSize: 18, fontWeight: 600, color: "#1a2733" },
// //   warmupNote: { fontSize: 10, color: "#b0b8c0" }
// // };


// import { useState, useRef, useEffect } from "react";
// import { PerfResult } from "../types";
// import { IconPerf, IconStop, IconExport } from "./Icons";
// import { exportPerfExcel } from "../api";

// const TEMPLATES = [
//   { label: "Raw payload", value: "" },
//   { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
//   { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
//   { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
//   { label: "Custom", value: "custom" },
// ];

// interface PerfPanelProps {
//   onResult?: (r: PerfResult) => void;
//   onIngressSample?: (v: number) => void;
//   onEgressSample?: (v: number) => void;
//   onRunning?: (v: boolean) => void;
//   savedResult?: PerfResult | null;
//   savedProgress?: number;
//   savedLiveStats?: { tps: number; ingress: number; elapsed: number } | null;
//   savedError?: string;
//   onProgressChange?: (v: number) => void;
//   onLiveStatsChange?: (v: { tps: number; ingress: number; elapsed: number } | null) => void;
//   onErrorChange?: (v: string) => void;
// }

// export default function PerfPanel({
//   onResult, onIngressSample, onEgressSample, onRunning,
//   savedResult, savedProgress, savedLiveStats, savedError,
//   onProgressChange, onLiveStatsChange, onErrorChange
// }: PerfPanelProps) {

//   const [target, setTarget] = useState("perf/test");
//   const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
//   const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
//   const [count, setCount] = useState(1000);
//   const [size, setSize] = useState(256);
//   const [rateLimit, setRateLimit] = useState(0);
//   const [windowSize, setWindowSize] = useState(50);
//   const [selectedTemplate, setSelectedTemplate] = useState("");
//   const [customTemplate, setCustomTemplate] = useState("");
//   const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
//   const [warmupCount, setWarmupCount] = useState(50);
//   const [consumerCount, setConsumerCount] = useState(1);
//   const [running, setRunning] = useState(false);

//   // ── Lifted state — initialized from Dashboard so they survive tab switches ──
//   const [progressState, setProgressState] = useState(savedProgress ?? 0);
//   const [liveStatsState, setLiveStatsState] = useState<{
//     tps: number; ingress: number; elapsed: number
//   } | null>(savedLiveStats ?? null);
//   const [resultState, setResultState] = useState<PerfResult | null>(savedResult ?? null);
//   const [errorState, setErrorState] = useState(savedError ?? "");

//   // Wrapper setters — update local + parent
//   const setProgress = (v: number) => { setProgressState(v); onProgressChange?.(v); };
//   const setLiveStats = (v: { tps: number; ingress: number; elapsed: number } | null) => {
//     setLiveStatsState(v); onLiveStatsChange?.(v);
//   };
//   const setResult = (v: PerfResult | null) => { setResultState(v); };
//   const setError = (v: string) => { setErrorState(v); onErrorChange?.(v); };

//   // Convenience aliases for reading
//   const progress  = progressState;
//   const liveStats = liveStatsState;
//   const result    = resultState;
//   const error     = errorState;
//   const [publishTopic, setPublishTopic] = useState("");


//   const wsRef = useRef<WebSocket | null>(null);
//   const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

//   const handleRun = () => {
//     if (wsRef.current) wsRef.current.close();
//     setRunning(true);
//     setError("");
//     setResult(null);
//     setProgress(0);
//     setLiveStats(null);
//     onProgressChange?.(0);
//     onLiveStatsChange?.(null);
//     onErrorChange?.("");
//     onRunning?.(true);

    
//     const ws = new WebSocket("ws://localhost:8000/ws/perf");
//     wsRef.current = ws;

//     ws.onopen = () => {
//       ws.send(JSON.stringify({
//         target,
//         target_type: targetType,
//         publish_topic: publishTopic,
//         message_count: count,
//         message_size: size,
//         message_template: effectiveTemplate,
//         delivery_mode: deliveryMode,
//         rate_limit: rateLimit,
//         window_size: windowSize,
//         queue_type: queueType,
//         warmup_count: warmupCount,
//         consumer_count: consumerCount,
//       }));
//     };

//     ws.onmessage = (e) => {
//       const data = JSON.parse(e.data);

//       if (data.type === "progress") {
//         const stats = {
//           tps: data.tps,
//           ingress: data.ingress_tps ?? 0,
//           elapsed: data.elapsed
//         };
//         setProgress(data.percent);
//         setLiveStats(stats);
//         if (data.ingress_tps !== undefined) onIngressSample?.(data.ingress_tps);
//         if (data.tps !== undefined) onEgressSample?.(data.tps);

//       } else if (data.type === "complete") {
//         setResult(data.results);
//         setRunning(false);
//         setProgress(100);
//         setLiveStats(null);
//         onProgressChange?.(100);
//         onLiveStatsChange?.(null);
//         onResult?.(data.results);
//         onRunning?.(false);

//       } else if (data.error) {
//         setError(data.error);
//         setRunning(false);
//         onRunning?.(false);
//       }
//     };

//     ws.onclose = () => {
//       setRunning(false);
//       onRunning?.(false);
//     };
//   };

//   const handleStop = () => {
//     wsRef.current?.close();
//     setRunning(false);
//     setProgress(0);
//     setLiveStats(null);
//     onProgressChange?.(0);
//     onLiveStatsChange?.(null);
//     onRunning?.(false);
//   };

// useEffect(() => {
//   if (targetType === "queue") {
//     setDeliveryMode("persistent");
//   }
// }, [targetType]);
//   const handleExportJSON = () => {
//     if (!result) return;
//     const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = `solengineer-perf-${Date.now()}.json`;
//     a.click();
//     URL.revokeObjectURL(url);
//   };

//   const handleExportExcel = async () => {
//     if (!result) return;
//     try {
//       const response = await exportPerfExcel(result);
//       const blob = new Blob([response.data], {
//         type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
//       });
//       const url = URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = url;
//       a.download = `solengineer-perf-${Date.now()}.xlsx`;
//       a.click();
//       URL.revokeObjectURL(url);
//     } catch {
//       console.error("Excel export failed");
//     }
//   };

//   const warmupImprovement = () => {
//     if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
//     const pct = (
//       (result.warmup_avg_ms - result.avg_latency_ms)
//       / result.warmup_avg_ms * 100
//     ).toFixed(0);
//     return `${pct}% faster`;
//   };

//   return (
//     <div style={s.page}>

//       {/* Topbar */}
//       <div style={s.topbar}>
//         <div style={s.topbarLeft}>
//           <span style={s.pageTitle}>SDK Performance Test</span>
//           {running && <span style={s.tagAmber}>● Running</span>}
//           {result && !running && <span style={s.tagGreen}>✓ Complete</span>}
//         </div>
//         <div style={s.topbarRight}>
//           {result && (
//             <div style={{ display: "flex", gap: 8 }}>
//               <button style={s.btnGhost} onClick={handleExportJSON}>
//                 <IconExport color="#5a6675" /> JSON
//               </button>
//               <button style={{ ...s.btnGhost, color: "#00874a", borderColor: "#b8e6cc" }}
//                 onClick={handleExportExcel}>
//                 <IconExport color="#00874a" /> Excel
//               </button>
//             </div>
//           )}
//         </div>
//       </div>

//       <div style={s.body}>
//         <div style={s.card}>
//           <div style={s.cardTitle}>Configuration</div>

//           {/* Row 1 — Target Type + Delivery Mode */}
//           <div style={s.grid2}>
//             <div style={s.fieldGroup}>
//               <div style={s.label}>Target Type</div>
//               <div style={s.toggleRow}>
//                 {(["topic", "queue"] as const).map((t) => (
//                   <button key={t} onClick={() => setTargetType(t)}
//                     style={{ ...s.toggleBtn, ...(targetType === t ? s.toggleActive : {}) }}>
//                     {t === "topic" ? "📡 Topic" : "📦 Queue"}
//                   </button>
//                 ))}
//               </div>
//             </div>
//             {/* Delivery Mode */}
// <div style={s.fieldGroup}>
//   <div style={s.label}>
//     Delivery Mode
//     {targetType === "queue" && (
//       <span style={s.disabledTag}>(forced Persistent for queues)</span>
//     )}
//   </div>
//   <div style={s.toggleRow}>
//     {(["direct", "persistent"] as const).map((m) => (
//       <button key={m}
//         onClick={() => targetType === "topic" && setDeliveryMode(m)}
//         style={{
//           ...s.toggleBtn,
//           ...(deliveryMode === m ? s.toggleActive : {}),
//           ...(targetType === "queue" ? s.toggleForced : {})
//         }}>
//         {m === "direct" ? "⚡ Direct" : "🔒 Persistent"}
//       </button>
//     ))}
//   </div>
// </div>
//           </div>

//           {/* Queue Type — only when queue selected */}
//           {targetType === "queue" && (
//             <div style={s.fieldGroup}>
//               <div style={s.label}>Queue Type</div>
//               <div style={{ display: "flex", gap: 8, maxWidth: 400 }}>
//                 {(["exclusive", "non_exclusive"] as const).map((q) => (
//                   <button key={q} onClick={() => setQueueType(q)}
//                     style={{ ...s.toggleBtn, ...(queueType === q ? s.toggleActive : {}) }}>
//                     {q === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
//                   </button>
//                 ))}
//               </div>
//               <div style={s.hint}>
//                 {queueType === "exclusive"
//                   ? "One active consumer — ordered delivery, automatic failover"
//                   : "Messages distributed round-robin across all consumers — higher throughput, no order guarantee"
//                 }
//               </div>

//               {/* Consumer count — non-exclusive only */}
//               {queueType === "non_exclusive" && (
//                 <div style={{ marginTop: 8 }}>
//                   <div style={s.label}>
//                     Consumer Count
//                     <span style={s.disabledTag}>(non-exclusive only)</span>
//                   </div>
//                   <input
//                     style={{ ...s.input, maxWidth: 200 }}
//                     type="number"
//                     min={1}
//                     max={10}
//                     value={consumerCount}
//                     onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))}
//                   />
//                   <div style={s.hint}>
//                     Spawns N receiver threads — simulates real multi-consumer load.
//                     Messages distributed round-robin across all {consumerCount} consumer{consumerCount > 1 ? "s" : ""}.
//                   </div>
//                 </div>
//               )}
//             </div>
//           )}

//           {/* Row 2 — Target + Template */}
// <div style={s.grid2}>
//   <div style={s.fieldGroup}>
//     <div style={s.label}>{targetType === "topic" ? "Topic" : "Queue Name"}</div>
//     <input style={s.input} value={target}
//       onChange={(e) => setTarget(e.target.value)}
//       placeholder={targetType === "topic" ? "perf/test" : "perf-queue"} />
//   </div>
//   <div style={s.fieldGroup}>
//     <div style={s.label}>Message Template</div>
//     <select style={s.select} value={selectedTemplate}
//       onChange={(e) => setSelectedTemplate(e.target.value)}>
//       {TEMPLATES.map((t) => (
//         <option key={t.label} value={t.value}>{t.label}</option>
//       ))}
//     </select>
//   </div>
// </div>

// {/* Publish Topic — only for queue mode */}
// {targetType === "queue" && (
//   <div style={s.fieldGroup}>
//     <div style={s.label}>Publish Topic</div>
//     <input
//       style={s.input}
//       value={publishTopic}
//       onChange={(e) => setPublishTopic(e.target.value)}
//       placeholder="e.g. perf/test (must match queue subscription)"
//     />
//     <div style={{ ...s.hint, background: "#e8f0fe", border: "1px solid #c2d8fb", borderRadius: 6, padding: "8px 10px" }}>
//       📌 Publisher sends to this topic → Broker routes to queue via subscription.
//       Go to Solace Console → Queue → Subscriptions → Add topic subscription matching this value.
//     </div>
//   </div>
// )}

          

//           {/* Row 3 — Count + Size */}
//           <div style={s.grid2}>
//             <div style={s.fieldGroup}>
//               <div style={s.label}>Message Count</div>
//               <input style={s.input} type="number" value={count}
//                 onChange={(e) => setCount(Number(e.target.value))} />
//             </div>
//             <div style={s.fieldGroup}>
//               <div style={s.label}>Message Size (bytes)</div>
//               <input style={s.input} type="number" value={size}
//                 onChange={(e) => setSize(Number(e.target.value))} />
//             </div>
//           </div>

//           {/* Row 4 — Rate Limit + Window Size */}
//           <div style={s.grid2}>
//             <div style={s.fieldGroup}>
//               <div style={s.label}>Rate Limit (msg/sec)</div>
//               <input style={s.input} type="number" value={rateLimit}
//                 onChange={(e) => setRateLimit(Number(e.target.value))}
//                 placeholder="0 = unlimited" />
//               <div style={s.hint}>0 = send as fast as possible</div>
//             </div>
//             <div style={s.fieldGroup}>
//               <div style={s.label}>
//                 Window Size
//                 {deliveryMode === "direct" && (
//                   <span style={s.disabledTag}>(persistent only)</span>
//                 )}
//               </div>
//               <input
//                 style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
//                 type="number"
//                 value={windowSize}
//                 disabled={deliveryMode === "direct"}
//                 onChange={(e) => setWindowSize(Number(e.target.value))}
//               />
//               <div style={s.hint}>Max unacknowledged messages in-flight</div>
//             </div>
//           </div>

//           {/* Row 5 — Warmup Count */}
//           <div style={s.fieldGroup}>
//             <div style={s.label}>Warmup Messages to Skip</div>
//             <input
//               style={{ ...s.input, maxWidth: 280 }}
//               type="number"
//               value={warmupCount}
//               onChange={(e) => setWarmupCount(Number(e.target.value))}
//               placeholder="0"
//             />
//             <div style={s.hint}>
//               First N messages excluded from latency stats — removes TCP slow-start
//               and SDK warmup bias. Set to 0 to include all messages.
//             </div>
//           </div>

//           {/* Custom template */}
//           {selectedTemplate === "custom" && (
//             <div style={s.fieldGroup}>
//               <div style={s.label}>
//                 Custom Template — use {"{{index}}"}, {"{{timestamp}}"}, {"{{random}}"}
//               </div>
//               <input style={s.input} value={customTemplate}
//                 onChange={(e) => setCustomTemplate(e.target.value)}
//                 placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
//             </div>
//           )}

//           {/* Template preview */}
//           {selectedTemplate !== "" && selectedTemplate !== "custom" && (
//             <div style={s.preview}>
//               <span style={s.previewLabel}>Preview: </span>
//               <span style={s.previewValue}>
//                 {selectedTemplate
//                   .replace("{{index}}", "42")
//                   .replace("{{timestamp}}", "1741234567890")
//                   .replace("{{random}}", "xKpQmRnL")}
//               </span>
//             </div>
//           )}

//           {error && <div style={s.errorBox}>{error}</div>}

//           {/* Run / Stop */}
//           <div>
//             {!running
//               ? (
//                 <button style={s.btnPrimary} onClick={handleRun}>
//                   <IconPerf color="#fff" size={13} /> Run Perf Test
//                 </button>
//               ) : (
//                 <button style={s.btnDanger} onClick={handleStop}>
//                   <IconStop color="#fff" size={13} /> Stop Test
//                 </button>
//               )
//             }
//           </div>
//         </div>

//         {/* Progress */}
//         {(running || progress > 0) && (
//           <div style={s.card}>
//             <div style={s.progressHeader}>
//               <span style={s.cardTitle}>
//                 {running ? `Running... ${progress.toFixed(1)}%` : `Completed — ${progress.toFixed(1)}%`}
//               </span>
//               {liveStats && (
//                 <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
//                   <span style={{ ...s.liveStatText, color: "#1a73e8" }}>
//                     ↑ {liveStats.ingress} msg/s ingress
//                   </span>
//                   <span style={{ ...s.liveStatText, color: "#00874a" }}>
//                     ↓ {liveStats.tps} msg/s egress
//                   </span>
//                   <span style={s.liveStatText}>
//                     {liveStats.elapsed}s elapsed
//                   </span>
//                 </div>
//               )}
//             </div>
//             <div style={s.progressTrack}>
//               <div style={{ ...s.progressFill, width: `${progress}%` }} />
//             </div>
//           </div>
//         )}

//         {/* Results */}
//         {result && (
//           <div style={s.card}>
//             <div style={s.cardTitle}>Results</div>

//             {/* Badges */}
//             <div style={s.badgeRow}>
//               <span style={s.resultBadge}>
//                 {result.target_type === "topic" ? "📡" : "📦"} {result.target}
//               </span>
//               <span style={s.resultBadge}>
//                 {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
//               </span>
//               {result.queue_type && (
//                 <span style={s.resultBadge}>
//                   {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
//                   {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
//                 </span>
//               )}
//               {result.rate_limit > 0 && (
//                 <span style={s.resultBadge}>⏱ {result.rate_limit} msg/s limit</span>
//               )}
//               {result.window_size && (
//                 <span style={s.resultBadge}>🪟 Window {result.window_size}</span>
//               )}
//               {result.warmup_count > 0 && (
//                 <span style={s.resultBadge}>🌡️ {result.warmup_count} warmup skipped</span>
//               )}
//               {/* Show publish topic flow for queue mode */}
// {result.target_type === "queue" && (
//   <div style={s.flowBadge}>
//     <span style={s.flowStep}>
//       📨 Message Flow
//     </span>
//     <span style={s.flowArrow}>
//       topic: <strong>{result.publish_topic}</strong>
//       <span style={{ margin: "0 8px", color: "#8a96a3" }}>→</span>
//       broker routes via subscription
//       <span style={{ margin: "0 8px", color: "#8a96a3" }}>→</span>
//       Queue: <strong>{result.target}</strong>
//     </span>
//   </div>
// )}
//             </div>

//             {/* Stats grid */}
//             <div style={s.statsGrid}>
//               <StatCard label="Throughput"  value={`${result.throughput_msg_per_sec}`} unit="msg/s" highlight />
//               <StatCard label="Avg latency" value={`${result.avg_latency_ms}`}         unit="ms"    highlight />
//               <StatCard label="P95 latency" value={`${result.p95_latency_ms}`}         unit="ms" />
//               <StatCard label="P99 latency" value={`${result.p99_latency_ms}`}         unit="ms" />
//               <StatCard label="Min latency" value={`${result.min_latency_ms}`}         unit="ms" />
//               <StatCard label="Max latency" value={`${result.max_latency_ms}`}         unit="ms" />
//               <StatCard label="Sent"        value={`${result.sent}`}                   unit="msgs" />
//               <StatCard label="Received"    value={`${result.received}`}               unit="msgs" />
//               <StatCard label="Errors"      value={`${result.errors}`}                 unit="" />
//               <StatCard label="Total time"  value={`${result.total_time_sec}`}         unit="sec" />
//             </div>

//             {/* Warmup analysis */}
//             {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
//               <div style={s.warmupBox}>
//                 <div style={s.warmupTitle}>
//                   🌡️ Warmup Analysis — first {result.warmup_count} messages excluded from stats above
//                 </div>
//                 <div style={s.warmupGrid}>
//                   <div style={s.warmupStat}>
//                     <div style={s.warmupLabel}>Warmup Avg</div>
//                     <div style={s.warmupValue}>{result.warmup_avg_ms} ms</div>
//                     <div style={s.warmupNote}>cold-start latency</div>
//                   </div>
//                   <div style={s.warmupStat}>
//                     <div style={s.warmupLabel}>Warmup Max</div>
//                     <div style={s.warmupValue}>{result.warmup_max_ms} ms</div>
//                     <div style={s.warmupNote}>TCP slow-start peak</div>
//                   </div>
//                   <div style={s.warmupStat}>
//                     <div style={s.warmupLabel}>Steady-State Avg</div>
//                     <div style={{ ...s.warmupValue, color: "#00874a" }}>
//                       {result.avg_latency_ms} ms
//                     </div>
//                     <div style={s.warmupNote}>true production latency</div>
//                   </div>
//                   <div style={s.warmupStat}>
//                     <div style={s.warmupLabel}>Improvement</div>
//                     <div style={{ ...s.warmupValue, color: "#1a73e8" }}>
//                       {warmupImprovement() ?? "—"}
//                     </div>
//                     <div style={s.warmupNote}>warmup vs steady-state</div>
//                   </div>
//                 </div>
//               </div>
//             )}

//             {/* Egress chart */}
//             {result.throughput_samples && result.throughput_samples.length > 0 && (
//               <div style={{ marginTop: 8 }}>
//                 <div style={s.label}>Egress — Receive rate over time (msg/s)</div>
//                 <ThroughputChart samples={result.throughput_samples} color="#00874a" />
//               </div>
//             )}

//             {/* Ingress chart */}
//             {result.ingress_samples && result.ingress_samples.length > 0 && (
//               <div style={{ marginTop: 8 }}>
//                 <div style={s.label}>Ingress — Publish rate over time (msg/s)</div>
//                 <ThroughputChart samples={result.ingress_samples} color="#1a73e8" />
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// function StatCard({ label, value, unit, highlight }: {
//   label: string; value: string; unit: string; highlight?: boolean;
// }) {
//   return (
//     <div style={{
//       background: "#f5f7fa",
//       border: `1px solid ${highlight ? "#b8d4f7" : "#e1e6eb"}`,
//       borderRadius: 8, padding: "12px 14px"
//     }}>
//       <div style={{ fontSize: 11, color: "#8a96a3", marginBottom: 4 }}>{label}</div>
//       <div style={{ color: highlight ? "#1a73e8" : "#1a2733", fontSize: 20, fontWeight: 600 }}>
//         {value}
//         <span style={{ fontSize: 11, fontWeight: 400, color: "#8a96a3", marginLeft: 4 }}>
//           {unit}
//         </span>
//       </div>
//     </div>
//   );
// }

// function ThroughputChart({ samples, color }: { samples: number[]; color: string }) {
//   const max = Math.max(...samples, 1);
//   const W = 600;
//   const H = 80;
//   const pts = samples.map((v, i) => {
//     const x = samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W;
//     const y = H - (v / max) * (H - 8);
//     return `${x},${y}`;
//   }).join(" ");

//   return (
//     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
//       style={{ background: "#f5f7fa", borderRadius: 6, border: "1px solid #e1e6eb", marginTop: 6 }}>
//       <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
//       {samples.map((v, i) => (
//         <circle key={i}
//           cx={samples.length === 1 ? W / 2 : (i / (samples.length - 1)) * W}
//           cy={H - (v / max) * (H - 8)}
//           r="3" fill={color}
//         />
//       ))}
//     </svg>
//   );
// }


// const s: Record<string, React.CSSProperties> = {
//   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//   topbar: {
//     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
//     display: "flex", alignItems: "center", padding: "0 20px",
//     justifyContent: "space-between", flexShrink: 0
//   },
//   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
//   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
//   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
//   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
//   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
//   btnGhost: {
//     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
//     color: "#5a6675", padding: "4px 10px", fontSize: 12,
//     cursor: "pointer", display: "flex", alignItems: "center", gap: 5
//   },
//   body: {
//     flex: 1, overflowY: "auto", padding: 20,
//     background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14
//   },
//   card: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 10, padding: 16,
//     display: "flex", flexDirection: "column", gap: 14
//   },
//   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
//   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
//   fieldGroup: { display: "flex", flexDirection: "column", gap: 6 },
//   label: {
//     fontSize: 11, fontWeight: 600, color: "#8a96a3",
//     textTransform: "uppercase", letterSpacing: "0.6px"
//   },
//   disabledTag: {
//     fontSize: 10, color: "#b0b8c0",
//     textTransform: "none", fontWeight: 400, marginLeft: 4
//   },
//   hint: { fontSize: 11, color: "#b0b8c0", lineHeight: "1.5" },
//   input: {
//     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
//     padding: "8px 12px", color: "#1a2733", fontSize: 13, outline: "none"
//   },
//   inputDisabled: { background: "#f5f7fa", color: "#b0b8c0", cursor: "not-allowed" },
//   select: {
//     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
//     padding: "8px 12px", color: "#1a2733", fontSize: 13,
//     outline: "none", cursor: "pointer"
//   },
//   toggleRow: { display: "flex", gap: 8 },
//   toggleBtn: {
//     background: "#fff", border: "1px solid #d4dae0",
//     color: "#5a6675", borderRadius: 6, padding: "7px 14px",
//     fontSize: 13, cursor: "pointer", flex: 1
//   },
//   toggleActive: { border: "1px solid #1a73e8", color: "#1a73e8", background: "#e8f0fe" },
//   preview: {
//     background: "#f5f7fa", border: "1px solid #e1e6eb",
//     borderRadius: 6, padding: "8px 12px"
//   },
//   previewLabel: { fontSize: 12, color: "#8a96a3" },
//   previewValue: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },
//   errorBox: {
//     background: "#fce8e6", border: "1px solid #f5b9b3",
//     borderRadius: 6, padding: "8px 12px", color: "#d93025", fontSize: 13
//   },
//   btnPrimary: {
//     background: "#1a73e8", color: "#fff", border: "none",
//     borderRadius: 6, padding: "9px 20px", fontSize: 13,
//     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
//   },
//   btnDanger: {
//     background: "#d93025", color: "#fff", border: "none",
//     borderRadius: 6, padding: "9px 20px", fontSize: 13,
//     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
//   },
//   progressHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
//   liveStatText: { fontSize: 12, color: "#1a73e8" },
//   progressTrack: { background: "#e1e6eb", borderRadius: 4, height: 6, overflow: "hidden" },
//   progressFill: {
//     height: "100%", background: "#1a73e8",
//     borderRadius: 4, transition: "width 0.3s ease"
//   },
//   badgeRow: { display: "flex", gap: 8, flexWrap: "wrap" },
//   resultBadge: {
//     display: "inline-block", background: "#f5f7fa", border: "1px solid #e1e6eb",
//     color: "#1a2733", borderRadius: 6, padding: "4px 12px", fontSize: 12
//   },
//   statsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 },
//   warmupBox: {
//     background: "#fef9ec", border: "1px solid #fcd9a0",
//     borderRadius: 8, padding: "14px 16px",
//     display: "flex", flexDirection: "column", gap: 12
//   },
//   toggleForced: {
//   opacity: 0.5,
//   cursor: "not-allowed",
//   pointerEvents: "none" as const
// },
// flowBadge: {
//   background: "#f5f7fa", border: "1px solid #e1e6eb",
//   borderRadius: 6, padding: "10px 14px",
//   display: "flex", flexDirection: "column", gap: 4
// },
// flowStep: {
//   fontSize: 11, fontWeight: 600, color: "#8a96a3",
//   textTransform: "uppercase", letterSpacing: "0.6px"
// },
// flowArrow: {
//   fontSize: 13, color: "#1a2733"
// },
//   warmupTitle: { fontSize: 12, fontWeight: 600, color: "#e8710a" },
//   warmupGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
//   warmupStat: { display: "flex", flexDirection: "column", gap: 3 },
//   warmupLabel: {
//     fontSize: 10, fontWeight: 600, color: "#8a96a3",
//     textTransform: "uppercase", letterSpacing: "0.6px"
//   },
//   warmupValue: { fontSize: 18, fontWeight: 600, color: "#1a2733" },
//   warmupNote: { fontSize: 10, color: "#b0b8c0" }
// };  


//Updated 17-07-26

import { useState, useRef, useEffect } from "react";
import { PerfResult} from "../../../types/perf";
import { IconPerf, IconStop, IconExport } from "../../common/Icons";
import { exportPerfExcel } from "../../../api/index";

const TEMPLATES = [
  { label: "Raw payload", value: "" },
  { label: "JSON with index", value: '{"id": {{index}}, "ts": {{timestamp}}}' },
  { label: "JSON with random", value: '{"id": {{index}}, "key": "{{random}}", "ts": {{timestamp}}}' },
  { label: "CSV row", value: "{{index}},{{random}},{{timestamp}}" },
  { label: "Custom", value: "custom" },
];

interface PerfPanelProps {
  onResult?: (r: PerfResult) => void;
  onIngressSample?: (v: number) => void;
  onEgressSample?: (v: number) => void;
  onRunning?: (v: boolean) => void;
  savedResult?: PerfResult | null;
  savedProgress?: number;
  savedLiveStats?: { tps: number; ingress: number; elapsed: number } | null;
  savedError?: string;
  onProgressChange?: (v: number) => void;
  onLiveStatsChange?: (v: { tps: number; ingress: number; elapsed: number } | null) => void;
  onErrorChange?: (v: string) => void;
}

export default function PerfPanel({
  onResult, onIngressSample, onEgressSample, onRunning,
  savedResult, savedProgress, savedLiveStats, savedError,
  onProgressChange, onLiveStatsChange, onErrorChange
}: PerfPanelProps) {

  const [target, setTarget] = useState("perf/test");
  const [targetType, setTargetType] = useState<"topic" | "queue">("topic");
  const [deliveryMode, setDeliveryMode] = useState<"direct" | "persistent">("direct");
  const [count, setCount] = useState(1000);
  const [size, setSize] = useState(256);
  const [rateLimit, setRateLimit] = useState(0);
  const [windowSize, setWindowSize] = useState(50);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [customTemplate, setCustomTemplate] = useState("");
  const [queueType, setQueueType] = useState<"exclusive" | "non_exclusive">("exclusive");
  const [warmupCount, setWarmupCount] = useState(50);
  const [consumerCount, setConsumerCount] = useState(1);
  const [publishTopic, setPublishTopic] = useState("");
  const [running, setRunning] = useState(false);

  const [progressState, setProgressState] = useState(savedProgress ?? 0);
  const [liveStatsState, setLiveStatsState] = useState<{ tps: number; ingress: number; elapsed: number } | null>(savedLiveStats ?? null);
  const [resultState, setResultState] = useState<PerfResult | null>(savedResult ?? null);
  const [errorState, setErrorState] = useState(savedError ?? "");

  const setProgress = (v: number) => { setProgressState(v); onProgressChange?.(v); };
  const setLiveStats = (v: { tps: number; ingress: number; elapsed: number } | null) => { setLiveStatsState(v); onLiveStatsChange?.(v); };
  const setResult = (v: PerfResult | null) => { setResultState(v); };
  const setError = (v: string) => { setErrorState(v); onErrorChange?.(v); };

  const progress  = progressState;
  const liveStats = liveStatsState;
  const result    = resultState;
  const error     = errorState;

  const wsRef = useRef<WebSocket | null>(null);
  const effectiveTemplate = selectedTemplate === "custom" ? customTemplate : selectedTemplate;

  useEffect(() => {
    if (targetType === "queue") setDeliveryMode("persistent");
  }, [targetType]);

  const handleRun = () => {
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

    const ws = new WebSocket("ws://localhost:8000/ws/perf");
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        target, target_type: targetType,
        publish_topic: publishTopic,
        message_count: count, message_size: size,
        message_template: effectiveTemplate,
        delivery_mode: deliveryMode,
        rate_limit: rateLimit, window_size: windowSize,
        queue_type: queueType, warmup_count: warmupCount,
        consumer_count: consumerCount,
      }));
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "progress") {
        const stats = { tps: data.tps, ingress: data.ingress_tps ?? 0, elapsed: data.elapsed };
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
  };

  const handleStop = () => {
    wsRef.current?.close();
    setRunning(false);
    setProgress(0);
    setLiveStats(null);
    onProgressChange?.(0);
    onLiveStatsChange?.(null);
    onRunning?.(false);
  };

  const handleExportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `solengineer-perf-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportExcel = async () => {
    if (!result) return;
    try {
      const response = await exportPerfExcel(result);
      const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `solengineer-perf-${Date.now()}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { console.error("Excel export failed"); }
  };

  const warmupImprovement = () => {
    if (!result?.warmup_avg_ms || !result?.avg_latency_ms) return null;
    return `${((result.warmup_avg_ms - result.avg_latency_ms) / result.warmup_avg_ms * 100).toFixed(0)}% faster`;
  };

  return (
    <div style={s.page}>

      {/* Topbar */}
      <div style={s.topbar}>
        <div style={s.topbarLeft}>
          <div style={s.topbarTitle}>
            <span style={s.pageTitle}>SDK Performance Test</span>
            <span style={s.pageSub}>Measure throughput, latency and broker performance</span>
          </div>
        </div>
        <div style={s.topbarRight}>
          {running && (
            <div style={s.runningPill}>
              <div style={s.pulsingDot} />
              Running
            </div>
          )}
          {result && !running && <span style={s.completePill}>✓ Complete</span>}
          {result && (
            <div style={{ display: "flex", gap: 6 }}>
              <button style={s.exportBtn} onClick={handleExportJSON}>
                <IconExport color="#5a6675" size={12} /> JSON
              </button>
              <button style={{ ...s.exportBtn, color: "#00874a", borderColor: "#b8e6cc" }}
                onClick={handleExportExcel}>
                <IconExport color="#00874a" size={12} /> Excel
              </button>
            </div>
          )}
        </div>
      </div>

      <div style={s.body}>

        {/* ── Configuration ── */}
        <div style={s.section}>
          <div style={s.sectionHeader}>
            <span style={s.sectionTitle}>Configuration</span>
            <span style={s.sectionSub}>Set up your performance test parameters</span>
          </div>

          <div style={s.configGrid}>

            {/* Target */}
            <div style={s.configBlock}>
              <div style={s.blockLabel}>Target Type</div>
              <div style={s.segmented}>
                {(["topic", "queue"] as const).map((t) => (
                  <button key={t}
                    onClick={() => setTargetType(t)}
                    style={{ ...s.seg, ...(targetType === t ? s.segActive : {}) }}>
                    {t === "topic" ? " Topic" : " Queue"}
                  </button>
                ))}
              </div>
            </div>

            {/* Delivery Mode */}
            <div style={s.configBlock}>
              <div style={s.blockLabel}>
                Delivery Mode
                {targetType === "queue" && <span style={s.forcedTag}>auto-set for queues</span>}
              </div>
              <div style={s.segmented}>
                {(["direct", "persistent"] as const).map((m) => (
                  <button key={m}
                    onClick={() => targetType === "topic" && setDeliveryMode(m)}
                    style={{
                      ...s.seg,
                      ...(deliveryMode === m ? s.segActive : {}),
                      ...(targetType === "queue" ? s.segDisabled : {})
                    }}>
                    {m === "direct" ? " Direct" : " Persistent"}
                  </button>
                ))}
              </div>
            </div>

            {/* Queue Type — queue only */}
            {targetType === "queue" && (
              <div style={s.configBlock}>
                <div style={s.blockLabel}>Queue Type</div>
                <div style={s.segmented}>
                  {(["exclusive", "non_exclusive"] as const).map((q) => (
                    <button key={q}
                      onClick={() => setQueueType(q)}
                      style={{ ...s.seg, ...(queueType === q ? s.segActive : {}) }}>
                      {q === "exclusive" ? " Exclusive" : " Non-Exclusive"}
                    </button>
                  ))}
                </div>
                <div style={s.fieldHint}>
                  {queueType === "exclusive"
                    ? "Single active consumer — ordered delivery, automatic failover"
                    : "Round-robin across all consumers — higher throughput, no order guarantee"}
                </div>
              </div>
            )}
          </div>

          {/* Fields row */}
          <div style={s.fieldsGrid}>
            <Field label={targetType === "topic" ? "Topic" : "Queue Name"}>
              <input style={s.input} value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder={targetType === "topic" ? "e.g. perf/test" : "e.g. perf-queue"} />
            </Field>

            {targetType === "queue" && (
              <Field label="Publish Topic">
                <input style={s.input} value={publishTopic}
                  onChange={(e) => setPublishTopic(e.target.value)}
                  placeholder="e.g. perf/test" />
                <div style={s.fieldHint}>Must match a subscription on the queue above</div>
              </Field>
            )}

            <Field label="Message Count">
              <input style={s.input} type="number" value={count}
                onChange={(e) => setCount(Number(e.target.value))} />
            </Field>

            <Field label="Message Size (bytes)">
              <input style={s.input} type="number" value={size}
                onChange={(e) => setSize(Number(e.target.value))} />
            </Field>

            <Field label="Rate Limit (msg/s)">
              <input style={s.input} type="number" value={rateLimit}
                onChange={(e) => setRateLimit(Number(e.target.value))}
                placeholder="0 = unlimited" />
              <div style={s.fieldHint}>0 = send as fast as possible</div>
            </Field>

            <Field label={`Window Size${deliveryMode === "direct" ? " (persistent only)" : ""}`}>
              <input
                style={{ ...s.input, ...(deliveryMode === "direct" ? s.inputDisabled : {}) }}
                type="number" value={windowSize}
                disabled={deliveryMode === "direct"}
                onChange={(e) => setWindowSize(Number(e.target.value))} />
              <div style={s.fieldHint}>Max unacknowledged in-flight messages</div>
            </Field>

            <Field label="Warmup Messages to Skip">
              <input style={s.input} type="number" value={warmupCount}
                onChange={(e) => setWarmupCount(Number(e.target.value))} />
              <div style={s.fieldHint}>First N excluded from latency stats</div>
            </Field>

            {targetType === "queue" && queueType === "non_exclusive" && (
              <Field label="Consumer Count">
                <input style={s.input} type="number" min={1} max={10}
                  value={consumerCount}
                  onChange={(e) => setConsumerCount(Math.max(1, Number(e.target.value)))} />
                <div style={s.fieldHint}>Parallel receiver threads (max 10)</div>
              </Field>
            )}
          </div>

          {/* Message template */}
          <div style={s.templateRow}>
            <Field label="Message Template" style={{ flex: 1 }}>
              <select style={s.select} value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}>
                {TEMPLATES.map((t) => (
                  <option key={t.label} value={t.value}>{t.label}</option>
                ))}
              </select>
            </Field>

            {selectedTemplate === "custom" && (
              <Field label="Custom template — use {{index}}, {{timestamp}}, {{random}}" style={{ flex: 2 }}>
                <input style={s.input} value={customTemplate}
                  onChange={(e) => setCustomTemplate(e.target.value)}
                  placeholder='{"id": {{index}}, "ts": {{timestamp}}}' />
              </Field>
            )}

            {selectedTemplate !== "" && selectedTemplate !== "custom" && (
              <div style={s.previewBox}>
                <span style={s.previewLabel}>Preview</span>
                <code style={s.previewCode}>
                  {selectedTemplate
                    .replace("{{index}}", "42")
                    .replace("{{timestamp}}", "1741234567890")
                    .replace("{{random}}", "xKpQmRnL")}
                </code>
              </div>
            )}
          </div>

          {error && <div style={s.errorBox}>⚠ {error}</div>}

          {/* Action */}
          <div style={s.actionRow}>
            {!running ? (
              <button style={s.runBtn} onClick={handleRun}>
                <IconPerf color="#fff" size={14} />
                Run Performance Test
              </button>
            ) : (
              <button style={s.stopBtn} onClick={handleStop}>
                <IconStop color="#fff" size={14} />
                Stop Test
              </button>
            )}
          </div>
        </div>

        {/* ── Progress ── */}
        {(running || progress > 0) && (
          <div style={s.progressSection}>
            <div style={s.progressTop}>
              <div style={s.progressLeft}>
                <span style={s.progressLabel}>
                  {running ? "Test running" : "Completed"}
                </span>
                <span style={s.progressPct}>{progress.toFixed(1)}%</span>
              </div>
              {liveStats && running && (
                <div style={s.liveRow}>
                  <div style={s.livePill}>
                    <span style={{ color: "#1a73e8" }}>↑</span>
                    <strong>{liveStats.ingress.toLocaleString()}</strong>
                    <span style={s.liveUnit}>msg/s ingress</span>
                  </div>
                  <div style={s.livePill}>
                    <span style={{ color: "#00874a" }}>↓</span>
                    <strong>{liveStats.tps.toLocaleString()}</strong>
                    <span style={s.liveUnit}>msg/s egress</span>
                  </div>
                  <div style={s.livePill}>
                    <span style={s.liveUnit}>{liveStats.elapsed}s elapsed</span>
                  </div>
                </div>
              )}
            </div>
            <div style={s.track}>
              <div style={{ ...s.fill, width: `${progress}%` }} />
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {result && (
          <div style={s.resultsSection}>
            <div style={s.resultsSectionHeader}>
              <span style={s.sectionTitle}>Results</span>
              <div style={s.resultsMeta}>
                {result.target_type === "queue" && (
                  <span style={s.flowTag}>
                    topic/{result.publish_topic}
                    <span style={{ margin: "0 6px", color: "#b0b8c0" }}>→</span>
                    Queue: {result.target}
                  </span>
                )}
                {result.target_type === "topic" && (
                  <span style={s.flowTag}>Topic: {result.target}</span>
                )}
                <span style={s.metaTag}>
                  {result.delivery_mode === "direct" ? "⚡ Direct" : "🔒 Persistent"}
                </span>
                {result.queue_type && (
                  <span style={s.metaTag}>
                    {result.queue_type === "exclusive" ? "🔒 Exclusive" : "🔀 Non-Exclusive"}
                    {result.consumer_count > 1 && ` · ${result.consumer_count} consumers`}
                  </span>
                )}
                {result.warmup_count > 0 && (
                  <span style={s.metaTag}>🌡️ {result.warmup_count} warmup excluded</span>
                )}
              </div>
            </div>

            {/* Key metrics — top row highlighted */}
            <div style={s.keyMetrics}>
              <KeyMetric label="Throughput" value={result.throughput_msg_per_sec.toLocaleString()} unit="msg/s" accent="#1a73e8" />
              <KeyMetric label="Avg Latency" value={`${result.avg_latency_ms}`} unit="ms" accent="#1a73e8" />
              <KeyMetric label="P95 Latency" value={`${result.p95_latency_ms}`} unit="ms" accent="#e8710a" />
              <KeyMetric label="P99 Latency" value={`${result.p99_latency_ms}`} unit="ms" accent="#d93025" />
            </div>

            {/* Secondary metrics */}
            <div style={s.secondaryMetrics}>
              <SmallMetric label="Min Latency" value={`${result.min_latency_ms} ms`} />
              <SmallMetric label="Max Latency" value={`${result.max_latency_ms} ms`} />
              <SmallMetric label="Sent" value={result.sent.toLocaleString()} />
              <SmallMetric label="Received" value={result.received.toLocaleString()} />
              <SmallMetric label="Errors" value={`${result.errors}`} warn={result.errors > 0} />
              <SmallMetric label="Total Time" value={`${result.total_time_sec}s`} />
            </div>

            {/* Warmup */}
            {result.warmup_count > 0 && result.warmup_avg_ms !== null && (
              <div style={s.warmupCard}>
                <div style={s.warmupHeader}>
                  <span style={s.warmupTitle}>🌡️ Warmup Analysis</span>
                  <span style={s.warmupSub}>First {result.warmup_count} messages excluded from stats above</span>
                </div>
                <div style={s.warmupRow}>
                  <WarmupStat label="Warmup Avg" value={`${result.warmup_avg_ms} ms`} sub="cold-start" />
                  <WarmupStat label="Warmup Max" value={`${result.warmup_max_ms} ms`} sub="TCP peak" />
                  <WarmupStat label="Steady-State" value={`${result.avg_latency_ms} ms`} sub="production avg" green />
                  <WarmupStat label="Improvement" value={warmupImprovement() ?? "—"} sub="vs warmup" blue />
                </div>
              </div>
            )}

            {/* Mini charts */}
            {result.throughput_samples && result.throughput_samples.length > 0 && (
              <div style={s.miniChartRow}>
                <div style={s.miniChart}>
                  <div style={s.miniChartLabel}>Egress — Receive rate (msg/s)</div>
                  <MiniLineChart data={result.throughput_samples} color="#00874a" />
                </div>
                {result.ingress_samples && result.ingress_samples.length > 0 && (
                  <div style={s.miniChart}>
                    <div style={s.miniChartLabel}>Ingress — Publish rate (msg/s)</div>
                    <MiniLineChart data={result.ingress_samples} color="#1a73e8" />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Field({ label, children, style }: { label: string; children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 5, ...style }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: "#5a6675", letterSpacing: "0.3px" }}>
        {label}
      </div>
      {children}
    </div>
  );
}

function KeyMetric({ label, value, unit, accent }: { label: string; value: string; unit: string; accent: string }) {
  return (
    <div style={{
      background: "#fff", border: `1px solid ${accent}22`,
      borderTop: `3px solid ${accent}`,
      borderRadius: 8, padding: "16px 20px",
      display: "flex", flexDirection: "column", gap: 4, flex: 1
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" }}>
        {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: accent, lineHeight: 1.1 }}>
        {value}
        <span style={{ fontSize: 13, fontWeight: 500, color: "#8a96a3", marginLeft: 4 }}>{unit}</span>
      </div>
    </div>
  );
}

function SmallMetric({ label, value, warn }: { label: string; value: string; warn?: boolean }) {
  return (
    <div style={{
      background: "#f9fafb", border: "1px solid #e8edf2",
      borderRadius: 6, padding: "10px 14px",
      display: "flex", flexDirection: "column", gap: 3
    }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        {label}
      </div>
      <div style={{ fontSize: 15, fontWeight: 600, color: warn ? "#d93025" : "#1a2733" }}>
        {value}
      </div>
    </div>
  );
}

function WarmupStat({ label, value, sub, green, blue }: {
  label: string; value: string; sub: string; green?: boolean; blue?: boolean;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        {label}
      </div>
      <div style={{ fontSize: 17, fontWeight: 700, color: green ? "#00874a" : blue ? "#1a73e8" : "#1a2733" }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: "#b0b8c0" }}>{sub}</div>
    </div>
  );
}

function MiniLineChart({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data, 1);
  const W = 400;
  const H = 56;
  const pts = data.map((v, i) => {
    const x = data.length === 1 ? W / 2 : (i / (data.length - 1)) * W;
    const y = H - (v / max) * (H - 8);
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`}
      style={{ borderRadius: 4, background: "#f9fafb", border: "1px solid #e8edf2", marginTop: 4 }}>
      <defs>
        <linearGradient id={`g-${color}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.15" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={`0,${H} ${pts} ${W},${H}`}
        fill={`url(#g-${color})`}
      />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
      {data.length > 0 && (
        <>
          <circle
            cx={data.length === 1 ? W / 2 : W}
            cy={H - (data[data.length - 1] / max) * (H - 8)}
            r="3" fill={color}
          />
          <text x={W - 4} y={10} fontSize={9} fill={color} textAnchor="end" fontWeight="600">
            {data[data.length - 1].toLocaleString()}
          </text>
          <text x={4} y={H - 4} fontSize={9} fill="#b0b8c0">0</text>
        </>
      )}
    </svg>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden", background: "#f4f6f9" },

  // Topbar
  topbar: {
    height: 56, background: "#fff", borderBottom: "1px solid #e1e6eb",
    display: "flex", alignItems: "center", padding: "0 24px",
    justifyContent: "space-between", flexShrink: 0
  },
  topbarLeft: { display: "flex", flexDirection: "column", gap: 1 },
  topbarTitle: { display: "flex", flexDirection: "column", gap: 1 },
  pageTitle: { fontSize: 15, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.2px" },
  pageSub: { fontSize: 11, color: "#8a96a3" },
  topbarRight: { display: "flex", alignItems: "center", gap: 10 },
  runningPill: {
    display: "flex", alignItems: "center", gap: 6,
    background: "#fef3e0", border: "1px solid #fcd9a0",
    borderRadius: 20, padding: "4px 12px",
    fontSize: 12, fontWeight: 600, color: "#e8710a"
  },
  pulsingDot: {
    width: 7, height: 7, borderRadius: "50%", background: "#e8710a",
    animation: "pulse 1.5s infinite"
  },
  completePill: {
    background: "#e8f7ef", border: "1px solid #b8e6cc",
    borderRadius: 20, padding: "4px 12px",
    fontSize: 12, fontWeight: 600, color: "#00874a"
  },
  exportBtn: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    color: "#5a6675", padding: "5px 10px", fontSize: 12,
    cursor: "pointer", display: "flex", alignItems: "center", gap: 4
  },

  // Body
  body: { flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: 16 },

  // Section
  section: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 10, padding: "20px 24px",
    display: "flex", flexDirection: "column", gap: 18
  },
  sectionHeader: { display: "flex", flexDirection: "column", gap: 2, paddingBottom: 12, borderBottom: "1px solid #f0f2f5" },
  sectionTitle: { fontSize: 13, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.1px" },
  sectionSub: { fontSize: 11, color: "#8a96a3" },

  // Config grid
  configGrid: { display: "flex", gap: 24, flexWrap: "wrap" },
  configBlock: { display: "flex", flexDirection: "column", gap: 8, minWidth: 200 },
  blockLabel: { fontSize: 11, fontWeight: 600, color: "#5a6675", display: "flex", alignItems: "center", gap: 6 },
  forcedTag: { fontSize: 10, color: "#b0b8c0", fontWeight: 400 },

  // Segmented control
  segmented: { display: "flex", background: "#f4f6f9", borderRadius: 7, padding: 3, gap: 2 },
  seg: {
    flex: 1, border: "none", borderRadius: 5, padding: "6px 12px",
    fontSize: 12, fontWeight: 500, cursor: "pointer",
    background: "transparent", color: "#5a6675", transition: "all 0.15s"
  },
  segActive: { background: "#fff", color: "#1a73e8", fontWeight: 600, boxShadow: "0 1px 3px rgba(0,0,0,0.08)" },
  segDisabled: { opacity: 0.4, cursor: "not-allowed", pointerEvents: "none" as const },

  // Fields
  fieldsGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 },
  templateRow: { display: "flex", gap: 14, alignItems: "flex-start" },
  fieldHint: { fontSize: 10, color: "#b0b8c0", marginTop: 2, lineHeight: 1.4 },

  input: {
    background: "#f9fafb", border: "1px solid #dde2e8", borderRadius: 6,
    padding: "8px 11px", color: "#1a2733", fontSize: 13, outline: "none",
    width: "100%", boxSizing: "border-box" as const
  },
  inputDisabled: { background: "#f0f2f5", color: "#b0b8c0", cursor: "not-allowed" },
  select: {
    background: "#f9fafb", border: "1px solid #dde2e8", borderRadius: 6,
    padding: "8px 11px", color: "#1a2733", fontSize: 13,
    outline: "none", cursor: "pointer", width: "100%"
  },

  // Preview
  previewBox: {
    background: "#f4f6f9", border: "1px solid #e1e6eb",
    borderRadius: 6, padding: "8px 12px",
    display: "flex", flexDirection: "column", gap: 4, flex: 1
  },
  previewLabel: { fontSize: 10, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.5px" },
  previewCode: { fontSize: 12, color: "#00874a", fontFamily: "monospace" },

  errorBox: {
    background: "#fce8e6", border: "1px solid #f5b9b3",
    borderRadius: 6, padding: "10px 14px", color: "#d93025", fontSize: 13
  },

  // Action
  actionRow: { display: "flex", alignItems: "center", paddingTop: 4, borderTop: "1px solid #f0f2f5" },
  runBtn: {
    background: "#1a73e8", color: "#fff", border: "none",
    borderRadius: 7, padding: "10px 24px", fontSize: 13,
    fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 7
  },
  stopBtn: {
    background: "#d93025", color: "#fff", border: "none",
    borderRadius: 7, padding: "10px 24px", fontSize: 13,
    fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 7
  },

  // Progress
  progressSection: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 10, padding: "16px 24px",
    display: "flex", flexDirection: "column", gap: 12
  },
  progressTop: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  progressLeft: { display: "flex", alignItems: "baseline", gap: 10 },
  progressLabel: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
  progressPct: { fontSize: 22, fontWeight: 700, color: "#1a73e8" },
  liveRow: { display: "flex", gap: 8 },
  livePill: {
    background: "#f4f6f9", border: "1px solid #e1e6eb",
    borderRadius: 6, padding: "4px 10px", fontSize: 12,
    display: "flex", alignItems: "center", gap: 5, color: "#1a2733"
  },
  liveUnit: { color: "#8a96a3", fontSize: 11 },
  track: { background: "#eef1f5", borderRadius: 6, height: 6, overflow: "hidden" },
  fill: { height: "100%", background: "linear-gradient(90deg, #1a73e8, #34a853)", borderRadius: 6, transition: "width 0.4s ease" },

  // Results
  resultsSection: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 10, padding: "20px 24px",
    display: "flex", flexDirection: "column", gap: 16
  },
  resultsSectionHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start" },
  resultsMeta: { display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" },
  flowTag: {
    background: "#f4f6f9", border: "1px solid #dde2e8",
    borderRadius: 5, padding: "3px 10px", fontSize: 12, color: "#1a2733", fontFamily: "monospace"
  },
  metaTag: {
    background: "#f4f6f9", border: "1px solid #e1e6eb",
    borderRadius: 5, padding: "3px 10px", fontSize: 11, color: "#5a6675"
  },
  keyMetrics: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
  secondaryMetrics: { display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 8 },

  // Warmup
  warmupCard: {
    background: "#fffbf0", border: "1px solid #fde8b4",
    borderRadius: 8, padding: "14px 18px",
    display: "flex", flexDirection: "column", gap: 12
  },
  warmupHeader: { display: "flex", alignItems: "baseline", gap: 10 },
  warmupTitle: { fontSize: 12, fontWeight: 700, color: "#b45309" },
  warmupSub: { fontSize: 11, color: "#c4965a" },
  warmupRow: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 },

  // Mini charts
  miniChartRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
  miniChart: { display: "flex", flexDirection: "column", gap: 4 },
  miniChartLabel: { fontSize: 11, fontWeight: 600, color: "#5a6675" },
};