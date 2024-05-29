import { v4 as uuidv4} from 'uuid';

describe("Register page Test", () => {
	const firstEmail = `test-${uuidv4()}@example.com`;
	const secondEmail = `test-${uuidv4()}@example.com`;

	beforeEach(()=>{
		cy.visit("/#/register");
	});

	it("Registers the user in correctly", () => {
		cy.getByTestId('email')
			.typeInWebComponent(firstEmail);
		cy.getByTestId('password')
			.typeInWebComponent("testtest");
		cy.getByTestId('confirm')
			.typeInWebComponent("testtest");
		cy.getByTestId('submit')
			.shadow()
			.find('button')
			.clickAtTop();

		cy.url().should("contain", "/#/login");

		cy.on('window:alert', (str) => {
			expect(str).to.equal(`We have send you an email to verify your email address.`);
		});
	});

	it("Registers when user already exists", () => {
		cy.getByTestId('email')
			.typeInWebComponent(secondEmail);
		cy.getByTestId('password')
			.typeInWebComponent("testtest");
		cy.getByTestId('confirm')
			.typeInWebComponent("testtest");
		cy.getByTestId('submit')
			.shadow()
			.find('button')
			.clickAtTop();

		cy.url().should("contain", "/#/login");

		cy.visit("/#/register");

		cy.getByTestId('email')
			.typeInWebComponent(secondEmail);
		cy.getByTestId('password')
			.typeInWebComponent("testtest");
		cy.getByTestId('confirm')
			.typeInWebComponent("testtest");
		cy.getByTestId('submit')
			.shadow()
			.find('button')
			.clickAtTop();

		cy.contains("This email address has already been registered!");
	});
});
