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

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { useQuery } from "@tanstack/react-query";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { Send, Loader2, RefreshCw } from "lucide-react";
import { AppLayout } from "@/components/layout/app-layout";
import { customInstance } from "@/lib/axios-instance";
import { Skeleton } from "@/components/ui/skeleton";
import { AgentAvatar } from "@/components/agents/agent-avatar";
import { Badge } from "@/components/ui/badge";

interface Agent {
  slug: string;
  display_name: string;
  role: string;
  status?: string;
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

const SESSION_KEY_RE = /^agent:([a-z0-9_-]+):(.+)$/i;

type ParsedSessionKey = {
  agentSlug: string;
  sessionKey: string;
};

const fetchAgents = () =>
  customInstance<AgentsResponse>({ url: "/agents", method: "GET" });

const parseSessionKey = (rawValue: string | null): ParsedSessionKey | null => {
  if (!rawValue) return null;
  const value = rawValue.trim();
  const match = SESSION_KEY_RE.exec(value);
  if (!match) return null;
  return {
    agentSlug: match[1].toLowerCase(),
    sessionKey: value,
  };
};

const buildMainSessionKey = (agentSlug: string) => `agent:${agentSlug}:main`;

const fetchHistory = (slug: string, sessionKey?: string) =>
  customInstance<HistoryResponse>({
    url: `/chat/history/${slug}`,
    method: "GET",
    params: sessionKey ? { session_key: sessionKey } : undefined,
  });

export default function ChatPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  });

  const agents = agentsData?.items ?? [];
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedSessionKey, setSelectedSessionKey] = useState<string | null>(null);
  const [sessionParamError, setSessionParamError] = useState<string | null>(null);

  const rawSessionParam = searchParams.get("session");
  const parsedSessionParam = useMemo(
    () => parseSessionKey(rawSessionParam),
    [rawSessionParam]
  );

  const syncSessionParam = useCallback(
    (nextSessionKey: string, replace = true) => {
      const params = new URLSearchParams(searchParams.toString());
      if (params.get("session") === nextSessionKey) return;
      params.set("session", nextSessionKey);
      const nextUrl = `${pathname}?${params.toString()}`;
      if (replace) {
        router.replace(nextUrl);
      } else {
        router.push(nextUrl);
      }
    },
    [pathname, router, searchParams]
  );

  useEffect(() => {
    if (rawSessionParam && !parsedSessionParam) {
      setSessionParamError(
        "Session inválida. Use o formato agent:<slug>:<rest>."
      );
      return;
    }
    setSessionParamError(null);
  }, [rawSessionParam, parsedSessionParam]);

  useEffect(() => {
    if (parsedSessionParam) {
      const knownAgent =
        agents.length === 0 ||
        agents.some((agent) => agent.slug === parsedSessionParam.agentSlug);

      if (knownAgent) {
        setSelectedAgent(parsedSessionParam.agentSlug);
        setSelectedSessionKey(parsedSessionParam.sessionKey);
        return;
      }

      if (agents.length > 0) {
        const fallbackAgent = agents[0].slug;
        const fallbackSessionKey = buildMainSessionKey(fallbackAgent);
        setSelectedAgent(fallbackAgent);
        setSelectedSessionKey(fallbackSessionKey);
        setSessionParamError(
          "A sessão informada não corresponde a um agente disponível."
        );
        syncSessionParam(fallbackSessionKey, true);
      }
      return;
    }

    if (selectedAgent) {
      const fallbackSessionKey = buildMainSessionKey(selectedAgent);
      if (selectedSessionKey !== fallbackSessionKey) {
        setSelectedSessionKey(fallbackSessionKey);
      }
      syncSessionParam(fallbackSessionKey, true);
      return;
    }

    if (agents.length > 0) {
      const fallbackAgent = agents[0].slug;
      const fallbackSessionKey = buildMainSessionKey(fallbackAgent);
      setSelectedAgent(fallbackAgent);
      setSelectedSessionKey(fallbackSessionKey);
      syncSessionParam(fallbackSessionKey, true);
    }
  }, [
    agents,
    parsedSessionParam,
    selectedAgent,
    selectedSessionKey,
    syncSessionParam,
  ]);

  const {
    data: historyData,
    isFetching: historyLoading,
    refetch: refetchHistory,
  } = useQuery({
    queryKey: ["chat-history", selectedAgent, selectedSessionKey],
    queryFn: () =>
      fetchHistory(selectedAgent as string, selectedSessionKey ?? undefined),
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

  const selectedAgentData = useMemo(
    () => agents.find((a) => a.slug === selectedAgent) ?? null,
    [agents, selectedAgent]
  );
  const selectedAgentName = selectedAgentData?.display_name ?? selectedAgent ?? "";
  const selectedAgentRole = (selectedAgentData?.role ?? "Profissional").replace(/_/g, " ");
  const selectedAgentLabel = selectedAgentName
    ? `${selectedAgentRole} · ${selectedAgentName}`
    : "";
  const activeSessionKey =
    selectedSessionKey ??
    (selectedAgent ? buildMainSessionKey(selectedAgent) : null);

  function handleAgentChange(nextAgent: string) {
    const nextSessionKey = buildMainSessionKey(nextAgent);
    setSelectedAgent(nextAgent);
    setSelectedSessionKey(nextSessionKey);
    setSessionParamError(null);
    syncSessionParam(nextSessionKey, false);
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!sending && selectedAgent && input.trim()) {
        void sendMessage();
      }
    }
  }

  function getMessageAuthor(role: string) {
    if (role === "assistant") return selectedAgentLabel || "Assistente";
    if (role === "user") return "Você";
    if (role === "system") return "Sistema";
    return role;
  }

  async function sendMessage() {
    if (!selectedAgent || !input.trim()) return;
    const sessionKeyForRequest = activeSessionKey ?? buildMainSessionKey(selectedAgent);
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
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          agent_slug: selectedAgent,
          session_key: sessionKeyForRequest,
          message: userInput,
        }),
      });

      if (!res.ok || !res.body) {
        // Better error messages based on status code
        if (res.status === 503) {
          throw new Error("Agente offline - aguarde e tente novamente");
        } else if (res.status === 404) {
          throw new Error("Agente não encontrado");
        } else {
          throw new Error("Falha ao conectar com agente");
        }
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
      <div className="mx-auto flex h-full w-full max-w-6xl flex-col gap-4">
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 sm:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-center gap-3">
              <AgentAvatar
                slug={selectedAgentData?.slug ?? "agent"}
                displayName={selectedAgentName || "Profissional"}
                size="md"
                className={!selectedAgentData ? "opacity-60" : ""}
              />
              <div className="min-w-0">
                <p className="text-[11px] uppercase tracking-[0.14em] text-[hsl(var(--muted-foreground))]">
                  Profissional em foco
                </p>
                <p className="truncate text-sm font-semibold text-[hsl(var(--foreground))]">
                  {selectedAgentName || "Selecione um profissional"}
                </p>
                <p className="truncate text-xs text-[hsl(var(--muted-foreground))]">{selectedAgentRole}</p>
              </div>
              {selectedAgentData?.status ? (
                <Badge
                  variant={selectedAgentData.status === "online" ? "success" : "secondary"}
                  className="ml-1 hidden sm:inline-flex"
                >
                  {selectedAgentData.status}
                </Badge>
              ) : null}
            </div>

            <div className="grid w-full gap-2 sm:w-auto sm:grid-cols-[auto_minmax(220px,320px)_auto] sm:items-center">
              <label className="text-xs font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Agente
              </label>
              <select
                value={selectedAgent ?? ""}
                onChange={(e) => handleAgentChange(e.target.value)}
                className="h-10 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 text-sm text-[hsl(var(--foreground))] outline-none transition-colors focus:border-[hsl(var(--primary))]"
              >
                {agents.map((a) => (
                  <option key={a.slug} value={a.slug}>
                    {`${a.role.replace(/_/g, " ")} · ${a.display_name}`}
                  </option>
                ))}
              </select>
              <button
                onClick={() => selectedAgent && refetchHistory()}
                className="inline-flex h-10 items-center justify-center gap-1.5 rounded-xl border border-[hsl(var(--border))] px-3 text-xs font-medium text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/40 disabled:opacity-50"
                disabled={!selectedAgent || historyLoading}
              >
                <RefreshCw className={`h-3.5 w-3.5 ${historyLoading ? "animate-spin" : ""}`} />
                Histórico
              </button>
            </div>
          </div>
        </div>

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))]">
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,hsla(var(--primary),0.12),transparent_55%)] p-4 sm:p-6"
          >
            {agentsLoading || historyLoading ? (
              <div className="mx-auto w-full max-w-4xl space-y-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-2xl" />
                ))}
              </div>
            ) : messages.length === 0 ? (
              <div className="mx-auto flex h-full min-h-[280px] w-full max-w-4xl items-center justify-center">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Ainda não há mensagens para este profissional.
                </p>
              </div>
            ) : (
              <div className="mx-auto flex w-full max-w-4xl flex-col gap-3">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[88%] rounded-2xl border px-4 py-3 shadow-sm ${
                        msg.role === "user"
                          ? "border-[hsl(var(--primary)/0.4)] bg-[hsl(var(--primary)/0.14)]"
                          : "border-[hsl(var(--border))] bg-[hsl(var(--background))]/95"
                      }`}
                    >
                      <p className="mb-1 text-[10px] uppercase tracking-[0.14em] text-[hsl(var(--muted-foreground))]">
                        {getMessageAuthor(msg.role)}
                      </p>
                      <div className="prose prose-invert prose-sm max-w-none break-words">
                        {msg.content ? (
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        ) : sending && msg.role === "assistant" ? (
                          <div className="flex items-center gap-1.5">
                            <span className="flex gap-0.5">
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "0ms" }} />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "150ms" }} />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "300ms" }} />
                            </span>
                            <span className="text-sm text-[hsl(var(--muted-foreground))]">Stream em andamento...</span>
                          </div>
                        ) : (
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">Pensando...</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="border-t border-[hsl(var(--border))] bg-[hsl(var(--background))]/75 p-3 sm:p-4">
            <div className="mx-auto w-full max-w-4xl space-y-3">
              {sessionParamError && (
                <p className="text-sm text-[hsl(var(--destructive))]">{sessionParamError}</p>
              )}
              {error && <p className="text-sm text-[hsl(var(--destructive))]">{error}</p>}
              <div className="flex items-end gap-3">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  placeholder={`Mensagem para ${selectedAgentLabel || "o profissional selecionado"}`}
                  className="min-h-[56px] max-h-44 flex-1 resize-none rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-3 py-2.5 text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
                />
                <button
                  onClick={sendMessage}
                  disabled={sending || !selectedAgent || !input.trim()}
                  className="inline-flex h-11 items-center gap-2 rounded-xl bg-[hsl(var(--primary))] px-4 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
                >
                  {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  Enviar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
