// import { useState, useEffect } from "react";
// import { publish, getHistory, clearHistory } from "../api";
// import { HistoryItem } from "../types";
// import { IconSend, IconClear, IconReplay } from "./Icons";

// export default function PublishPanel() {
//   const [topic, setTopic] = useState("");
//   const [message, setMessage] = useState("");
//   const [status, setStatus] = useState<"idle"|"ok"|"err">("idle");
//   const [publishCount, setPublishCount] = useState(0);
//   const [history, setHistory] = useState<HistoryItem[]>([]);

//   useEffect(() => {
//     getHistory().then((r) => setHistory(r.data)).catch(() => {});
//   }, []);

//   const handlePublish = async () => {
//     try {
//       await publish(topic, message);
//       setStatus("ok");
//       setPublishCount(c => c + 1);
//       getHistory().then((r) => setHistory(r.data));
//     } catch {
//       setStatus("err");
//     }
//   };

//   const handleClear = async () => {
//     await clearHistory();
//     setHistory([]);
//     setStatus("idle");
//     setPublishCount(0);
//   };

//   const replay = (item: HistoryItem) => {
//     setTopic(item.topic);
//     setMessage(item.message);
//     setStatus("idle");
//   };

//   return (
//     <div style={s.page}>
//       {/* Topbar */}
//       <div style={s.topbar}>
//         <div style={s.topbarLeft}>
//           <span style={s.pageTitle}>Publish Message</span>
//           <span style={s.tagBlue}>Direct</span>
//         </div>
//         <div style={s.topbarRight}>
//           {publishCount > 0 && (
//             <span style={s.tagGreen}>✓ {publishCount} published</span>
//           )}
//           {status === "err" && (
//             <span style={s.tagRed}>✗ Publish failed</span>
//           )}
//         </div>
//       </div>

//       {/* Form */}
//       <div style={s.body}>
//         <div style={s.section}>
//           <div style={s.label}>Topic</div>
//           <input
//             style={s.input}
//             placeholder="e.g. trade/stock"
//             value={topic}
//             onChange={(e) => setTopic(e.target.value)}
//           />
//         </div>

//         <div style={s.section}>
//           <div style={s.label}>Payload</div>
//           <textarea
//             style={s.textarea}
//             placeholder='{"key": "value"}'
//             value={message}
//             onChange={(e) => setMessage(e.target.value)}
//             rows={5}
//           />
//         </div>

//         <div style={s.actionRow}>
//           <button style={s.btnPrimary} onClick={handlePublish}>
//             <IconSend color="#fff" />
//             Publish
//           </button>
//         </div>

//         <div style={s.divider} />

//         {/* History */}
//         <div style={s.historyHeader}>
//           <span style={s.label}>History & Replay</span>
//           {history.length > 0 && (
//             <button style={s.btnGhost} onClick={handleClear}>
//               <IconClear color="#848d97" />
//               Clear
//             </button>
//           )}
//         </div>

