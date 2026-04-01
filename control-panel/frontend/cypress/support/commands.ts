declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Stub-authenticate by setting a fake token in localStorage.
       * No real backend call is made — works entirely offline.
       */
      login(username?: string, password?: string): Chainable<void>;
    }
  }
}

Cypress.Commands.add("login", (_username = "admin", _password = "admin") => {
  cy.session([_username, _password], () => {
    window.localStorage.setItem("panel_token", "e2e-test-token-stub");
  });
});

export {};
