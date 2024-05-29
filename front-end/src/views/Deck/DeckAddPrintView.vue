<script setup lang="ts">
import {ref} from "vue";
import DecoratedText from "@/components/DecoratedText.vue";
import type {CardInstance, PrintCard} from "@/models/cardModels";

const props = defineProps<{card : any, location : any, printId : string}>()
const emit = defineEmits(['addCard', 'unselectPrint'])


const loading = ref(true)
const card = ref<PrintCard | null>(null);
const instances = ref<CardInstance[]>([])

let loadingRemaining = 2;

async function getCard() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/cards/${props.card['oracle_id']}/${props.printId}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed card fetch. Status: ${response.status}`)
    return;
  }
  card.value = await response.json() as PrintCard;
  // TODO: remove loading.value = false here when getInstances has been implemented
  loading.value = false;
  loaded()
}

async function getInstances() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/collections/${props.card['oracle_id']}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed card instances. Status: ${response.status}`)
    return;
  }
  const unfilteredInstances = await response.json() as CardInstance[];
  instances.value = unfilteredInstances.filter((instance) => instance.PrintId === props.printId)
  loaded()
}

function loaded(){
  loadingRemaining -= 1;
  if (loadingRemaining === 0) {
    loading.value = false;
  }
}

function unselectPrint(){
  emit("unselectPrint");
}

function addCardToDeck(instance? : string) {
    emit('addCard', {oracleId : props.card['oracle_id'], location : props.location, cardInstance : instance, printId : props.printId})
}

getCard();
getInstances();
</script>

<template>
  <p v-if="loading" class="centered-content">Loading</p>
  <div v-if="!loading && card != null" class="card-wrapper">
    <button class="backbutton" @click="unselectPrint">Back</button>
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
          <sl-button class="add-to-deck-button" @click="addCardToDeck()">Add Card to Deck</sl-button>
        </div>
        <div class="instances">
        <table>
          <thead>
          <tr>
            <th>Set name</th>
            <th>Release date</th>
            <th>Rarity</th>
            <th>Price</th>
            <th>Condition</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="instance in instances">
            <td>{{ instance.SetName }}</td>
            <td>{{ new Date(instance.ReleasedAt).toLocaleDateString("nl-nl") }}</td>
            <td>{{ instance.Rarity }}</td>
            <td>{{ instance.Price == null ? "-" : `€${instance.Price}` }}</td>
            <td>{{ instance.Condition }}</td>
            <!-- show in which deck instance currently is -->
            <td><button @click="addCardToDeck(instance.CardInstanceId)">Select this print</button></td>
          </tr>
          </tbody>
        </table>
      </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

table {
  border-spacing: 1rem 0;

  th {
    text-align: left;
  }
}

.add-to-deck-button {
  margin-top: 1rem;
}

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