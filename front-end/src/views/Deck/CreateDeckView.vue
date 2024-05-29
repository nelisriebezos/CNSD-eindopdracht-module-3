<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import "@shoelace-style/shoelace/dist/components/button/button";
import "@shoelace-style/shoelace/dist/components/input/input";

type CreateDeckResponse = {
  id: string;
  name: string;
};

const router = useRouter();

const deckName = ref("");
const loading = ref(false);

const error = ref<string | null>(null);

function getToken(): string | null {
  return localStorage.getItem("jwtToken");
}

async function createDeck(): Promise<ReturnType<typeof router.push>> {
  error.value = null;
  loading.value = true;

  if (!deckName.value) {
    error.value = "No name specified";
    loading.value = false;

    return;
  }

  const token = getToken();
  if (!token) {
    return router.push(`/login/?redirect_url=${encodeURIComponent(router.currentRoute.value.path)}`);
  }
  const response = await fetch("/api/decks/", {
    method: "POST",
    headers: {
      Authorization: token,
    },
    body: JSON.stringify({
      name: deckName.value,
    }),
  });

  if (!response.ok) {
    error.value = `Something went wrong while creating deck. Response code: ${response.status}`;
    loading.value = false;

    return;
  }

  const body = await response.json() as CreateDeckResponse;

  return router.push(`/decks/${body.id}/`);
}
</script>

<template>
  <div id="CreateDeck">
    <sl-card class="container">
      <h2>Create new deck</h2>

      <form @submit.prevent="createDeck()">
        <sl-input
          label="Name"
          v-model="deckName"
          placeholder="My amazing deck"
          ref="nameInput"
          data-test-id="deck-name"
        />

        <p v-show="!!error" class="error" data-test-id="errors">
          {{ error }}
        </p>

        <sl-button
          variant="primary"
          type="submit"
          :loading="loading"
          data-test-id="submit"
        >
          Create
        </sl-button>
      </form>
    </sl-card>
  </div>
</template>

<style lang="scss" scoped>
#CreateDeck {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;

  .container {
    width: 25%;

    h1 {
      margin: 0;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 1em;
      margin-top: 1em;

      p.error {
        color: var(--sl-color-red-200);
      }
    }
  }
}
</style>
