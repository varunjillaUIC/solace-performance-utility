
import { Message } from "../types";
import { IconClear, IconStop, IconQueue } from "./Icons";

interface Props {
  queueName: string;
  setQueueName: (v: string) => void;
  messages: Message[];
  connected: boolean;
  status: string;
  onStart: (name: string) => void;
  onStop: () => void;
  onClear: () => void;
}

export default function QueuePanel({
  queueName, setQueueName, messages, connected, status, onStart, onStop, onClear
}: Props) {
  return (
    <div style={s.page}>
      <div style={s.topbar}>
        <div style={s.topbarLeft}>
          <span style={s.pageTitle}>Queue Consumer</span>
          {connected && <span style={s.tagPurple}>● Consuming</span>}
        </div>
        <div style={s.topbarRight}>
          {messages.length > 0 && <span style={s.msgCount}>{messages.length} messages</span>}
          {messages.length > 0 && (
            <button style={s.btnGhost} onClick={onClear}>
              <IconClear color="#5a6675" /> Clear
            </button>
          )}
        </div>
      </div>

      <div style={s.body}>
        <div style={s.controlRow}>
          <input
            style={s.input}
            placeholder="Queue name"
            value={queueName}
            onChange={(e) => setQueueName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !connected && onStart(queueName)}
          />
          {!connected
            ? (
              <button style={s.btnPrimary} onClick={() => onStart(queueName)}>
                <IconQueue color="#fff" size={13} /> Start
              </button>
            ) : (
              <button style={s.btnDanger} onClick={onStop}>
                <IconStop color="#fff" size={13} /> Stop
              </button>
            )
          }
        </div>

        {status && (
          <div style={{ ...s.statusBar, ...(connected ? s.statusBarActive : {}) }}>
            {status}
          </div>
        )}

        <div style={s.feed}>
          {messages.length === 0
            ? (
              <div style={s.emptyState}>
                <IconQueue color="#d4dae0" size={32} />
                <p style={s.emptyText}>
                  {connected ? "Waiting for messages..." : "Enter a queue name to start consuming"}
                </p>
              </div>
            )
            : messages.map((m) => (
              <div key={m.id} style={s.msgCard}>
                <div style={s.msgHeader}>
                  <span style={s.queuePill}>{m.queue}</span>
                  <span style={s.timestamp}>{new Date(m.timestamp).toLocaleTimeString()}</span>
                </div>
                <p style={s.msgBody}>{m.message}</p>
              </div>
            ))
          }
        </div>
      </div>
    </div>
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
  tagPurple: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#ede7ff", color: "#7c4dff", fontWeight: 500 },
  msgCount: { fontSize: 12, color: "#8a96a3" },
  btnGhost: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    color: "#5a6675", padding: "4px 10px", fontSize: 12,
    cursor: "pointer", display: "flex", alignItems: "center", gap: 5
  },
  body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14 },
  controlRow: { display: "flex", gap: 8, maxWidth: 560 },
  input: {
    flex: 1, background: "#fff", border: "1px solid #d4dae0",
    borderRadius: 6, padding: "9px 12px", color: "#1a2733",
    fontSize: 13, outline: "none"
  },
  btnPrimary: {
    background: "#1a73e8", color: "#fff", border: "none",
    borderRadius: 6, padding: "9px 18px", fontSize: 13,
    fontWeight: 500, cursor: "pointer", display: "flex",
    alignItems: "center", gap: 6, whiteSpace: "nowrap"
  },
  btnDanger: {
    background: "#d93025", color: "#fff", border: "none",
    borderRadius: 6, padding: "9px 18px", fontSize: 13,
    fontWeight: 500, cursor: "pointer", display: "flex",
    alignItems: "center", gap: 6, whiteSpace: "nowrap"
  },
  statusBar: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 6, padding: "8px 12px", fontSize: 12,
    color: "#5a6675", maxWidth: 560
  },
  statusBarActive: { borderColor: "#c9b3ff", color: "#7c4dff", background: "#ede7ff" },
  feed: { display: "flex", flexDirection: "column", gap: 6 },
  emptyState: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", gap: 12, padding: "60px 0"
  },
  emptyText: { color: "#8a96a3", fontSize: 13 },
  msgCard: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 8, padding: "10px 14px"
  },
  msgHeader: { display: "flex", alignItems: "center", gap: 8, marginBottom: 6 },
  queuePill: { fontSize: 11, background: "#ede7ff", color: "#7c4dff", padding: "2px 8px", borderRadius: 20 },
  timestamp: { fontSize: 11, color: "#8a96a3" },
  msgBody: { color: "#5a6675", fontSize: 12, fontFamily: "monospace", wordBreak: "break-all" }
};