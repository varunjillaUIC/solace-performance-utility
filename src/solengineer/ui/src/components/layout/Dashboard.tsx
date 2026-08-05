// import { useState, useRef, useCallback } from "react";
// import PublishPanel from "./PublishPanel";
// import SubscribePanel from "./SubscribePanel";
// import QueuePanel from "./QueuePanel";
// import ProfilesPanel from "./ProfilesPanel";
// import PerfPanel from "./PerfPanel";
// import Logo from "./Logo";
// import {
//   IconPublish, IconSubscribe, IconQueue,
//   IconPerf, IconProfiles, IconDisconnect
// } from "./Icons";
// import { disconnect } from "../api";
// import { Message } from "../types";

// interface Props {
//   onDisconnect: () => void;
//   vpn?: string;
// }

// type Tab = "Publish" | "Subscribe" | "Queue" | "Perf" | "Charts" | "Profiles";


// const navItems: { id: Tab; label: string; icon: any; section: string }[] = [
//   { id: "Publish",   label: "Publish",   icon: IconPublish,   section: "Messaging" },
//   { id: "Subscribe", label: "Subscribe", icon: IconSubscribe, section: "Messaging" },
//   { id: "Queue",     label: "Queue",     icon: IconQueue,     section: "Messaging" },
//   { id: "Perf",      label: "Perf Test", icon: IconPerf,      section: "Tools"     },
//   { id: "Charts",    label: "Charts",    icon: IconChart,     section: "Tools"     },
//   { id: "Profiles",  label: "Profiles",  icon: IconProfiles,  section: "Tools"     },
  
// ];


// export default function Dashboard({ onDisconnect, vpn }: Props) {
//   const [tab, setTab] = useState<Tab>("Publish");

//   const [subTopic, setSubTopic] = useState("");
//   const [subMessages, setSubMessages] = useState<Message[]>([]);
//   const [subConnected, setSubConnected] = useState(false);
//   const [subStatus, setSubStatus] = useState("");
//   const subWsRef = useRef<WebSocket | null>(null);

//   const [perfResult, setPerfResult] = useState<PerfResult | null>(null);
//   const [liveIngress, setLiveIngress] = useState<number[]>([]);
//   const [liveEgress, setLiveEgress] = useState<number[]>([]);
//   const [perfRunning, setPerfRunning] = useState(false);

//   const [queueName, setQueueName] = useState("");
//   const [queueMessages, setQueueMessages] = useState<Message[]>([]);
//   const [queueConnected, setQueueConnected] = useState(false);
//   const [queueStatus, setQueueStatus] = useState("");
//   const queueWsRef = useRef<WebSocket | null>(null);

//   const startSubscribe = useCallback((topic: string) => {
//     if (subWsRef.current) subWsRef.current.close();
//     const ws = new WebSocket(`ws://localhost:8000/ws/subscribe?topic=${encodeURIComponent(topic)}`);
//     subWsRef.current = ws;
//     ws.onmessage = (e) => {
//       const data = JSON.parse(e.data);
//       if (data.status) { setSubStatus(data.status); setSubConnected(true); return; }
//       if (data.error) { setSubStatus(data.error); return; }
//       setSubMessages((prev) => [{
//         id: Date.now().toString(),
//         topic: data.topic,
//         message: data.message,
//         timestamp: new Date().toISOString()
//       }, ...prev].slice(0, 200));
//     };
//     ws.onclose = () => { setSubConnected(false); setSubStatus("Disconnected"); };
//   }, []);

//   const stopSubscribe = useCallback(() => {
//     subWsRef.current?.close();
//     setSubConnected(false);
//     setSubStatus("Stopped");
//   }, []);

//   const clearSubMessages = useCallback(() => {
//     setSubMessages([]);
//     setSubStatus("");
//   }, []);

//   const startQueue = useCallback((name: string) => {
//     if (queueWsRef.current) queueWsRef.current.close();
//     const ws = new WebSocket(`ws://localhost:8000/ws/queue?queue_name=${encodeURIComponent(name)}`);
//     queueWsRef.current = ws;
//     ws.onmessage = (e) => {
//       const data = JSON.parse(e.data);
//       if (data.status) { setQueueStatus(data.status); setQueueConnected(true); return; }
//       if (data.error) { setQueueStatus(data.error); return; }
//       setQueueMessages((prev) => [{
//         id: Date.now().toString(),
//         queue: data.queue,
//         message: data.message,
//         timestamp: new Date().toISOString()
//       }, ...prev].slice(0, 200));
//     };
//     ws.onclose = () => { setQueueConnected(false); setQueueStatus("Disconnected"); };
//   }, []);

