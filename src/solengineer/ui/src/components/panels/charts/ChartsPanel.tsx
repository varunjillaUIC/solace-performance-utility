//     // import { PerfResult } from "../types";

//     // interface Props {
//     // result: PerfResult | null;
//     // liveIngress: number[];
//     // liveEgress: number[];
//     // running: boolean;
//     // }

//     // export default function ChartsPanel({ result, liveIngress, liveEgress, running }: Props) {

//     // const ingressData = running ? liveIngress : (result?.ingress_samples || []);
//     // const egressData  = running ? liveEgress  : (result?.throughput_samples || []);
//     // const maxIngress  = Math.max(...ingressData, 1);
//     // const maxEgress   = Math.max(...egressData, 1);
//     // const globalMax   = Math.max(maxIngress, maxEgress, 1);

//     // return (
//     //     <div style={s.page}>
//     //     <div style={s.topbar}>
//     //         <div style={s.topbarLeft}>
//     //         <span style={s.pageTitle}>Live Charts</span>
//     //         {running && <span style={s.tagAmber}>● Live</span>}
//     //         {result && !running && <span style={s.tagGreen}>✓ Last Run</span>}
//     //         {!result && !running && <span style={s.tagGray}>Run a Perf Test to see charts</span>}
//     //         </div>
//     //     </div>

//     //     <div style={s.body}>

//     //         {/* Summary cards */}
//     //         {(result || running) && (
//     //         <div style={s.summaryRow}>
//     //             <div style={s.summaryCard}>
//     //             <div style={s.summaryLabel}>Peak Ingress</div>
//     //             <div style={{ ...s.summaryValue, color: "#1a73e8" }}>
//     //                 {ingressData.length ? Math.max(...ingressData).toLocaleString() : "—"}
//     //                 <span style={s.summaryUnit}>msg/s</span>
//     //             </div>
//     //             <div style={s.summaryNote}>Max publish rate to broker</div>
//     //             </div>
//     //             <div style={s.summaryCard}>
//     //             <div style={s.summaryLabel}>Peak Egress</div>
//     //             <div style={{ ...s.summaryValue, color: "#00874a" }}>
//     //                 {egressData.length ? Math.max(...egressData).toLocaleString() : "—"}
//     //                 <span style={s.summaryUnit}>msg/s</span>
//     //             </div>
//     //             <div style={s.summaryNote}>Max receive rate from broker</div>
//     //             </div>
//     //             <div style={s.summaryCard}>
//     //             <div style={s.summaryLabel}>Avg Ingress</div>
//     //             <div style={{ ...s.summaryValue, color: "#1a73e8" }}>
//     //                 {ingressData.length
//     //                 ? Math.round(ingressData.reduce((a, b) => a + b, 0) / ingressData.length).toLocaleString()
//     //                 : "—"}
//     //                 <span style={s.summaryUnit}>msg/s</span>
//     //             </div>
//     //             <div style={s.summaryNote}>Average publish rate</div>
//     //             </div>
//     //             <div style={s.summaryCard}>
//     //             <div style={s.summaryLabel}>Avg Egress</div>
//     //             <div style={{ ...s.summaryValue, color: "#00874a" }}>
//     //                 {egressData.length
//     //                 ? Math.round(egressData.reduce((a, b) => a + b, 0) / egressData.length).toLocaleString()
//     //                 : "—"}
//     //                 <span style={s.summaryUnit}>msg/s</span>
//     //             </div>
//     //             <div style={s.summaryNote}>Average receive rate</div>
//     //             </div>
//     //         </div>
//     //         )}

//     //         {/* Charts side by side */}
//     //         <div style={s.chartsRow}>

//     //         {/* Ingress Chart */}
//     //         <div style={s.chartCard}>
//     //             <div style={s.chartHeader}>
//     //             <div style={s.chartTitle}>
//     //                 <span style={{ ...s.dot, background: "#1a73e8" }} />
//     //                 Ingress — Publish Rate (msg/s)
//     //             </div>
//     //             <div style={s.chartSub}>Messages going INTO broker per second</div>
//     //             </div>
//     //             {ingressData.length > 0
//     //             ? <DualChart data={ingressData} color="#1a73e8" maxVal={globalMax} />
//     //             : <EmptyChart label="Start a Perf Test to see ingress data" />
//     //             }
//     //         </div>

//     //         {/* Egress Chart */}
//     //         <div style={s.chartCard}>
//     //             <div style={s.chartHeader}>
//     //             <div style={s.chartTitle}>
//     //                 <span style={{ ...s.dot, background: "#00874a" }} />
//     //                 Egress — Receive Rate (msg/s)
//     //             </div>
//     //             <div style={s.chartSub}>Messages coming OUT of broker per second</div>
//     //             </div>
//     //             {egressData.length > 0
//     //             ? <DualChart data={egressData} color="#00874a" maxVal={globalMax} />
//     //             : <EmptyChart label="Start a Perf Test to see egress data" />
//     //             }
//     //         </div>
//     //         </div>

//     //         {/* Combined overlay chart */}
//     //         {(ingressData.length > 0 || egressData.length > 0) && (
//     //         <div style={s.chartCard}>
//     //             <div style={s.chartHeader}>
//     //             <div style={s.chartTitle}>
//     //                 <span style={{ ...s.dot, background: "#1a73e8" }} /> Ingress
//     //                 <span style={{ ...s.dot, background: "#00874a", marginLeft: 12 }} /> Egress
//     //                 &nbsp;— Combined View
//     //             </div>
//     //             <div style={s.chartSub}>
//     //                 Gap between ingress and egress = broker processing overhead
//     //             </div>
//     //             </div>
//     //             <CombinedChart
//     //             ingress={ingressData}
//     //             egress={egressData}
//     //             maxVal={globalMax}
//     //             />
//     //         </div>
//     //         )}

