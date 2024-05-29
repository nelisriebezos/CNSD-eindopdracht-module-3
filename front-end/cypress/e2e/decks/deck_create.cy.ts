const TEST_UUID = "af7c1fe6-d669-414e-b066-e9733f0de7a8";
// test jwt token {{{
const TEST_JWT = "eyJraWQiOiJ5cDRXM3o0Rng4Z3FUZ0JDeXh0MkFcLzBZb2Q1Y2hFakd2Sk13MTk3RzhVST0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyYjdlM2VmNS03ZTc4LTQ4NTQtOGFjNS1lZTdmOTRjMDI1ZDUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfZTBCVzNWUXJXIiwiY29nbml0bzp1c2VybmFtZSI6IjJiN2UzZWY1LTdlNzgtNDg1NC04YWM1LWVlN2Y5NGMwMjVkNSIsIm9yaWdpbl9qdGkiOiIwZTFhYTA3ZS01YmM4LTQ5NzctOGE3Zi0yMDdlMzQwYzM3YmIiLCJhdWQiOiJtbDlkMnU3YXAzM3Z0dXNhMzl2dnM4bnA1IiwiZXZlbnRfaWQiOiI4YjUwMDk1Zi01YTBlLTRjYTEtOGZiNy1lMjcyNTgxNmQ5NzgiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwNTMzMzA3MywiZXhwIjoxNzA1MzM2NjczLCJpYXQiOjE3MDUzMzMwNzMsImp0aSI6IjFlMTNmODg5LWVmYWMtNGU1Ni1iOWRkLWJjMTdhYjRkM2Y1NiIsImVtYWlsIjoiam9yYW0uYnVpdGVuaHVpc0BzdHVkZW50Lmh1Lm5sIn0.Yl9B-63AIRoneShr6-TpyjEpIUuOvg7Tas1NCr8AQpFhFNo4S5eB-6H26JMd3pEawmWaWcNuhmXp7Y8K2IYR6FjLFF2ciUS9B-xNKVLH_9MUWdHqioLdlI39fWFeWDpbNXsF7LMM79H5DTFH_1EwnPNghsZMgNLpFhJtfb4ofoOG0AIG0xQXuYO1tzCHSeIilNbp1W_ITruQEQrqDknxIx98M2tHdxm69m27WPSCVFZaGSJq0GNdCVg7DtYbEzJ20vSn4k-BP6OtdUa7wL_mg5CzWeIUxdCkMixQ8Tnefdi2U9MVJdkoAGo1DRRLS45Hx5uDBkZZJCLRH7-M33LStA";
// }}}

describe("CreateDeckView", () => {
	beforeEach(() => {
		cy.clearLocalStorage()
			.then(ls => {
				ls.setItem("jwtToken", TEST_JWT);
			});

		cy.intercept(
			{
				method: "POST",
				url: "/api/decks/",
			},
			(req) => {
				req.reply({
					statusCode: 201,
					body: {
						id: TEST_UUID,
						name: req.body.name,
					},
				});
			},
		);
	});

	it("creates a new deck and navigates to the url when create button is pressed", () => {
		cy.visit("/#/decks/new/");

		cy.getByTestId("deck-name")
			.typeInWebComponent("CY test deck");

		cy.getByTestId("submit")
			.clickAtTop();

		cy.location("hash")
			.should("equal", `#/decks/${TEST_UUID}/`);
	});

	it("shows an error that the deck name isn't specified", () => {
		cy.visit("/#/decks/new/");

		cy.getByTestId("submit")
			.clickAtTop();

		cy.getByTestId("errors")
			.contains("No name specified");

		cy.location("hash")
			.should("equals", "#/decks/new/");
	});
});
