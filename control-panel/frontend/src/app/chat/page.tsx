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

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { Send, Loader2 } from "lucide-react";
import { AppLayout } from "@/components/layout/app-layout";
import { customInstance } from "@/lib/axios-instance";
import { Skeleton } from "@/components/ui/skeleton";

interface Agent {
  slug: string;
  display_name: string;
}

interface ToolCall {
  id?: string;
  name?: string;
  tool?: string;
  input?: unknown;
  result?: unknown;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | string;
  content: string;
  tool_calls?: ToolCall[] | null;
}

interface AgentsResponse {
  items: Agent[];
  total: number;
}

interface HistoryResponse {
  agent_slug: string;
  messages: ChatMessage[];
}

const fetchAgents = () =>
  customInstance<AgentsResponse>({ url: "/agents", method: "GET" });

const fetchHistory = (slug: string) =>
  customInstance<HistoryResponse>({
    url: `/chat/history/${slug}`,
    method: "GET",
  });

export default function ChatPage() {
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  });

  const agents = agentsData?.items ?? [];
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedAgent && agents.length > 0) {
      setSelectedAgent(agents[0].slug);
    }
  }, [agents, selectedAgent]);

  const {
    data: historyData,
    isFetching: historyLoading,
    refetch: refetchHistory,
  } = useQuery({
    queryKey: ["chat-history", selectedAgent],
    queryFn: () => fetchHistory(selectedAgent as string),
    enabled: !!selectedAgent,
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (historyData?.messages) {
      setMessages(
        historyData.messages.map((m, idx) => ({
          ...m,
          id: m.id ?? `history-${idx}`,
        }))
      );
    }
  }, [historyData]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const selectedAgentName = useMemo(() => {
    const match = agents.find((a) => a.slug === selectedAgent);
    return match?.display_name ?? selectedAgent ?? "";
  }, [agents, selectedAgent]);

  async function sendMessage() {
    if (!selectedAgent || !input.trim()) return;
    setSending(true);
    setError(null);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input.trim(),
    };
    const assistantMsgId = `assistant-${Date.now()}`;
    setMessages((prev) => [...prev, userMsg, { id: assistantMsgId, role: "assistant", content: "" }]);
    const userInput = input.trim();
    setInput("");

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("panel_token") : null;
      const res = await fetch("/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ agent_slug: selectedAgent, message: userInput }),
      });

      if (!res.ok || !res.body) {
        throw new Error("Falha ao iniciar streaming");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const chunk of parts) {
          const line = chunk.trim();
          if (!line.startsWith("data:")) continue;
          const data = line.replace("data:", "").trim();
          if (!data || data === "[DONE]") {
            continue;
          }
          try {
            const parsed = JSON.parse(data);
            const delta =
              parsed?.choices?.[0]?.delta?.content ??
              parsed?.choices?.[0]?.delta?.tool_calls?.map((t: any) => t?.function?.name).join(", ");
            if (delta) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, content: (m.content ?? "") + delta } : m
                )
              );
            }
          } catch {
            setError("Falha ao interpretar resposta do gateway.");
          }
        }
      }

      // refresh persisted history when finished
      refetchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar mensagem");
      // rollback assistant stub
      setMessages((prev) => prev.filter((m) => m.id !== assistantMsgId));
    } finally {
      setSending(false);
    }
  }

  return (
    <AppLayout>
      <div className="flex flex-col gap-4 h-full">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <label className="text-sm text-[hsl(var(--muted-foreground))]">Agente</label>
            <select
              value={selectedAgent ?? ""}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-sm"
            >
              {agents.map((a) => (
                <option key={a.slug} value={a.slug}>
                  {a.display_name}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => selectedAgent && refetchHistory()}
            className="text-xs px-2 py-1 rounded border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/30"
            disabled={!selectedAgent || historyLoading}
          >
            Atualizar histórico
          </button>
          {historyLoading && <span className="text-xs text-[hsl(var(--muted-foreground))]">Carregando…</span>}
        </div>

        <div
          ref={scrollRef}
          className="flex-1 min-h-[300px] max-h-[60vh] overflow-y-auto rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-4"
        >
          {agentsLoading || historyLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : messages.length === 0 ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Nenhuma mensagem ainda.</p>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`rounded-lg px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-[hsl(var(--primary)/0.1)] border border-[hsl(var(--primary)/0.3)]"
                    : "bg-[hsl(var(--muted))]/20 border border-[hsl(var(--border))]"
                }`}
              >
                <p className="text-xs uppercase tracking-wide text-[hsl(var(--muted-foreground))] mb-1">
                  {msg.role === "assistant" ? selectedAgentName : msg.role}
                </p>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{msg.content || ""}</ReactMarkdown>
                </div>
              </div>
            ))
          )}
        </div>

        {error && <p className="text-sm text-[hsl(var(--destructive))]">{error}</p>}

        <div className="flex items-center gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Mensagem para ${selectedAgentName || "o agente"}`}
            className="flex-1 min-h-[60px] rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
          />
          <button
            onClick={sendMessage}
            disabled={sending || !selectedAgent || !input.trim()}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Enviar
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