//   const stopQueue = useCallback(() => {
//     queueWsRef.current?.close();
//     setQueueConnected(false);
//     setQueueStatus("Stopped");
//   }, []);

//   const clearQueueMessages = useCallback(() => {
//     setQueueMessages([]);
//     setQueueStatus("");
//   }, []);

//   const handleDisconnect = async () => {
//     subWsRef.current?.close();
//     queueWsRef.current?.close();
//     await disconnect();
//     onDisconnect();
//   };

//   const sections = ["Messaging", "Tools"];

//   return (
//     <div style={s.app}>
//       <div style={s.sidebar}>
//         <div style={s.logoArea}>
//           <div style={s.logoRow}>
//             <Logo />
//             <div>
//               <div style={s.logoText}>SolEngineer</div>
//               <div style={s.logoVersion}>v1.0.0</div>
//             </div>
//           </div>
//           <div style={s.connBadge}>
//             <div style={s.connDot} />
//             <span style={s.connText}>{vpn || "Connected"}</span>
//           </div>
//         </div>

//         <nav style={s.nav}>
//           {sections.map((section) => (
//             <div key={section}>
//               <div style={s.navSection}>{section}</div>
//               {navItems.filter(n => n.section === section).map((item) => {
//                 const Icon = item.icon;
//                 const isActive = tab === item.id;
//                 const hasLive = (item.id === "Subscribe" && subConnected) ||
//                                 (item.id === "Queue" && queueConnected);
//                 return (
//                   <button
//                     key={item.id}
//                     style={{ ...s.navItem, ...(isActive ? s.navItemActive : {}) }}
//                     onClick={() => setTab(item.id)}
//                   >
//                     <Icon color={isActive ? "#1a73e8" : "#5a6675"} />
//                     <span style={{ flex: 1 }}>{item.label}</span>
//                     {hasLive && <div style={s.liveDot} />}
//                   </button>
//                 );
//               })}
//             </div>
//           ))}
//         </nav>

//         <div style={s.sidebarFooter}>
//           <button style={s.discBtn} onClick={handleDisconnect}>
//             <IconDisconnect color="#5a6675" />
//             Disconnect
//           </button>
//         </div>
//       </div>

//       <div style={s.main}>
//         {tab === "Publish"   && <PublishPanel />}
//         {tab === "Subscribe" && (
//           <SubscribePanel
//             topic={subTopic} setTopic={setSubTopic}
//             messages={subMessages} connected={subConnected}
//             status={subStatus}
//             onStart={startSubscribe} onStop={stopSubscribe}
//             onClear={clearSubMessages}
//           />
//         )}
//         {tab === "Queue" && (
//           <QueuePanel
//             queueName={queueName} setQueueName={setQueueName}
//             messages={queueMessages} connected={queueConnected}
//             status={queueStatus}
//             onStart={startQueue} onStop={stopQueue}
//             onClear={clearQueueMessages}
//           />
//         )}
//         {tab === "Perf"     && <PerfPanel />}
//         {tab === "Profiles" && <ProfilesPanel />}
//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   app: { display: "flex", height: "100vh", background: "#f5f7fa" },
//   sidebar: {
//     width: 210, background: "#ffffff",
//     borderRight: "1px solid #e1e6eb",
//     display: "flex", flexDirection: "column"
//   },
//   logoArea: { padding: "18px 16px 14px", borderBottom: "1px solid #e1e6eb" },
//   logoRow: { display: "flex", alignItems: "center", gap: 10, marginBottom: 10 },
//   logoText: { fontSize: 14, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.3px" },
//   logoVersion: { fontSize: 10, color: "#8a96a3", marginTop: 1 },
//   connBadge: {
//     background: "#e8f7ef", border: "1px solid #b8e6cc",
//     borderRadius: 6, padding: "6px 10px",
//     display: "flex", alignItems: "center", gap: 6
//   },
//   connDot: { width: 6, height: 6, borderRadius: "50%", background: "#00874a", flexShrink: 0 },
//   connText: { fontSize: 11, color: "#00874a", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
//   nav: { padding: "10px 8px", flex: 1, display: "flex", flexDirection: "column", gap: 1 },
//   navSection: {
//     padding: "10px 10px 4px",
//     fontSize: 10, fontWeight: 700, color: "#8a96a3",
//     letterSpacing: "0.6px", textTransform: "uppercase"
//   },
//   navItem: {
//     width: "100%", display: "flex", alignItems: "center", gap: 9,
//     padding: "8px 10px", borderRadius: 6, border: "none",
//     background: "transparent", color: "#5a6675",
//     fontSize: 13, cursor: "pointer", textAlign: "left", position: "relative"
//   },
//   navItemActive: { background: "#e8f0fe", color: "#1a73e8", fontWeight: 500 },
//   liveDot: { width: 6, height: 6, borderRadius: "50%", background: "#00874a" },
//   sidebarFooter: { padding: "10px 8px", borderTop: "1px solid #e1e6eb" },
//   discBtn: {
//     width: "100%", padding: "7px 10px",
//     background: "#fff", border: "1px solid #d4dae0",
//     borderRadius: 6, color: "#5a6675", fontSize: 12,
//     cursor: "pointer", display: "flex", alignItems: "center", gap: 8
//   },
//   main: { flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }
// };


