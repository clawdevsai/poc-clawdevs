import { NextRequest, NextResponse } from "next/server";

import { resetTotalRuntime } from "@/lib/server/data";

type ResetTotalRequest = {
  confirmationText?: string;
};

const REQUIRED_CONFIRMATION_TEXT = "RESET TOTAL";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json().catch(() => ({}))) as ResetTotalRequest;
    const confirmationText = String(body.confirmationText ?? "").trim().toUpperCase();
    if (confirmationText !== REQUIRED_CONFIRMATION_TEXT) {
      return NextResponse.json(
        {
          error: "invalid_confirmation_text",
          requiredConfirmationText: REQUIRED_CONFIRMATION_TEXT
        },
        { status: 400 }
      );
    }

    const result = await resetTotalRuntime();
    return NextResponse.json(
      {
        status: "reset_completed",
        ...result
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "reset_total_error"
      },
      { status: 500 }
    );
  }
}

