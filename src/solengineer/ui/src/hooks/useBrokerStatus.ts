import { useState, useEffect } from "react";
import { checkStatus } from "../api/index";

export function useBrokerStatus() {
  const [connected, setConnected] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkStatus()
      .then((res) => setConnected(res.data.connected))
      .catch(() => setConnected(false))
      .finally(() => setChecking(false));
  }, []);

  return { connected, setConnected, checking };
}