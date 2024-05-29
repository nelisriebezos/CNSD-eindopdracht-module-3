<script setup lang="ts">
import {ref} from "vue";
import {useRouter} from "vue-router";

import "@shoelace-style/shoelace/dist/components/button/button";
import "@shoelace-style/shoelace/dist/components/card/card";
import "@shoelace-style/shoelace/dist/components/icon/icon";

type Deck = {
  id: string,
  name: string,
}

const router = useRouter();
const decks = ref<Deck[]>([]);
const loading = ref(true);

function createDeck(): void {
  void router.push("/decks/new");
}

async function getDecks() {
  const token = localStorage.getItem("jwtToken");

  if (!token) return;

  const response = await fetch("/api/decks", { headers: { Authorization: token } });

  if (!response.ok) {
    console.error(`Failed collections fetch. Status: ${response.status}`)

    return;
  }

  decks.value = await response.json() as Deck[];
  loading.value = false;
}
getDecks();
</script>

<template>
  <div class="header">
    <h2>My decks</h2>
    <sl-button @click="createDeck()" data-test-id="create-deck">
      <sl-icon slot="prefix" name="plus" />
      New deck
    </sl-button>
  </div>

  <p v-if="loading" class="centered-content">Loading</p>

  <div v-if="!loading && decks.length == 0" class="centered-content">
    <p>You have no decks yet.</p>
    <sl-button @click="createDeck()" data-test-id="create-deck">
      <sl-icon slot="prefix" name="plus" />
      Create new deck
    </sl-button>
  </div>

  <div v-if="!loading && decks.length != 0" class="deck-list">
    <sl-card
      v-for="deck in decks"
      :key="deck.id"
    >
      <router-link :to="`/decks/${deck.id}`">{{deck.name}}</router-link>
    </sl-card>
  </div>
</template>

<style scoped lang="scss">
div.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 2em;

  h1 {
    margin: 0;
  }
}
.deck-list {
  display: flex;
  flex-direction: column;
  margin: 2rem;
  gap: 0.5rem;
}
.centered-content {
  margin-top: 20%;
  text-align: center;
}
</style>

