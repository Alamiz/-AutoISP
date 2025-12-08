import { LogEntry } from "@/lib/types";
import { useEffect, useState } from "react";

export function useLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/logs"); // adjust URL for backend

    socket.onopen = () => console.log("WebSocket connected");
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLogs((prev) => [...prev, data]);
        console.log("Received log:", data);
      } catch (err) {
        console.error("Error parsing log:", err);
      }
    };

    socket.onclose = () => console.log("WebSocket disconnected");
    return () => socket.close();
  }, []);

  return logs;
}
