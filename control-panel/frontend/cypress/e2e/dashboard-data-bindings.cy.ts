/**
 * Focused smoke coverage to verify dashboard/monitoring metric bindings.
 * The test guarantees visual values map to intercepted telemetry payloads.
 */

const API = "/api"

const metricsSeriesBody = {
  items: [
    { metric_type: "active_sessions", value: 11, period_start: "2026-04-09T09:00:00.000Z" },
    { metric_type: "active_sessions", value: 13, period_start: "2026-04-09T09:05:00.000Z" },
    { metric_type: "active_sessions", value: 15, period_start: "2026-04-09T09:10:00.000Z" },
  ],
  total: 3,
}

const sessionsBody = {
  items: [
    {
      id: "sess-main",
      agent_slug: "ops-agent",
      session_label: "Ops Main",
      session_kind: "main",
      status: "active",
      message_count: 24,
      token_count: 4096,
      last_active_at: "2026-04-09T09:15:00.000Z",
      created_at: "2026-04-09T08:50:00.000Z",
    },
  ],
  total: 3,
}

const agentsBody = {
  items: [
    {
      id: "agent-ops",
      slug: "ops-agent",
      display_name: "Ops Agent",
      role: "operations",
      status: "online",
      runtime_status: "online",
      model: "gpt-5.4-mini",
      last_heartbeat_at: "2026-04-09T09:10:00.000Z",
    },
    {
      id: "agent-qa",
      slug: "qa-agent",
      display_name: "QA Agent",
      role: "quality",
      status: "idle",
      runtime_status: "idle",
      model: "gpt-5.4-mini",
      last_heartbeat_at: "2026-04-09T09:09:00.000Z",
    },
  ],
  total: 2,
}

function stubMetricBindingsApis() {
  cy.intercept("GET", /\/api\/metrics(\?.*)?$/, {
    statusCode: 200,
    body: metricsSeriesBody,
  }).as("getMetricsSeries")

  cy.intercept("GET", `${API}/metrics/overview*`, {
    fixture: "metrics-overview.json",
  }).as("getOverviewMetrics")

  cy.intercept("GET", `${API}/metrics/cycle-time*`, {
    fixture: "metrics-cycle-time.json",
  }).as("getCycleTime")

  cy.intercept("GET", `${API}/metrics/throughput*`, {
    fixture: "metrics-throughput.json",
  }).as("getThroughput")

  cy.intercept("GET", `${API}/agents*`, { statusCode: 200, body: agentsBody }).as("getAgents")
  cy.intercept("GET", `${API}/sessions*`, { statusCode: 200, body: sessionsBody }).as("getSessions")
  cy.intercept("GET", `${API}/tasks*`, { statusCode: 200, body: { items: [], total: 11 } }).as(
    "getTasks"
  )
  cy.intercept("GET", `${API}/approvals*`, { statusCode: 200, body: { items: [], total: 2 } }).as(
    "getApprovals"
  )
  cy.intercept("GET", `${API}/activity-events*`, {
    statusCode: 200,
    body: { items: [], total: 0 },
  }).as("getActivity")
  cy.intercept("GET", `${API}/api/health/summary*`, {
    statusCode: 200,
    body: { healthy: 6, stalled: 1, failed: 1, blocked: 0 },
  }).as("getHealthSummary")
  cy.intercept("GET", `${API}/api/health/failures*`, {
    statusCode: 200,
    body: { total: 0, offset: 0, limit: 50, tasks: [] },
  }).as("getFailures")
  cy.intercept("GET", `${API}/tasks/*/failure`, {
    statusCode: 200,
    body: { message: null, stack_trace: null, evidence: [] },
  }).as("getFailureDetail")
}

describe("Dashboard and monitoring data bindings", () => {
  beforeEach(() => {
    cy.login()
    stubMetricBindingsApis()
  })

  it("renders dashboard KPI values from intercepted metrics/session payloads", () => {
    cy.visit("/")
    cy.wait("@getSessions")
    cy.wait("@getMetricsSeries")

    cy.contains("Total Sessions (24h)")
      .closest("div")
      .contains(/^3$/)
      .should("be.visible")

    cy.contains("Uso de Sessões").should("be.visible")
    cy.contains("Sem dados de uso no período selecionado.").should("not.exist")
  })

  it("renders monitoring chart values from cycle-time and throughput payloads", () => {
    cy.visit("/monitoring")
    cy.wait("@getOverviewMetrics")
    cy.wait("@getCycleTime")
    cy.wait("@getThroughput")

    cy.contains("button", "Tasks").click()

    cy.contains("Cycle Time")
      .closest("div.rounded-2xl")
      .within(() => {
        cy.contains("Average").should("be.visible")
        cy.contains("140s").should("be.visible")
      })

    cy.contains("Throughput by Label")
      .closest("div.rounded-2xl")
      .within(() => {
        cy.contains("triage").should("exist")
      })
  })
})