//     //         {/* Latency chart if result available */}
//     //         {result && (
//     //         <div style={s.chartCard}>
//     //             <div style={s.chartHeader}>
//     //             <div style={s.chartTitle}>
//     //                 <span style={{ ...s.dot, background: "#e8710a" }} />
//     //                 Latency Summary
//     //             </div>
//     //             <div style={s.chartSub}>End-to-end latency breakdown</div>
//     //             </div>
//     //             <LatencyBar result={result} />
//     //         </div>
//     //         )}
//     //     </div>
//     //     </div>
//     // );
//     // }

//     // // ── Line + Bar dual chart ─────────────────────────────────────────────────────
//     // function DualChart({ data, color, maxVal }: { data: number[]; color: string; maxVal: number }) {
//     // const W = 500;
//     // const H = 120;
//     // const barW = Math.max(2, W / data.length - 1);

//     // const linePoints = data.map((v, i) => {
//     //     const x = data.length === 1 ? W / 2 : (i / (data.length - 1)) * W;
//     //     const y = H - (v / maxVal) * (H - 10);
//     //     return `${x},${y}`;
//     // }).join(" ");

//     // return (
//     //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
//     //     style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//     //     {/* Y axis gridlines */}
//     //     {[0.25, 0.5, 0.75, 1].map((pct) => (
//     //         <line key={pct}
//     //         x1={0} y1={H - pct * (H - 10)}
//     //         x2={W} y2={H - pct * (H - 10)}
//     //         stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//     //         />
//     //     ))}

//     //     {/* Bars */}
//     //     {data.map((v, i) => {
//     //         const x = (i / data.length) * W;
//     //         const barH = (v / maxVal) * (H - 10);
//     //         return (
//     //         <rect key={i}
//     //             x={x} y={H - barH}
//     //             width={barW} height={barH}
//     //             fill={color} opacity={0.15}
//     //         />
//     //         );
//     //     })}

//     //     {/* Line */}
//     //     <polyline points={linePoints} fill="none" stroke={color} strokeWidth="2" />

//     //     {/* Dots */}
//     //     {data.map((v, i) => (
//     //         <circle key={i}
//     //         cx={data.length === 1 ? W / 2 : (i / (data.length - 1)) * W}
//     //         cy={H - (v / maxVal) * (H - 10)}
//     //         r="3" fill={color}
//     //         />
//     //     ))}

//     //     {/* Max label */}
//     //     <text x={4} y={14} fontSize={9} fill="#8a96a3">
//     //         {maxVal.toLocaleString()} msg/s
//     //     </text>

//     //     {/* Current value label */}
//     //     {data.length > 0 && (
//     //         <text x={W - 4} y={14} fontSize={9} fill={color} textAnchor="end">
//     //         {data[data.length - 1].toLocaleString()} msg/s
//     //         </text>
//     //     )}
//     //     </svg>
//     // );
//     // }

//     // // ── Combined overlay chart ────────────────────────────────────────────────────
//     // function CombinedChart({ ingress, egress, maxVal }: {
//     // ingress: number[]; egress: number[]; maxVal: number;
//     // }) {
//     // const W = 1040;
//     // const H = 140;
//     // const maxLen = Math.max(ingress.length, egress.length, 1);

//     // const toPoints = (data: number[]) =>
//     //     data.map((v, i) => {
//     //     const x = data.length === 1 ? W / 2 : (i / (maxLen - 1)) * W;
//     //     const y = H - (v / maxVal) * (H - 16);
//     //     return `${x},${y}`;
//     //     }).join(" ");

//     // return (
//     //     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
//     //     style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//     //     {/* Gridlines */}
//     //     {[0.25, 0.5, 0.75, 1].map((pct) => (
//     //         <line key={pct}
//     //         x1={0} y1={H - pct * (H - 16)}
//     //         x2={W} y2={H - pct * (H - 16)}
//     //         stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//     //         />
//     //     ))}

//     //     {/* Fill area between ingress and egress */}
//     //     {ingress.length > 0 && egress.length > 0 && (
//     //         <polygon
//     //         points={[
//     //             ...ingress.map((v, i) => {
//     //             const x = ingress.length === 1 ? W / 2 : (i / (maxLen - 1)) * W;
//     //             const y = H - (v / maxVal) * (H - 16);
//     //             return `${x},${y}`;
//     //             }),
//     //             ...egress.slice().reverse().map((v, i) => {
//     //             const ri = egress.length - 1 - i;
//     //             const x = egress.length === 1 ? W / 2 : (ri / (maxLen - 1)) * W;
//     //             const y = H - (v / maxVal) * (H - 16);
//     //             return `${x},${y}`;
//     //             })
//     //         ].join(" ")}
//     //         fill="#1a73e8"
//     //         opacity={0.06}
//     //         />
//     //     )}

//     //     {/* Egress line */}
//     //     {egress.length > 0 && (
//     //         <polyline points={toPoints(egress)}
//     //         fill="none" stroke="#00874a" strokeWidth="2" />
//     //     )}

//     //     {/* Ingress line */}
//     //     {ingress.length > 0 && (
//     //         <polyline points={toPoints(ingress)}
//     //         fill="none" stroke="#1a73e8" strokeWidth="2" strokeDasharray="6,3" />
//     //     )}

//     //     {/* Labels */}
//     //     <text x={4} y={12} fontSize={9} fill="#8a96a3">
//     //         {maxVal.toLocaleString()} msg/s
//     //     </text>
//     //     <text x={4} y={H - 4} fontSize={9} fill="#8a96a3">0</text>
//     //     </svg>
//     // );
//     // }

