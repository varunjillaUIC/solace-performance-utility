import { useState, useRef, useCallback } from "react";
import PublishPanel from "./PublishPanel";
import SubscribePanel from "./SubscribePanel";
import QueuePanel from "./QueuePanel";
import ProfilesPanel from "./ProfilesPanel";
import PerfPanel from "./PerfPanel";
import Logo from "./Logo";
import {
  IconPublish, IconSubscribe, IconQueue,
  IconPerf, IconProfiles, IconDisconnect
} from "./Icons";
import { disconnect } from "../api";
import { Message } from "../types";

interface Props {
  onDisconnect: () => void;
  vpn?: string;
}

type Tab = "Publish" | "Subscribe" | "Queue" | "Perf" | "Profiles";

const navItems: { id: Tab; label: string; icon: any; section: string }[] = [
  { id: "Publish",   label: "Publish",   icon: IconPublish,   section: "Messaging" },
  { id: "Subscribe", label: "Subscribe", icon: IconSubscribe, section: "Messaging" },
  { id: "Queue",     label: "Queue",     icon: IconQueue,     section: "Messaging" },
  { id: "Perf",      label: "Perf Test", icon: IconPerf,      section: "Tools"     },
  { id: "Profiles",  label: "Profiles",  icon: IconProfiles,  section: "Tools"     },
];

