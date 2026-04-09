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
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Loader2,
  RefreshCw,
  Paperclip,
  Mic,
  Plus,
  Download,
  Copy,
  Check,
  ChevronsUpDown,
  FileText,
} from "lucide-react";
import { AppLayout } from "@/components/layout/app-layout";
import { customInstance } from "@/lib/axios-instance";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { AgentAvatar } from "@/components/agents/agent-avatar";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface Agent {
  slug: string;
  display_name: string;
  role: string;
  status?: string;
  runtime_status?: string;
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
  created_at?: string | null;
}

function extractTimestampFromId(id: string): Date | null {
  const parts = id.split("-");
  if (parts.length >= 2) {
    const ts = parseInt(parts[parts.length - 1], 10);
    if (!isNaN(ts) && ts > 1000000000) {
      return new Date(ts);
    }
  }
  return null;
}

function formatMessageTimestamp(date: Date | null): string {
  if (!date || isNaN(date.getTime())) return "";
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

interface AgentsResponse {
  items: Agent[];
  total: number;
}

interface ChatSessionRow {
  id: string;
  openclaw_session_id: string;
  openclaw_session_key?: string | null;
  session_kind: string;
  session_label: string;
  status: string;
  created_at: string;
  last_active_at?: string | null;
}

interface SessionsListResponse {
  items: ChatSessionRow[];
  total: number;
}

interface HistoryResponse {
  agent_slug: string;
  messages: ChatMessage[];
}

interface RagSearchResult {
  id: string;
  title: string;
  body?: string | null;
  similarity_score: number;
  retrieval_mode?: string;
}

interface RagSearchResponse {
  query: string;
  agent_slug?: string | null;
  session_key?: string | null;
  results_count: number;
  results: RagSearchResult[];
}

const SESSION_KEY_RE = /^agent:([a-z0-9_-]+):(.+)$/i;

type ParsedSessionKey = {
  agentSlug: string;
  sessionKey: string;
};

const fetchAgents = () =>
  customInstance<AgentsResponse>({ url: "/agents", method: "GET" });

const fetchSessionsForAgent = (slug: string) =>
  customInstance<SessionsListResponse>({
    url: "/sessions",
    method: "GET",
    params: { agent_slug: slug, page: 1, page_size: 100 },
  });

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

function getAgentOptionLabel(agent: Agent): string {
  return `${agent.role.replace(/_/g, " ")} · ${agent.display_name}`;
}

function buildRagContext(results: RagSearchResult[]): string | null {
  const compactItems = results
    .filter((item) => (item.body ?? "").trim().length > 0)
    .slice(0, 4)
    .map((item, index) => {
      const clippedBody = (item.body ?? "").trim().replace(/\s+/g, " ").slice(0, 320);
      return `${index + 1}. ${item.title} (score ${item.similarity_score.toFixed(3)}, ${item.retrieval_mode ?? "semantic"})\n${clippedBody}`;
    });

  if (compactItems.length === 0) return null;
  return compactItems.join("\n\n");
}

const FILE_EXT_RE = /\.(?:md|txt|json|yaml|yml|csv)$/i;

function basenameFromPathHint(text: string): string | null {
  const re = /([\w./\\-]+\.(?:md|txt|json|yaml|yml|csv))/gi;
  let last: string | null = null;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    last = m[1];
  }
  if (!last) return null;
  const base = last.split(/[/\\]/).pop();
  if (!base || !FILE_EXT_RE.test(base)) return null;
  return base;
}

function slugifyMarkdownHeading(raw: string): string {
  const cleaned = raw.replace(/^#+\s*/, "").trim();
  const slug = cleaned
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 80);
  return slug || "document";
}

/** First line index that starts a markdown heading (agent-pasted docs usually start with # / ##). */
function findFirstHeadingLineIndex(lines: string[]): number {
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*#{1,6}\s+\S/.test(lines[i])) return i;
  }
  return -1;
}

/**
 * Splits trailing conversational CTA (e.g. "Deseja que eu...") from document-like body text.
 */
