<script setup lang="ts">
import {useRoute} from "vue-router";
import {ref} from "vue";
import DecoratedText from "@/components/DecoratedText.vue";
import type {PrintCard} from "@/models/cardModels";

const route = useRoute();
const oracleId = route.params["oracle_id"];
const cardId = route.params["card_id"];
const wantsToAddThisCard = ref<boolean>(false);
const loading = ref(true)
const card = ref<PrintCard | null>(null);
const collectionCardConditionValue = ref<string>("near_mint");

async function getCard() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/cards/${oracleId}/${cardId}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed card fetch. Status: ${response.status}`)
    return;
  }
  card.value = await response.json() as PrintCard;
  loading.value = false;
}
getCard();

async function flipWantsToAddThisCard() {
  wantsToAddThisCard.value = !wantsToAddThisCard.value;
}

async function addCardToCollection() {
  if (collectionCardConditionValue.value == "") return;
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/collections`,
    {
      headers: {
        Authorization: token,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        "oracle_id": oracleId,
        "print_id": cardId,
        "condition": collectionCardConditionValue.value
      }),
      method: "post"
    });
  if (!response.ok) {
    console.error(`Failed to add a card to the collection. Status: ${response.status}`)
    return;
  }
}
</script>

<template>
  <p v-if="loading" class="centered-content">Loading</p>
  <div v-if="!loading && card != null" class="card-wrapper">
    <div class="card-image">
      <img v-for="face in card.CardFaces" :src="face.ImageUrl" :alt="face.FaceName">
    </div>

    <div>
      <div class="card-info">
        <h2>{{ card.OracleName }}</h2>
        <DecoratedText :text="card.CardFaces[0].OracleText"/>
        <div v-for="face in card.CardFaces" class="face-info">
          <div>
            <p>{{ face.FaceName }}</p>
            <DecoratedText :text="face.ManaCost"/>
          </div>
          <p>{{ face.TypeLine }}</p>
          <DecoratedText :text="face.FlavorText"/>
        </div>
        <div>
          <div v-if="!wantsToAddThisCard" class="add-to-collection-button-wrapper">
            <sl-button @click="flipWantsToAddThisCard">Add Card to Collection</sl-button>
          </div>
          <div v-if="wantsToAddThisCard" class="add-to-collection-button-wrapper">
            <sl-select label="Card condition" value="near_mint" @sl-change="collectionCardConditionValue = $event.target.value">
              <sl-option value="mint">Mint</sl-option>
              <sl-option value="near_mint">Near Mint</sl-option>
              <sl-option value="slightly_played">Slightly Played</sl-option>
              <sl-option value="played">Played</sl-option>
              <sl-option value="heavily_played">Heavily Played</sl-option>
              <sl-option value="poor">Poor</sl-option>
            </sl-select>
            <div class="add-card-confirmation-wrapper">
              <sl-button variant="danger" outline @click="flipWantsToAddThisCard">Cancel</sl-button>
              <sl-button variant="success" outline @click="addCardToCollection">Confirm</sl-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
p {
  margin: 0;
}

.centered-content {
  margin-top: 20%;
  text-align: center;
}

.card-wrapper {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
  margin: 2rem;
}

.card-image img {
  max-width: 25rem;
}

.add-to-collection-button-wrapper {
  border-top: 1px solid #333;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  width: fit-content;
}

.add-card-confirmation-wrapper {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;

  >* {
    flex-grow: 1;
  }
}

.face-info {
  border-top: 1px solid #333;
  margin-top: 0.5rem;
  padding-top: 0.5rem;

  >div {
    display: flex;
    gap: 1rem;
  }
}
</style>