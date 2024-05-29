<script setup lang="ts">
import {ref} from 'vue';
import SearchCard from '../components/SearchCard.vue';
import {useRoute, useRouter} from "vue-router";

const router = useRouter();
const route = useRoute();

const searchQuery = ref(route.query.q ? route.query.q : "");
const cards = ref([]);
const errorText = ref("");

const formDisabled = ref(false);
const formSubmitCount = ref(0);
const MAX_SUBMITS_PER_SECOND = 2;

function canSubmit() {
  if (formDisabled.value) {
    return false;
  }

  setTimeout(() => {
    formSubmitCount.value = 0;
  }, 1000);

  formSubmitCount.value++;

  if (formSubmitCount.value >= MAX_SUBMITS_PER_SECOND) {
    formDisabled.value = true;

    setTimeout(() => {
      formSubmitCount.value = 0;
      formDisabled.value = false;
    }, 500);

    return false;
  }

  if (searchQuery.value === "") return false;

  return true;
}


async function findCards() {
  if (!canSubmit()) {
    return;
  }

  // reset values
  cards.value = [];
  errorText.value = "";

  await router.replace({query: {q: searchQuery.value}});
  const apiUrl: string = `https://api.scryfall.com/cards/search?q=${searchQuery.value}`;
  const response = await requestCards(apiUrl);
  cards.value = response.data;
}
if (searchQuery.value !== "") findCards();

async function requestCards(scryfallAPI: string): Promise<any> {
  try {
    const response = await fetch(scryfallAPI,
      {
        "method": "get",
        "headers": {
          "Content-Type": "application/json"
        },
      }
    );

    if (response.status === 404) {
      throw new CardNotFoundError("Could not find any cards");
    }

    if (!response.ok) {
      throw new Error("HTTP error couldn't fetch the data")
    }

    const data = await response.json();
    return data;
  } catch (error) {

    if (error instanceof CardNotFoundError) {
      errorText.value = error.message;
    }

    console.error("Error fetching data:", error);
  }
}

class CardNotFoundError extends Error {
  constructor(message = "", ...args: any) {
    // @ts-ignore
    super(message, ...args);
    this.message = message + " has not yet been implemented.";
  }
}
</script>

<template>
  <div id="search-container" class="container">
    <h1>Search a card:</h1>
    <form @submit.prevent.submit="findCards">
      <sl-input v-model="searchQuery"></sl-input>
    </form>

    <p v-if="errorText.length > 0">
      {{ errorText }}
    </p>

    <section v-else class="cardsContainer">
      <SearchCard :cardObject="card" class="card" v-for="card in cards"></SearchCard>
    </section>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 1rem;
  flex-direction: column;
}

.cardsContainer {
  display: flex;
  flex-wrap: wrap;
  padding-top: 1rem;
  width: 80%;
}
</style>