//         {history.length === 0
//           ? <p style={s.empty}>No history yet</p>
//           : (
//             <div style={s.historyList}>
//               {history.map((h, i) => (
//                 <div key={i} style={s.historyItem}>
//                   <div style={{ flex: 1, minWidth: 0 }}>
//                     <div style={s.historyTop}>
//                       <span style={s.topicPill}>{h.topic}</span>
//                       <span style={s.timestamp}>{new Date(h.timestamp).toLocaleTimeString()}</span>
//                     </div>
//                     <p style={s.historyMsg}>{h.message}</p>
//                   </div>
//                   <button style={s.replayBtn} onClick={() => replay(h)}>
//                     <IconReplay color="#58a6ff" />
//                   </button>
//                 </div>
//               ))}
//             </div>
//           )
//         }
//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//   topbar: {
//     height: 48, background: "#161b22", borderBottom: "1px solid #21262d",
//     display: "flex", alignItems: "center", padding: "0 20px",
//     justifyContent: "space-between", flexShrink: 0
//   },
//   topbarLeft: { display: "flex", alignItems: "center", gap: 10 },
//   topbarRight: { display: "flex", alignItems: "center", gap: 8 },
// pageTitle: { fontSize: 14, fontWeight: 600, color: "#e6edf3", letterSpacing: "-0.2px", fontFamily: "'Inter', sans-serif" },
//   tagBlue: { fontSize: 11, padding: "2px 8px", borderRadius: 20, background: "#1f3a5f", color: "#58a6ff", fontWeight: 500 },
//   tagGreen: { fontSize: 11, padding: "2px 8px", borderRadius: 20, background: "#0d2b1a", color: "#3fb950", fontWeight: 500 },
//   tagRed: { fontSize: 11, padding: "2px 8px", borderRadius: 20, background: "#3d1212", color: "#f85149", fontWeight: 500 },
//   body: { flex: 1, overflowY: "auto", padding: 20, display: "flex", flexDirection: "column", gap: 16 },
//   section: { display: "flex", flexDirection: "column", gap: 6 },
//   label: { fontSize: 11, fontWeight: 600, color: "#484f58", textTransform: "uppercase", letterSpacing: "0.8px" },
//   input: {
//     background: "#0d1117", border: "1px solid #30363d", borderRadius: 6,
//     padding: "8px 12px", color: "#c9d1d9", fontSize: 13, outline: "none",
//     maxWidth: 520
//   },
//   textarea: {
//     background: "#0d1117", border: "1px solid #30363d", borderRadius: 6,
//     padding: "10px 12px", color: "#c9d1d9", fontSize: 12,
//     fontFamily: "monospace", resize: "vertical", outline: "none", maxWidth: 520
//   },
//   actionRow: { display: "flex", gap: 8, alignItems: "center" },
//   btnPrimary: {
//     background: "#1f6feb", color: "#fff", border: "none",
//     borderRadius: 6, padding: "8px 16px", fontSize: 13,
//     fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
//   },
//   btnGhost: {
//     background: "transparent", border: "1px solid #30363d",
//     borderRadius: 6, color: "#848d97", padding: "4px 10px",
//     fontSize: 12, cursor: "pointer", display: "flex", alignItems: "center", gap: 5
//   },
//   divider: { height: 1, background: "#21262d" },
//   historyHeader: { display: "flex", alignItems: "center", justifyContent: "space-between" },
//   historyList: { display: "flex", flexDirection: "column", gap: 6 },
//   historyItem: {
//     background: "#161b22", border: "1px solid #21262d",
//     borderRadius: 8, padding: "10px 14px",
//     display: "flex", alignItems: "flex-start", gap: 10
//   },
//   historyTop: { display: "flex", alignItems: "center", gap: 8, marginBottom: 4 },
//   topicPill: { fontSize: 11, background: "#1f3a5f", color: "#58a6ff", padding: "2px 8px", borderRadius: 20 },
//   timestamp: { fontSize: 11, color: "#484f58" },
//   historyMsg: { color: "#8b949e", fontSize: 12, fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 380 },
//   replayBtn: {
//     background: "transparent", border: "1px solid #30363d",
//     borderRadius: 6, padding: "6px 8px", cursor: "pointer",
//     display: "flex", alignItems: "center", flexShrink: 0
//   },
//   empty: { color: "#484f58", fontSize: 13 }
// };

import { useState, useEffect } from "react";
import { publish, getHistory, clearHistory } from "../api";
import { HistoryItem } from "../types";
import { IconSend, IconClear, IconReplay } from "./Icons";

