import { NextResponse } from "next/server";

import { loadActivityFeed, loadTimeline } from "@/lib/server/data";

export async function GET() {
  try {
    const [activity, timeline] = await Promise.all([loadActivityFeed(), loadTimeline()]);
    return NextResponse.json({ activity, timeline });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "activity_error"
      },
      { status: 500 }
    );
  }
}