// New Code after chart before chart is upperside 


// import { useState, useRef, useCallback } from "react";
// import PublishPanel   from "../panels/publish/PublishPanel";
// import SubscribePanel from "../panels/subscribe/SubscribePanel";
// import QueuePanel     from "../panels/queue/QueuePanel";
// import ProfilesPanel  from "../panels/profiles/ProfilesPanel";
// import PerfPanel      from "../panels/perf/PerfPanel";
// import ChartsPanel    from "../panels/charts/ChartsPanel";
// import Logo           from "../common/Logo";
// import { IconPublish, IconSubscribe, IconQueue, IconPerf, IconProfiles, IconDisconnect, IconChart } from "../common/Icons";
// import { disconnectBroker } from "../../api/broker";
// import { Message, PerfResult, LiveStats } from "../../types/index";
// import { APP_NAME, APP_VERSION, MAX_CHART_POINTS } from "../../config/constants";
// import { useSubscriber }    from "../../hooks/useSubscriber";
// import { useQueueConsumer } from "../../hooks/useQueueConsumer";

// interface Props {
//   onDisconnect: () => void;
//   vpn?: string;
// }

// type Tab = "Publish" | "Subscribe" | "Queue" | "Perf" | "Charts" | "Profiles";

// const navItems: { id: Tab; label: string; icon: any; section: string }[] = [
//   { id: "Publish",   label: "Publish",   icon: IconPublish,   section: "Messaging" },
//   { id: "Subscribe", label: "Subscribe", icon: IconSubscribe, section: "Messaging" },
//   { id: "Queue",     label: "Queue",     icon: IconQueue,     section: "Messaging" },
//   { id: "Perf",      label: "Perf Test", icon: IconPerf,      section: "Tools"     },
//   { id: "Charts",    label: "Charts",    icon: IconChart,     section: "Tools"     },
//   { id: "Profiles",  label: "Profiles",  icon: IconProfiles,  section: "Tools"     },
// ];

// export default function Dashboard({ onDisconnect, vpn }: Props) {
//   const [tab, setTab] = useState<Tab>("Publish");

//   // Subscribe state
//   const [subTopic, setSubTopic] = useState("");
//   const [subMessages, setSubMessages] = useState<Message[]>([]);
//   const [subConnected, setSubConnected] = useState(false);
//   const [subStatus, setSubStatus] = useState("");
//   const subWsRef = useRef<WebSocket | null>(null);

//   // Queue state
//   const [queueName, setQueueName] = useState("");
//   const [queueMessages, setQueueMessages] = useState<Message[]>([]);
//   const [queueConnected, setQueueConnected] = useState(false);
//   const [queueStatus, setQueueStatus] = useState("");
//   const queueWsRef = useRef<WebSocket | null>(null);

//   // Perf + Charts shared state
//   const [perfResult, setPerfResult] = useState<PerfResult | null>(null);
//   const [liveIngress, setLiveIngress] = useState<number[]>([]);
//   const [liveEgress, setLiveEgress] = useState<number[]>([]);
//   const [perfRunning, setPerfRunning] = useState(false);

//   // Perf panel lifted state — survives tab switches
//  const [perfProgress, setPerfProgress] = useState(0);
// const [perfLiveStats, setPerfLiveStats] = useState<{
//   tps: number; ingress: number; elapsed: number
// } | null>(null);
// const [perfError, setPerfError] = useState("");

//   const startSubscribe = useCallback((topic: string) => {
//     if (subWsRef.current) subWsRef.current.close();
//     const ws = new WebSocket(
//       `ws://localhost:8000/ws/subscribe?topic=${encodeURIComponent(topic)}`
//     );
//     subWsRef.current = ws;
//     ws.onmessage = (e) => {
//       const data = JSON.parse(e.data);
//       if (data.status) { setSubStatus(data.status); setSubConnected(true); return; }
//       if (data.error) { setSubStatus(data.error); return; }
//       setSubMessages((prev) => [{
//         id: Date.now().toString(),
//         topic: data.topic,
//         message: data.message,
//         timestamp: new Date().toISOString()
//       }, ...prev].slice(0, 200));
//     };
//     ws.onclose = () => { setSubConnected(false); setSubStatus("Disconnected"); };
//   }, []);

