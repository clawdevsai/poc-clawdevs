import { NextRequest, NextResponse } from "next/server";

import { enqueueDirectorCommand } from "@/lib/server/data";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as { directive?: string };
    const directive = (body.directive ?? "").trim();
    if (!directive) {
      return NextResponse.json({ error: "directive_required" }, { status: 400 });
    }
    const result = await enqueueDirectorCommand(directive);
    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "directive_error"
      },
      { status: 500 }
    );
  }
}
