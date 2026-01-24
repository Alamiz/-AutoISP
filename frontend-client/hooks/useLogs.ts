import { LogEntry } from "@/lib/types";
import { useEffect, useState } from "react";
import { auth } from "@/lib/auth";

export function useLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    // Load initial logs from localStorage
    try {
      const storedLogs = localStorage.getItem("auto_isp_logs");
      if (storedLogs) {
        setLogs(JSON.parse(storedLogs));
      }
    } catch (e) {
      console.error("Failed to load logs from storage", e);
    }

    let socket: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      const token = auth.getAccessToken();
      const wsUrl = `ws://139.162.141.200:8000/ws/logs/?token=${token}`;
      socket = new WebSocket(wsUrl); // adjust URL for backend

      socket.onopen = () => console.log("WebSocket connected");

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLogs((prev) => {
            const newLogs = [...prev, data].slice(-1000); // Keep last 1000 logs
            // Save to localStorage
            try {
              localStorage.setItem("auto_isp_logs", JSON.stringify(newLogs));
            } catch (e) {
              console.error("Failed to save logs to storage", e);
            }
            return newLogs;
          });
          // console.log("Received log:", data);
        } catch (err) {
          console.error("Error parsing log:", err);
        }
      };

      socket.onclose = () => {
        console.log("WebSocket disconnected, attempting to reconnect...");
        reconnectTimeout = setTimeout(connect, 3000);
      };

      socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        socket?.close();
      };
    };

    const timeoutId = setTimeout(connect, 500);

    return () => {
      if (socket) socket.close();
      clearTimeout(reconnectTimeout);
      clearTimeout(timeoutId);
    };
  }, []);

  return logs;
}
