
// import { useState, useEffect } from "react";
// import { getProfiles, saveProfile, deleteProfile } from "../../../api/profiles";
// import { Profile } from "../../../types/index";

// export default function ProfilesPanel() {
//   const [profiles, setProfiles] = useState<Profile[]>([]);
//   const [name, setName] = useState("");
//   const [host, setHost] = useState("");
//   const [vpn, setVpn] = useState("");
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [status, setStatus] = useState("");

//   const load = () => getProfiles().then((r) => setProfiles(r.data));
//   useEffect(() => { load(); }, []);

//   const handleSave = async () => {
//     try {
//       await saveProfile({ name, host, vpn, username, password });
//       setStatus("✓ Saved");
//       setName(""); setHost(""); setVpn(""); setUsername(""); setPassword("");
//       load();
//     } catch { setStatus("✗ Failed"); }
//   };

//   return (
//     <div style={s.page}>
//       <div style={s.topbar}>
//         <span style={s.pageTitle}>Connection Profiles</span>
//         <span style={s.count}>{profiles.length} saved</span>
//       </div>

//       <div style={s.body}>
//         <div style={s.card}>
//           <div style={s.cardTitle}>Save New Profile</div>
//           <div style={s.grid2}>
//             <div style={s.field}>
//               <label style={s.label}>Profile Name</label>
//               <input style={s.input} placeholder="e.g. Mumbai Prod"
//                 value={name} onChange={(e) => setName(e.target.value)} />
//             </div>
//             <div style={s.field}>
//               <label style={s.label}>VPN Name</label>
//               <input style={s.input} placeholder="VPN"
//                 value={vpn} onChange={(e) => setVpn(e.target.value)} />
//             </div>
//           </div>
//           <div style={s.field}>
//             <label style={s.label}>Broker Host</label>
//             <input style={s.input} placeholder="tcps://..."
//               value={host} onChange={(e) => setHost(e.target.value)} />
//           </div>
//           <div style={s.grid2}>
//             <div style={s.field}>
//               <label style={s.label}>Username</label>
//               <input style={s.input} placeholder="Username"
//                 value={username} onChange={(e) => setUsername(e.target.value)} />
//             </div>
//             <div style={s.field}>
//               <label style={s.label}>Password</label>
//               <input style={s.input} type="password" placeholder="Password"
//                 value={password} onChange={(e) => setPassword(e.target.value)} />
//             </div>
//           </div>
//           <div style={s.saveRow}>
//             <button style={s.btnPrimary} onClick={handleSave}>Save Profile</button>
//             {status && <span style={status.startsWith("✓") ? s.ok : s.err}>{status}</span>}
//           </div>
//         </div>

//         <div style={s.cardTitle}>Saved Profiles</div>
//         {profiles.length === 0
//           ? <p style={s.empty}>No profiles saved yet</p>
//           : profiles.map((p) => (
//             <div key={p.name} style={s.profileCard}>
//               <div style={s.profileIcon}>{p.name[0].toUpperCase()}</div>
//               <div style={{ flex: 1 }}>
//                 <div style={s.profileName}>{p.name}</div>
//                 <div style={s.profileDetail}>{p.host} · {p.vpn}</div>
//               </div>
//               <button style={s.deleteBtn}
//                 onClick={() => deleteProfile(p.name).then(load)}>
//                 Delete
//               </button>
//             </div>
//           ))
//         }
//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//   topbar: {
//     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
//     display: "flex", alignItems: "center", padding: "0 20px",
//     justifyContent: "space-between", flexShrink: 0
//   },
//   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
//   count: { fontSize: 12, color: "#8a96a3" },
//   body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14 },
//   card: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 10, padding: 16, display: "flex",
//     flexDirection: "column", gap: 12, maxWidth: 560
//   },
//   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
//   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 },
//   field: { display: "flex", flexDirection: "column", gap: 5 },
//   label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
//   input: {
//     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
//     padding: "9px 12px", color: "#1a2733", fontSize: 13, outline: "none"
//   },
//   saveRow: { display: "flex", alignItems: "center", gap: 10 },
//   btnPrimary: {
//     background: "#1a73e8", color: "#fff", border: "none",
//     borderRadius: 6, padding: "9px 18px", fontSize: 13,
//     fontWeight: 500, cursor: "pointer"
//   },
//   ok: { fontSize: 12, color: "#00874a" },
//   err: { fontSize: 12, color: "#d93025" },
//   empty: { color: "#8a96a3", fontSize: 13 },
//   profileCard: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 8, padding: "12px 16px",
//     display: "flex", alignItems: "center", gap: 12, maxWidth: 560
//   },
//   profileIcon: {
//     width: 36, height: 36, borderRadius: "50%",
//     background: "#e8f0fe", color: "#1a73e8",
//     display: "flex", alignItems: "center", justifyContent: "center",
//     fontSize: 14, fontWeight: 600, flexShrink: 0
//   },
//   profileName: { fontSize: 13, fontWeight: 600, color: "#1a2733", marginBottom: 2 },
//   profileDetail: { fontSize: 11, color: "#8a96a3" },
//   deleteBtn: {
//     background: "#fff", border: "1px solid #d4dae0",
//     color: "#d93025", borderRadius: 6, padding: "5px 12px",
//     fontSize: 12, cursor: "pointer"
//   }
// };


