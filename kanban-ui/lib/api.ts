// API types and client for the Kanban backend

export interface Issue {
    id: string;
    title: string;
    summary: string;
    state: string;
    priority: string;
    created_by: string;
    created_at: string;
}

export interface BoardData {
    columns: string[];
    board: Record<string, Issue[]>;
    total: number;
}

export interface KanbanEvent {
    issue_id: string;
    from_state: string;
    to_state: string;
    agent: string;
    ts: string;
    action?: string;
    title?: string;
}

// Resolve API URL: in-browser use relative proxy, in-cluster use env var
function getApiUrl(): string {
    // Client-side: use relative /api path (proxied by next.config)
    if (typeof window !== "undefined") {
        return "/kanban-api";
    }
    // Server-side: use the env var pointing to the cluster service
    return (
        process.env.NEXT_PUBLIC_API_URL ||
        "http://kanban-api-service.ai-agents.svc.cluster.local:5001"
    );
}

export async function fetchBoard(): Promise<BoardData> {
    const res = await fetch(`${getApiUrl()}/api/board`, {
        cache: "no-store",
    });
    if (!res.ok) throw new Error(`Failed to fetch board: ${res.status}`);
    return res.json();
}

export async function fetchIssue(id: string): Promise<Issue> {
    const res = await fetch(`${getApiUrl()}/api/issues/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch issue: ${res.status}`);
    return res.json();
}

export async function createIssue(data: {
    title: string;
    summary?: string;
    priority?: string;
}): Promise<{ ok: boolean; id: string; state: string }> {
    const res = await fetch(`${getApiUrl()}/api/issues`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create issue: ${res.status}`);
    return res.json();
}

export async function updateIssueState(
    id: string,
    state: string,
    agent: string = "director"
): Promise<{ ok: boolean; from: string; to: string }> {
    const res = await fetch(`${getApiUrl()}/api/issues/${id}/state`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, agent }),
    });
    if (!res.ok) throw new Error(`Failed to update issue: ${res.status}`);
    return res.json();
}

export async function syncExistingIssues(): Promise<{
    ok: boolean;
    synced: number;
}> {
    const res = await fetch(`${getApiUrl()}/api/sync`, {
        method: "POST",
    });
    if (!res.ok) throw new Error(`Failed to sync: ${res.status}`);
    return res.json();
}

export function getSSEUrl(): string {
    return `${getApiUrl()}/api/events`;
}
