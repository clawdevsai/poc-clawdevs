/**
 * E2E tests for the Chat page (/chat).
 *
 * All network calls are intercepted and stubbed so the tests run
 * deterministically without a real backend.
 */

const API = "/api";
const AGENTS_URL = `${API}/agents`;
const SESSIONS_URL = `${API}/sessions`;
const HISTORY_URL = `${API}/chat/history/*`;
const RAG_SEARCH_URL = `${API}/memory/rag/search`;
const RAG_TURN_URL = `${API}/chat/rag/turn`;
const TRANSCRIPT_URL = `${API}/chat/transcript/turn`;
const STREAM_URL = "/openclaw/chat/stream";

/** Builds an SSE stream body from an array of text chunks. */
function buildSseStream(chunks: string[]): string {
  return chunks
    .map((text) => {
      const data = JSON.stringify({
        choices: [{ delta: { content: text } }],
      });
      return `data: ${data}\n\n`;
    })
    .join("") + "data: [DONE]\n\n";
}

/** Stubs the standard set of APIs the chat page calls on load. */
function stubChatApis(
  opts: {
    agentsFixture?: string;
    historyFixture?: string;
    sessionsFixture?: string;
  } = {}
) {
  cy.intercept("GET", AGENTS_URL, { fixture: opts.agentsFixture ?? "agents.json" }).as(
    "getAgents"
  );
  cy.intercept("GET", SESSIONS_URL, { fixture: opts.sessionsFixture ?? "sessions.json" }).as(
    "getSessions"
  );
  cy.intercept("GET", HISTORY_URL, {
    fixture: opts.historyFixture ?? "chat-history.json",
  }).as("getHistory");
  // Stub persistence endpoints as no-ops
  cy.intercept("POST", RAG_TURN_URL, { statusCode: 200, body: { status: "ok", memory_id: "m1" } }).as(
    "persistRag"
  );
  cy.intercept("POST", TRANSCRIPT_URL, { statusCode: 200, body: { status: "ok" } }).as(
    "persistTranscript"
  );
  cy.intercept("GET", RAG_SEARCH_URL, {
    statusCode: 200,
    body: { query: "", results_count: 0, results: [] },
  }).as("ragSearch");
}

