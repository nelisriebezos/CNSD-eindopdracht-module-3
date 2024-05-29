describe("LoginView", () => {
	it("Navigates to login when there is no jwt present in localstorage", () => {
		cy.clearLocalStorage();
		cy.visit("/#/collection");
		cy.url().should("contain", "/#/login");
	});

	it("Does not navigate when jwt is present in localstorage", () => {
		cy.clearLocalStorage().then(ls => {
			ls.setItem("jwtToken", "test");
		});
		cy.visit("/#/collection");
		cy.wait(1000);
		cy.url().should("contain", "/collection");
	});

	it("Can login", () => {
		cy.clearLocalStorage();
		cy.visit("/#/login");
		cy.getByTestId('email').typeInWebComponent('test@example.com');
		cy.getByTestId('password').typeInWebComponent("testtest");
		cy.getByTestId('submit').shadow().find('button').clickAtTop();
		cy.url().should("contain", "/#/collection");
	});
});