// import { useState, useEffect } from "react";
// import { getProfiles, saveProfile, deleteProfile } from "../../../api/profiles";
// import { Profile } from "../../../types/index";

// export default function ProfilesPanel() {
//   const [profiles, setProfiles] = useState<Profile[]>([]);
//   const [name, setName] = useState("");
//   const [host, setHost] = useState("");
//   const [vpn, setVpn] = useState("");
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [status, setStatus] = useState("");

//   const load = () => getProfiles().then((r) => setProfiles(r.data));
//   useEffect(() => { load(); }, []);

//   const handleSave = async () => {
//     if (!name.trim() || !host.trim()) {
//       setStatus("✗ Name and host are required");
//       return;
//     }
//     try {
//       await saveProfile({ name, host, vpn, username, password });
//       setStatus("✓ Saved");
//       setName(""); setHost(""); setVpn(""); setUsername(""); setPassword("");
//       load();
//     } catch { setStatus("✗ Failed"); }
//   };

//   const visibleProfiles = profiles.filter((p) => !!p.name);

//   const handleDelete = (p: Profile) => {
//     if (!p.name) {
//       setStatus("✗ This profile has no name and can't be deleted here — remove it from the backend directly");
//       return;
//     }
//     deleteProfile(p.name)
//       .then(load)
//       .catch((err) => {
//         console.error("Delete failed:", err);
//         setStatus("✗ Delete failed");
//       });
//   };

//   return (
//     <div style={s.page}>
//       <div style={s.topbar}>
//         <span style={s.pageTitle}>Connection Profiles</span>
//         <span style={s.count}>{visibleProfiles.length} saved</span>
//       </div>

//       <div style={s.body}>
//         <div style={s.card}>
//           <div style={s.cardTitle}>Save New Profile</div>
//           <div style={s.grid2}>
//             <div style={s.field}>
//               <label style={s.label}>Profile Name</label>
//               <input style={s.input} placeholder="e.g. Mumbai Prod"
//                 value={name} onChange={(e) => setName(e.target.value)} />
//             </div>
//             <div style={s.field}>
//               <label style={s.label}>VPN Name</label>
//               <input style={s.input} placeholder="VPN"
//                 value={vpn} onChange={(e) => setVpn(e.target.value)} />
//             </div>
//           </div>
//           <div style={s.field}>
//             <label style={s.label}>Broker Host</label>
//             <input style={s.input} placeholder="tcps://..."
//               value={host} onChange={(e) => setHost(e.target.value)} />
//           </div>
//           <div style={s.grid2}>
//             <div style={s.field}>
//               <label style={s.label}>Username</label>
//               <input style={s.input} placeholder="Username"
//                 value={username} onChange={(e) => setUsername(e.target.value)} />
//             </div>
//             <div style={s.field}>
//               <label style={s.label}>Password</label>
//               <input style={s.input} type="password" placeholder="Password"
//                 value={password} onChange={(e) => setPassword(e.target.value)} />
//             </div>
//           </div>
//           <div style={s.saveRow}>
//             <button style={s.btnPrimary} onClick={handleSave}>Save Profile</button>
//             {status && <span style={status.startsWith("✓") ? s.ok : s.err}>{status}</span>}
//           </div>
//         </div>

//         <div style={s.cardTitle}>Saved Profiles</div>
//         {visibleProfiles.length === 0
//           ? <p style={s.empty}>No profiles saved yet</p>
//           : visibleProfiles.map((p) => (
//             <div key={p.name} style={s.profileCard}>
//               <div style={s.profileIcon}>{p.name[0].toUpperCase()}</div>
//               <div style={{ flex: 1 }}>
//                 <div style={s.profileName}>{p.name}</div>
//                 <div style={s.profileDetail}>{p.host} · {p.vpn}</div>
//               </div>
//               <button style={s.deleteBtn} onClick={() => handleDelete(p)}>
//                 Delete
//               </button>
//             </div>
//           ))
//         }
//       </div>
//     </div>
//   );
// }

