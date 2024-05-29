<script setup lang="ts">
import { onDeactivated, ref, toRefs } from 'vue';
import DeckSearchView from './DeckSearchView.vue';
import CardAddOracleView from './CardAddOracleView.vue';
import { useRoute } from 'vue-router';
import DeckAddPrintView from './DeckAddPrintView.vue'

const route = useRoute();

const props = defineProps<{
    location: string
}>()
const emit = defineEmits(['cardAdded'])

const inactive = ref(true);
const selecting = ref(false);
const print = ref(false);

const selectedCard = ref();
const selectedPrint = ref();

function activate() {
    inactive.value = false;
}

function deactivate() {
    inactive.value = true;
    selecting.value = false;
}

function cardClicked(event : any){
    selectedCard.value = event['card']
    selecting.value = true;
}

function selectPrint(event : any) {
    print.value = true;
    selectedPrint.value = event['printId'];
}

function unselectPrint() {
    print.value = false;
    selectedPrint.value = "";
}

function backToSearch(){
    selecting.value = false;
}

function addCardToDeck(event : any){
    let toSend = {
        'cardOracle' : event['oracleId'],
        'cardLocation' : event['location'],
        'cardPrintId' : event['printId'],
        'cardInstanceId' : event['cardInstance']
    }
    const token = localStorage.getItem("jwtToken");
    if (!token) return;

    fetch(`/api/decks/${route.params["deck_id"]}/cards/`,
    {
        method: "POST",
        headers: {Authorization: token},
        body: JSON.stringify(toSend)
    }).then(
        (response) =>
        {
            if (response.ok) {
                    response.json().then(
                        (body) => {
                            confirmCardAdded(body['deck_card_id'])
                        }
                )
            } else {
                console.error(response)
            }
        }
    )
}

function confirmCardAdded(deckCardId : string){
    emit('cardAdded', {'deckCardId' : deckCardId, 'location' : props.location})
    deactivate();
}
</script>

<template>
<div class="inactive-box" v-if="inactive.valueOf()" @click="activate">
    <!-- WHEN INACTIVE -->
    <div class="plus"></div>
</div>
<div v-if="!inactive.valueOf()">
    <!-- WHEN ACTIVE -->
    <div class="hide-box" @click="deactivate">Hide</div>

    <DeckSearchView v-bind:location="props.location" v-on:card-clicked="cardClicked" v-if="!selecting.valueOf()"></DeckSearchView>

    <CardAddOracleView v-if="selecting.valueOf() && !print.valueOf()" v-bind:card="selectedCard.valueOf()" v-bind:location="location" v-on:add-card="addCardToDeck" v-on:switch-to-print="selectPrint" v-on:back="backToSearch"></CardAddOracleView>
    <DeckAddPrintView v-if="selecting.valueOf() && print.valueOf()" v-bind:card="selectedCard.valueOf()" v-bind:location="location" v-bind:printId="selectedPrint.valueOf()" v-on:add-card="addCardToDeck" v-on:unselect-print="unselectPrint"></DeckAddPrintView>
</div>
</template>

<style scoped lang="scss">
.inactive-box{
    background-color: rgba(180, 180, 180, 0.329);
    width: 100%;
    height: 70px;
    position: relative;
}

.inactive-box:hover {
    background-color: rgba(180, 180, 180, 0.671);
}

.hide-box{
    background-color: rgba(180, 180, 180, 0.329);
    width: 100%;
    position: relative;
    text-align: center;
}

.hide-box:hover{
    background-color: rgba(180, 180, 180, 0.671);
}

.plus {
    --b: 4px; /* the thickness */
    aspect-ratio: 1;
    height: 80%;
    border: none;
    margin: 0;
    background:
        conic-gradient(from 90deg at var(--b) var(--b),#ffffff00 90deg,#000 0) 
        calc(100% + var(--b)/2) calc(100% + var(--b)/2)/
        calc(50%  + var(--b))   calc(50%  + var(--b));
    position: absolute;
    top: 10%;
    right: 45%;
}
</style>