//   const stopSubscribe = useCallback(() => {
//     subWsRef.current?.close();
//     setSubConnected(false);
//     setSubStatus("Stopped");
//   }, []);

//   const clearSubMessages = useCallback(() => {
//     setSubMessages([]);
//     setSubStatus("");
//   }, []);

//   const startQueue = useCallback((name: string) => {
//     if (queueWsRef.current) queueWsRef.current.close();
//     const ws = new WebSocket(
//       `ws://localhost:8000/ws/queue?queue_name=${encodeURIComponent(name)}`
//     );
//     queueWsRef.current = ws;
//     ws.onmessage = (e) => {
//       const data = JSON.parse(e.data);
//       if (data.status) { setQueueStatus(data.status); setQueueConnected(true); return; }
//       if (data.error) { setQueueStatus(data.error); return; }
//       setQueueMessages((prev) => [{
//         id: Date.now().toString(),
//         queue: data.queue,
//         message: data.message,
//         timestamp: new Date().toISOString()
//       }, ...prev].slice(0, 200));
//     };
//     ws.onclose = () => { setQueueConnected(false); setQueueStatus("Disconnected"); };
//   }, []);

//   const stopQueue = useCallback(() => {
//     queueWsRef.current?.close();
//     setQueueConnected(false);
//     setQueueStatus("Stopped");
//   }, []);

//   const clearQueueMessages = useCallback(() => {
//     setQueueMessages([]);
//     setQueueStatus("");
//   }, []);

//   const handleDisconnect = async () => {
//     subWsRef.current?.close();
//     queueWsRef.current?.close();
//     await disconnectBroker();
//     onDisconnect();
//   };

//   const sections = ["Messaging", "Tools"];

//   return (
//     <div style={s.app}>
//       <div style={s.sidebar}>
//         <div style={s.logoArea}>
//           <div style={s.logoRow}>
//             <Logo />
//             <div>
//               <div style={s.logoText}>SolEngineer</div>
//               <div style={s.logoVersion}>v1.0.0</div>
//             </div>
//           </div>
//           <div style={s.connBadge}>
//             <div style={s.connDot} />
//             <span style={s.connText}>{vpn || "Connected"}</span>
//           </div>
//         </div>

//         <nav style={s.nav}>
//           {sections.map((section) => (
//             <div key={section}>
//               <div style={s.navSection}>{section}</div>
//               {navItems.filter(n => n.section === section).map((item) => {
//                 const Icon = item.icon;
//                 const isActive = tab === item.id;
//                 const hasLive =
//                   (item.id === "Subscribe" && subConnected) ||
//                   (item.id === "Queue" && queueConnected) ||
//                   (item.id === "Charts" && perfRunning);
//                 return (
//                   <button
//                     key={item.id}
//                     style={{ ...s.navItem, ...(isActive ? s.navItemActive : {}) }}
//                     onClick={() => setTab(item.id)}
//                   >
//                     <Icon color={isActive ? "#1a73e8" : "#5a6675"} />
//                     <span style={{ flex: 1 }}>{item.label}</span>
//                     {hasLive && <div style={s.liveDot} />}
//                   </button>
//                 );
//               })}
//             </div>
//           ))}
//         </nav>

//         <div style={s.sidebarFooter}>
//           <button style={s.discBtn} onClick={handleDisconnect}>
//             <IconDisconnect color="#5a6675" />
//             Disconnect
//           </button>
//         </div>
//       </div>

//       <div style={s.main}>
//         {tab === "Publish" && <PublishPanel />}

//         {tab === "Subscribe" && (
//           <SubscribePanel
//             topic={subTopic} setTopic={setSubTopic}
//             messages={subMessages} connected={subConnected}
//             status={subStatus}
//             onStart={startSubscribe} onStop={stopSubscribe}
//             onClear={clearSubMessages}
//           />
//         )}

//         {tab === "Queue" && (
//           <QueuePanel
//             queueName={queueName} setQueueName={setQueueName}
//             messages={queueMessages} connected={queueConnected}
//             status={queueStatus}
//             onStart={startQueue} onStop={stopQueue}
//             onClear={clearQueueMessages}
//           />
//         )}

