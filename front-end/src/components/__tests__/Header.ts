import {mount, shallowMount} from "@vue/test-utils";
import Header from "../Header.vue";
import {useRoute} from "vue-router";
import {vi} from "vitest";

vi.mock('vue-router')

describe("Title component", () => {
	// @ts-ignore
	useRoute.mockReturnValue({
    	path: "/",
  	})

	let element: ReturnType<typeof mount>;

	beforeEach(() => {
		element = shallowMount(Header);
	});

	it("should create a component", () => {
		expect(element).toBeTruthy();
	});
});