// const s: Record<string, React.CSSProperties> = {
//   page: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
//   topbar: {
//     height: 52, background: "#fff", borderBottom: "1px solid #e1e6eb",
//     display: "flex", alignItems: "center", padding: "0 20px",
//     justifyContent: "space-between", flexShrink: 0
//   },
//   pageTitle: { fontSize: 15, fontWeight: 600, color: "#1a2733" },
//   count: { fontSize: 12, color: "#8a96a3" },
//   body: { flex: 1, overflowY: "auto", padding: 20, background: "#f5f7fa", display: "flex", flexDirection: "column", gap: 14 },
//   card: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 10, padding: 16, display: "flex",
//     flexDirection: "column", gap: 12, maxWidth: 560
//   },
//   cardTitle: { fontSize: 13, fontWeight: 600, color: "#1a2733" },
//   grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 },
//   field: { display: "flex", flexDirection: "column", gap: 5 },
//   label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
//   input: {
//     background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
//     padding: "9px 12px", color: "#1a2733", fontSize: 13, outline: "none"
//   },
//   saveRow: { display: "flex", alignItems: "center", gap: 10 },
//   btnPrimary: {
//     background: "#1a73e8", color: "#fff", border: "none",
//     borderRadius: 6, padding: "9px 18px", fontSize: 13,
//     fontWeight: 500, cursor: "pointer"
//   },
//   ok: { fontSize: 12, color: "#00874a" },
//   err: { fontSize: 12, color: "#d93025" },
//   empty: { color: "#8a96a3", fontSize: 13 },
//   profileCard: {
//     background: "#fff", border: "1px solid #e1e6eb",
//     borderRadius: 8, padding: "12px 16px",
//     display: "flex", alignItems: "center", gap: 12, maxWidth: 560
//   },
//   profileIcon: {
//     width: 36, height: 36, borderRadius: "50%",
//     background: "#e8f0fe", color: "#1a73e8",
//     display: "flex", alignItems: "center", justifyContent: "center",
//     fontSize: 14, fontWeight: 600, flexShrink: 0
//   },
//   profileName: { fontSize: 13, fontWeight: 600, color: "#1a2733", marginBottom: 2 },
//   profileDetail: { fontSize: 11, color: "#8a96a3" },
//   deleteBtn: {
//     background: "#fff", border: "1px solid #d4dae0",
//     color: "#d93025", borderRadius: 6, padding: "5px 12px",
//     fontSize: 12, cursor: "pointer"
//   }
// };


import { useState, useEffect } from "react";
import { getProfiles, saveProfile, deleteProfile } from "../../../api/profiles";
import { Profile } from "../../../types/index";
import styles from "./ProfilesPanel.module.css";

export default function ProfilesPanel() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [name, setName] = useState("");
  const [host, setHost] = useState("");
  const [vpn, setVpn] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");

  const load = () => getProfiles().then((r) => setProfiles(r.data));
  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    if (!name.trim() || !host.trim()) {
      setStatus("✗ Name and host are required");
      return;
    }
    try {
      await saveProfile({ name, host, vpn, username, password });
      setStatus("✓ Saved");
      setName(""); setHost(""); setVpn(""); setUsername(""); setPassword("");
      load();
    } catch { setStatus("✗ Failed"); }
  };

  const visibleProfiles = profiles.filter((p) => !!p.name);

  const handleDelete = (p: Profile) => {
    if (!p.name) {
      setStatus("✗ This profile has no name and can't be deleted here — remove it from the backend directly");
      return;
    }
    deleteProfile(p.name)
      .then(load)
      .catch((err) => {
        console.error("Delete failed:", err);
        setStatus("✗ Delete failed");
      });
  };

  return (
    <div className={styles.page}>
      <div className={styles.topbar}>
        <span className={styles.pageTitle}>Connection Profiles</span>
        <span className={styles.count}>{visibleProfiles.length} saved</span>
      </div>

      <div className={styles.body}>
        <div className={styles.card}>
          <div className={styles.cardTitle}>Save New Profile</div>
          <div className={styles.grid2}>
            <div className={styles.field}>
              <label className={styles.label}>Profile Name</label>
              <input className={styles.input} placeholder="e.g. Mumbai Prod"
                value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>VPN Name</label>
              <input className={styles.input} placeholder="VPN"
                value={vpn} onChange={(e) => setVpn(e.target.value)} />
            </div>
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Broker Host</label>
            <input className={styles.input} placeholder="tcps://..."
              value={host} onChange={(e) => setHost(e.target.value)} />
          </div>
          <div className={styles.grid2}>
            <div className={styles.field}>
              <label className={styles.label}>Username</label>
              <input className={styles.input} placeholder="Username"
                value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input className={styles.input} type="password" placeholder="Password"
                value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
          </div>
          <div className={styles.saveRow}>
            <button className={styles.btnPrimary} onClick={handleSave}>Save Profile</button>
            {status && <span className={status.startsWith("✓") ? styles.ok : styles.err}>{status}</span>}
          </div>
        </div>

        <div className={styles.cardTitle}>Saved Profiles</div>
        {visibleProfiles.length === 0
          ? <p className={styles.empty}>No profiles saved yet</p>
          : visibleProfiles.map((p) => (
            <div key={p.name} className={styles.profileCard}>
              <div className={styles.profileIcon}>{p.name[0].toUpperCase()}</div>
              <div style={{ flex: 1 }}>
                <div className={styles.profileName}>{p.name}</div>
                <div className={styles.profileDetail}>{p.host} · {p.vpn}</div>
              </div>
              <button className={styles.deleteBtn} onClick={() => handleDelete(p)}>
                Delete
              </button>
            </div>
          ))
        }
      </div>
    </div>
  );
}