export default function Dashboard({ onDisconnect, vpn }: Props) {
  const [tab, setTab] = useState<Tab>("Publish");

  const [subTopic, setSubTopic] = useState("");
  const [subMessages, setSubMessages] = useState<Message[]>([]);
  const [subConnected, setSubConnected] = useState(false);
  const [subStatus, setSubStatus] = useState("");
  const subWsRef = useRef<WebSocket | null>(null);

  const [queueName, setQueueName] = useState("");
  const [queueMessages, setQueueMessages] = useState<Message[]>([]);
  const [queueConnected, setQueueConnected] = useState(false);
  const [queueStatus, setQueueStatus] = useState("");
  const queueWsRef = useRef<WebSocket | null>(null);

  const startSubscribe = useCallback((topic: string) => {
    if (subWsRef.current) subWsRef.current.close();
    const ws = new WebSocket(`ws://localhost:8000/ws/subscribe?topic=${encodeURIComponent(topic)}`);
    subWsRef.current = ws;
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status) { setSubStatus(data.status); setSubConnected(true); return; }
      if (data.error) { setSubStatus(data.error); return; }
      setSubMessages((prev) => [{
        id: Date.now().toString(),
        topic: data.topic,
        message: data.message,
        timestamp: new Date().toISOString()
      }, ...prev].slice(0, 200));
    };
    ws.onclose = () => { setSubConnected(false); setSubStatus("Disconnected"); };
  }, []);

  const stopSubscribe = useCallback(() => {
    subWsRef.current?.close();
    setSubConnected(false);
    setSubStatus("Stopped");
  }, []);

  const clearSubMessages = useCallback(() => {
    setSubMessages([]);
    setSubStatus("");
  }, []);

  const startQueue = useCallback((name: string) => {
    if (queueWsRef.current) queueWsRef.current.close();
    const ws = new WebSocket(`ws://localhost:8000/ws/queue?queue_name=${encodeURIComponent(name)}`);
    queueWsRef.current = ws;
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status) { setQueueStatus(data.status); setQueueConnected(true); return; }
      if (data.error) { setQueueStatus(data.error); return; }
      setQueueMessages((prev) => [{
        id: Date.now().toString(),
        queue: data.queue,
        message: data.message,
        timestamp: new Date().toISOString()
      }, ...prev].slice(0, 200));
    };
    ws.onclose = () => { setQueueConnected(false); setQueueStatus("Disconnected"); };
  }, []);

  const stopQueue = useCallback(() => {
    queueWsRef.current?.close();
    setQueueConnected(false);
    setQueueStatus("Stopped");
  }, []);

  const clearQueueMessages = useCallback(() => {
    setQueueMessages([]);
    setQueueStatus("");
  }, []);

  const handleDisconnect = async () => {
    subWsRef.current?.close();
    queueWsRef.current?.close();
    await disconnect();
    onDisconnect();
  };

  const sections = ["Messaging", "Tools"];

  return (
    <div style={s.app}>
      <div style={s.sidebar}>
        <div style={s.logoArea}>
          <div style={s.logoRow}>
            <Logo />
            <div>
              <div style={s.logoText}>SolEngineer</div>
              <div style={s.logoVersion}>v1.0.0</div>
            </div>
          </div>
          <div style={s.connBadge}>
            <div style={s.connDot} />
            <span style={s.connText}>{vpn || "Connected"}</span>
          </div>
        </div>

        <nav style={s.nav}>
          {sections.map((section) => (
            <div key={section}>
              <div style={s.navSection}>{section}</div>
              {navItems.filter(n => n.section === section).map((item) => {
                const Icon = item.icon;
                const isActive = tab === item.id;
                const hasLive = (item.id === "Subscribe" && subConnected) ||
                                (item.id === "Queue" && queueConnected);
                return (
                  <button
                    key={item.id}
                    style={{ ...s.navItem, ...(isActive ? s.navItemActive : {}) }}
                    onClick={() => setTab(item.id)}
                  >
                    <Icon color={isActive ? "#1a73e8" : "#5a6675"} />
                    <span style={{ flex: 1 }}>{item.label}</span>
                    {hasLive && <div style={s.liveDot} />}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        <div style={s.sidebarFooter}>
          <button style={s.discBtn} onClick={handleDisconnect}>
            <IconDisconnect color="#5a6675" />
            Disconnect
          </button>
        </div>
      </div>

      <div style={s.main}>
        {tab === "Publish"   && <PublishPanel />}
        {tab === "Subscribe" && (
          <SubscribePanel
            topic={subTopic} setTopic={setSubTopic}
            messages={subMessages} connected={subConnected}
            status={subStatus}
            onStart={startSubscribe} onStop={stopSubscribe}
            onClear={clearSubMessages}
          />
        )}
        {tab === "Queue" && (
          <QueuePanel
            queueName={queueName} setQueueName={setQueueName}
            messages={queueMessages} connected={queueConnected}
            status={queueStatus}
            onStart={startQueue} onStop={stopQueue}
            onClear={clearQueueMessages}
          />
        )}
        {tab === "Perf"     && <PerfPanel />}
        {tab === "Profiles" && <ProfilesPanel />}
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  app: { display: "flex", height: "100vh", background: "#f5f7fa" },
  sidebar: {
    width: 210, background: "#ffffff",
    borderRight: "1px solid #e1e6eb",
    display: "flex", flexDirection: "column"
  },
  logoArea: { padding: "18px 16px 14px", borderBottom: "1px solid #e1e6eb" },
  logoRow: { display: "flex", alignItems: "center", gap: 10, marginBottom: 10 },
  logoText: { fontSize: 14, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.3px" },
  logoVersion: { fontSize: 10, color: "#8a96a3", marginTop: 1 },
  connBadge: {
    background: "#e8f7ef", border: "1px solid #b8e6cc",
    borderRadius: 6, padding: "6px 10px",
    display: "flex", alignItems: "center", gap: 6
  },
  connDot: { width: 6, height: 6, borderRadius: "50%", background: "#00874a", flexShrink: 0 },
  connText: { fontSize: 11, color: "#00874a", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
  nav: { padding: "10px 8px", flex: 1, display: "flex", flexDirection: "column", gap: 1 },
  navSection: {
    padding: "10px 10px 4px",
    fontSize: 10, fontWeight: 700, color: "#8a96a3",
    letterSpacing: "0.6px", textTransform: "uppercase"
  },
  navItem: {
    width: "100%", display: "flex", alignItems: "center", gap: 9,
    padding: "8px 10px", borderRadius: 6, border: "none",
    background: "transparent", color: "#5a6675",
    fontSize: 13, cursor: "pointer", textAlign: "left", position: "relative"
  },
  navItemActive: { background: "#e8f0fe", color: "#1a73e8", fontWeight: 500 },
  liveDot: { width: 6, height: 6, borderRadius: "50%", background: "#00874a" },
  sidebarFooter: { padding: "10px 8px", borderTop: "1px solid #e1e6eb" },
  discBtn: {
    width: "100%", padding: "7px 10px",
    background: "#fff", border: "1px solid #d4dae0",
    borderRadius: 6, color: "#5a6675", fontSize: 12,
    cursor: "pointer", display: "flex", alignItems: "center", gap: 8
  },
  main: { flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }
};