function splitOutroFromBody(body: string): { doc: string; outro: string | null } {
  const ctaPatterns = [
    /\n\n(?=Deseja\b)/gi,
    /\n\n(?=Responda com\b)/gi,
    /\n\n(?=Would you like\b)/gi,
    /\n\n(?=Do you want\b)/gi,
    /\n\n(?=Gostaria que\b)/gi,
  ];
  let bestIdx = -1;
  for (const re of ctaPatterns) {
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(body)) !== null) {
      if (m.index > bestIdx) bestIdx = m.index;
    }
  }
  if (bestIdx >= 0) {
    return {
      doc: body.slice(0, bestIdx).trim(),
      outro: body.slice(bestIdx).replace(/^\s*\n+/, "").trim(),
    };
  }

  const paras = body.split(/\n\n+/);
  if (paras.length >= 2) {
    const last = paras[paras.length - 1]!;
    const prev = paras.slice(0, -1).join("\n\n");
    if (
      last.length < 450 &&
      !/^\s*#/.test(last) &&
      (/[?¿]/.test(last) ||
        /\*\*(?:SIM|AJUSTAR|YES|NO)\*\*/i.test(last) ||
        /(?:^|[\s.!?])(?:😉|👍)/u.test(last))
    ) {
      return { doc: prev.trim(), outro: last.trim() };
    }
  }
  return { doc: body, outro: null };
}

interface AssistantMessageSplit {
  intro: string | null;
  document: string | null;
  outro: string | null;
}

/**
 * Separates conversational text from embedded file-style markdown (headings + body + optional CTA outro).
 */
function splitAssistantMessageForDisplay(content: string): AssistantMessageSplit {
  const trimmed = content.trim();
  if (!trimmed) {
    return { intro: null, document: null, outro: null };
  }

  const lines = trimmed.split("\n");
  const docStartLine = findFirstHeadingLineIndex(lines);
  if (docStartLine < 0) {
    return { intro: trimmed, document: null, outro: null };
  }

  const intro =
    docStartLine > 0 ? lines.slice(0, docStartLine).join("\n").trim() || null : null;
  const body = lines.slice(docStartLine).join("\n");
  const { doc, outro } = splitOutroFromBody(body);

  return {
    intro,
    document: doc || null,
    outro: outro || null,
  };
}

function assistantDownloadPayload(content: string): string {
  const split = splitAssistantMessageForDisplay(content);
  if (split.document && (split.intro != null || split.outro != null)) {
    return split.document;
  }
  return content;
}

function AssistantMessageBody({
  content,
  pathHintExtra,
}: {
  content: string;
  pathHintExtra?: string;
}) {
  const split = splitAssistantMessageForDisplay(content);
  const pathHint =
    basenameFromPathHint([pathHintExtra, content].filter(Boolean).join("\n")) ??
    basenameFromPathHint(content);
  const docLabel = pathHint ?? "Conteúdo do documento";

  if (!split.document) {
    return <ReactMarkdown>{content}</ReactMarkdown>;
  }

  return (
    <>
      {split.intro ? (
        <div className="mb-3 [&_p]:my-2 [&_p:first-child]:mt-0">
          <ReactMarkdown>{split.intro}</ReactMarkdown>
        </div>
      ) : null}
      <div className="my-1 overflow-hidden rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/20 not-prose">
        <div className="flex items-center gap-2 border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30 px-3 py-2">
          <FileText className="h-4 w-4 shrink-0 text-[hsl(var(--muted-foreground))]" aria-hidden />
          <span className="text-xs font-medium text-[hsl(var(--muted-foreground))]">{docLabel}</span>
        </div>
        <div className="prose prose-invert prose-sm max-w-none min-w-0 px-3 py-3 break-words [overflow-wrap:anywhere] [&_pre]:max-w-full [&_pre]:overflow-x-auto">
          <ReactMarkdown>{split.document}</ReactMarkdown>
        </div>
      </div>
      {split.outro ? (
        <div className="mt-3 [&_p]:my-2 [&_p:first-child]:mt-0">
          <ReactMarkdown>{split.outro}</ReactMarkdown>
        </div>
      ) : null}
    </>
  );
}

function suggestFilename(
  assistantContent: string,
  previousUserContent: string | undefined,
  agentSlug: string,
  messageId: string
): string {
  const fromUser = previousUserContent ? basenameFromPathHint(previousUserContent) : null;
  if (fromUser) return fromUser;

  const trimmed = assistantContent.trim();
  const firstLine = trimmed.split("\n")[0]?.trim() ?? "";
  if (firstLine.startsWith("#")) {
    return `${slugifyMarkdownHeading(firstLine)}.md`;
  }

  const short = messageId.replace(/^assistant-/, "").slice(0, 8);
  const date = new Date().toISOString().slice(0, 10);
  return `documento-${agentSlug}-${date}-${short}.md`;
}

