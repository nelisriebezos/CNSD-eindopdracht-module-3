<script setup lang="ts">
import "@shoelace-style/shoelace/dist/components/card/card";
import {ref} from "vue";
import type {CollectionPrintCard} from "@/models/cardModels";

type Collection = {
  [key: string]: CollectionPrintCard[],
}

const collection = ref<Collection>({});
const collectionFilterQuery = ref<string>("");
const collectionOffsetPK = ref<string | null>(null);
const collectionOffsetSK = ref<string | null>(null);
const collectionLoading = ref<boolean>(true);

const oracleGroupingModal = ref<HTMLDialogElement>();
const selectedOracle = ref<string>("");
const selectedOraclePrints = ref<CollectionPrintCard[]>([]);

function constructGetCollectionUrl() {
  let url = "/api/collections";
  if (collectionFilterQuery.value != "") {
    url += `?q=${encodeURIComponent(collectionFilterQuery.value)}`
  }
  if (collectionOffsetPK.value != null && collectionOffsetSK.value != null) {
     url += collectionFilterQuery.value === "" ? "?" : "&";
     url += `pk-last-evaluated=${encodeURIComponent(collectionOffsetPK.value)}&sk-last-evaluated=${encodeURIComponent(collectionOffsetSK.value)}`
  }
  return url;
}

async function getCollection() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;

  collectionOffsetPK.value = null;
  collectionOffsetSK.value = null;

  const response = await fetch(constructGetCollectionUrl(), { headers: { Authorization: token } });
  if (!response.ok) {
    console.error(`Failed collections fetch. Status: ${response.status}`)
    return;
  }
  const body = await response.json() as any;
  const data = body["Items"] as CollectionPrintCard[];
  const newCollection: Collection = {};

  for (const instanceCard of data) {
    if (instanceCard.OracleId in newCollection) {
      newCollection[instanceCard.OracleId].push(instanceCard)
      continue;
    }
    newCollection[instanceCard.OracleId] = [instanceCard]
  }

  collectionOffsetPK.value = body["pk-last-evaluated"]
  collectionOffsetSK.value = body["sk-last-evaluated"]
  collection.value = newCollection;
  collectionLoading.value = false;
}
getCollection();

async function loadMoreFromCollection() {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;

  if (collectionOffsetPK.value == null || collectionOffsetSK.value == null) return;

  const response = await fetch(constructGetCollectionUrl(), {
    headers: { Authorization: token },
  });
  if (!response.ok) {
    console.error(`Failed collections fetch. Status: ${response.status}`)
    return;
  }
  const body = await response.json() as any;
  const data = body["Items"] as CollectionPrintCard[];

  for (const instanceCard of data) {
    if (instanceCard.OracleId in collection.value) {
      collection.value[instanceCard.OracleId].push(instanceCard)
      continue;
    }
    collection.value[instanceCard.OracleId] = [instanceCard]
  }

  collectionOffsetPK.value = body["pk-last-evaluated"]
  collectionOffsetSK.value = body["sk-last-evaluated"]
  collectionLoading.value = false;
}

async function removeCardFromCollection(oracleId: string, instanceId: string) {
  const token = localStorage.getItem("jwtToken");
  if (!token) return;

  const response = await fetch(`/api/collections/${instanceId}`, {
    headers: { Authorization: token },
    method: "delete"
  });
  if (!response.ok) {
    console.error(`Failed remove card from collection fetch. Status: ${response.status}`)
    return;
  }
  selectedOraclePrints.value = selectedOraclePrints.value.filter(v => v.CardInstanceId != instanceId);
  collection.value[oracleId] = collection.value[oracleId].filter(v => v.CardInstanceId != instanceId);
  if (selectedOraclePrints.value.length === 0) {
    delete collection.value[oracleId]
    closeOracleGroupingModal();
  }
}

function openOracleGroupingModal(oracleId: string) {
  if (!(oracleId in collection.value)) return;

  selectedOracle.value = oracleId;
  selectedOraclePrints.value = collection.value[oracleId];
  oracleGroupingModal.value?.showModal();
}
function closeOracleGroupingModal() {
  selectedOracle.value = "";
  selectedOraclePrints.value = [];
  oracleGroupingModal.value?.close();
}
</script>

<template>
  <div class="collection-wrapper">
    <h2>My Collection</h2>

    <div class="search-collection-input-wrapper">
      <sl-input label="Filter collection" v-model="collectionFilterQuery" />
      <sl-button @click="getCollection">Filter</sl-button>
    </div>

    <p v-if="Object.keys(collection).length === 0 && !collectionLoading" class="centered-content">
      Your collection is empty.
    </p>

    <p v-if="collectionLoading" class="centered-content">
      Loading
    </p>

    <section class="cards-container">
      <sl-card v-for="(card, oracle) in collection" class="card" @click="() => openOracleGroupingModal(oracle as string)">
        <img slot="image" :src="card[0].CardFaces[0].ImageUrl" alt="MTG - Card face">
        <div>Instances: {{card.length}}</div>
      </sl-card>
    </section>
    <sl-button class="load-more-button" @click="loadMoreFromCollection" :disabled="collectionOffsetPK == null || collectionOffsetSK == null">Load more</sl-button>

    <dialog ref="oracleGroupingModal" @click="closeOracleGroupingModal" class="oracle-grouping-dialog">
      <div @click="$event.stopPropagation()">
        <div v-if="selectedOracle != ''">
          <h3>{{selectedOraclePrints[0].OracleName}}</h3>
          <table>
            <thead>
              <tr>
                <th>Set name</th>
                <th>Condition</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="print in selectedOraclePrints">
                <td>{{ print.SetName }}</td>
                <td>{{ print.Condition }}</td>
                <td><sl-button title="Remove card" variant="danger" @click="() => removeCardFromCollection(selectedOracle, print.CardInstanceId)">X</sl-button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </dialog>
  </div>
</template>

<style scoped lang="scss">
h2 {
  margin: 2rem;
}
.collection-wrapper {
    display: flex;
    padding-top: 1rem;
    flex-direction: column;
}
.search-collection-input-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 0.2rem;
}
.cards-container {
  display: flex;
  flex-wrap: wrap;
  padding: 1rem;
}
.card {
  margin: 1rem;
  width: 15rem;
  cursor: pointer;
  img {
    height: inherit;
    border-radius: 1rem;
  }
}
.centered-content {
  margin-top: 20%;
  text-align: center;
}
.load-more-button {
  margin: 0 2rem 2rem 2rem;
}
.oracle-grouping-dialog {
  padding: 0;
  border: 1px solid white;
  border-radius: 10px;

  h3 {
    margin: 1rem;
  }

  table {
    border-spacing: 1rem 0.2rem;

    th {
      text-align: left;
    }
    button {
      margin: 0;
    }
  }

  &:focus-visible {
    outline: none;
  }
  &::backdrop {
    backdrop-filter: blur(10px);
  }
}
</style>
