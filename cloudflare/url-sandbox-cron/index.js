/**
 * Cron Worker: dispara o Job url-sandbox no cluster (via trigger service).
 * Secrets: TRIGGER_ENDPOINT (URL base, ex. https://url-sandbox-trigger.seudominio.com),
 *          URL_SANDBOX_TARGET (URL a buscar), TRIGGER_SECRET (Bearer token para POST /trigger).
 */
export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(triggerUrlSandbox(env));
  },

  async fetch(request, env, ctx) {
    return new Response("url-sandbox-cron Worker. Trigger via Cron; GET /health or see README.\n", {
      headers: { "Content-Type": "text/plain" },
    });
  },
};

async function triggerUrlSandbox(env) {
  const endpoint = env.TRIGGER_ENDPOINT;
  const url = env.URL_SANDBOX_TARGET;
  const secret = env.TRIGGER_SECRET || "";

  if (!endpoint || !url) {
    console.error("Missing TRIGGER_ENDPOINT or URL_SANDBOX_TARGET");
    return;
  }

  const triggerUrl = endpoint.replace(/\/$/, "") + "/trigger";
  const headers = {
    "Content-Type": "application/json",
    ...(secret ? { Authorization: `Bearer ${secret}` } : {}),
  };

  try {
    const res = await fetch(triggerUrl, {
      method: "POST",
      headers,
      body: JSON.stringify({ url }),
    });
    const text = await res.text();
    if (!res.ok) {
      console.error(`Trigger failed ${res.status}: ${text}`);
      return;
    }
    console.log(`Trigger OK: ${text}`);
  } catch (e) {
    console.error("Trigger request failed:", e.message);
  }
}