//         {tab === "Perf" && (
//   <PerfPanel
//     onResult={(r) => { setPerfResult(r); }}
//     onIngressSample={(v) =>
//       setLiveIngress((prev) => [...prev, v].slice(-60))
//     }
//     onEgressSample={(v) =>
//       setLiveEgress((prev) => [...prev, v].slice(-60))
//     }
//     onRunning={(v) => {
//       setPerfRunning(v);
//       if (v) {
//         setLiveIngress([]);
//         setLiveEgress([]);
//       }
//     }}
//     savedResult={perfResult}
//     savedProgress={perfProgress}
//     savedLiveStats={perfLiveStats}
//     savedError={perfError}
//     onProgressChange={setPerfProgress}
//     onLiveStatsChange={setPerfLiveStats}
//     onErrorChange={setPerfError}
//   />
// )}

//         {tab === "Charts" && (
//           <ChartsPanel
//             result={perfResult}
//             liveIngress={liveIngress}
//             liveEgress={liveEgress}
//             running={perfRunning}
//           />
//         )}

//         {tab === "Profiles" && <ProfilesPanel />}
//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   app: { display: "flex", height: "100vh", background: "#f5f7fa" },
//   sidebar: {
//     width: 210, background: "#ffffff",
//     borderRight: "1px solid #e1e6eb",
//     display: "flex", flexDirection: "column"
//   },
//   logoArea: { padding: "18px 16px 14px", borderBottom: "1px solid #e1e6eb" },
//   logoRow: { display: "flex", alignItems: "center", gap: 10, marginBottom: 10 },
//   logoText: { fontSize: 14, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.3px" },
//   logoVersion: { fontSize: 10, color: "#8a96a3", marginTop: 1 },
//   connBadge: {
//     background: "#e8f7ef", border: "1px solid #b8e6cc",
//     borderRadius: 6, padding: "6px 10px",
//     display: "flex", alignItems: "center", gap: 6
//   },
//   connDot: {
//     width: 6, height: 6, borderRadius: "50%",
//     background: "#00874a", flexShrink: 0
//   },
//   connText: {
//     fontSize: 11, color: "#00874a", fontWeight: 500,
//     overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
//   },
//   nav: {
//     padding: "10px 8px", flex: 1,
//     display: "flex", flexDirection: "column", gap: 1
//   },
//   navSection: {
//     padding: "10px 10px 4px",
//     fontSize: 10, fontWeight: 700, color: "#8a96a3",
//     letterSpacing: "0.6px", textTransform: "uppercase"
//   },
//   navItem: {
//     width: "100%", display: "flex", alignItems: "center", gap: 9,
//     padding: "8px 10px", borderRadius: 6, border: "none",
//     background: "transparent", color: "#5a6675",
//     fontSize: 13, cursor: "pointer", textAlign: "left", position: "relative"
//   },
//   navItemActive: { background: "#e8f0fe", color: "#1a73e8", fontWeight: 500 },
//   liveDot: { width: 6, height: 6, borderRadius: "50%", background: "#00874a" },
//   sidebarFooter: { padding: "10px 8px", borderTop: "1px solid #e1e6eb" },
//   discBtn: {
//     width: "100%", padding: "7px 10px",
//     background: "#fff", border: "1px solid #d4dae0",  
//     borderRadius: 6, color: "#5a6675", fontSize: 12,
//     cursor: "pointer", display: "flex", alignItems: "center", gap: 8
//   },
//   main: { flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }
// };


// import { useState} from "react";
// import PublishPanel   from "../panels/publish/PublishPanel";
// import SubscribePanel from "../panels/subscribe/SubscribePanel";
// import QueuePanel     from "../panels/queue/QueuePanel";
// import ProfilesPanel  from "../panels/profiles/ProfilesPanel";
// import PerfPanel      from "../panels/perf/PerfPanel";
// import ChartsPanel    from "../panels/charts/ChartsPanel";
// import Logo           from "../common/Logo";
// import {
//   IconPublish, IconSubscribe, IconQueue,
//   IconPerf, IconProfiles, IconDisconnect, IconChart
// } from "../common/Icons";
// import { disconnectBroker } from "../../api/broker";
// import {PerfResult, LiveStats } from "../../types/index";
// import { APP_NAME, APP_VERSION, MAX_CHART_POINTS } from "../../config/constants";
// import { useSubscriber }    from "../../hooks/useSubscriber";
// import { useQueueConsumer } from "../../hooks/useQueueConsumer";

// interface Props {
//   onDisconnect: () => void;
//   vpn?: string;
// }

// type Tab = "Publish" | "Subscribe" | "Queue" | "Perf" | "Charts" | "Profiles";

