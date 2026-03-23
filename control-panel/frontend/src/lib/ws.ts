type WSChannel = "dashboard" | "agents" | "approvals" | "cluster" | "crons";

type WSListener = (data: unknown) => void;

class WSManager {
  private sockets = new Map<string, WebSocket>();
  private listeners = new Map<string, Set<WSListener>>();
  private baseUrl: string;

  constructor() {
    this.baseUrl =
      process.env.NEXT_PUBLIC_API_URL?.replace("http", "ws") ??
      "ws://localhost:8000";
  }

  connect(channel: WSChannel) {
    if (this.sockets.has(channel)) return;
    const url = `${this.baseUrl}/ws/${channel}`;
    const ws = new WebSocket(url);

    // Send token in the first frame instead of the URL query param.
    // Tokens in URLs are visible in server logs, proxy logs, and browser history.
    ws.onopen = () => {
      const token = localStorage.getItem("panel_token") ?? "";
      ws.send(JSON.stringify({ type: "auth", token }));
    };

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data as string);
        this.listeners.get(channel)?.forEach((fn) => fn(data));
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      this.sockets.delete(channel);
      // Only reconnect if there are still active listeners
      if ((this.listeners.get(channel)?.size ?? 0) > 0) {
        setTimeout(() => this.connect(channel), 3000);
      }
    };

    ws.onerror = () => ws.close();

    this.sockets.set(channel, ws);
  }

  subscribe(channel: WSChannel, fn: WSListener): () => void {
    if (!this.listeners.has(channel)) {
      this.listeners.set(channel, new Set());
    }
    this.listeners.get(channel)!.add(fn);
    this.connect(channel);
    return () => this.listeners.get(channel)?.delete(fn);
  }
}

// Singleton — only instantiated on client
export const wsManager =
  typeof window !== "undefined" ? new WSManager() : null;
