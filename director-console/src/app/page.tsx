import { DashboardShell } from "@/components/dashboard-shell";
import { loadActivityFeed, loadApprovals, loadOverview, loadTimeline } from "@/lib/server/data";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [overview, activity, timeline, approvals] = await Promise.all([
    loadOverview(),
    loadActivityFeed(),
    loadTimeline(),
    loadApprovals()
  ]);

  return <DashboardShell initialData={{ overview, activity, timeline, approvals }} />;
}