// const navItems: { id: Tab; label: string; icon: any; section: string }[] = [
//   { id: "Publish",   label: "Publish",   icon: IconPublish,   section: "Messaging" },
//   { id: "Subscribe", label: "Subscribe", icon: IconSubscribe, section: "Messaging" },
//   { id: "Queue",     label: "Queue",     icon: IconQueue,     section: "Messaging" },
//   { id: "Perf",      label: "Perf Test", icon: IconPerf,      section: "Tools"     },
//   { id: "Charts",    label: "Charts",    icon: IconChart,     section: "Tools"     },
//   { id: "Profiles",  label: "Profiles",  icon: IconProfiles,  section: "Tools"     },
// ];

// export default function Dashboard({ onDisconnect, vpn }: Props) {
//   const [tab, setTab] = useState<Tab>("Publish");

//   // Subscribe — via hook
//   const [subTopic, setSubTopic] = useState("");
//   const subscriber = useSubscriber();

//   // Queue — via hook
//   const [queueName, setQueueName] = useState("");
//   const queueConsumer = useQueueConsumer();

//   // Perf + Charts shared lifted state
//   const [perfResult,   setPerfResult]   = useState<PerfResult | null>(null);
//   const [liveIngress,  setLiveIngress]  = useState<number[]>([]);
//   const [liveEgress,   setLiveEgress]   = useState<number[]>([]);
//   const [perfRunning,  setPerfRunning]  = useState(false);
//   const [perfProgress, setPerfProgress] = useState(0);
//   const [perfLiveStats, setPerfLiveStats] = useState<LiveStats | null>(null);
//   const [perfError,    setPerfError]    = useState("");

//   const handleDisconnect = async () => {
//     subscriber.stop();
//     queueConsumer.stop();
//     await disconnectBroker();
//     onDisconnect();
//   };

//   const sections = ["Messaging", "Tools"];

//   return (
//     <div style={s.app}>

//       {/* Sidebar */}
//       <div style={s.sidebar}>
//         <div style={s.logoArea}>
//           <div style={s.logoRow}>
//             <Logo />
//             <div>
//               <div style={s.logoText}>{APP_NAME}</div>
//               <div style={s.logoVersion}>{APP_VERSION}</div>
//             </div>
//           </div>
//           <div style={s.connBadge}>
//             <div style={s.connDot} />
//             <span style={s.connText}>{vpn || "Connected"}</span>
//           </div>
//         </div>

//         <nav style={s.nav}>
//           {sections.map((section) => (
//             <div key={section}>
//               <div style={s.navSection}>{section}</div>
//               {navItems.filter(n => n.section === section).map((item) => {
//                 const Icon = item.icon;
//                 const isActive = tab === item.id;
//                 const hasLive =
//                   (item.id === "Subscribe" && subscriber.connected) ||
//                   (item.id === "Queue"     && queueConsumer.connected) ||
//                   (item.id === "Charts"    && perfRunning);
//                 return (
//                   <button
//                     key={item.id}
//                     style={{ ...s.navItem, ...(isActive ? s.navItemActive : {}) }}
//                     onClick={() => setTab(item.id)}
//                   >
//                     <Icon color={isActive ? "#1a73e8" : "#5a6675"} />
//                     <span style={{ flex: 1 }}>{item.label}</span>
//                     {hasLive && <div style={s.liveDot} />}
//                   </button>
//                 );
//               })}
//             </div>
//           ))}
//         </nav>

//         <div style={s.sidebarFooter}>
//           <button style={s.discBtn} onClick={handleDisconnect}>
//             <IconDisconnect color="#5a6675" />
//             Disconnect
//           </button>
//         </div>
//       </div>

//       {/* Main content */}
//       <div style={s.main}>

//         {tab === "Publish" && <PublishPanel />}

//         {tab === "Subscribe" && (
//           <SubscribePanel
//             topic={subTopic}
//             setTopic={setSubTopic}
//             messages={subscriber.messages}
//             connected={subscriber.connected}
//             status={subscriber.status}
//             onStart={subscriber.start}
//             onStop={subscriber.stop}
//             onClear={subscriber.clear}
//           />
//         )}

//         {tab === "Queue" && (
//           <QueuePanel
//             queueName={queueName}
//             setQueueName={setQueueName}
//             messages={queueConsumer.messages}
//             connected={queueConsumer.connected}
//             status={queueConsumer.status}
//             onStart={queueConsumer.start}
//             onStop={queueConsumer.stop}
//             onClear={queueConsumer.clear}
//           />
//         )}

//         {tab === "Perf" && (
//           <PerfPanel
//             onResult={(r) => setPerfResult(r)}
//             onIngressSample={(v) =>
//               setLiveIngress((prev) => [...prev, v].slice(-MAX_CHART_POINTS))
//             }
//             onEgressSample={(v) =>
//               setLiveEgress((prev) => [...prev, v].slice(-MAX_CHART_POINTS))
//             }
//             onRunning={(v) => {
//               setPerfRunning(v);
//               if (v) { setLiveIngress([]); setLiveEgress([]); }
//             }}
//             savedResult={perfResult}
//             savedProgress={perfProgress}
//             savedLiveStats={perfLiveStats}
//             savedError={perfError}
//             onProgressChange={setPerfProgress}
//             onLiveStatsChange={setPerfLiveStats}
//             onErrorChange={setPerfError}
//           />
//         )}