export default function PublishPanel() {
  const [topic, setTopic] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle"|"ok"|"err">("idle");
  const [publishCount, setPublishCount] = useState(0);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    getHistory().then((r) => setHistory(r.data)).catch(() => {});
  }, []);

  const handlePublish = async () => {
    try {
      await publish(topic, message);
      setStatus("ok");
      setPublishCount(c => c + 1);
      getHistory().then((r) => setHistory(r.data));
    } catch {
      setStatus("err");
    }
  };

  const handleClear = async () => {
    await clearHistory();
    setHistory([]);
    setStatus("idle");
    setPublishCount(0);
  };

  const replay = (item: HistoryItem) => {
    setTopic(item.topic);
    setMessage(item.message);
    setStatus("idle");
  };

  return (
    <div style={s.page}>
      <div style={s.topbar}>
        <div style={s.topbarLeft}>
          <span style={s.pageTitle}>Publish Message</span>
          <span style={s.tagBlue}>Direct</span>
        </div>
        <div style={s.topbarRight}>
          {publishCount > 0 && <span style={s.tagGreen}>✓ {publishCount} published</span>}
          {status === "err" && <span style={s.tagRed}>✗ Publish failed</span>}
        </div>
      </div>

      <div style={s.body}>
        <div style={s.section}>
          <div style={s.label}>Topic</div>
          <input
            style={s.input}
            placeholder="e.g. trade/stock"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div style={s.section}>
          <div style={s.label}>Payload</div>
          <textarea
            style={s.textarea}
            placeholder='{"key": "value"}'
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
          />
        </div>

        <div style={s.actionRow}>
          <button style={s.btnPrimary} onClick={handlePublish}>
            <IconSend color="#fff" />
            Publish
          </button>
        </div>

        <div style={s.divider} />

        <div style={s.historyHeader}>
          <span style={s.label}>History & Replay</span>
          {history.length > 0 && (
            <button style={s.btnGhost} onClick={handleClear}>
              <IconClear color="#5a6675" />
              Clear
            </button>
          )}
        </div>

        {history.length === 0
          ? <p style={s.empty}>No history yet</p>
          : (
            <div style={s.historyList}>
              {history.map((h, i) => (
                <div key={i} style={s.historyItem}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={s.historyTop}>
                      <span style={s.topicPill}>{h.topic}</span>
                      <span style={s.timestamp}>{new Date(h.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p style={s.historyMsg}>{h.message}</p>
                  </div>
                  <button style={s.replayBtn} onClick={() => replay(h)}>
                    <IconReplay color="#1a73e8" />
                  </button>
                </div>
              ))}
            </div>
          )
        }
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
  tagBlue: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f0fe", color: "#1a73e8", fontWeight: 500 },
  tagGreen: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#e8f7ef", color: "#00874a", fontWeight: 500 },
  tagRed: { fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#fce8e6", color: "#d93025", fontWeight: 500 },
  body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 16 },
  section: { display: "flex", flexDirection: "column", gap: 6 },
  label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
  input: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    padding: "9px 12px", color: "#1a2733", fontSize: 13, outline: "none",
    maxWidth: 520
  },
  textarea: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    padding: "10px 12px", color: "#1a2733", fontSize: 12,
    fontFamily: "monospace", resize: "vertical", outline: "none", maxWidth: 520
  },
  actionRow: { display: "flex", gap: 8, alignItems: "center" },
  btnPrimary: {
    background: "#1a73e8", color: "#fff", border: "none",
    borderRadius: 6, padding: "9px 18px", fontSize: 13,
    fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6
  },
  btnGhost: {
    background: "#fff", border: "1px solid #d4dae0",
    borderRadius: 6, color: "#5a6675", padding: "4px 10px",
    fontSize: 12, cursor: "pointer", display: "flex", alignItems: "center", gap: 5
  },
  divider: { height: 1, background: "#e1e6eb" },
  historyHeader: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  historyList: { display: "flex", flexDirection: "column", gap: 6 },
  historyItem: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 8, padding: "10px 14px",
    display: "flex", alignItems: "flex-start", gap: 10
  },
  historyTop: { display: "flex", alignItems: "center", gap: 8, marginBottom: 4 },
  topicPill: { fontSize: 11, background: "#e8f0fe", color: "#1a73e8", padding: "2px 8px", borderRadius: 20 },
  timestamp: { fontSize: 11, color: "#8a96a3" },
  historyMsg: { color: "#5a6675", fontSize: 12, fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 380 },
  replayBtn: {
    background: "#fff", border: "1px solid #d4dae0",
    borderRadius: 6, padding: "6px 8px", cursor: "pointer",
    display: "flex", alignItems: "center", flexShrink: 0
  },
  empty: { color: "#8a96a3", fontSize: 13 }
};