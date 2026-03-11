import { NextResponse } from "next/server";

import { loadActivityFeed, loadApprovals, loadOverview, loadTimeline } from "@/lib/server/data";

export async function GET() {
  try {
    const [overview, activity, timeline, approvals] = await Promise.all([
      loadOverview(),
      loadActivityFeed(),
      loadTimeline(),
      loadApprovals()
    ]);
    return NextResponse.json({ overview, activity, timeline, approvals });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "dashboard_error"
      },
      { status: 500 }
    );
  }
}
