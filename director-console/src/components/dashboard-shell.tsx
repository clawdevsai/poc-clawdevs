"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

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
  const [activeMenu, setActiveMenu] = useState<MenuId>("overview");
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [refreshSeconds, setRefreshSeconds] = useState(60);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);

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
              </div>
            </div>
            {refreshError ? <p className="mt-3 text-xs text-amber-300">Falha no refresh: {refreshError}</p> : null}
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
    </main>
  );
}
