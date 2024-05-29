describe("DeckView", () => {
	it("Navigates to create deck when create new deck button is pressed", () => {
		cy.clearLocalStorage().then(ls => {
			ls.setItem("jwtToken", "test");
		});
		cy.visit("/#/decks");
		cy.getByTestId("create-deck").clickAtTop();
		cy.url().should("contain", "/decks/new");
	});
});