//     // // ── Latency bar chart ─────────────────────────────────────────────────────────
//     // function LatencyBar({ result }: { result: PerfResult }) {
//     // const metrics = [
//     //     { label: "Min",  value: result.min_latency_ms,          color: "#00874a" },
//     //     { label: "Avg",  value: result.avg_latency_ms,          color: "#1a73e8" },
//     //     { label: "P95",  value: result.p95_latency_ms,          color: "#e8710a" },
//     //     { label: "P99",  value: result.p99_latency_ms,          color: "#d93025" },
//     //     { label: "Max",  value: result.max_latency_ms,          color: "#9e1010" },
//     // ];

//     // const maxVal = Math.max(...metrics.map(m => m.value), 1);
//     // const W = 500;
//     // const H = 100;
//     // const barW = 60;
//     // const gap = (W - metrics.length * barW) / (metrics.length + 1);

//     // return (
//     //     <svg width="100%" viewBox={`0 0 ${W} ${H + 30}`}
//     //     style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//     //     {/* Gridlines */}
//     //     {[0.5, 1].map((pct) => (
//     //         <line key={pct}
//     //         x1={0} y1={H - pct * (H - 10)}
//     //         x2={W} y2={H - pct * (H - 10)}
//     //         stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//     //         />
//     //     ))}

//     //     {metrics.map((m, i) => {
//     //         const x = gap + i * (barW + gap);
//     //         const barH = (m.value / maxVal) * (H - 10);
//     //         return (
//     //         <g key={m.label}>
//     //             {/* Bar */}
//     //             <rect
//     //             x={x} y={H - barH}
//     //             width={barW} height={barH}
//     //             fill={m.color} opacity={0.8} rx={4}
//     //             />
//     //             {/* Value on top */}
//     //             <text
//     //             x={x + barW / 2} y={H - barH - 4}
//     //             fontSize={10} fill={m.color}
//     //             textAnchor="middle" fontWeight="600">
//     //             {m.value}ms
//     //             </text>
//     //             {/* Label below */}
//     //             <text
//     //             x={x + barW / 2} y={H + 16}
//     //             fontSize={10} fill="#5a6675"
//     //             textAnchor="middle">
//     //             {m.label}
//     //             </text>
//     //         </g>
//     //         );
//     //     })}
//     //     </svg>
//     // );
//     // }

//     // // ── Empty state ───────────────────────────────────────────────────────────────
//     // function EmptyChart({ label }: { label: string }) {
//     // return (
//     //     <div style={{
//     //     height: 120, display: "flex", alignItems: "center",
//     //     justifyContent: "center", background: "#f5f7fa",
//     //     borderRadius: 6, marginTop: 8
//     //     }}>
//     //     <p style={{ color: "#b0b8c0", fontSize: 13 }}>{label}</p>
//     //     </div>
//     // );
//     // }

//     // // ── Styles ────────────────────────────────────────────────────────────────────
//     // const s: Record<string, React.CSSProperties> = {
//     // page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//     // topbar: {
//     //     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
//     //     display: "flex", alignItems: "center", padding: "0 20px",
//     //     justifyContent: "space-between", flexShrink: 0
//     // },
//     // topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
//     // pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
//     // tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
//     // tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
//     // tagGray: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#f5f7fa", color: "#8a96a3", fontWeight: 500 },
//     // body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 16 },
//     // summaryRow: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
//     // summaryCard: {
//     //     background: "#fff", border: "1px solid #e1e6eb",
//     //     borderRadius: 10, padding: "14px 16px",
//     //     display: "flex", flexDirection: "column", gap: 4
//     // },
//     // summaryLabel: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
//     // summaryValue: { fontSize: 24, fontWeight: 700, color: "#1a2733", lineHeight: 1.2 },
//     // summaryUnit: { fontSize: 12, fontWeight: 400, color: "#8a96a3", marginLeft: 4 },
//     // summaryNote: { fontSize: 11, color: "#b0b8c0" },
//     // chartsRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 },
//     // chartCard: {
//     //     background: "#fff", border: "1px solid #e1e6eb",
//     //     borderRadius: 10, padding: "14px 16px"
//     // },
//     // chartHeader: { display: "flex", flexDirection: "column", gap: 3 },
//     // chartTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733", display: "flex", alignItems: "center", gap: 6 },
//     // chartSub: { fontSize: 11, color: "#8a96a3" },
//     // dot: { display: "inline-block", width: 8, height: 8, borderRadius: "50%" },
//     // };


//     import { PerfResult } from "../types";

// interface Props {
//   result: PerfResult | null;
//   liveIngress: number[];
//   liveEgress: number[];
//   running: boolean;
// }

// export default function ChartsPanel({ result, liveIngress, liveEgress, running }: Props) {

//   const ingressData = running ? liveIngress : (result?.ingress_samples || []);
//   const egressData  = running ? liveEgress  : (result?.throughput_samples || []);
//   const maxIngress  = Math.max(...ingressData, 1);
//   const maxEgress   = Math.max(...egressData, 1);
//   const globalMax   = Math.max(maxIngress, maxEgress, 1);

//   return (
//     <div style={s.page}>
//       <div style={s.topbar}>
//         <div style={s.topbarLeft}>
//           <span style={s.pageTitle}>Live Charts</span>
//           {running && <span style={s.tagAmber}>● Live</span>}
//           {result && !running && <span style={s.tagGreen}>✓ Last Run</span>}
//           {!result && !running && <span style={s.tagGray}>Run a Perf Test to see charts</span>}
//         </div>
//       </div>

