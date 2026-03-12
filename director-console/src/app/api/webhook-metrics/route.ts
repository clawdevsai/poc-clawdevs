import { NextResponse } from "next/server";

import { env } from "@/lib/server/env";

export async function POST() {
  if (!env.githubWebhookAdminToken) {
    return NextResponse.json({ error: "webhook_admin_token_missing" }, { status: 500 });
  }

  try {
    const target = `${env.webhookInternalUrl.replace(/\/$/, "")}/metrics/reset`;
    const response = await fetch(target, {
      method: "POST",
      headers: {
        "X-Webhook-Admin-Token": env.githubWebhookAdminToken
      },
      cache: "no-store"
    });
    const payload = (await response.json().catch(() => ({}))) as { error?: string; status?: string };
    if (!response.ok) {
      return NextResponse.json(
        { error: payload.error ?? "webhook_metrics_reset_failed", status: payload.status ?? "" },
        { status: 502 }
      );
    }
    return NextResponse.json({ status: payload.status ?? "metrics_reset" }, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "webhook_metrics_reset_error" },
      { status: 500 }
    );
  }
}

