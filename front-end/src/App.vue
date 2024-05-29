<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterView } from "vue-router";
import Header from "@/components/Header.vue";

const HTML_ELEMENT_CLASS_LIST = document.documentElement.classList;

function toggleDarkMode(enabled: boolean): void {
	if (enabled) {
		HTML_ELEMENT_CLASS_LIST.add("sl-theme-dark")
		HTML_ELEMENT_CLASS_LIST.remove("sl-theme-light")
	} else {
		HTML_ELEMENT_CLASS_LIST.add("sl-theme-light")
		HTML_ELEMENT_CLASS_LIST.remove("sl-theme-dark")
	}
}

onBeforeMount(() => {
	const preferDarkMode = window.matchMedia("(prefers-color-scheme: dark)")
		.matches;

	toggleDarkMode(preferDarkMode);
});
</script>

<template>
  <Header/>
  <main>
	  <RouterView />
  </main>
</template>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap");

html,
body {
	margin: 0;
	padding: 0;
	font-size: 16px;
	line-height: 1.6;
}

* {
	box-sizing: border-box;
	font-family: "Inter", sans-serif;
}
</style>
