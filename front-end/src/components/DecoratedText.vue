<script setup lang="ts">
const {text} = defineProps<{ text: string }>();

function getIconUrl(t: string): string {
  let image_name: string
  switch (t.replace("/", "")) {
    case "½":
      image_name = "HALF";
      break;
    case "∞":
      image_name = "INFINITY";
      break;
    default:
      image_name = t
  }
  return `/icons/${image_name}.svg`
}

function getIconDescription(t: string): string {
  switch (t) {
    case "T":
      return "tap this permanent";
    case "Q":
      return "untap this permanent";
    case "E":
      return "an energy counter";
    case "PW":
      return "planeswalker";
    case "CHAOS":
      return "chaos";
    case "A":
      return "an acorn counter";
    case "TK":
      return "a ticket counter";
    case "X":
      return "X generic mana";
    case "Y":
      return "Y generic mana";
    case "Z":
      return "Z generic mana";
    case "0":
      return "zero mana";
    case "½":
      return "one-half generic mana";
    case "1":
      return "one generic mana";
    case "2":
      return "two generic mana";
    case "3":
      return "three generic mana";
    case "4":
      return "four generic mana";
    case "5":
      return "five generic mana";
    case "6":
      return "six generic mana";
    case "7":
      return "seven generic mana";
    case "8":
      return "eight generic mana";
    case "9":
      return "nine generic mana";
    case "10":
      return "ten generic mana";
    case "11":
      return "eleven generic mana";
    case "12":
      return "twelve generic mana";
    case "13":
      return "thirteen generic mana";
    case "14":
      return "fourteen generic mana";
    case "15":
      return "fifteen generic mana";
    case "16":
      return "sixteen generic mana";
    case "17":
      return "seventeen generic mana";
    case "18":
      return "eighteen generic mana";
    case "19":
      return "nineteen generic mana";
    case "20":
      return "twenty generic mana";
    case "100":
      return "one hundred generic mana";
    case "1000000":
      return "one million generic mana";
    case "∞":
      return "infinite generic mana";
    case "W/U":
      return "one white or blue mana";
    case "W/B":
      return "one white or black mana";
    case "B/R":
      return "one black or red mana";
    case "B/G":
      return "one black or green mana";
    case "U/B":
      return "one blue or black mana";
    case "U/R":
      return "one blue or red mana";
    case "R/G":
      return "one red or green mana";
    case "R/W":
      return "one red or white mana";
    case "G/W":
      return "one green or white mana";
    case "G/U":
      return "one green or blue mana";
    case "B/G/P":
      return "one black mana, one green mana, or 2 life";
    case "B/R/P":
      return "one black mana, one red mana, or 2 life";
    case "G/U/P":
      return "one green mana, one blue mana, or 2 life";
    case "G/W/P":
      return "one green mana, one white mana, or 2 life";
    case "R/G/P":
      return "one red mana, one green mana, or 2 life";
    case "R/W/P":
      return "one red mana, one white mana, or 2 life";
    case "U/B/P":
      return "one blue mana, one black mana, or 2 life";
    case "U/R/P":
      return "one blue mana, one red mana, or 2 life";
    case "W/B/P":
      return "one white mana, one black mana, or 2 life";
    case "W/U/P":
      return "one white mana, one blue mana, or 2 life";
    case "2/W":
      return "two generic mana or one white mana";
    case "2/U":
      return "two generic mana or one blue mana";
    case "2/B":
      return "two generic mana or one black mana";
    case "2/R":
      return "two generic mana or one red mana";
    case "2/G":
      return "two generic mana or one green mana";
    case "P":
      return "one colored mana or two life";
    case "W/P":
      return "one white mana or two life";
    case "U/P":
      return "one blue mana or two life";
    case "B/P":
      return "one black mana or two life";
    case "R/P":
      return "one red mana or two life";
    case "G/P":
      return "one green mana or two life";
    case "HW":
      return "one-half white mana";
    case "HR":
      return "one-half red mana";
    case "W":
      return "one white mana";
    case "U":
      return "one blue mana";
    case "B":
      return "one black mana";
    case "R":
      return "one red mana";
    case "G":
      return "one green mana";
    case "C":
      return "one colorless mana";
    case "S":
      return "one snow mana";
    default:
      return ""
  }
}
</script>

<template>
  <p>
    <span>{{ text.split("{")[0] }}</span>
    <span v-for="textPart in text.split('{').splice(1)">
      <img
        :src="getIconUrl(textPart.slice(0, textPart.indexOf('}')))"
        :alt="`${getIconDescription(textPart.slice(0, textPart.indexOf('}')))} icon`"
        :title="getIconDescription(textPart.slice(0, textPart.indexOf('}')))"
      >
      {{ textPart.slice(textPart.indexOf('}') + 1) }}
    </span>
  </p>
</template>

<style scoped lang="scss">
img {
  height: 1em;
  cursor: help;
}
p {
  margin: 0;
}
</style>