//       <div style={s.body}>

//         {/* Summary cards */}
//         {(result || running) && (
//           <div style={s.summaryRow}>
//             <div style={s.summaryCard}>
//               <div style={s.summaryLabel}>Peak Ingress</div>
//               <div style={{ ...s.summaryValue, color: "#1a73e8" }}>
//                 {ingressData.length ? Math.max(...ingressData).toLocaleString() : "—"}
//                 <span style={s.summaryUnit}>msg/s</span>
//               </div>
//               <div style={s.summaryNote}>Max publish rate to broker</div>
//             </div>
//             <div style={s.summaryCard}>
//               <div style={s.summaryLabel}>Peak Egress</div>
//               <div style={{ ...s.summaryValue, color: "#00874a" }}>
//                 {egressData.length ? Math.max(...egressData).toLocaleString() : "—"}
//                 <span style={s.summaryUnit}>msg/s</span>
//               </div>
//               <div style={s.summaryNote}>Max receive rate from broker</div>
//             </div>
//             <div style={s.summaryCard}>
//               <div style={s.summaryLabel}>Avg Ingress</div>
//               <div style={{ ...s.summaryValue, color: "#1a73e8" }}>
//                 {ingressData.length
//                   ? Math.round(ingressData.reduce((a, b) => a + b, 0) / ingressData.length).toLocaleString()
//                   : "—"}
//                 <span style={s.summaryUnit}>msg/s</span>
//               </div>
//               <div style={s.summaryNote}>Average publish rate</div>
//             </div>
//             <div style={s.summaryCard}>
//               <div style={s.summaryLabel}>Avg Egress</div>
//               <div style={{ ...s.summaryValue, color: "#00874a" }}>
//                 {egressData.length
//                   ? Math.round(egressData.reduce((a, b) => a + b, 0) / egressData.length).toLocaleString()
//                   : "—"}
//                 <span style={s.summaryUnit}>msg/s</span>
//               </div>
//               <div style={s.summaryNote}>Average receive rate</div>
//             </div>
//           </div>
//         )}

//         {/* Charts side by side */}
//         <div style={s.chartsRow}>

//           {/* Ingress Chart */}
//           <div style={s.chartCard}>
//             <div style={s.chartHeader}>
//               <div style={s.chartTitle}>
//                 <span style={{ ...s.dot, background: "#1a73e8" }} />
//                 Ingress — Publish Rate (msg/s)
//               </div>
//               <div style={s.chartSub}>Messages going INTO broker per second</div>
//             </div>
//             {ingressData.length > 0
//               ? <DualChart data={ingressData} color="#1a73e8" maxVal={globalMax} />
//               : <EmptyChart label="Start a Perf Test to see ingress data" />
//             }
//           </div>

//           {/* Egress Chart */}
//           <div style={s.chartCard}>
//             <div style={s.chartHeader}>
//               <div style={s.chartTitle}>
//                 <span style={{ ...s.dot, background: "#00874a" }} />
//                 Egress — Receive Rate (msg/s)
//               </div>
//               <div style={s.chartSub}>Messages coming OUT of broker per second</div>
//             </div>
//             {egressData.length > 0
//               ? <DualChart data={egressData} color="#00874a" maxVal={globalMax} />
//               : <EmptyChart label="Start a Perf Test to see egress data" />
//             }
//           </div>
//         </div>

//         {/* Combined overlay chart */}
//         {(ingressData.length > 0 || egressData.length > 0) && (
//           <div style={s.chartCard}>
//             <div style={s.chartHeader}>
//               <div style={s.chartTitle}>
//                 <span style={{ ...s.dot, background: "#1a73e8" }} /> Ingress
//                 <span style={{ ...s.dot, background: "#00874a", marginLeft: 12 }} /> Egress
//                 &nbsp;— Combined View
//               </div>
//               <div style={s.chartSub}>
//                 Gap between ingress and egress = broker processing overhead
//               </div>
//             </div>
//             <CombinedChart
//               ingress={ingressData}
//               egress={egressData}
//               maxVal={globalMax}
//             />
//           </div>
//         )}

//         {/* Latency chart if result available */}
//         {result && (
//           <div style={s.chartCard}>
//             <div style={s.chartHeader}>
//               <div style={s.chartTitle}>
//                 <span style={{ ...s.dot, background: "#e8710a" }} />
//                 Latency Summary
//               </div>
//               <div style={s.chartSub}>End-to-end latency breakdown</div>
//             </div>
//             <LatencyBar result={result} />
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// // ── Line + Bar dual chart ─────────────────────────────────────────────────────
// function DualChart({ data, color, maxVal }: { data: number[]; color: string; maxVal: number }) {
//   const W = 500;
//   const H = 120;
//   const barW = Math.max(2, W / data.length - 1);

//   const linePoints = data.map((v, i) => {
//     const x = data.length === 1 ? W / 2 : (i / (data.length - 1)) * W;
//     const y = H - (v / maxVal) * (H - 10);
//     return `${x},${y}`;
//   }).join(" ");

//   return (
//     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
//       style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//       {/* Y axis gridlines */}
//       {[0.25, 0.5, 0.75, 1].map((pct) => (
//         <line key={pct}
//           x1={0} y1={H - pct * (H - 10)}
//           x2={W} y2={H - pct * (H - 10)}
//           stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//         />
//       ))}

//       {/* Bars */}
//       {data.map((v, i) => {
//         const x = (i / data.length) * W;
//         const barH = (v / maxVal) * (H - 10);
//         return (
//           <rect key={i}
//             x={x} y={H - barH}
//             width={barW} height={barH}
//             fill={color} opacity={0.15}
//           />
//         );
//       })}

