import { useState, useEffect } from "react";
import ConnectScreen from "./components/ConnectScreen";
import Dashboard from "./components/Dashboard";
import { checkStatus } from "./api";

export default function App() {
  const [connected, setConnected] = useState(false);
  const [vpn, setVpn] = useState("");
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkStatus()
      .then((res) => setConnected(res.data.connected))
      .catch(() => setConnected(false))
      .finally(() => setChecking(false));
  }, []);

  if (checking) {
    return (
      <div style={{
        height: "100vh", display: "flex", alignItems: "center",
        justifyContent: "center", background: "#0d1117", color: "#484f58"
      }}>
        <p style={{ fontSize: 14 }}>Starting SolEngineer...</p>
      </div>
    );
  }

  return connected
    ? <Dashboard onDisconnect={() => setConnected(false)} vpn={vpn} />
    : <ConnectScreen onConnected={(v) => { setVpn(v); setConnected(true); }} />;
}