describe("Chat page", () => {
  beforeEach(() => {
    cy.login();
    stubChatApis();
  });

  // ─── Page load ───────────────────────────────────────────────────────

  it("loads and displays agent info, history, and composer", () => {
    cy.visit("/chat");
    cy.wait("@getAgents");

    // Agent header shows the first agent
    cy.contains("CTO Agent").should("exist");
    cy.contains("chief technology officer").should("exist");

    // History messages are rendered
    cy.wait("@getHistory");
    cy.contains("Qual a arquitetura recomendada para microsserviços?").should("exist");
    cy.contains("Arquitetura de Microsserviços").should("exist");

    // Composer is present
    cy.get("textarea").should("be.visible");
    cy.get('[aria-label="Enviar mensagem"]').should("be.visible");
  });

  it("shows empty state when history has no messages", () => {
    cy.intercept("GET", HISTORY_URL, {
      body: { agent_slug: "cto-agent", messages: [] },
    }).as("emptyHistory");
    cy.visit("/chat");
    cy.wait("@getAgents");
    cy.wait("@emptyHistory");

    cy.contains("Nenhuma mensagem nesta conversa.").should("be.visible");
  });

  // ─── Agent selector ──────────────────────────────────────────────────

  describe("agent selector", () => {
    it("opens dropdown and switches agent", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Open the agent dropdown via the toggle button
      cy.get('[aria-label="Abrir seletor de agente"]').click();

      // Dropdown lists all fixture agents
      cy.contains("Dev Agent").should("be.visible");
      cy.contains("PM Agent").should("be.visible");

      // Click on Dev Agent
      cy.contains("software developer · Dev Agent").click();

      // Agent header updates
      cy.contains("Dev Agent").should("exist");
    });

    it("filters agents by typing in the input", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");

      // Open dropdown via toggle button (avoids blur-closing the dropdown)
      cy.get('[aria-label="Abrir seletor de agente"]').click();

      // Wait for dropdown to render
      cy.contains("product manager · PM Agent").should("be.visible");

      // Type filter in the agent input
      cy.get("input[placeholder='Digite para buscar agente']").clear().type("PM");

      // PM Agent should remain visible
      cy.contains("product manager · PM Agent").should("be.visible");

      // Dev Agent (role: software developer) should be filtered out
      cy.contains("software developer · Dev Agent").should("not.exist");
    });
  });

  // ─── Send message ────────────────────────────────────────────────────

  describe("send message", () => {
    it("sends a message via button click and displays streamed response", () => {
      const sseBody = buildSseStream(["Olá! ", "Como posso ajudar?"]);
      cy.intercept("POST", STREAM_URL, {
        statusCode: 200,
        body: sseBody,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
        },
      }).as("streamChat");

      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Type and send
      cy.get("textarea").type("Nova pergunta sobre arquitetura");
      cy.get('[aria-label="Enviar mensagem"]').should("not.be.disabled").click();

      // Stream request fires
      cy.wait("@streamChat");

      // User message appears
      cy.contains("Nova pergunta sobre arquitetura").should("be.visible");

      // Assistant response appears (accumulated from stream chunks)
      cy.contains("Olá! Como posso ajudar?").should("exist");

      // Persistence calls happen
      cy.wait("@persistRag");
      cy.wait("@persistTranscript");
    });

    it("sends a message via Enter key", () => {
      const sseBody = buildSseStream(["Resposta rápida"]);
      cy.intercept("POST", STREAM_URL, {
        statusCode: 200,
        body: sseBody,
        headers: { "Content-Type": "text/event-stream" },
      }).as("streamChat");

      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      cy.get("textarea").type("Pergunta via Enter{enter}");
      cy.wait("@streamChat");
      cy.contains("Pergunta via Enter").should("be.visible");
      cy.contains("Resposta rápida").should("exist");
    });

    it("does not send empty messages", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");

      // Send button should be disabled when input is empty
      cy.get('[aria-label="Enviar mensagem"]').should("be.disabled");
    });

    it("disables send button while streaming", () => {
      // Slow stream to keep the button in "sending" state
      cy.intercept("POST", STREAM_URL, (req) => {
        req.reply({
          statusCode: 200,
          body: buildSseStream(["lento"]),
          headers: { "Content-Type": "text/event-stream" },
          delay: 1500,
        });
      }).as("slowStream");

      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      cy.get("textarea").type("Mensagem com stream lento");
      cy.get('[aria-label="Enviar mensagem"]').click();

      // While streaming, the button should show a spinner and be disabled
      cy.get('[aria-label="Enviar mensagem"]').should("be.disabled");

      cy.wait("@slowStream");
    });

    it("handles stream error gracefully", () => {
      cy.intercept("POST", STREAM_URL, {
        statusCode: 500,
        body: JSON.stringify({ detail: "Gateway timeout" }),
      }).as("streamError");

      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      cy.get("textarea").type("Mensagem com erro");
      cy.get('[aria-label="Enviar mensagem"]').click();
      cy.wait("@streamError");

      // Error message is shown
      cy.contains("Gateway timeout").should("be.visible");

      // The placeholder assistant bubble is removed
      cy.contains("Pensando...").should("not.exist");
    });
  });

  // ─── Copy message ────────────────────────────────────────────────────

  describe("copy message", () => {
    it("copies user message to clipboard", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Find the user message bubble (right-aligned) and its copy button.
      // Use .first() to avoid multi-match when both user+assistant have copy buttons.
      cy.get('[aria-label="Copiar texto da mensagem"]').first().click();

      // After clicking, at least one button should show "Copiado"
      cy.get('[aria-label="Copiado"]').should("have.length.at.least", 1);
    });
  });

  // ─── Download assistant document ─────────────────────────────────────

  describe("download assistant message", () => {
    it("shows download button on assistant messages with document content", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // The assistant message has a document (markdown with heading), so
      // the download button should exist
      cy.get('[aria-label="Baixar documento"]').should("have.length.at.least", 1);
    });
  });

  // ─── Export chat ─────────────────────────────────────────────────────

  describe("export chat", () => {
    it("export button is enabled when there are messages", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      cy.get('[aria-label="Exportar conversa"]').should("not.be.disabled");
    });

    it("export button is disabled when there are no messages", () => {
      cy.intercept("GET", HISTORY_URL, {
        body: { agent_slug: "cto-agent", messages: [] },
      }).as("emptyHistory");
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@emptyHistory");

      cy.get('[aria-label="Exportar conversa"]').should("be.disabled");
    });
  });

  // ─── Refresh history ─────────────────────────────────────────────────

  describe("refresh history", () => {
    it("refetches history when the button is clicked", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Click the refresh button
      cy.contains("button", "Histórico").click();
      cy.wait("@getHistory");
    });
  });

  // ─── Session URL param ───────────────────────────────────────────────

  describe("session from URL", () => {
    it("loads chat with a valid session param", () => {
      cy.visit("/chat?session=agent:cto-agent:main");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Agent name should be present in the header
      cy.contains("CTO Agent").should("exist");
      cy.contains("Qual a arquitetura recomendada para microsserviços?").should("exist");
    });

    it("shows error for invalid session param format", () => {
      cy.visit("/chat?session=invalid-format");
      cy.wait("@getAgents");

      // The error text about invalid session should appear
      cy.contains("Session inválida").should("exist");
    });
  });

  // ─── Session selector ────────────────────────────────────────────────

  describe("session selector", () => {
    it("shows session dropdown for selected agent", () => {
      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      // Session select should be visible and not disabled
      cy.get('[aria-label="Sessão OpenClaw"]').should("be.visible").and("not.be.disabled");
    });
  });

  // ─── Stream timer ────────────────────────────────────────────────────

  describe("stream timer", () => {
    it("shows last response time after stream completes", () => {
      const sseBody = buildSseStream(["ok"]);
      cy.intercept("POST", STREAM_URL, {
        statusCode: 200,
        body: sseBody,
        headers: { "Content-Type": "text/event-stream" },
      }).as("streamChat");

      cy.visit("/chat");
      cy.wait("@getAgents");
      cy.wait("@getHistory");

      cy.get("textarea").type("teste timer");
      cy.get('[aria-label="Enviar mensagem"]').click();
      cy.wait("@streamChat");

      cy.contains("Tempo da última resposta:").should("be.visible");
    });
  });
});
