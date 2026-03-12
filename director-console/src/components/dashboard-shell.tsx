"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ActivityFeed } from "@/components/activity-feed";
import { AgentTimeline } from "@/components/agent-timeline";
import { ApprovalsPanel } from "@/components/approvals-panel";
import { DirectiveForm } from "@/components/directive-form";
import { StatCard } from "@/components/stat-card";
import type { ActivityFeed as ActivityFeedType, ApprovalsData, OverviewData, TimelineData } from "@/lib/server/types";

type DashboardData = {
  overview: OverviewData;
  activity: ActivityFeedType;
  timeline: TimelineData;
  approvals: ApprovalsData;
};

type MenuId = "overview" | "operations" | "activity" | "approvals" | "issues";

type DashboardShellProps = {
  initialData: DashboardData;
};

type WebhookSnapshot = {
  at: number;
  received: number;
  processed: number;
  duplicates: number;
  invalidSignature: number;
};

type WebhookLiveStats = {
  minutes: number;
  receivedPerMin: number;
  processedPerMin: number;
  duplicatesPerMin: number;
  invalidSignaturePerMin: number;
  duplicateDelta: number;
  invalidSignatureDelta: number;
  abruptDuplicateSpike: boolean;
  abruptInvalidSignatureSpike: boolean;
  spikeDeltaThreshold: number;
  spikePerMinuteThreshold: number;
};

type ResetTotalResponse = {
  status?: string;
  error?: string;
  requiredConfirmationText?: string;
  deletedRedisKeys?: number;
  deletedStreams?: number;
  github?: {
    attempted: number;
    closed: number;
    failed: number;
    note: string;
  };
};

const REQUIRED_RESET_CONFIRMATION = "RESET TOTAL";

const MENU_GROUPS: Array<{ title: string; items: Array<{ id: MenuId; label: string }> }> = [
  {
    title: "Painel",
    items: [
      { id: "overview", label: "Resumo executivo" },
      { id: "operations", label: "Operacao" }
    ]
  },
  {
    title: "Fluxo",
    items: [
      { id: "activity", label: "Timeline e feed" },
      { id: "approvals", label: "Aprovacoes" },
      { id: "issues", label: "Issues" }
    ]
  }
];

function formatPrs(open: number | null, total: number | null, note: string) {
  if (open === null || total === null) {
    return note;
  }
  return `${open} abertos / ${total} total`;
}

