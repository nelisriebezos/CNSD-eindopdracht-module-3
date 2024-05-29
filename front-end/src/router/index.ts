import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: "/",
			name: "home",
			component: () => import(/* webpackChunkName: "home" */ "../views/HomeView.vue"),
		},
		{
			path: "/register",
			name: "register",
			component: () => import(/* webpackChunkName: "register" */ "../views/RegisterView.vue"),
		},
		{
			path: "/login",
			name: "login",
			component: () => import(/* webpackChunkName: "login" */ "../views/LoginView.vue"),
		},
		{
			path: "/decks",
			name: "decks",
			component: () => import(/* webpackChunkName: "decks-view" */ "../views/Deck/DecksView.vue"),
		},
		{
			path: "/decks/:deck_id",
			name: "deck",
			component: () => import(/* webpackChunkName: "deck-view" */ "../views/Deck/DeckView.vue"),
		},
		{
			path: "/decks/new",
			name: "create-deck",
			component: () => import(/* webpackChunkName: "create-deck" */ "../views/Deck/CreateDeckView.vue"),
		},
		{
			path: "/collection",
			name: "collection",
			component: () => import(/* webpackChunkName: "collection" */ "../views/CollectionView.vue"),
		},
        {
			path: "/search",
			name: "search",
			component: () => import(/* webpackChunkName: "search" */ "../views/SearchView.vue"),
		},
		{
			path: "/cards/:oracle_id",
			name: "oracles",
			component: () => import(/* webpackChunkName: "oracles" */ "../views/OracleDetailView.vue"),
		},
		{
			path: "/cards/:oracle_id/:card_id",
			name: "cards",
			component: () => import(/* webpackChunkName: "cards" */ "../views/CardDetailView.vue"),
		},
		{
			path: "/:pathMatch(.*)*",
			name: "not-found",
			component: () => import(/* webpackChunkName: "not-found" */ "../views/NotFoundView.vue"),
		},
	],
});

export default router;
