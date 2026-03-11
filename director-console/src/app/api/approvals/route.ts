import { NextRequest, NextResponse } from "next/server";

import { approvePending, createApproval, denyPending, loadApprovals } from "@/lib/server/data";

type ApprovalRequest =
  | { action: "create"; directive: string }
  | { action: "approve"; key: string }
  | { action: "deny"; key: string };

export async function GET() {
  try {
    const data = await loadApprovals();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "approvals_error"
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as ApprovalRequest;
    if (body.action === "create") {
      const directive = (body.directive ?? "").trim();
      if (!directive) {
        return NextResponse.json({ error: "directive_required" }, { status: 400 });
      }
      const result = await createApproval(directive);
      return NextResponse.json(result, { status: 201 });
    }
    if (body.action === "approve") {
      const key = (body.key ?? "").trim();
      if (!key) {
        return NextResponse.json({ error: "key_required" }, { status: 400 });
      }
      const result = await approvePending(key);
      if (!result.ok) {
        return NextResponse.json({ error: result.error }, { status: 400 });
      }
      return NextResponse.json(result, { status: 200 });
    }
    if (body.action === "deny") {
      const key = (body.key ?? "").trim();
      if (!key) {
        return NextResponse.json({ error: "key_required" }, { status: 400 });
      }
      const result = await denyPending(key);
      return NextResponse.json(result, { status: 200 });
    }
    return NextResponse.json({ error: "invalid_action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "approvals_action_error"
      },
      { status: 500 }
    );
  }
}
