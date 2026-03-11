import { NextResponse } from "next/server";

import { loadOverview } from "@/lib/server/data";

export async function GET() {
  try {
    const data = await loadOverview();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "overview_error"
      },
      { status: 500 }
    );
  }
}