//         {tab === "Charts" && (
//           <ChartsPanel
//             result={perfResult}
//             liveIngress={liveIngress}
//             liveEgress={liveEgress}
//             running={perfRunning}
//           />
//         )}

//         {tab === "Profiles" && <ProfilesPanel />}

//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   app: { display: "flex", height: "100vh", background: "#f5f7fa" },
//   sidebar: {
//     width: 210, background: "#ffffff",
//     borderRight: "1px solid #e1e6eb",
//     display: "flex", flexDirection: "column"
//   },
//   logoArea: { padding: "18px 16px 14px", borderBottom: "1px solid #e1e6eb" },
//   logoRow: { display: "flex", alignItems: "center", gap: 10, marginBottom: 10 },
//   logoText: {
//     fontSize: 14, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.3px"
//   },
//   logoVersion: { fontSize: 10, color: "#8a96a3", marginTop: 1 },
//   connBadge: {
//     background: "#e8f7ef", border: "1px solid #b8e6cc",
//     borderRadius: 6, padding: "6px 10px",
//     display: "flex", alignItems: "center", gap: 6
//   },
//   connDot: {
//     width: 6, height: 6, borderRadius: "50%",
//     background: "#00874a", flexShrink: 0
//   },
//   connText: {
//     fontSize: 11, color: "#00874a", fontWeight: 500,
//     overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
//   },
//   nav: {
//     padding: "10px 8px", flex: 1,
//     display: "flex", flexDirection: "column", gap: 1
//   },
//   navSection: {
//     padding: "10px 10px 4px",
//     fontSize: 10, fontWeight: 700, color: "#8a96a3",
//     letterSpacing: "0.6px", textTransform: "uppercase"
//   },
//   navItem: {
//     width: "100%", display: "flex", alignItems: "center", gap: 9,
//     padding: "8px 10px", borderRadius: 6, border: "none",
//     background: "transparent", color: "#5a6675",
//     fontSize: 13, cursor: "pointer", textAlign: "left"
//   },
//   navItemActive: { background: "#e8f0fe", color: "#1a73e8", fontWeight: 500 },
//   liveDot: {
//     width: 6, height: 6, borderRadius: "50%", background: "#00874a"
//   },
//   sidebarFooter: { padding: "10px 8px", borderTop: "1px solid #e1e6eb" },
//   discBtn: {
//     width: "100%", padding: "7px 10px",
//     background: "#fff", border: "1px solid #d4dae0",
//     borderRadius: 6, color: "#5a6675", fontSize: 12,
//     cursor: "pointer", display: "flex", alignItems: "center", gap: 8
//   },
//   main: { flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }
// };

import { useState } from "react";
import PublishPanel   from "../panels/publish/PublishPanel";
import SubscribePanel from "../panels/subscribe/SubscribePanel";
import QueuePanel     from "../panels/queue/QueuePanel";
import ProfilesPanel  from "../panels/profiles/ProfilesPanel";
import PerfPanel      from "../panels/perf/PerfPanel";
import ChartsPanel    from "../panels/charts/ChartsPanel";
import Logo           from "../common/Logo";
import {
  IconPublish, IconSubscribe, IconQueue,
  IconPerf, IconProfiles, IconDisconnect, IconChart
} from "../common/Icons";
import { disconnectBroker } from "../../api";
import { PerfResult, LiveStats } from "../../types";
import { APP_NAME, APP_VERSION, MAX_CHART_POINTS } from "../../config/constants";
import { useSubscriber }    from "../../hooks/useSubscriber";
import { useQueueConsumer } from "../../hooks/useQueueConsumer";
import styles from "./Dashboard.module.css";

interface Props {
  onDisconnect: () => void;
  vpn?: string;
}

type Tab = "Publish" | "Subscribe" | "Queue" | "Perf" | "Charts" | "Profiles";

const navItems: { id: Tab; label: string; icon: any; section: string }[] = [
  { id: "Publish",   label: "Publish",   icon: IconPublish,   section: "Messaging" },
  { id: "Subscribe", label: "Subscribe", icon: IconSubscribe, section: "Messaging" },
  { id: "Queue",     label: "Queue",     icon: IconQueue,     section: "Messaging" },
  { id: "Perf",      label: "Perf Test", icon: IconPerf,      section: "Tools"     },
  { id: "Charts",    label: "Charts",    icon: IconChart,     section: "Tools"     },
  { id: "Profiles",  label: "Profiles",  icon: IconProfiles,  section: "Tools"     },
];

