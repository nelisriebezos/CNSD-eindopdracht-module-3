<script setup lang="ts">
import {useRoute} from "vue-router";
import {ref} from "vue";
import DecoratedText from "@/components/DecoratedText.vue";
import type {PrintCard} from "@/models/cardModels";

const route = useRoute();
const allPrints = ref<PrintCard[] | null>()
const oracle = ref<PrintCard | null>()
const loading = ref(true)

async function getOracle() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;
  const response = await fetch(`/api/cards/${route.params["oracle_id"]}`, {headers: {Authorization: token}});
  if (!response.ok) {
    console.error(`Failed oracle fetch. Status: ${response.status}`)
    return;
  }
  const parsedData = await response.json() as any;
  const data = await parsedData["Items"] as PrintCard[];
  // Sort the prints on release date
  data.sort((a, b) => new Date(b.ReleasedAt).getTime() - new Date(a.ReleasedAt).getTime())

  allPrints.value = data;
  oracle.value = data[0];
  loading.value = false;
}
getOracle();
</script>

<template>
  <p v-if="loading" class="centered-content">Loading</p>
  <div v-if="!loading && oracle != null" class="oracle-wrapper">
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
          <sl-button class="add-to-deck-button">Add Card to Deck</sl-button>
        </div>
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
            <td><router-link :to="`/cards/${print.OracleId}/${print.PrintId}`">View</router-link></td>
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
  border-spacing: 1rem 0;

  th {
    text-align: left;
  }
}
</style>