//       {/* Line */}
//       <polyline points={linePoints} fill="none" stroke={color} strokeWidth="2" />

//       {/* Dots */}
//       {data.map((v, i) => (
//         <circle key={i}
//           cx={data.length === 1 ? W / 2 : (i / (data.length - 1)) * W}
//           cy={H - (v / maxVal) * (H - 10)}
//           r="3" fill={color}
//         />
//       ))}

//       {/* Max label */}
//       <text x={4} y={14} fontSize={9} fill="#8a96a3">
//         {maxVal.toLocaleString()} msg/s
//       </text>

//       {/* Current value label */}
//       {data.length > 0 && (
//         <text x={W - 4} y={14} fontSize={9} fill={color} textAnchor="end">
//           {data[data.length - 1].toLocaleString()} msg/s
//         </text>
//       )}
//     </svg>
//   );
// }

// // ── Combined overlay chart ────────────────────────────────────────────────────
// function CombinedChart({ ingress, egress, maxVal }: {
//   ingress: number[]; egress: number[]; maxVal: number;
// }) {
//   const W = 1040;
//   const H = 140;
//   const maxLen = Math.max(ingress.length, egress.length, 1);

//   const toPoints = (data: number[]) =>
//     data.map((v, i) => {
//       const x = data.length === 1 ? W / 2 : (i / (maxLen - 1)) * W;
//       const y = H - (v / maxVal) * (H - 16);
//       return `${x},${y}`;
//     }).join(" ");

//   return (
//     <svg width="100%" viewBox={`0 0 ${W} ${H}`}
//       style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//       {/* Gridlines */}
//       {[0.25, 0.5, 0.75, 1].map((pct) => (
//         <line key={pct}
//           x1={0} y1={H - pct * (H - 16)}
//           x2={W} y2={H - pct * (H - 16)}
//           stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//         />
//       ))}

//       {/* Fill area between ingress and egress */}
//       {ingress.length > 0 && egress.length > 0 && (
//         <polygon
//           points={[
//             ...ingress.map((v, i) => {
//               const x = ingress.length === 1 ? W / 2 : (i / (maxLen - 1)) * W;
//               const y = H - (v / maxVal) * (H - 16);
//               return `${x},${y}`;
//             }),
//             ...egress.slice().reverse().map((v, i) => {
//               const ri = egress.length - 1 - i;
//               const x = egress.length === 1 ? W / 2 : (ri / (maxLen - 1)) * W;
//               const y = H - (v / maxVal) * (H - 16);
//               return `${x},${y}`;
//             })
//           ].join(" ")}
//           fill="#1a73e8"
//           opacity={0.06}
//         />
//       )}

//       {/* Egress line */}
//       {egress.length > 0 && (
//         <polyline points={toPoints(egress)}
//           fill="none" stroke="#00874a" strokeWidth="2" />
//       )}

//       {/* Ingress line */}
//       {ingress.length > 0 && (
//         <polyline points={toPoints(ingress)}
//           fill="none" stroke="#1a73e8" strokeWidth="2" strokeDasharray="6,3" />
//       )}

//       {/* Labels */}
//       <text x={4} y={12} fontSize={9} fill="#8a96a3">
//         {maxVal.toLocaleString()} msg/s
//       </text>
//       <text x={4} y={H - 4} fontSize={9} fill="#8a96a3">0</text>
//     </svg>
//   );
// }

// // ── Latency bar chart ─────────────────────────────────────────────────────────
// function LatencyBar({ result }: { result: PerfResult }) {
//   const metrics = [
//     { label: "Min",  value: result.min_latency_ms,          color: "#00874a" },
//     { label: "Avg",  value: result.avg_latency_ms,          color: "#1a73e8" },
//     { label: "P95",  value: result.p95_latency_ms,          color: "#e8710a" },
//     { label: "P99",  value: result.p99_latency_ms,          color: "#d93025" },
//     { label: "Max",  value: result.max_latency_ms,          color: "#9e1010" },
//   ];

//   const maxVal = Math.max(...metrics.map(m => m.value), 1);
//   const W = 500;
//   const H = 100;
//   const barW = 60;
//   const gap = (W - metrics.length * barW) / (metrics.length + 1);

//   return (
//     <svg width="100%" viewBox={`0 0 ${W} ${H + 30}`}
//       style={{ borderRadius: 6, background: "#f5f7fa", marginTop: 8 }}>

//       {/* Gridlines */}
//       {[0.5, 1].map((pct) => (
//         <line key={pct}
//           x1={0} y1={H - pct * (H - 10)}
//           x2={W} y2={H - pct * (H - 10)}
//           stroke="#e1e6eb" strokeWidth="1" strokeDasharray="4,4"
//         />
//       ))}

//       {metrics.map((m, i) => {
//         const x = gap + i * (barW + gap);
//         const barH = (m.value / maxVal) * (H - 10);
//         return (
//           <g key={m.label}>
//             {/* Bar */}
//             <rect
//               x={x} y={H - barH}
//               width={barW} height={barH}
//               fill={m.color} opacity={0.8} rx={4}
//             />
//             {/* Value on top */}
//             <text
//               x={x + barW / 2} y={H - barH - 4}
//               fontSize={10} fill={m.color}
//               textAnchor="middle" fontWeight="600">
//               {m.value}ms
//             </text>
//             {/* Label below */}
//             <text
//               x={x + barW / 2} y={H + 16}
//               fontSize={10} fill="#5a6675"
//               textAnchor="middle">
//               {m.label}
//             </text>
//           </g>
//         );
//       })}
//     </svg>
//   );
// }

