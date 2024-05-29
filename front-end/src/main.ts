import "@shoelace-style/shoelace/dist/themes/light.css";
import "@shoelace-style/shoelace/dist/themes/dark.css";
import { setBasePath } from "@shoelace-style/shoelace";

// TODO: do we want to change this to our own hosted version?
setBasePath("https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.12.0/cdn/");

import { createApp, ref } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

let app = createApp(App)
			
app.use(createPinia());
app.use(router);
app.mount("#app");