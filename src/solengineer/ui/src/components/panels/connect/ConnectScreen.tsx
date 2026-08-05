import { useState, useEffect } from "react";
import { connectBroker, getProfiles } from "../../../api/index";
import { Profile } from "../../../types/index";
import Logo from "../../common/Logo";

interface Props {
  onConnected: (vpn: string) => void;
}

export default function ConnectScreen({ onConnected }: Props) {
  const [host, setHost] = useState("");
  const [vpn, setVpn] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProfiles().then((r) => setProfiles(r.data)).catch(() => {});
  }, []);

  const handleConnect = async () => {
    setLoading(true);
    setError("");
    try {
      await connectBroker({ host, vpn, username, password });
      onConnected(vpn);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  const loadProfile = (p: Profile) => {
    setHost(p.host); setVpn(p.vpn);
    setUsername(p.username); setPassword(p.password);
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.logoRow}>
          <Logo />
          <div>
            <div style={s.title}>SolEngineer</div>
            <div style={s.subtitle}>Solace PubSub+ Debug Tool</div>
          </div>
        </div>

        {profiles.length > 0 && (
          <div>
            <div style={s.label}>Saved Profiles</div>
            <div style={s.profileRow}>
              {profiles.map((p) => (
                <button key={p.name} style={s.profileBtn} onClick={() => loadProfile(p)}>
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <div style={s.divider} />

        <div style={s.fields}>
          <div style={s.field}>
            <label style={s.label}>Broker Host</label>
            <input style={s.input} placeholder="tcps://mr-connection-xxx.messaging.solace.cloud:55443"
              value={host} onChange={(e) => setHost(e.target.value)} />
          </div>
          <div style={s.grid2}>
            <div style={s.field}>
              <label style={s.label}>VPN Name</label>
              <input style={s.input} placeholder="VPN"
                value={vpn} onChange={(e) => setVpn(e.target.value)} />
            </div>
            <div style={s.field}>
              <label style={s.label}>Username</label>
              <input style={s.input} placeholder="Username"
                value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
          </div>
          <div style={s.field}>
            <label style={s.label}>Password</label>
            <input style={s.input} type="password" placeholder="Password"
              value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
        </div>

        {error && <div style={s.errorBox}>{error}</div>}

        <button style={s.connectBtn} onClick={handleConnect} disabled={loading}>
          {loading ? "Connecting..." : "Connect to Broker"}
        </button>

        <p style={s.hint}>Supports TLS (tcps://) and plain (tcp://) connections</p>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: {
    height: "100vh", display: "flex", alignItems: "center",
    justifyContent: "center", background: "#f5f7fa"
  },
  card: {
    background: "#fff", border: "1px solid #e1e6eb",
    borderRadius: 14, padding: 32, width: 460,
    display: "flex", flexDirection: "column", gap: 16,
    boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
  },
  logoRow: { display: "flex", alignItems: "center", gap: 12, marginBottom: 4 },
  title: { fontSize: 19, fontWeight: 700, color: "#1a2733", letterSpacing: "-0.3px" },
  subtitle: { fontSize: 12, color: "#8a96a3", marginTop: 2 },
  divider: { height: 1, background: "#e1e6eb" },
  fields: { display: "flex", flexDirection: "column", gap: 12 },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 },
  field: { display: "flex", flexDirection: "column", gap: 5 },
  label: { fontSize: 11, fontWeight: 600, color: "#8a96a3", textTransform: "uppercase", letterSpacing: "0.6px" },
  input: {
    background: "#fff", border: "1px solid #d4dae0", borderRadius: 6,
    padding: "9px 12px", color: "#1a2733", fontSize: 13, outline: "none"
  },
  profileRow: { display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6 },
  profileBtn: {
    background: "#e8f0fe", border: "1px solid #c2d8fb",
    borderRadius: 6, color: "#1a73e8", padding: "4px 12px",
    fontSize: 12, cursor: "pointer"
  },
  errorBox: {
    background: "#fce8e6", border: "1px solid #f5b9b3",
    borderRadius: 6, padding: "8px 12px",
    color: "#d93025", fontSize: 13
  },
  connectBtn: {
    background: "#1a73e8", color: "#fff", border: "none",
    borderRadius: 8, padding: "11px 0", fontSize: 14,
    fontWeight: 600, cursor: "pointer", marginTop: 4
  },
  hint: { fontSize: 11, color: "#b0b8c0", textAlign: "center" }
};