export function DashboardShell({ initialData }: DashboardShellProps) {
  const [data, setData] = useState(initialData);
  const webhookPreviousRef = useRef<WebhookSnapshot | null>(null);
  const [webhookLive, setWebhookLive] = useState<WebhookLiveStats | null>(null);
  const [activeMenu, setActiveMenu] = useState<MenuId>("overview");
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [refreshSeconds, setRefreshSeconds] = useState(60);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [isResettingWebhookMetrics, setIsResettingWebhookMetrics] = useState(false);
  const [webhookMetricsMessage, setWebhookMetricsMessage] = useState<string | null>(null);
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);
  const [resetConfirmationText, setResetConfirmationText] = useState("");
  const [isResettingTotal, setIsResettingTotal] = useState(false);
  const [resetTotalMessage, setResetTotalMessage] = useState<string | null>(null);

  const refreshDashboard = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch("/api/dashboard", { cache: "no-store" });
      const payload = (await response.json()) as DashboardData & { error?: string };
      if (!response.ok) {
        setRefreshError(payload.error ?? "dashboard_refresh_error");
        return;
      }
      setData(payload);
      setRefreshError(null);
    } catch (error) {
      setRefreshError(error instanceof Error ? error.message : "dashboard_refresh_error");
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (!autoRefreshEnabled) {
      return undefined;
    }
    const intervalMs = Math.max(60, refreshSeconds) * 1000;
    const timer = setInterval(() => {
      void refreshDashboard();
    }, intervalMs);
    return () => clearInterval(timer);
  }, [autoRefreshEnabled, refreshSeconds, refreshDashboard]);

  useEffect(() => {
    const currentAt = Date.parse(data.overview.generatedAt);
    const current: WebhookSnapshot = {
      at: Number.isFinite(currentAt) ? currentAt : Date.now(),
      received: data.overview.webhook.received,
      processed: data.overview.webhook.processed,
      duplicates: data.overview.webhook.duplicates,
      invalidSignature: data.overview.webhook.invalidSignature
    };

    const previous = webhookPreviousRef.current;
    if (!previous) {
      webhookPreviousRef.current = current;
      return;
    }

    const elapsedMinutes = Math.max((current.at - previous.at) / 60000, 0.0001);
    const receivedDelta = Math.max(0, current.received - previous.received);
    const processedDelta = Math.max(0, current.processed - previous.processed);
    const duplicateDelta = Math.max(0, current.duplicates - previous.duplicates);
    const invalidSignatureDelta = Math.max(0, current.invalidSignature - previous.invalidSignature);

    const duplicatesPerMin = duplicateDelta / elapsedMinutes;
    const invalidSignaturePerMin = invalidSignatureDelta / elapsedMinutes;
    const spikeDeltaThreshold = Math.max(1, data.overview.webhook.spikeDeltaThreshold);
    const spikePerMinuteThreshold = Math.max(0.1, data.overview.webhook.spikePerMinuteThreshold);

    setWebhookLive({
      minutes: elapsedMinutes,
      receivedPerMin: receivedDelta / elapsedMinutes,
      processedPerMin: processedDelta / elapsedMinutes,
      duplicatesPerMin,
      invalidSignaturePerMin,
      duplicateDelta,
      invalidSignatureDelta,
      abruptDuplicateSpike: duplicateDelta >= spikeDeltaThreshold || duplicatesPerMin >= spikePerMinuteThreshold,
      abruptInvalidSignatureSpike:
        invalidSignatureDelta >= spikeDeltaThreshold || invalidSignaturePerMin >= spikePerMinuteThreshold,
      spikeDeltaThreshold,
      spikePerMinuteThreshold
    });
    webhookPreviousRef.current = current;
  }, [data.overview.generatedAt, data.overview.webhook]);

  const headerDescription = useMemo(() => {
    if (activeMenu === "overview") {
      return "Visao consolidada do runtime com foco em capacidade e saude operacional.";
    }
    if (activeMenu === "operations") {
      return "Envio de diretivas e controle de aprovacoes humanas em um unico fluxo.";
    }
    if (activeMenu === "activity") {
      return "Timeline por agente e feed cronologico dos eventos de stream.";
    }
    if (activeMenu === "approvals") {
      return "Pendencias vindas da UI e do Telegram, com aprovacao direta.";
    }
    return "Estado persistido das issues com strikes e invalid output por item.";
  }, [activeMenu]);

  const resetWebhookMetrics = useCallback(async () => {
    const confirmed = window.confirm(
      "Tem certeza que deseja resetar as métricas do webhook? Esta ação zera os contadores operacionais."
    );
    if (!confirmed) {
      return;
    }
    setIsResettingWebhookMetrics(true);
    setWebhookMetricsMessage(null);
    try {
      const response = await fetch("/api/webhook-metrics", {
        method: "POST",
        cache: "no-store"
      });
      const payload = (await response.json()) as { error?: string; status?: string };
      if (!response.ok) {
        setWebhookMetricsMessage(`Falha no reset: ${payload.error ?? "webhook_metrics_reset_failed"}`);
        return;
      }
      setWebhookMetricsMessage("Métricas do webhook resetadas com sucesso.");
      await refreshDashboard();
    } catch (error) {
      setWebhookMetricsMessage(
        `Falha no reset: ${error instanceof Error ? error.message : "webhook_metrics_reset_error"}`
      );
    } finally {
      setIsResettingWebhookMetrics(false);
    }
  }, [refreshDashboard]);

  const openResetModal = useCallback(() => {
    setResetConfirmationText("");
    setResetTotalMessage(null);
    setIsResetModalOpen(true);
  }, []);

  const closeResetModal = useCallback(() => {
    if (isResettingTotal) {
      return;
    }
    setIsResetModalOpen(false);
    setResetConfirmationText("");
  }, [isResettingTotal]);

  const runTotalReset = useCallback(async () => {
    if (resetConfirmationText.trim().toUpperCase() !== REQUIRED_RESET_CONFIRMATION) {
      setResetTotalMessage(`Digite "${REQUIRED_RESET_CONFIRMATION}" para confirmar.`);
      return;
    }
    setIsResettingTotal(true);
    setResetTotalMessage(null);
    try {
      const response = await fetch("/api/reset-total", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ confirmationText: resetConfirmationText }),
        cache: "no-store"
      });
      const payload = (await response.json()) as ResetTotalResponse;
      if (!response.ok) {
        setResetTotalMessage(`Falha no reset: ${payload.error ?? "reset_total_failed"}`);
        return;
      }
      const githubSummary = payload.github
        ? `GitHub fechadas ${payload.github.closed}/${payload.github.attempted} (falhas: ${payload.github.failed})`
        : "GitHub sem retorno";
      setResetTotalMessage(
        `Reset concluido. Redis keys removidas: ${payload.deletedRedisKeys ?? 0}, streams removidas: ${
          payload.deletedStreams ?? 0
        }. ${githubSummary}.`
      );
      await refreshDashboard();
      setIsResetModalOpen(false);
      setResetConfirmationText("");
    } catch (error) {
      setResetTotalMessage(`Falha no reset: ${error instanceof Error ? error.message : "reset_total_error"}`);
    } finally {
      setIsResettingTotal(false);
    }
  }, [refreshDashboard, resetConfirmationText]);

  return (
    <main className="mx-auto min-h-screen max-w-[1400px] px-4 py-6 md:px-6">
      <div className="grid gap-6 lg:grid-cols-[250px_1fr]">
        <aside className="panel panel-strong rounded-3xl p-4 lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] lg:overflow-auto">
          <div className="border-b border-white/10 pb-4">
            <div className="text-xs uppercase tracking-[0.32em] text-cyan-300">Director Console</div>
            <h1 className="mt-3 text-2xl font-semibold text-white">ClawDevs</h1>
            <p className="mt-2 text-sm text-[var(--muted)]">Menu lateral com subareas do painel executivo.</p>
          </div>

          <nav className="mt-4 space-y-5">
            {MENU_GROUPS.map((group) => (
              <div key={group.title}>
                <div className="px-2 text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">{group.title}</div>
                <div className="mt-2 space-y-1">
                  {group.items.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setActiveMenu(item.id)}
                      className={`w-full rounded-xl px-3 py-2 text-left text-sm transition ${
                        activeMenu === item.id
                          ? "bg-cyan-300/20 text-cyan-100 border border-cyan-300/40"
                          : "text-[var(--muted)] hover:bg-white/5 hover:text-white"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        </aside>

        <section className="space-y-6">
          <header className="panel panel-strong rounded-3xl p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-3xl font-semibold text-white">Uma superficie limpa para operar o time de agentes</h2>
                <p className="mt-2 text-sm text-[var(--muted)]">{headerDescription}</p>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
                <span className="rounded-full border border-white/10 px-3 py-1">
                  Ultima leitura: <span className="text-white">{data.overview.generatedAt}</span>
                </span>
                <label className="rounded-full border border-white/10 px-3 py-1">
                  Refresh:
                  <select
                    value={refreshSeconds}
                    onChange={(event) => setRefreshSeconds(Number(event.target.value))}
                    className="ml-2 bg-transparent text-white outline-none"
                  >
                    <option value={60}>60s</option>
                    <option value={120}>120s</option>
                    <option value={180}>180s</option>
                    <option value={300}>300s</option>
                    <option value={600}>600s</option>
                  </select>
                </label>
                <label className="rounded-full border border-white/10 px-3 py-1">
                  <input
                    type="checkbox"
                    checked={autoRefreshEnabled}
                    onChange={(event) => setAutoRefreshEnabled(event.target.checked)}
                    className="mr-2 align-middle"
                  />
                  auto
                </label>
                <button
                  type="button"
                  onClick={() => void refreshDashboard()}
                  disabled={isRefreshing}
                  className="rounded-full border border-cyan-300/50 px-3 py-1 text-cyan-100 transition hover:bg-cyan-300/15 disabled:opacity-60"
                >
                  {isRefreshing ? "Atualizando..." : "Atualizar agora"}
                </button>
                <button
                  type="button"
                  onClick={openResetModal}
                  className="rounded-full border border-rose-300/55 px-3 py-1 text-rose-100 transition hover:bg-rose-300/15"
                >
                  Reset total
                </button>
              </div>
            </div>
            {refreshError ? <p className="mt-3 text-xs text-amber-300">Falha no refresh: {refreshError}</p> : null}
            {resetTotalMessage ? <p className="mt-3 text-xs text-[var(--muted)]">{resetTotalMessage}</p> : null}
          </header>

          {activeMenu === "overview" ? (
            <div className="space-y-6">
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Issues totais" value={data.overview.issuesTotal} />
                <StatCard label="Backlog" value={data.overview.byState.Backlog} tone="warning" />
                <StatCard label="Em desenvolvimento" value={data.overview.byState.InProgress} tone="accent" />
                <StatCard label="Done" value={data.overview.byState.Done} tone="success" />
              </section>

              <section className="panel panel-strong rounded-3xl p-6">
                <div className="mb-5 flex items-center justify-between gap-4">
                  <div>
                    <h3 className="text-xl font-semibold text-white">Radar operacional</h3>
                    <p className="mt-1 text-sm text-[var(--muted)]">Volumes por stream e saude do fluxo principal.</p>
                  </div>
                  <div className="rounded-full border border-white/10 px-3 py-1 text-xs text-[var(--muted)]">
                    Repo: <span className="text-white">{data.overview.githubRepo || "nao configurado"}</span>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <StatCard label="cmd:strategy" value={data.overview.streams.strategy} />
                  <StatCard label="draft.2.issue" value={data.overview.streams.draftIssue} />
                  <StatCard label="pr:review" value={data.overview.streams.prReview} />
                  <StatCard label="code:ready" value={data.overview.streams.codeReady} />
                  <StatCard label="event:devops" value={data.overview.streams.devopsEvents} />
                </div>
                <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-[var(--muted)]">
                  PRs GitHub:{" "}
                  <span className="text-white">
                    {formatPrs(data.overview.prs.open, data.overview.prs.total, data.overview.prs.note)}
                  </span>
                </div>
              </section>

              <section className="panel panel-strong rounded-3xl p-6">
                <div className="mb-5">
                  <h3 className="text-xl font-semibold text-white">Webhook GitHub</h3>
                  <p className="mt-1 text-sm text-[var(--muted)]">
                    Saude de ingestao de eventos pull_request em tempo real.
                  </p>
                </div>
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <StatCard label="Recebidos" value={data.overview.webhook.received} />
                  <StatCard label="Processados" value={data.overview.webhook.processed} tone="success" />
                  <StatCard label="Duplicados" value={data.overview.webhook.duplicates} tone="warning" />
                  <StatCard
                    label="Rejeitados (assinatura)"
                    value={data.overview.webhook.invalidSignature}
                    tone="warning"
                  />
                </div>
                <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <StatCard label="Invalid JSON" value={data.overview.webhook.invalidJson} tone="warning" />
                  <StatCard label="Ignored Events" value={data.overview.webhook.ignoredEvents} />
                  <StatCard label="PRs em review" value={data.overview.webhook.inReview} tone="accent" />
                  <StatCard label="PRs mergeadas" value={data.overview.webhook.merged} tone="success" />
                </div>
                <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4 text-xs text-[var(--muted)]">
                  last_delivery_id: <span className="text-white">{data.overview.webhook.lastDeliveryId || "n/a"}</span>{" "}
                  | last_event: <span className="text-white">{data.overview.webhook.lastEvent || "n/a"}</span> |
                  last_result: <span className="text-white">{data.overview.webhook.lastResult || "n/a"}</span>
                </div>
              </section>

              <section className="panel panel-strong rounded-3xl p-6">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-xl font-semibold text-white">Webhook Live</h3>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                      Taxa por minuto desde a ultima leitura e alerta de subida abrupta.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {webhookLive?.abruptDuplicateSpike || webhookLive?.abruptInvalidSignatureSpike ? (
                      <span className="rounded-full border border-rose-300/70 bg-rose-400/20 px-3 py-1 text-xs font-semibold text-rose-200">
                        ALERTA DE ANOMALIA
                      </span>
                    ) : (
                      <span className="rounded-full border border-emerald-300/40 bg-emerald-400/15 px-3 py-1 text-xs font-semibold text-emerald-200">
                        Estavel
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => void resetWebhookMetrics()}
                      disabled={isResettingWebhookMetrics}
                      className="rounded-full border border-amber-300/50 px-3 py-1 text-xs font-semibold text-amber-100 transition hover:bg-amber-300/15 disabled:opacity-60"
                    >
                      {isResettingWebhookMetrics ? "Resetando..." : "Reset métricas"}
                    </button>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <StatCard
                    label="Recebidos/min"
                    value={webhookLive ? webhookLive.receivedPerMin.toFixed(2) : "0.00"}
                    tone="accent"
                  />
                  <StatCard
                    label="Processados/min"
                    value={webhookLive ? webhookLive.processedPerMin.toFixed(2) : "0.00"}
                    tone="success"
                  />
                  <StatCard
                    label="Duplicados/min"
                    value={webhookLive ? webhookLive.duplicatesPerMin.toFixed(2) : "0.00"}
                    tone={webhookLive?.abruptDuplicateSpike ? "warning" : "default"}
                  />
                  <StatCard
                    label="Invalid sig/min"
                    value={webhookLive ? webhookLive.invalidSignaturePerMin.toFixed(2) : "0.00"}
                    tone={webhookLive?.abruptInvalidSignatureSpike ? "warning" : "default"}
                  />
                </div>
                <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4 text-xs text-[var(--muted)]">
                  janela_min: <span className="text-white">{webhookLive ? webhookLive.minutes.toFixed(2) : "n/a"}</span>{" "}
                  | delta_duplicates: <span className="text-white">{webhookLive?.duplicateDelta ?? 0}</span> |
                  delta_invalid_signature:{" "}
                  <span className="text-white">{webhookLive?.invalidSignatureDelta ?? 0}</span> | threshold_delta:{" "}
                  <span className="text-white">{webhookLive?.spikeDeltaThreshold ?? data.overview.webhook.spikeDeltaThreshold}</span>{" "}
                  | threshold_per_min:{" "}
                  <span className="text-white">
                    {webhookLive?.spikePerMinuteThreshold ?? data.overview.webhook.spikePerMinuteThreshold}
                  </span>
                </div>
                {webhookMetricsMessage ? (
                  <p className="mt-3 text-xs text-[var(--muted)]">{webhookMetricsMessage}</p>
                ) : null}
              </section>
            </div>
          ) : null}

          {activeMenu === "operations" ? (
            <div className="grid gap-6 xl:grid-cols-2">
              <DirectiveForm onCompleted={() => void refreshDashboard()} />
              <ApprovalsPanel pendingItems={data.approvals.pending} onChanged={() => void refreshDashboard()} />
            </div>
          ) : null}

          {activeMenu === "activity" ? (
            <div className="space-y-6">
              <AgentTimeline buckets={data.timeline.buckets} />
              <ActivityFeed items={data.activity.items.slice(0, 40)} />
            </div>
          ) : null}

          {activeMenu === "approvals" ? (
            <ApprovalsPanel pendingItems={data.approvals.pending} onChanged={() => void refreshDashboard()} />
          ) : null}

          {activeMenu === "issues" ? (
            <div className="panel panel-strong rounded-3xl p-6">
              <div className="mb-5">
                <h3 className="text-xl font-semibold text-white">Issues acompanhadas</h3>
                <p className="mt-1 text-sm text-[var(--muted)]">Estados persistidos no Redis pelo runtime.</p>
              </div>
              <div className="overflow-hidden rounded-2xl border border-white/10">
                <table className="min-w-full divide-y divide-white/10 text-sm">
                  <thead className="bg-white/5 text-left text-[var(--muted)]">
                    <tr>
                      <th className="px-4 py-3 font-medium">Issue</th>
                      <th className="px-4 py-3 font-medium">Estado</th>
                      <th className="px-4 py-3 font-medium">Strikes</th>
                      <th className="px-4 py-3 font-medium">Invalid output</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {data.overview.issues.length === 0 ? (
                      <tr>
                        <td className="px-4 py-5 text-[var(--muted)]" colSpan={4}>
                          Nenhuma issue registrada ainda.
                        </td>
                      </tr>
                    ) : (
                      data.overview.issues.map((issue) => (
                        <tr key={issue.issueId}>
                          <td className="px-4 py-3 text-white">{issue.issueId}</td>
                          <td className="px-4 py-3 text-[var(--muted)]">{issue.state}</td>
                          <td className="px-4 py-3 text-[var(--muted)]">{issue.strikes}</td>
                          <td className="px-4 py-3 text-[var(--muted)]">{issue.invalidOutputCount}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </section>
      </div>
      {isResetModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="panel panel-strong w-full max-w-xl rounded-3xl border border-rose-300/35 p-6">
            <h3 className="text-xl font-semibold text-white">Confirmar reset total</h3>
            <p className="mt-2 text-sm text-[var(--muted)]">
              Esta acao apaga eventos, historico e issues no Redis, remove streams operacionais e fecha issues abertas
              no GitHub.
            </p>
            <p className="mt-2 text-sm text-rose-200">
              Para continuar, digite <span className="font-semibold">{REQUIRED_RESET_CONFIRMATION}</span>.
            </p>
            <input
              type="text"
              value={resetConfirmationText}
              onChange={(event) => setResetConfirmationText(event.target.value)}
              placeholder={REQUIRED_RESET_CONFIRMATION}
              className="mt-4 w-full rounded-xl border border-white/20 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-rose-300/60"
            />
            <div className="mt-5 flex justify-end gap-3">
              <button
                type="button"
                onClick={closeResetModal}
                disabled={isResettingTotal}
                className="rounded-xl border border-white/20 px-4 py-2 text-sm text-[var(--muted)] transition hover:bg-white/10 disabled:opacity-60"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => void runTotalReset()}
                disabled={isResettingTotal}
                className="rounded-xl border border-rose-300/60 px-4 py-2 text-sm font-semibold text-rose-100 transition hover:bg-rose-300/15 disabled:opacity-60"
              >
                {isResettingTotal ? "Resetando..." : "Confirmar reset"}
              </button>
            </div>
            {resetTotalMessage ? <p className="mt-3 text-xs text-[var(--muted)]">{resetTotalMessage}</p> : null}
          </div>
        </div>
      ) : null}
    </main>
  );
}
