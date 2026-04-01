/* 
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { getWsBaseUrl } from "./api-base-url";

type WSChannel = "dashboard" | "agents" | "approvals" | "cluster" | "crons" | "context-mode-metrics";

type WSListener = (data: unknown) => void;

class WSManager {
  private sockets = new Map<string, WebSocket>();
  private listeners = new Map<string, Set<WSListener>>();
  private baseUrl: string;

  constructor() {
    this.baseUrl = getWsBaseUrl();
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