// // ── Empty state ───────────────────────────────────────────────────────────────
// function EmptyChart({ label }: { label: string }) {
//   return (
//     <div style={{
//       height: 120, display: "flex", alignItems: "center",
//       justifyContent: "center", background: "#f5f7fa",
//       borderRadius: 6, marginTop: 8
//     }}>
//       <p style={{ color: "#b0b8c0", fontSize: 13 }}>{label}</p>
//     </div>
//   );
// }

// // ── Styles ────────────────────────────────────────────────────────────────────
// const s: Record<string, React.CSSProperties> = {
//   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//   topbar: {
//     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
//     display: "flex", alignItems: "center", padding: "0 20px",
//     justifyContent: "space-between", flexShrink: 0
//   },
//   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
//   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
//   tagAmber: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fef3e0", color: "#e8710a", fontWeight: 500 },
//   tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
//   tagGray: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#f5f7fa", color: "#8a96a3", fontWeight: 500 },
//   body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 16 },
//   summaryRow: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 },
//   summaryCard: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 10, padding: "14px 16px",
//     display: "flex", flexDirection: "column", gap: 4
//   },
//   summaryLabel: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
//   summaryValue: { fontSize: 24, fontWeight: 700, color: "#1a2733", lineHeight: 1.2 },
//   summaryUnit: { fontSize: 12, fontWeight: 400, color: "#8a96a3", marginLeft: 4 },
//   summaryNote: { fontSize: 11, color: "#b0b8c0" },
//   chartsRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 },
//   chartCard: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 10, padding: "14px 16px"
//   },
//   chartHeader: { display: "flex", flexDirection: "column", gap: 3 },
//   chartTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733", display: "flex", alignItems: "center", gap: 6 },
//   chartSub: { fontSize: 11, color: "#8a96a3" },
//   dot: { display: "inline-block", width: 8, height: 8, borderRadius: "50%" },
// };


//Updated 17-07-26

import { PerfResult } from "../../../types/perf";

interface Props {
  result: PerfResult | null;
  liveIngress: number[];
  liveEgress: number[];
  running: boolean;
}