export default function Dashboard({ onDisconnect, vpn }: Props) {
  const [tab, setTab] = useState<Tab>("Publish");

  const [subTopic, setSubTopic] = useState("");
  const subscriber = useSubscriber();

  const [queueName, setQueueName] = useState("");
  const queueConsumer = useQueueConsumer();

  const [perfResult,    setPerfResult]    = useState<PerfResult | null>(null);
  const [liveIngress,   setLiveIngress]   = useState<number[]>([]);
  const [liveEgress,    setLiveEgress]    = useState<number[]>([]);
  const [perfRunning,   setPerfRunning]   = useState(false);
  const [perfProgress,  setPerfProgress]  = useState(0);
  const [perfLiveStats, setPerfLiveStats] = useState<LiveStats | null>(null);
  const [perfError,     setPerfError]     = useState("");

  const handleDisconnect = async () => {
    subscriber.stop();
    queueConsumer.stop();
    await disconnectBroker();
    onDisconnect();
  };

  const sections = ["Messaging", "Tools"];

  return (
    <div className={styles.app}>

      {/* Sidebar */}
      <div className={styles.sidebar}>
        <div className={styles.logoArea}>
          <div className={styles.logoRow}>
            <Logo />
            <div>
              <div className={styles.logoText}>{APP_NAME}</div>
              <div className={styles.logoVersion}>{APP_VERSION}</div>
            </div>
          </div>
          <div className={styles.connBadge}>
            <div className={styles.connDot} />
            <span className={styles.connText}>{vpn || "Connected"}</span>
          </div>
        </div>

        <nav className={styles.nav}>
          {sections.map((section) => (
            <div key={section}>
              <div className={styles.navSection}>{section}</div>
              {navItems.filter(n => n.section === section).map((item) => {
                const Icon = item.icon;
                const isActive = tab === item.id;
                const hasLive =
                  (item.id === "Subscribe" && subscriber.connected) ||
                  (item.id === "Queue"     && queueConsumer.connected) ||
                  (item.id === "Charts"    && perfRunning);
                return (
                  <button
                    key={item.id}
                    className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
                    onClick={() => setTab(item.id)}
                  >
                    <Icon color={isActive ? "#1a73e8" : "#5a6675"} />
                    <span className={styles.navLabel}>{item.label}</span>
                    {hasLive && <div className={styles.liveDot} />}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <button className={styles.discBtn} onClick={handleDisconnect}>
            <IconDisconnect color="#5a6675" />
            Disconnect
          </button>
        </div>
      </div>

      {/* Main */}
      <div className={styles.main}>
        {tab === "Publish" && <PublishPanel />}

        {tab === "Subscribe" && (
          <SubscribePanel
            topic={subTopic}
            setTopic={setSubTopic}
            messages={subscriber.messages}
            connected={subscriber.connected}
            status={subscriber.status}
            onStart={subscriber.start}
            onStop={subscriber.stop}
            onClear={subscriber.clear}
          />
        )}

        {tab === "Queue" && (
          <QueuePanel
            queueName={queueName}
            setQueueName={setQueueName}
            messages={queueConsumer.messages}
            connected={queueConsumer.connected}
            status={queueConsumer.status}
            onStart={queueConsumer.start}
            onStop={queueConsumer.stop}
            onClear={queueConsumer.clear}
          />
        )}

        {tab === "Perf" && (
          <PerfPanel
            onResult={(r) => setPerfResult(r)}
            onIngressSample={(v) =>
              setLiveIngress((prev) => [...prev, v].slice(-MAX_CHART_POINTS))
            }
            onEgressSample={(v) =>
              setLiveEgress((prev) => [...prev, v].slice(-MAX_CHART_POINTS))
            }
            onRunning={(v) => {
              setPerfRunning(v);
              if (v) { setLiveIngress([]); setLiveEgress([]); }
            }}
            savedResult={perfResult}
            savedProgress={perfProgress}
            savedLiveStats={perfLiveStats}
            savedError={perfError}
            onProgressChange={setPerfProgress}
            onLiveStatsChange={setPerfLiveStats}
            onErrorChange={setPerfError}
          />
        )}

        {tab === "Charts" && (
          <ChartsPanel
            result={perfResult}
            liveIngress={liveIngress}
            liveEgress={liveEgress}
            running={perfRunning}
          />
        )}

        {tab === "Profiles" && <ProfilesPanel />}
      </div>
    </div>
  );
}