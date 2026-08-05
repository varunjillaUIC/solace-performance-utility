import { useState, useRef, useCallback } from "react";
import { Message } from "../types/index";
import { WS_ENDPOINTS, MAX_MESSAGES } from "../config/constants";

export function useSubscriber() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connected, setConnected] = useState(false);
  const [status, setStatus]       = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  const start = useCallback((topic: string) => {
    if (wsRef.current) wsRef.current.close();
    const ws = new WebSocket(WS_ENDPOINTS.subscribe(topic));
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status) { setStatus(data.status); setConnected(true); return; }
      if (data.error)  { setStatus(data.error); return; }
      setMessages((prev) => [{
        id: Date.now().toString(),
        topic: data.topic,
        message: data.message,
        timestamp: new Date().toISOString(),
      }, ...prev].slice(0, MAX_MESSAGES));
    };

    ws.onclose = () => { setConnected(false); setStatus("Disconnected"); };
  }, []);

  const stop = useCallback(() => {
    wsRef.current?.close();
    setConnected(false);
    setStatus("Stopped");
  }, []);

  const clear = useCallback(() => {
    setMessages([]);
    setStatus("");
  }, []);

  return { messages, connected, status, start, stop, clear };
}