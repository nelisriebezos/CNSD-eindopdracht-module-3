<script setup lang="ts">
import {ref, onMounted} from 'vue';

const cardName = ref("");
const cardOracle = ref("");
const cardImageLink = ref("");

const {cardObject} = defineProps<{cardObject: any}>()

cardName.value = cardObject.name
cardOracle.value = cardObject.oracle_id;
if (cardObject.hasOwnProperty('image_uris')) {
  cardImageLink.value = cardObject.image_uris.normal;
} else {
  cardImageLink.value = cardObject.card_faces[0].image_uris.normal
}
</script>

<template>
  <article class="cardItem">
      <span>{{ cardName }}</span>
      <div>
        <img class="image" :src="cardImageLink" :alt="cardName">
      </div>
  </article>
</template>


<style scoped>
.cardItem {
  max-width: 25%;
  padding: 0.4rem;
}

.image {
  height: auto;
  width: 100%;
  display: block;
  border-radius: 1rem;
}
</style>