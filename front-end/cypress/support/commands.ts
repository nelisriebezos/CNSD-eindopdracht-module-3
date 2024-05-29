/// <reference types="cypress" />

// @ts-expect-error
Cypress.Commands.add("getByTestId", (selector, ...args) => {
	return cy.get(`[data-test-id=${selector}]`, ...args);
})

// @ts-expect-error
Cypress.Commands.add("clickAtTop", { prevSubject: "element" }, (subject) => {
	// @ts-expect-error
	cy.wrap(subject).click({ position: "top" });
});

// @ts-expect-error
Cypress.Commands.add("typeInWebComponent", { prevSubject: "element" }, (subject, toType) => {
	cy.wrap(subject)
		.shadow()
		.find("input")
		.type(toType);
});

export {};
