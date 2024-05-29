<script setup lang="ts">
import DecoratedText from "@/components/DecoratedText.vue";
import type {DeckCard} from "@/models/cardModels";
import { ref } from "vue";

const emit = defineEmits(['delete'])


const faceName = ref();
const manaCost = ref();
const oracleText = ref();
const image = ref();
const typeline = ref();
const colors = ref();
const borderColor = ref("black");
let faceNumber = 0;

const props = defineProps<{
  card: DeckCard
}>()

if (props.card.card_instance_id) {
    borderColor.value = "green";
}

setFace();

let red = 255;
let green = 255;
let blue = 255;
let alpha = 0.22;


function flip(){
    faceNumber++;
    if (faceNumber > props.card.CardFaces.length-1){
        faceNumber = 0
    }
    setFace();
}

function deleteCard(){
    if (confirm("Are you sure you want to delete: \"" + props.card.OracleName + "\"?")){
        emit('delete', props.card);
    }
}

function setFace(){
    faceName.value = props.card.CardFaces[faceNumber].FaceName;
    manaCost.value = props.card.CardFaces[faceNumber].ManaCost;
    oracleText.value = props.card.CardFaces[faceNumber].OracleText;
    image.value = props.card.CardFaces[faceNumber].ImageUrl;
    typeline.value = props.card.CardFaces[faceNumber].TypeLine;
    colors.value = props.card.CardFaces[faceNumber].Colors;
}

</script>

<template>
    <div class="card" v-bind:style="{ 'background-image': 'url(' + image + ')', 
    'box-shadow': 'inset 0 0 0 1000px rgba(' + red + ',' + green + ',' + blue + ',' + alpha + ')'}">
        <span class="titlebox">
            <p><span class="title">{{props.card.OracleName}}</span><DecoratedText :text="manaCost"></DecoratedText></p>
            <p><span>{{ typeline }}</span></p>
            <button v-if="props.card.CardFaces.length > 1" @click="flip">flip</button>
        </span>
        <div class="seperator"></div>
        <span class="descriptionbox" :title="oracleText">
            <p>
                <DecoratedText :text="oracleText"></DecoratedText>
            </p>
        </span>
        <button @click="deleteCard()">x</button>
    </div>
</template>

<style scoped lang="scss">
.card {
    padding: 10px;
    padding-top: 5px;
    padding-bottom: 5px;
    border-radius: 5px;

    background-position-y: 15%;
    background-position-x: 50%;
    background-size: 119% auto;

    min-width: 550px;
    max-width: 550px;
    display: inline-flex;
    height: 70px;
    border: 2px solid v-bind(borderColor);
}

p {
    line-height: 1;
    margin: 0px;
    text-shadow: 1px 0 #ffffff9c, -1px 0 #ffffff9c, 0 1px #ffffff9c, 0 -1px #ffffff9c,
             1px 1px #ffffff9c, -1px -1px #ffffff9c, 1px -1px #ffffff9c, -1px 1px #ffffff9c;
}

.title {
    font-size: large;
    font-weight: bold;
    white-space: nowrap;
}

.titlebox {
    display: inline-block;
}

.descriptionbox {
    display: inline-block;
    text-wrap: balance;
    text-overflow: ellipsis;
    overflow:hidden;
}

.seperator {
    border-right: 1px solid black;
    width: 0px;
    border-radius: 1px;
    height: 100%;
    margin: 7px;
    margin-right: 15px;
    margin-top: 0;
    margin-bottom: 0;
}
</style>