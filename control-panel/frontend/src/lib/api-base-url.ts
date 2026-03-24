const PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL;

function normalizeWsUrl(url: string): string {
  if (url.startsWith("https://")) return url.replace("https://", "wss://");
  if (url.startsWith("http://")) return url.replace("http://", "ws://");
  return url;
}

export function getApiBaseUrl(): string {
  // Prefer explicit public API URL when provided for external deployments.
  if (PUBLIC_API_URL) return PUBLIC_API_URL;

  // In browser, route through same-origin Next.js rewrite (/api/*).
  if (typeof window !== "undefined") return "/api";

  // Server-side fallback for local development.
  return process.env.API_INTERNAL_URL ?? "http://localhost:8000";
}

export function getWsBaseUrl(): string {
  if (PUBLIC_API_URL) return normalizeWsUrl(PUBLIC_API_URL);

  // In browser, route WS via same-origin Next.js rewrite (/api/ws/*).
  if (typeof window !== "undefined") {
    return `${window.location.origin.replace(/^http/, "ws")}/api`;
  }

  return "ws://localhost:8000";
}