export default function ChartsPanel({ result, liveIngress, liveEgress, running }: Props) {
  const ingressData = running ? liveIngress : (result?.ingress_samples || []);
  const egressData  = running ? liveEgress  : (result?.throughput_samples || []);
  const globalMax   = Math.max(...ingressData, ...egressData, 1);

  const avgOf = (arr: number[]) =>
    arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0;

  const isEmpty = ingressData.length === 0 && egressData.length === 0;

  return (
    <div style={s.page}>
      <div style={s.topbar}>
        <div style={s.topbarLeft}>
          <div style={s.pageTitle}>Live Charts</div>
          <div style={s.pageSub}>Real-time ingress and egress visualization</div>
        </div>
        <div style={s.topbarRight}>
          {running && (
            <div style={s.liveBadge}>
              <div style={s.liveDot} /> Live
            </div>
          )}
          {result && !running && (
            <span style={s.completeBadge}>Last run · {result.total_time_sec}s</span>
          )}
        </div>
      </div>

      <div style={s.body}>

        {isEmpty && (
          <div style={s.emptyState}>
            <div style={s.emptyIcon}>📊</div>
            <div style={s.emptyTitle}>No data yet</div>
            <div style={s.emptyDesc}>Run a performance test to see live ingress and egress charts</div>
          </div>
        )}

        {!isEmpty && (
          <>
            {/* Summary cards */}
            <div style={s.summaryRow}>
              <SummaryCard
                label="Peak Ingress" icon="↑"
                value={ingressData.length ? Math.max(...ingressData).toLocaleString() : "—"}
                sub="max publish rate" color="#1a73e8"
              />
              <SummaryCard
                label="Avg Ingress" icon="↑"
                value={avgOf(ingressData).toLocaleString()}
                sub="avg publish rate" color="#1a73e8" muted
              />
              <SummaryCard
                label="Peak Egress" icon="↓"
                value={egressData.length ? Math.max(...egressData).toLocaleString() : "—"}
                sub="max receive rate" color="#00874a"
              />
              <SummaryCard
                label="Avg Egress" icon="↓"
                value={avgOf(egressData).toLocaleString()}
                sub="avg receive rate" color="#00874a" muted
              />
              {result && (
                <>
                  <SummaryCard
                    label="Throughput" icon="⚡"
                    value={result.throughput_msg_per_sec.toLocaleString()}
                    sub="msg/s overall" color="#7c4dff"
                  />
                  <SummaryCard
                    label="P99 Latency" icon="⏱"
                    value={`${result.p99_latency_ms} ms`}
                    sub="99th percentile" color="#e8710a"
                  />
                </>
              )}
            </div>

            {/* Side by side line charts */}
            <div style={s.chartsRow}>
              <ChartCard
                title="Ingress — Publish Rate"
                sub="Messages sent to broker per second"
                color="#1a73e8"
                data={ingressData}
                globalMax={globalMax}
                empty="No ingress data"
              />
              <ChartCard
                title="Egress — Receive Rate"
                sub="Messages received from broker per second"
                color="#00874a"
                data={egressData}
                globalMax={globalMax}
                empty="No egress data"
              />
            </div>

            {/* Combined chart */}
            {(ingressData.length > 0 || egressData.length > 0) && (
              <div style={s.card}>
                <div style={s.cardHeader}>
                  <div style={s.cardTitle}>Combined View</div>
                  <div style={s.cardSub}>
                    <LegendDot color="#1a73e8" dashed /> Ingress &nbsp;&nbsp;
                    <LegendDot color="#00874a" /> Egress &nbsp;&nbsp;
                    <span style={{ color: "#b0b8c0", fontSize: 11 }}>
                      Gap = broker processing overhead
                    </span>
                  </div>
                </div>
                <CombinedChart ingress={ingressData} egress={egressData} globalMax={globalMax} />
              </div>
            )}

            {/* Latency bar chart */}
            {result && (
              <div style={s.card}>
                <div style={s.cardHeader}>
                  <div style={s.cardTitle}>Latency Breakdown</div>
                  <div style={s.cardSub}>End-to-end latency percentiles (ms)</div>
                </div>
                <LatencyChart result={result} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Summary Card ──────────────────────────────────────────────────────────────
function SummaryCard({ label, icon, value, sub, color, muted }: {
  label: string; icon: string; value: string; sub: string; color: string; muted?: boolean;
}) {
  return (
    <div style={{
      background: "#fff", border: "1px solid #e1e6eb", borderRadius: 8,
      padding: "14px 16px", display: "flex", flexDirection: "column", gap: 6, flex: 1
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 10, fontWeight: 700, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          {label}
        </span>
        <span style={{ fontSize: 14, color: muted ? "#b0b8c0" : color }}>{icon}</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 700, color: muted ? "#5a6675" : color, lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: "#b0b8c0" }}>{sub}</div>
    </div>
  );
}

// ── Chart Card wrapper ────────────────────────────────────────────────────────
function ChartCard({ title, sub, color, data, globalMax, empty }: {
  title: string; sub: string; color: string;
  data: number[]; globalMax: number; empty: string;
}) {
  return (
    <div style={s.card}>
      <div style={s.cardHeader}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <LegendDot color={color} />
          <div style={s.cardTitle}>{title}</div>
        </div>
        <div style={s.cardSub}>{sub}</div>
      </div>
      {data.length > 0
        ? <AreaChart data={data} color={color} globalMax={globalMax} />
        : <EmptyChart label={empty} />
      }
    </div>
  );
}

// ── Area chart ────────────────────────────────────────────────────────────────
function AreaChart({ data, color, globalMax }: { data: number[]; color: string; globalMax: number }) {
  const W = 480;
  const H = 110;
  const pad = 4;
  const max = globalMax;

  const pts = data.map((v, i) => {
    const x = data.length === 1 ? W / 2 : (i / (data.length - 1)) * W;
    const y = H - pad - (v / max) * (H - pad * 2);
    return `${x},${y}`;
  });

  const polyPts = pts.join(" ");
  const areaPts = `0,${H} ${polyPts} ${W},${H}`;
  const gradId = `area-${color.replace("#", "")}`;

  const yLabels = [0, 0.25, 0.5, 0.75, 1].map(pct => ({
    y: H - pad - pct * (H - pad * 2),
    val: Math.round(max * pct)
  }));

  return (
    <div style={{ position: "relative" }}>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`}
        style={{ borderRadius: 6, background: "#f9fafb", border: "1px solid #eef0f3", display: "block" }}>
        <defs>
          <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.2" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {/* Gridlines */}
        {yLabels.map((l, i) => (
          <g key={i}>
            <line x1={0} y1={l.y} x2={W} y2={l.y}
              stroke="#e8edf2" strokeWidth="1" strokeDasharray="3,3" />
            <text x={4} y={l.y - 3} fontSize={8} fill="#c0c8d0">{l.val.toLocaleString()}</text>
          </g>
        ))}

        {/* Area fill */}
        <polygon points={areaPts} fill={`url(#${gradId})`} />

        {/* Line */}
        <polyline points={polyPts} fill="none" stroke={color} strokeWidth="1.8" strokeLinejoin="round" />

        {/* Last point dot */}
        {data.length > 0 && (
          <>
            <circle
              cx={data.length === 1 ? W / 2 : W}
              cy={H - pad - (data[data.length - 1] / max) * (H - pad * 2)}
              r="3.5" fill={color} stroke="#fff" strokeWidth="1.5"
            />
            <text
              x={W - 5}
              y={H - pad - (data[data.length - 1] / max) * (H - pad * 2) - 6}
              fontSize={9} fill={color} textAnchor="end" fontWeight="700">
              {data[data.length - 1].toLocaleString()}
            </text>
          </>
        )}
      </svg>

      {/* X axis label */}
      <div style={{ display: "flex", justifyContent: "space-between", padding: "2px 0", marginTop: 2 }}>
        <span style={{ fontSize: 9, color: "#c0c8d0" }}>0s</span>
        <span style={{ fontSize: 9, color: "#c0c8d0" }}>{data.length}s</span>
      </div>
    </div>
  );
}

// ── Combined overlay chart ────────────────────────────────────────────────────
function CombinedChart({ ingress, egress, globalMax }: {
  ingress: number[]; egress: number[]; globalMax: number;
}) {
  const W = 900;
  const H = 120;
  const pad = 4;
  const maxLen = Math.max(ingress.length, egress.length, 1);

  const toPoints = (data: number[]) =>
    data.map((v, i) => {
      const x = data.length === 1 ? W / 2 : (i / (maxLen - 1)) * W;
      const y = H - pad - (v / globalMax) * (H - pad * 2);
      return `${x},${y}`;
    });

  const iPts = toPoints(ingress).join(" ");
  const ePts = toPoints(egress).join(" ");

  const yLabels = [0, 0.5, 1].map(pct => ({
    y: H - pad - pct * (H - pad * 2),
    val: Math.round(globalMax * pct)
  }));

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`}
      style={{ borderRadius: 6, background: "#f9fafb", border: "1px solid #eef0f3", display: "block" }}>

      {yLabels.map((l, i) => (
        <g key={i}>
          <line x1={0} y1={l.y} x2={W} y2={l.y} stroke="#e8edf2" strokeWidth="1" strokeDasharray="3,3" />
          <text x={4} y={l.y - 3} fontSize={8} fill="#c0c8d0">{l.val.toLocaleString()}</text>
        </g>
      ))}

      {/* Gap fill between lines */}
      {ingress.length > 0 && egress.length > 0 && (
        <polygon
          points={`${iPts} ${toPoints(egress).reverse().join(" ")}`}
          fill="#1a73e8" opacity={0.05}
        />
      )}

      {egress.length > 0 && (
        <polyline points={ePts} fill="none" stroke="#00874a" strokeWidth="2" strokeLinejoin="round" />
      )}
      {ingress.length > 0 && (
        <polyline points={iPts} fill="none" stroke="#1a73e8" strokeWidth="2"
          strokeDasharray="6,3" strokeLinejoin="round" />
      )}
    </svg>
  );
}

// ── Latency bar chart — redesigned ───────────────────────────────────────────
function LatencyChart({ result }: { result: PerfResult }) {
  const metrics = [
    { label: "Min",  value: result.min_latency_ms, color: "#00874a" },
    { label: "Avg",  value: result.avg_latency_ms, color: "#1a73e8" },
    { label: "P95",  value: result.p95_latency_ms, color: "#e8710a" },
    { label: "P99",  value: result.p99_latency_ms, color: "#d93025" },
    { label: "Max",  value: result.max_latency_ms, color: "#9e1010" },
  ];

  const maxVal = Math.max(...metrics.map(m => m.value), 1);

  return (
    <div style={{ display: "flex", gap: 12, alignItems: "flex-end", padding: "8px 0 0" }}>
      {metrics.map((m) => {
        const pct = (m.value / maxVal) * 100;
        return (
          <div key={m.label} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            {/* Value label */}
            <div style={{ fontSize: 12, fontWeight: 700, color: m.color }}>
              {m.value} <span style={{ fontSize: 10, fontWeight: 400, color: "#8a96a3" }}>ms</span>
            </div>
            {/* Bar */}
            <div style={{
              width: "100%", height: 80, background: "#f4f6f9",
              borderRadius: 6, overflow: "hidden",
              display: "flex", alignItems: "flex-end"
            }}>
              <div style={{
                width: "100%",
                height: `${Math.max(pct, 4)}%`,
                background: `linear-gradient(180deg, ${m.color}cc, ${m.color})`,
                borderRadius: "4px 4px 0 0",
                transition: "height 0.4s ease"
              }} />
            </div>
            {/* Label */}
            <div style={{
              fontSize: 11, fontWeight: 600, color: "#5a6675",
              background: "#f4f6f9", borderRadius: 4,
              padding: "2px 8px", letterSpacing: "0.3px"
            }}>
              {m.label}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function LegendDot({ color, dashed }: { color: string; dashed?: boolean }) {
  return (
    <svg width="20" height="10" style={{ flexShrink: 0 }}>
      <line x1="0" y1="5" x2="20" y2="5"
        stroke={color} strokeWidth="2"
        strokeDasharray={dashed ? "4,2" : "none"} />
      <circle cx="10" cy="5" r="2.5" fill={color} />
    </svg>
  );
}

function EmptyChart({ label }: { label: string }) {
  return (
    <div style={{
      height: 110, display: "flex", alignItems: "center",
      justifyContent: "center", background: "#f9fafb",
      borderRadius: 6, border: "1px solid #eef0f3"
    }}>
      <span style={{ color: "#c0c8d0", fontSize: 12 }}>{label}</span>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden", background: "#f4f6f9" },

  topbar: {
    height: 56, background: "#fff", borderBottom: "1px solid #e1e6eb",
    display: "flex", alignItems: "center", padding: "0 24px",
    justifyContent: "space-between", flexShrink: 0
  },
  topbarLeft: { display: "flex", flexDirection: "column", gap: 2 },
  topbarRight: { display: "flex", alignItems: "center", gap: 10 },
  pageTitle: { fontSize: 15, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.2px" },
  pageSub: { fontSize: 11, color: "#8a96a3" },
  liveBadge: {
    display: "flex", alignItems: "center", gap: 6,
    background: "#fef3e0", border: "1px solid #fcd9a0",
    borderRadius: 20, padding: "4px 12px",
    fontSize: 12, fontWeight: 600, color: "#e8710a"
  },
  liveDot: {
    width: 7, height: 7, borderRadius: "50%", background: "#e8710a"
  },
  completeBadge: {
    background: "#f4f6f9", border: "1px solid #e1e6eb",
    borderRadius: 20, padding: "4px 12px",
    fontSize: 11, color: "#5a6675"
  },

  body: { flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: 14 },

  emptyState: {
    flex: 1, display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center", gap: 10, padding: "80px 0"
  },
  emptyIcon: { fontSize: 36, opacity: 0.3 },
  emptyTitle: { fontSize: 15, fontWeight: 600, color: "#8a96a3" },
  emptyDesc: { fontSize: 12, color: "#b0b8c0", textAlign: "center", maxWidth: 320 },

  summaryRow: { display: "flex", gap: 10 },

  chartsRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 },

  card: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 10, padding: "16px 20px",
    display: "flex", flexDirection: "column", gap: 12
  },
  cardHeader: { display: "flex", flexDirection: "column", gap: 3 },
  cardTitle: { fontSize: 13, fontWeight: 700, color: "#1a2733" },
  cardSub: { fontSize: 11, color: "#8a96a3", display: "flex", alignItems: "center", gap: 4 },
};