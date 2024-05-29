import { fileURLToPath } from "node:url";
import { mergeConfig, defineConfig, configDefaults } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
	viteConfig,
	defineConfig({
		test: {
			coverage: {
				reportsDirectory: "coverage",
			},
			passWithNoTests: true,
			globals: true,
			environment: "jsdom",
			include: [ "**/__tests__/**.ts" ],
			exclude: [ ...configDefaults.exclude, "e2e/*", "src/main.ts", "src/assets"],
			root: fileURLToPath(
				new URL("./", import.meta.url),
			),
		},
	}),
);
