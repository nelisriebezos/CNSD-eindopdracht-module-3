<script setup lang="ts">
import {useRoute} from "vue-router";
import {ref} from "vue";
import DecoratedText from "@/components/DecoratedText.vue";
import type {CardInstance, PrintCard} from "@/models/cardModels";

const props = defineProps<{card : any, location : any}>()
const emit = defineEmits(['addCard', 'switchToPrint', 'back'])

const route = useRoute();
const allPrints = ref<PrintCard[] | null>()
const oracle = ref<PrintCard | null>()
const loading = ref(true)
let loadingRemaining = 2;
const instances = ref<CardInstance[]>([]);


function loaded(){
  loadingRemaining -= 1;
  if (loadingRemaining === 0) {
    loading.value = false;
  }
}

async function getOracle() {


  const token = localStorage.getItem('jwtToken');
  if (!token) return;
  const response = await fetch(`/api/cards/${props.card['oracle_id']}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed oracle fetch. Status: ${response.status}`)
    return;
  }

  const parsedData = await response.json() as any;
  const data = await parsedData['Items'] as PrintCard[];
  // Sort the prints on release date
  data.sort((a, b) => new Date(b.ReleasedAt).getTime() - new Date(a.ReleasedAt).getTime())

  allPrints.value = data;
  oracle.value = data[0];
  loaded();
  loading.value = false;
}

async function getInstances() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/collections/${oracle.value?.OracleId}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed card instances. Status: ${response.status}`)
    return;
  }
  instances.value = await response.json() as CardInstance[];
  loaded()
}

function addCardToDeck(instance? : string, printId? : string) {
    emit('addCard', {oracleId : props.card['oracle_id'], location : props.location, cardInstance : instance, printId : printId})
}

function switchToPrint(print : string){
  emit('switchToPrint', {oracleId : props.card['oracle_id'], location : props.location, printId : print})
}

function back() {
  emit('back')
}

getOracle().then(() =>
  getInstances()
);
</script>

<template>
  <p v-if="loading" class="centered-content">Loading</p>
  <div v-if="!loading && oracle != null" class="oracle-wrapper">
    <button class="backbutton" @click="back">Back</button>
    <div class="oracle-image">
      <img v-for="face in oracle.CardFaces" :src="face.ImageUrl" :alt="face.FaceName">
    </div>
    <div>
      <div class="oracle-info">
        <h2>{{ oracle.OracleName }}</h2>
        <DecoratedText :text="oracle.CardFaces[0].OracleText"/>
        <div v-for="face in oracle.CardFaces" class="face-info">
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
            <td><button @click="addCardToDeck(instance.CardInstanceId, instance.PrintId)">Select this print</button></td>
          </tr>
          </tbody>
        </table>
      </div>

      <div class="prints-info">
        <table>
          <thead>
          <tr>
            <th>Set name</th>
            <th>Release date</th>
            <th>Rarity</th>
            <th>Price</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="print in allPrints">
            <td>{{ print.SetName }}</td>
            <td>{{ new Date(print.ReleasedAt).toLocaleDateString("nl-nl") }}</td>
            <td>{{ print.Rarity }}</td>
            <td>{{ print.Price == null ? "-" : `€${print.Price}` }}</td>
            <td><button @click="switchToPrint(print.PrintId)">Select this print</button></td>
          </tr>
          </tbody>
        </table>
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

.oracle-wrapper {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
  margin: 2rem;
}

.oracle-image img {
  max-width: 25rem;
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

.prints-info {
  background-color: #333;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
}

.add-to-deck-button {
  margin-top: 1rem;
}

table {
  margin-top: 15px;
  border-spacing: 1rem 0;

  th {
    text-align: left;
  }
}
</style>