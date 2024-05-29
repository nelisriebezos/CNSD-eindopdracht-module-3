<script setup lang="ts">
import "@shoelace-style/shoelace/dist/components/button/button";
import "@shoelace-style/shoelace/dist/components/card/card";
import "@shoelace-style/shoelace/dist/components/icon/icon";
import {useRoute} from "vue-router";
import {ref} from "vue";
import CardListPreview from "./CardListPreview.vue";
import type { DeckCard } from "@/models/cardModels";
import AddCardToDeckView from "./AddCardToDeckView.vue";
import DeckSearchView from "./DeckSearchView.vue";
import ValidationBar from "@/components/Deck/ValidationBar.vue";

type Deck = {
  id: string,
  name: string,
}

const errorMesssage = ref("");
const route = useRoute();
const deck = ref<Deck | null>(null);
const loading = ref(true)

const cardsList = ref<DeckCard[]>([]);
const mainDeck = ref<DeckCard[]>([]);
const sideDeck = ref<DeckCard[]>([]);
const commanders = ref<DeckCard[]>([]);

function sortCards() {
  for (let card of cardsList.value) {
    sortInCard(card);
  }
}

function displayError(message : string){
  errorMesssage.value = message;
}

async function getDeck() {
  const token = localStorage.getItem("jwtToken");

  if (!token) return;
  const response = await fetch(`/api/decks/${route.params["deck_id"]}`, {headers: {Authorization: token}});

  if (!response.ok) {
    console.error(`Failed deck fetch. Status: ${response.status}`)

    return;
  }

  deck.value = await response.json() as Deck;
  // TODO: move to getcards
  loading.value = false;
}

async function getCards() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/decks/${route.params["deck_id"]}/cards/`, {
    headers: {Authorization: token},
  });

  if (!response.ok) {
    console.error(`Failed to fetch cards from deck. Status: ${response.status}`)
    return;
  }

  cardsList.value = await response.json() as DeckCard[];
  sortCards();
}

async function getCard(cardId : string) {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/decks/${route.params["deck_id"]}/cards/${cardId}`, {
    headers: {Authorization: token},
  });

  if (!response.ok) {
    console.error(`Failed to fetch cards from deck. Status: ${response.status}`)
    return;
  }
  return await response.json() as DeckCard;
}


function addCardToList(event : any) {
  getCard(event['deckCardId']).then((response) => {
    if (response === undefined){
      errorMesssage.value = "An error has occurred adding the selected card to your deck."
      return
    }
    sortInCard(response)})
}

function sortInCard(card : DeckCard){
  switch (card.card_location){
    case ('COMMANDER'):
      commanders.value.push(card);
      return;
    case ('MAIN_DECK'):
      mainDeck.value.push(card);
      return;
    case ('SIDE_DECK'):
      sideDeck.value.push(card);
      return;
  }
  console.error("Couldn't sort card with location: " + card.card_location + ".");
}

function deleteCard(card : DeckCard){
  const token = localStorage.getItem("jwtToken");
    if (!token) return;

  fetch(`/api/decks/${route.params["deck_id"]}/cards/${card.deck_card_id}`, 
    {
      method: "DELETE",
      headers: {Authorization: token}
    }
  ).then(
    (response) =>
    {
      if (response.ok) {
        cardsList.value = cardsList.value.filter((originalCard) => originalCard.deck_card_id !== card.deck_card_id)
        switch (card.card_location){
          case ('COMMANDER'):
            commanders.value = commanders.value.filter((originalCard) => originalCard.deck_card_id !== card.deck_card_id)
            return;
          case ('MAIN_DECK'):
            mainDeck.value = mainDeck.value.filter((originalCard) => originalCard.deck_card_id !== card.deck_card_id)
            return;
          case ('SIDE_DECK'):
            sideDeck.value = sideDeck.value.filter((originalCard) => originalCard.deck_card_id !== card.deck_card_id)
            return;
        }
      } else {
          console.error(response)
      }
    }
  )
}

getDeck();
getCards();
</script>

<template>
  <p v-if="loading" class="centered-content">Loading</p>
  <p v-if="errorMesssage !== ''" class="error">{{ errorMesssage }}</p>
  <div v-if="!loading && deck != null" class="page-content">
    <h2>Deck: {{deck.name}}</h2>

    <ValidationBar
      :commanders="commanders"
      :main-deck="mainDeck"
      :side-deck="sideDeck"
    />

    <div class="cardList">
      <h3>Commander(s):</h3>
      <div v-for="card in commanders">
        <CardListPreview :card="card" @delete="deleteCard"></CardListPreview>
      </div>
      <AddCardToDeckView location="COMMANDER" class="addbox" @card-added="addCardToList"></AddCardToDeckView>

      <h3>Main deck:</h3>
      <div v-for="card in mainDeck">
        <CardListPreview :card="card" @delete="deleteCard"></CardListPreview>
      </div>
      <AddCardToDeckView location="MAIN_DECK" class="addbox" @card-added="addCardToList"></AddCardToDeckView>

      <h3>Side deck:</h3>
      <div v-for="card in sideDeck">
        <CardListPreview :card="card" @delete="deleteCard"></CardListPreview>
      </div>
      <AddCardToDeckView location="SIDE_DECK" class="addbox" @card-added="addCardToList"></AddCardToDeckView>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-content {
  margin: 2rem;
}
.centered-content {
  margin-top: 20%;
  text-align: center;
}
.card-list {
  -moz-column-count: 5;
  -moz-column-gap: 5px;
  -webkit-column-count: 5;
  -webkit-column-gap: 5px;
  column-count: 5;
  column-gap: 5px;
}

.error {
  color: red;
}

.addbox {
  width: 550px;
}

.card {
  margin-bottom: 1px;
}
</style>

