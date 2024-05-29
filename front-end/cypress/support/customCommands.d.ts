// customCommands.d.ts

declare namespace Cypress {
	interface Chainable<Subject = any> {
		/**
		 * Custom command to select elements by data-testid attribute
		 * @example cy.getByTestId('some-test-id')
		 */
		getByTestId(value: string): Chainable<JQuery<HTMLElement>>;

		
	}

	interface Chainable {
		/**
		 * Custom command to perform a click action at the top position on the element.
		 * @example
		 * cy.get('button').clickAtTop();
		 */
		clickAtTop(): Chainable<Element>;
	}

	interface Chainable {
		typeInWebComponent(toType: string): Chainable<Element>;
	}
}
