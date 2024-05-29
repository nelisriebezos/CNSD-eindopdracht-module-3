<script setup lang="ts">
import { computed } from "vue";
import "@shoelace-style/shoelace/dist/components/card/card";
import type { DeckCard } from "@/models/cardModels";

const MAX_COMMANDERS = 1;
const MAX_MAIN_DECK = 100;

const props = defineProps<{
  commanders: DeckCard[];
  mainDeck: DeckCard[];
  sideDeck: DeckCard[];
}>();

const commanderCountValid = computed( () => props.commanders.length === MAX_COMMANDERS );
const commanderIsLegendaryCreature = computed(
  () => props.commanders[0]?.CardFaces[0]?.TypeLine.toLowerCase().includes("legendary")
    && props.commanders[0]?.CardFaces[0]?.TypeLine.toLowerCase().includes("creature"),
);

const allCardsCount = computed( () => props.commanders.length + props.mainDeck.length );
const mainDeckValid = computed( () => allCardsCount.value === MAX_MAIN_DECK );

const allCardsAreSameColorsAsCommander = computed(() => {
  if (!props.commanders[0]) return false;

  const commanderColors = props.commanders[0].CardFaces.flatMap(face => face.Colors);

  return !props.mainDeck.some(
    card => card.CardFaces.flatMap(face => face.Colors)
      .some(color => !commanderColors.includes(color))
  );
});

const allNonBasicLandCardsAreUnique = computed(() => {
  const filteredMainDeck = props.mainDeck.filter(
    card => card.CardFaces.every(face => !face.TypeLine.toLowerCase().includes("basic land")),
  );

  return (new Set( filteredMainDeck.map(card => card.OracleName) )).size === filteredMainDeck.length;
});
</script>

<template>
  <sl-card class="ValidationBar">
    <div class="validation-row">
      <p class="validation" :class="{ error: !commanderCountValid }">
        <strong>Commander:</strong> {{ commanders.length }}/{{ MAX_COMMANDERS }} card(s)
      </p>

      <p class="validation" :class="{ error: !commanderIsLegendaryCreature }">
        Commander is a legendary creature
      </p>

      <p class="validation" :class="{ error: !mainDeckValid }">
        <strong>Main deck:</strong> {{ allCardsCount }}/{{ MAX_MAIN_DECK }} card(s)
      </p>

      <p class="validation" :class="{ error: !allCardsAreSameColorsAsCommander }">
        Deck cards are same color as commander
      </p>

      <p class="validation" :class="{ error: !allNonBasicLandCardsAreUnique }">
        All cards are unique (except lands)
      </p>
    </div>
  </sl-card>
</template>

<style lang="scss" scoped>
.ValidationBar {
  width: 100%;

  p.validation {
      color: var(--sl-color-success-500);

    &.error {
      color: var(--sl-color-danger-500);
    }
  }

  div.validation-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>
