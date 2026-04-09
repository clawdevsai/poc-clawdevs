/**
 * Smoke coverage for shell navigation behavior across desktop and mobile.
 * Keeps route accessibility checks deterministic via API stubs.
 */

const CORE_ROUTES = [
  "/",
  "/chat",
  "/sessions",
  "/tasks",
  "/monitoring",
  "/settings",
  "/agents",
  "/approvals",
] as const;

function sidebarLink(href: string) {
  return cy.get(`aside nav a[href="${href}"]`).first();
}

function assertNoHorizontalOverflow() {
  cy.document().then((doc) => {
    const root = doc.documentElement;
    expect(root.scrollWidth, "document horizontal overflow").to.be.lte(
      root.clientWidth + 1
    );
  });
}

function stubShellApis() {
  cy.intercept("GET", "/api/**", {
    statusCode: 200,
    body: {},
  }).as("apiFallback");

  cy.intercept("GET", "/api/activity-events*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  });

  cy.intercept("GET", "/api/metrics*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  });

  cy.intercept("GET", "/api/metrics/overview*", {
    statusCode: 200,
    body: {
      active_agents: 0,
      pending_approvals: 0,
      open_tasks: 0,
      tokens_24h: 0,
      tokens_consumed_total: 0,
      tokens_consumed_avg_per_task: 0,
      backlog_count: 0,
      tasks_in_progress: 0,
      tasks_completed: 0,
    },
  });

  cy.intercept("GET", "/api/metrics/cycle-time*", {
    statusCode: 200,
    body: {
      cycle_time_avg_seconds: 0,
      cycle_time_p95_seconds: 0,
      window_minutes: 30,
    },
  });

  cy.intercept("GET", "/api/metrics/throughput*", {
    statusCode: 200,
    body: {
      window_minutes: 30,
      group_by: "label",
      items: [],
    },
  });

  cy.intercept("GET", "/api/tasks*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  }).as("getTasks");

  cy.intercept("GET", "/api/repositories*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  });

  cy.intercept("GET", "/api/settings/runtime*", {
    statusCode: 200,
    body: {
      limits: {},
      flags: {},
      model_provider: "openai",
      model_name: "gpt-5.4-mini",
      agent_updates: [],
      thresholds: {},
    },
  });

  cy.intercept("GET", "/api/settings/info*", {
    statusCode: 200,
    body: {
      gateway_url: "http://localhost:3000",
      cluster_namespace: "default",
      container_version: "0.0.0-e2e",
    },
  });

  cy.intercept("GET", "/api/cluster/info*", {
    statusCode: 200,
    body: {
      cluster_name: "local",
      namespace: "default",
      version: "1.30.0",
    },
  });

  cy.intercept("GET", "/api/settings/gateway-health*", {
    statusCode: 200,
    body: { status: "healthy" },
  });

  cy.intercept("GET", "/api/api/health/failures*", {
    statusCode: 200,
    body: { total: 0, offset: 0, limit: 50, tasks: [] },
  });

  cy.intercept("GET", "/api/health/failures*", {
    statusCode: 200,
    body: { total: 0, offset: 0, limit: 50, tasks: [] },
  });

  cy.intercept("POST", "/api/chat/rag/turn", {
    statusCode: 200,
    body: { status: "ok", memory_id: "m1" },
  });

  cy.intercept("POST", "/api/chat/transcript/turn", {
    statusCode: 200,
    body: { status: "ok" },
  });

  cy.intercept("GET", "/api/memory/rag/search*", {
    statusCode: 200,
    body: { results_count: 0, results: [] },
  });

  cy.intercept("GET", "/api/chat/history/*", {
    fixture: "chat-history.json",
  }).as("getHistory");

  cy.intercept("GET", "/api/sessions*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  }).as("getSessions");

  cy.intercept("GET", "/api/agents*", {
    fixture: "agents.json",
  }).as("getAgents");

  cy.intercept("GET", "/api/approvals*", {
    statusCode: 200,
    body: { items: [], total: 0 },
  }).as("getApprovals");

  cy.intercept("GET", "/api/approvals/stats*", {
    statusCode: 200,
    body: { pending: 0, approved_today: 0, rejected_today: 0 },
  }).as("getApprovalStats");
}

describe("Shell navigation smoke", () => {
  beforeEach(() => {
    cy.login();
    stubShellApis();
  });

  it("covers desktop route transitions with active nav state", () => {
    cy.viewport(1440, 900);
    cy.visit("/");

    CORE_ROUTES.forEach((route) => {
      sidebarLink(route).click();
      cy.location("pathname").should("eq", route);
      sidebarLink(route).should("have.attr", "aria-current", "page");
      assertNoHorizontalOverflow();
    });
  });

  it("covers mobile sidebar open/close and route navigation", () => {
    cy.viewport(390, 844);
    cy.visit("/");

    cy.get("aside").should("have.class", "-translate-x-full");
    cy.get('[aria-label="Abrir menu"]').should("be.visible").click();
    cy.get("aside").should("have.class", "translate-x-0");

    sidebarLink("/sessions").should("be.visible").click();
    cy.location("pathname").should("eq", "/sessions");
    cy.get("aside").should("have.class", "-translate-x-full");

    cy.get('[aria-label="Abrir menu"]').click();
    cy.get("aside").should("have.class", "translate-x-0");
    cy.get('[aria-label="Fechar menu"]').click();
    cy.get("aside").should("have.class", "-translate-x-full");

    cy.get('[aria-label="Abrir menu"]').click();
    cy.get('[aria-label="Fechar navegação"]').click({ force: true });
    cy.get("aside").should("have.class", "-translate-x-full");

    assertNoHorizontalOverflow();
  });
});