function downloadTextFile(content: string, filename: string, mimeType = "text/markdown; charset=utf-8") {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function buildChatExportMarkdown(
  messages: ChatMessage[],
  userLabel: string,
  assistantLabel: string
): string {
  const lines: string[] = [];
  lines.push("# Chat export\n");
  lines.push(`Generated: ${new Date().toISOString()}\n\n---\n\n`);
  for (const msg of messages) {
    const header =
      msg.role === "user" ? userLabel : msg.role === "assistant" ? assistantLabel : String(msg.role);
    lines.push(`## ${header}\n\n`);
    lines.push(`${(msg.content ?? "").trim() || "(empty)"}\n\n`);
  }
  return lines.join("");
}

function ChatPageContent() {
  const queryClient = useQueryClient();
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
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const pendingSessionUrlSyncRef = useRef<string | null>(null);

  const { data: sessionsData } = useQuery({
    queryKey: ["sessions", selectedAgent, "chat-picker"],
    queryFn: () => fetchSessionsForAgent(selectedAgent as string),
    enabled: !!selectedAgent,
  });

  const rawSessionParam = searchParams.get("session");
  const parsedSessionParam = useMemo(
    () => parseSessionKey(rawSessionParam),
    [rawSessionParam]
  );

  const syncSessionParam = useCallback(
    (nextSessionKey: string, replace = true) => {
      const params = new URLSearchParams(searchParams.toString());
      if (params.get("session") === nextSessionKey) return;
      pendingSessionUrlSyncRef.current = nextSessionKey;
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
    if (!pendingSessionUrlSyncRef.current) return;
    if (rawSessionParam === pendingSessionUrlSyncRef.current) {
      pendingSessionUrlSyncRef.current = null;
    }
  }, [rawSessionParam]);

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
      const hasLocalSelection = !!selectedAgent && !!selectedSessionKey;
      const localMatchesUrl =
        hasLocalSelection &&
        selectedSessionKey === parsedSessionParam.sessionKey &&
        selectedAgent.toLowerCase() === parsedSessionParam.agentSlug;

      // While router navigation updates the URL, keep the user's latest local choice.
      const localChangePendingUrlSync =
        hasLocalSelection &&
        !!pendingSessionUrlSyncRef.current &&
        selectedSessionKey === pendingSessionUrlSyncRef.current &&
        rawSessionParam !== pendingSessionUrlSyncRef.current;

      if (localMatchesUrl || localChangePendingUrlSync) {
        return;
      }

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
      if (selectedSessionKey == null) {
        setSelectedSessionKey(fallbackSessionKey);
        syncSessionParam(fallbackSessionKey, true);
        return;
      }
      const slug = selectedAgent.toLowerCase();
      const belongs = selectedSessionKey.toLowerCase().startsWith(`agent:${slug}:`);
      if (!belongs) {
        setSelectedSessionKey(fallbackSessionKey);
        syncSessionParam(fallbackSessionKey, true);
        return;
      }
      if (!rawSessionParam) {
        syncSessionParam(selectedSessionKey, true);
      }
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
    rawSessionParam,
    selectedAgent,
    selectedSessionKey,
    syncSessionParam,
  ]);

  const historyQueryEnabled =
    !!selectedAgent &&
    (!rawSessionParam || selectedSessionKey != null);

  const awaitingSessionFromUrl =
    !!rawSessionParam &&
    !!parsedSessionParam &&
    !!selectedAgent &&
    selectedSessionKey == null;

  const {
    data: historyData,
    isFetching: historyLoading,
    isFetched: historyFetched,
    refetch: refetchHistory,
  } = useQuery({
    queryKey: ["chat-history", selectedAgent, selectedSessionKey],
    queryFn: () =>
      fetchHistory(selectedAgent as string, selectedSessionKey ?? undefined),
    enabled: historyQueryEnabled,
    // Prevent stale data after page reload
    staleTime: 0,
    gcTime: 5 * 60 * 1000,
  });

  const showHistorySkeleton =
    agentsLoading ||
    awaitingSessionFromUrl ||
    (historyQueryEnabled && historyLoading && !historyFetched);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [streamSeconds, setStreamSeconds] = useState(0);
  const [lastStreamSeconds, setLastStreamSeconds] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [agentDropdownOpen, setAgentDropdownOpen] = useState(false);
  const [agentQuery, setAgentQuery] = useState("");
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const agentDropdownRef = useRef<HTMLDivElement | null>(null);
  const streamIntervalRef = useRef<number | null>(null);
  const streamSecondsRef = useRef(0);

  useEffect(() => {
    streamSecondsRef.current = streamSeconds;
  }, [streamSeconds]);

  /** Evita mostrar conversa do agente anterior enquanto o histórico novo carrega. */
  useEffect(() => {
    if (!historyQueryEnabled) return;
    setMessages([]);
  }, [selectedAgent, selectedSessionKey, historyQueryEnabled]);

  useEffect(() => {
    if (!historyQueryEnabled) return;
    if (historyData === undefined) return;
    setMessages(
      (historyData.messages ?? []).map((m, idx) => ({
        ...m,
        id: m.id ?? `history-${idx}`,
      }))
    );
  }, [historyData, historyQueryEnabled]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (!sending) {
      setStreamSeconds(0);
      if (streamIntervalRef.current !== null) {
        window.clearInterval(streamIntervalRef.current);
        streamIntervalRef.current = null;
      }
      return;
    }

    setStreamSeconds(0);
    setLastStreamSeconds(null);
    streamIntervalRef.current = window.setInterval(() => {
      setStreamSeconds((current) => current + 1);
    }, 1000);

    return () => {
      if (streamIntervalRef.current !== null) {
        window.clearInterval(streamIntervalRef.current);
        streamIntervalRef.current = null;
      }
    };
  }, [sending]);

  useEffect(() => {
    if (!agentDropdownOpen) return;

    function onPointerDown(event: MouseEvent) {
      const target = event.target as Node | null;
      if (!target) return;
      if (agentDropdownRef.current?.contains(target)) return;
      setAgentDropdownOpen(false);
      setAgentQuery("");
    }

    document.addEventListener("mousedown", onPointerDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
    };
  }, [agentDropdownOpen]);

  const selectedAgentData = useMemo(
    () => agents.find((a) => a.slug === selectedAgent) ?? null,
    [agents, selectedAgent]
  );

  const filteredAgents = useMemo(() => {
    const query = agentQuery.trim().toLowerCase();
    if (!query) return agents;
    return agents.filter((agent) => {
      const label = getAgentOptionLabel(agent).toLowerCase();
      const slug = agent.slug.toLowerCase();
      const role = agent.role.toLowerCase().replace(/_/g, " ");
      return label.includes(query) || slug.includes(query) || role.includes(query);
    });
  }, [agents, agentQuery]);

  useEffect(() => {
    if (!agentDropdownOpen) return;
    setActiveAgentIndex((current) => {
      if (filteredAgents.length === 0) return 0;
      if (current >= filteredAgents.length) return 0;
      return current;
    });
  }, [filteredAgents, agentDropdownOpen]);

  const selectedAgentName = selectedAgentData?.display_name ?? selectedAgent ?? "";
  const selectedAgentRole = (selectedAgentData?.role ?? "Profissional").replace(/_/g, " ");
  const selectedAgentLabel = selectedAgentName
    ? `${selectedAgentRole} · ${selectedAgentName}`
    : "";

  const sessionSelectOptions = useMemo(() => {
    if (!selectedAgent) return [];
    const mainKey = buildMainSessionKey(selectedAgent);
    const rows = sessionsData?.items ?? [];
    const withKeys = rows.filter((r) => (r.openclaw_session_key ?? "").length > 0);
    if (withKeys.length === 0) {
      return [{ key: mainKey, label: "Principal" }];
    }
    const sorted = [...withKeys].sort((a, b) => {
      if (a.session_kind === "main" && b.session_kind !== "main") return -1;
      if (a.session_kind !== "main" && b.session_kind === "main") return 1;
      const ta = new Date(a.last_active_at ?? a.created_at).getTime();
      const tb = new Date(b.last_active_at ?? b.created_at).getTime();
      return tb - ta;
    });
    return sorted.map((s) => ({
      key: s.openclaw_session_key as string,
      label: s.session_label || s.openclaw_session_key || "",
    }));
  }, [sessionsData, selectedAgent]);

  const sessionSelectOptionsResolved = useMemo(() => {
    if (!selectedSessionKey || !selectedAgent) return sessionSelectOptions;
    if (sessionSelectOptions.some((o) => o.key === selectedSessionKey)) {
      return sessionSelectOptions;
    }
    return [
      ...sessionSelectOptions,
      { key: selectedSessionKey, label: selectedSessionKey },
    ];
  }, [sessionSelectOptions, selectedSessionKey, selectedAgent]);

  const activeSessionKey =
    selectedSessionKey ??
    (selectedAgent ? buildMainSessionKey(selectedAgent) : null);

  const agentInputValue = agentDropdownOpen
    ? agentQuery
    : selectedAgentData
    ? getAgentOptionLabel(selectedAgentData)
    : "";

  function handleAgentChange(nextAgent: string) {
    const nextSessionKey = buildMainSessionKey(nextAgent);
    setSelectedAgent(nextAgent);
    setSelectedSessionKey(nextSessionKey);
    setSessionParamError(null);
    setAgentDropdownOpen(false);
    setAgentQuery("");
    syncSessionParam(nextSessionKey, false);
  }

  function handleSessionKeyChange(nextKey: string) {
    setSessionParamError(null);
    setSelectedSessionKey(nextKey);
    syncSessionParam(nextKey, false);
  }

  function handleAgentInputKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (!agentDropdownOpen && (event.key === "Enter" || event.key === "ArrowDown")) {
      event.preventDefault();
      setAgentDropdownOpen(true);
      return;
    }

    if (!agentDropdownOpen) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveAgentIndex((current) =>
        filteredAgents.length === 0 ? 0 : Math.min(current + 1, filteredAgents.length - 1)
      );
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveAgentIndex((current) => Math.max(current - 1, 0));
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const target = filteredAgents[activeAgentIndex];
      if (target) {
        handleAgentChange(target.slug);
      }
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      setAgentDropdownOpen(false);
      setAgentQuery("");
    }
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

  function getMessageHeader(msg: ChatMessage): string {
    const author = getMessageAuthor(msg.role);
    const ts = extractTimestampFromId(msg.id);
    const formatted = formatMessageTimestamp(ts);
    if (!formatted) return author;
    return `${author} ${formatted}`;
  }

  async function persistRagTurn(
    agentSlug: string,
    sessionKey: string,
    turnId: string,
    userMessage: string,
    assistantMessage: string
  ) {
    try {
      await customInstance<{ status: string; memory_id: string }>({
        url: "/chat/rag/turn",
        method: "POST",
        data: {
          agent_slug: agentSlug,
          session_key: sessionKey,
          turn_id: turnId,
          user_message: userMessage,
          assistant_message: assistantMessage,
        },
      });
    } catch (persistError) {
      console.warn("Failed to persist chat turn into RAG", persistError);
    }
  }

  async function persistChatTranscriptTurn(
    agentSlug: string,
    sessionKey: string,
    turnId: string,
    userMessage: string,
    assistantMessage: string
  ) {
    try {
      await customInstance<{ status: string }>({
        url: "/chat/transcript/turn",
        method: "POST",
        data: {
          agent_slug: agentSlug,
          session_key: sessionKey,
          turn_id: turnId,
          user_message: userMessage,
          assistant_message: assistantMessage,
        },
      });
    } catch (persistError) {
      console.warn("Failed to persist chat transcript", persistError);
    }
  }

  async function loadRagContext(
    agentSlug: string,
    sessionKey: string,
    userInput: string
  ): Promise<string | null> {
    try {
      const ragResponse = await customInstance<RagSearchResponse>({
        url: "/memory/rag/search",
        method: "GET",
        params: {
          query: userInput,
          top_k: 5,
          agent_slug: agentSlug,
          session_key: sessionKey,
        },
      });
      return buildRagContext(ragResponse.results ?? []);
    } catch (ragError) {
      console.warn("Failed to load RAG context", ragError);
      return null;
    }
  }

  async function sendMessage() {
    if (!selectedAgent || !input.trim()) return;

    const sessionKeyForRequest = activeSessionKey ?? buildMainSessionKey(selectedAgent);
    const turnId = `turn-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

    setSending(true);
    setError(null);
    setLastStreamSeconds(null);

    const userInput = input.trim();
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userInput,
    };
    const assistantMsgId = `assistant-${Date.now()}`;
    setMessages((prev) => [...prev, userMsg, { id: assistantMsgId, role: "assistant", content: "" }]);
    setInput("");

    try {
      const ragContext = await loadRagContext(selectedAgent, sessionKeyForRequest, userInput);

      const token = typeof window !== "undefined" ? localStorage.getItem("panel_token") : null;
      const res = await fetch("/openclaw/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          agent_slug: selectedAgent,
          session_key: sessionKeyForRequest,
          message: userInput,
          rag_context: ragContext,
        }),
      });

      if (!res.ok || !res.body) {
        const errorBody = await res.text();
        let detailMessage = "Falha ao conectar com OpenClaw";
        if (errorBody) {
          try {
            const parsedError = JSON.parse(errorBody) as { detail?: string };
            detailMessage = parsedError.detail || detailMessage;
          } catch {
            detailMessage = errorBody;
          }
        }
        throw new Error(detailMessage);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let assistantContent = "";

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
            const parsed = JSON.parse(data) as {
              choices?: Array<{
                delta?: {
                  content?: string;
                  tool_calls?: Array<{ function?: { name?: string } }>;
                };
              }>;
            };

            const deltaText =
              parsed?.choices?.[0]?.delta?.content ??
              parsed?.choices?.[0]?.delta?.tool_calls
                ?.map((toolCall) => toolCall?.function?.name)
                .filter(Boolean)
                .join(", ");

            if (deltaText) {
              assistantContent += deltaText;
              setMessages((prev) =>
                prev.map((message) =>
                  message.id === assistantMsgId
                    ? { ...message, content: (message.content ?? "") + deltaText }
                    : message
                )
              );
            }
          } catch {
            setError("Falha ao interpretar resposta do gateway.");
          }
        }
      }

      const assistantForPersist = (assistantContent || "[sem conteúdo textual]").trim();

      setMessages((prev) => {
        const next = prev.map((m) =>
          m.id === assistantMsgId
            ? { ...m, content: assistantForPersist || m.content }
            : m
        );
        queryClient.setQueryData<HistoryResponse>(
          ["chat-history", selectedAgent, sessionKeyForRequest],
          {
            agent_slug: selectedAgent,
            messages: next.map((m) => ({
              id: m.id,
              role: m.role,
              content: m.content,
              ...(m.tool_calls != null ? { tool_calls: m.tool_calls } : {}),
            })),
          }
        );
        return next;
      });

      await Promise.all([
        persistRagTurn(
          selectedAgent,
          sessionKeyForRequest,
          turnId,
          userInput,
          assistantForPersist
        ),
        persistChatTranscriptTurn(
          selectedAgent,
          sessionKeyForRequest,
          turnId,
          userInput,
          assistantForPersist
        ),
      ]);

      refetchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar mensagem");
      setMessages((prev) => prev.filter((message) => message.id !== assistantMsgId));
    } finally {
      setLastStreamSeconds(streamSecondsRef.current);
      setSending(false);
    }
  }

  return (
    <AppLayout>
      <div className="mx-auto flex h-[calc(100dvh-6rem)] min-h-0 w-full max-w-6xl flex-col gap-4 overflow-hidden">
        <div className="shrink-0 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 sm:p-5">
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
              {selectedAgentData?.runtime_status ? (
                <Badge
                  variant={["online", "working"].includes(selectedAgentData.runtime_status) ? "success" : "secondary"}
                  className="ml-1 hidden sm:inline-flex"
                >
                  {selectedAgentData.runtime_status === "working" ? "online" : selectedAgentData.runtime_status}
                </Badge>
              ) : null}
            </div>

            <div className="flex w-full flex-col gap-3 lg:w-auto lg:max-w-[min(100%,560px)]">
              <div className="grid w-full gap-2 sm:grid-cols-[auto_minmax(250px,340px)_auto] sm:items-center">
              <label className="text-xs font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Agente
              </label>
              <div className="relative" ref={agentDropdownRef}>
                <input
                  value={agentInputValue}
                  onFocus={() => {
                    setAgentDropdownOpen(true);
                    setAgentQuery("");
                  }}
                  onChange={(event) => {
                    setAgentDropdownOpen(true);
                    setAgentQuery(event.target.value);
                    setActiveAgentIndex(0);
                  }}
                  onKeyDown={handleAgentInputKeyDown}
                  placeholder="Digite para buscar agente"
                  className="h-10 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 pr-9 text-sm text-[hsl(var(--foreground))] outline-none transition-colors focus:border-[hsl(var(--primary))]"
                />
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      onClick={() => {
                        setAgentDropdownOpen((open) => {
                          const next = !open;
                          if (next) {
                            setAgentQuery("");
                          }
                          return next;
                        });
                      }}
                      className="absolute inset-y-0 right-0 inline-flex w-9 items-center justify-center text-[hsl(var(--muted-foreground))]"
                      aria-label="Abrir seletor de agente"
                    >
                      <ChevronsUpDown className="h-4 w-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Selecionar agente</TooltipContent>
                </Tooltip>

                {agentDropdownOpen && (
                  <div className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-1 shadow-2xl">
                    {filteredAgents.length === 0 ? (
                      <p className="px-3 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                        Nenhum agente encontrado.
                      </p>
                    ) : (
                      filteredAgents.map((agent, index) => {
                        const isActive = index === activeAgentIndex;
                        const isSelected = agent.slug === selectedAgent;
                        return (
                          <button
                            key={agent.slug}
                            type="button"
                            onMouseEnter={() => setActiveAgentIndex(index)}
                            onMouseDown={(event) => {
                              event.preventDefault();
                              handleAgentChange(agent.slug);
                            }}
                            className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-xs transition-colors ${
                              isActive
                                ? "bg-[hsl(var(--primary)/0.16)] text-[hsl(var(--foreground))]"
                                : "text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/40"
                            }`}
                          >
                            <span className="truncate">{getAgentOptionLabel(agent)}</span>
                            {isSelected ? (
                              <span className="ml-2 rounded bg-[hsl(var(--primary)/0.18)] px-1.5 py-0.5 text-[10px] uppercase tracking-wide">
                                atual
                              </span>
                            ) : null}
                          </button>
                        );
                      })
                    )}
                  </div>
                )}
              </div>
              <button
                onClick={() => selectedAgent && refetchHistory()}
                className="inline-flex h-10 items-center justify-center gap-1.5 rounded-xl border border-[hsl(var(--border))] px-3 text-xs font-medium text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/40 disabled:opacity-50"
                disabled={!selectedAgent || !historyQueryEnabled || historyLoading}
              >
                <RefreshCw className={`h-3.5 w-3.5 ${historyLoading ? "animate-spin" : ""}`} />
                Histórico
              </button>
              </div>

              <div className="grid w-full gap-2 sm:grid-cols-[auto_minmax(250px,340px)_auto] sm:items-center">
                <label className="text-xs font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                  Sessão
                </label>
                <select
                  value={activeSessionKey ?? ""}
                  onChange={(event) => handleSessionKeyChange(event.target.value)}
                  disabled={!selectedAgent}
                  className="h-10 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 text-sm text-[hsl(var(--foreground))] outline-none transition-colors focus:border-[hsl(var(--primary))] disabled:opacity-50"
                  aria-label="Sessão OpenClaw"
                >
                  {sessionSelectOptionsResolved.map((opt) => (
                    <option key={opt.key} value={opt.key}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <span className="hidden sm:block" aria-hidden />
              </div>
            </div>
          </div>
        </div>

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))]">
          <div
            ref={scrollRef}
            className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden bg-[radial-gradient(circle_at_top,hsla(var(--primary),0.12),transparent_55%)] p-4 sm:p-6"
          >
            {showHistorySkeleton ? (
              <div className="mx-auto w-full max-w-4xl space-y-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-2xl" />
                ))}
              </div>
            ) : messages.length === 0 ? (
              <div className="mx-auto flex h-full min-h-[280px] w-full max-w-4xl items-center justify-center">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Nenhuma mensagem nesta conversa.
                </p>
              </div>
            ) : (
              <div className="mx-auto flex w-full min-w-0 max-w-4xl flex-col gap-3">
                {messages.map((msg, index) => (
                  <div
                    key={msg.id}
                    className={`flex min-w-0 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`min-w-0 max-w-[88%] rounded-2xl border px-4 py-3 shadow-sm ${
                        msg.role === "user"
                          ? "border-[hsl(var(--primary)/0.4)] bg-[hsl(var(--primary)/0.14)]"
                          : "border-[hsl(var(--border))] bg-[hsl(var(--background))]/95"
                      }`}
                    >
                      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                        <p className="text-[10px] uppercase tracking-[0.14em] text-[hsl(var(--muted-foreground))]">
                          {getMessageHeader(msg)}
                        </p>
                        {msg.content.trim() &&
                        (msg.role === "user" || msg.role === "assistant") ? (
                          <div className="flex shrink-0 items-center gap-0.5">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <button
                                  type="button"
                                  onClick={async () => {
                                    try {
                                      await navigator.clipboard.writeText(msg.content);
                                      setCopiedMessageId(msg.id);
                                      window.setTimeout(() => {
                                        setCopiedMessageId((cur) => (cur === msg.id ? null : cur));
                                      }, 2000);
                                    } catch {
                                      console.warn("Clipboard write failed");
                                    }
                                  }}
                                  className="inline-flex h-7 w-7 items-center justify-center rounded-lg text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/50 hover:text-[hsl(var(--foreground))]"
                                  aria-label={
                                    copiedMessageId === msg.id
                                      ? "Copiado"
                                      : "Copiar texto da mensagem"
                                  }
                                >
                                  {copiedMessageId === msg.id ? (
                                    <Check className="h-3.5 w-3.5 text-[hsl(var(--primary))]" />
                                  ) : (
                                    <Copy className="h-3.5 w-3.5" />
                                  )}
                                </button>
                              </TooltipTrigger>
                              <TooltipContent>
                                {copiedMessageId === msg.id ? "Copiado" : "Copiar"}
                              </TooltipContent>
                            </Tooltip>
                            {msg.role === "assistant" ? (
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const prevUser =
                                        index > 0 && messages[index - 1]?.role === "user"
                                          ? messages[index - 1].content
                                          : undefined;
                                      const slug = selectedAgent ?? "agent";
                                      const payload = assistantDownloadPayload(msg.content);
                                      downloadTextFile(
                                        payload,
                                        suggestFilename(payload, prevUser, slug, msg.id)
                                      );
                                    }}
                                    className="inline-flex h-7 w-7 items-center justify-center rounded-lg text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/50 hover:text-[hsl(var(--foreground))]"
                                    aria-label="Baixar documento"
                                  >
                                    <Download className="h-3.5 w-3.5" />
                                  </button>
                                </TooltipTrigger>
                                <TooltipContent>Baixar documento</TooltipContent>
                              </Tooltip>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                      <div className="prose prose-invert prose-sm max-w-none min-w-0 break-words [overflow-wrap:anywhere] [&_pre]:max-w-full [&_pre]:overflow-x-auto">
                        {msg.content ? (
                          msg.role === "assistant" ? (
                            <AssistantMessageBody
                              content={msg.content}
                              pathHintExtra={
                                index > 0 && messages[index - 1]?.role === "user"
                                  ? messages[index - 1].content
                                  : undefined
                              }
                            />
                          ) : (
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                          )
                        ) : sending && msg.role === "assistant" ? (
                          <div className="flex items-center gap-1.5">
                            <span className="flex gap-0.5">
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "0ms" }} />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "150ms" }} />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "300ms" }} />
                            </span>
                            <span className="text-sm text-[hsl(var(--muted-foreground))]">
                              Stream em andamento... {streamSeconds}s
                            </span>
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

          <div className="shrink-0 border-t border-[hsl(var(--border))] bg-[hsl(var(--background))]/75 p-3 sm:p-4">
            <div className="mx-auto w-full max-w-4xl space-y-3">
              {sessionParamError && (
                <p className="text-sm text-[hsl(var(--destructive))]">{sessionParamError}</p>
              )}
              {error && <p className="text-sm text-[hsl(var(--destructive))]">{error}</p>}
              {!sending && lastStreamSeconds !== null && (
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  Tempo da última resposta: {lastStreamSeconds}s
                </p>
              )}

              <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--background))]/80 p-2.5">
                <textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  placeholder="Mensagem para Memo (Enter para enviar)"
                  className="min-h-[62px] max-h-44 w-full resize-none rounded-xl border border-transparent bg-transparent px-2.5 py-2 text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:border-[hsl(var(--primary)/0.3)] focus:outline-none"
                />

                <div className="mt-1 flex items-center justify-between px-1 pb-0.5">
                  <div className="flex items-center gap-1 text-[hsl(var(--muted-foreground))]">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-[hsl(var(--muted))]/50"
                          aria-label="Anexar arquivo"
                        >
                          <Paperclip className="h-4 w-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Anexar arquivo</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-[hsl(var(--muted))]/50"
                          aria-label="Usar microfone"
                        >
                          <Mic className="h-4 w-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Usar microfone</TooltipContent>
                    </Tooltip>
                  </div>

                  <div className="flex items-center gap-1 text-[hsl(var(--muted-foreground))]">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-[hsl(var(--muted))]/50"
                          aria-label="Adicionar ação"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Adicionar ação</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          type="button"
                          onClick={() => {
                            if (!selectedAgent || messages.length === 0) return;
                            const stamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
                            const filename = `chat-${selectedAgent}-${stamp}.md`;
                            downloadTextFile(
                              buildChatExportMarkdown(
                                messages,
                                "Você",
                                selectedAgentLabel || "Assistente"
                              ),
                              filename
                            );
                          }}
                          disabled={!selectedAgent || messages.length === 0}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-[hsl(var(--muted))]/50 disabled:cursor-not-allowed disabled:opacity-40"
                          aria-label="Exportar conversa"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Exportar conversa (Markdown)</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          onClick={sendMessage}
                          disabled={sending || !selectedAgent || !input.trim()}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
                          aria-label="Enviar mensagem"
                        >
                          {sending ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Send className="h-4 w-4" />
                          )}
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Enviar mensagem (Enter)</TooltipContent>
                    </Tooltip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="h-full" />
        </AppLayout>
      }
    >
      <ChatPageContent />
    </Suspense>
  );
}
