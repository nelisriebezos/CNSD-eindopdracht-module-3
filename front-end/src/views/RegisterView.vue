<script setup lang="ts">
import "@shoelace-style/shoelace/dist/components/input/input";
import '@shoelace-style/shoelace/dist/components/card/card';
import type SlInput from "@shoelace-style/shoelace/dist/components/input/input";

import { ref, type Ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const emailInput : Ref<null> | Ref<HTMLObjectElement> = ref(null);
const passwordInput : Ref<null> | Ref<HTMLObjectElement> = ref(null);
const passwordConfirmInput : Ref<null> | Ref<HTMLObjectElement> = ref(null);

const errorMessage = ref('');

const router = useRouter();

function register(){
    if (!isFormValid()) {
        return
    }
    sendData(email.value, password.value)
        .then((response) => {
            if (response.status === 409){
                showErrorMessage("This email address has already been registered!");
            } else if (response.ok) {
                alert("We have send you an email to verify your email address.");
                router.push("/login");
            } else if (response.status === 400) {
                alert(response.json().then((response) => showErrorMessage(response.error)))
            } else {
                showErrorMessage(`Something went wrong: \n${response.statusText}`);
            }
        });
}

function showErrorMessage(error : string){
    console.log(error);
    errorMessage.value = error;
}

function handleInput(){
    if (passwordConfirmInput.value === null || passwordInput.value === null) {
        throw "Where did my fields go?"
    }

    // @ts-ignore typescript zeikt over dat hij niet weet dat het html element een value heeft
    confirmPassword.value = passwordConfirmInput.value.value;
    // @ts-ignore typescript zeikt over dat hij niet weet dat het html element een value heeft
    password.value = passwordInput.value.value;

    if (password.value.length >= 8) {
        passwordInput.value.setCustomValidity(''); //Empty validity means it's valid
    } else {
        passwordInput.value.setCustomValidity('Password must be at least 8 characters long!')
        return //return so it can't be overwritten by other checks
    }

    //Checks if the passwords match
    if (password.value === confirmPassword.value) {
        passwordConfirmInput.value.setCustomValidity('');
    } else {
        passwordConfirmInput.value.setCustomValidity('Passwords must match!');
        return;
    }
}

function isFormValid() : boolean{
    // @ts-ignore typescript detecteerd het bestaan van getAttribute() niet
    if (emailInput.value.getAttribute('data-invalid') === ''){
        return false;
    }
    // @ts-ignore typescript detecteerd het bestaan van getAttribute() niet
    if (passwordInput.value.getAttribute('data-invalid') === ''){
        return false;
    }
    // @ts-ignore typescript detecteerd het bestaan van getAttribute() niet
    if (passwordConfirmInput.value.getAttribute('data-invalid') === ''){
        return false;
    }

    return true;
}

async function sendData(email : string, password : string){
    return await fetch("/api/users", {
        "method" : "post",
        "mode" : "cors",
        "headers" : {
            "Content-Type" : "application/json"
        },
        "body" : JSON.stringify({
            "email" : email,
            "password" : password
        })
    }
    )
}
</script>

<template>
<div class="container">
    <sl-card class="login-card">
    <h1>Register</h1>
    <form id="login-form" @submit.prevent.submit="register">
    <sl-input label="Email" data-test-id="email" id="email" type="email" placeholder="Email" required v-model="email" ref="emailInput"></sl-input>
    <sl-input label="Password" data-test-id="password" id="password" password-toggle placeholder="Password" type="password" required v-model="password" @sl-input="handleInput" ref="passwordInput"></sl-input>
    <sl-input label="Re-enter password" data-test-id="confirm" id="confirm" password-toggle placeholder="Confirm password" type="password" required v-model="confirmPassword" @sl-input="handleInput" ref="passwordConfirmInput"></sl-input>
    <p class="error" id="error-message" v-if="errorMessage">{{ errorMessage }}</p>
    <sl-button data-test-id="submit" id="submit" class="button" variant="primary" type="submit">Confirm</sl-button>
    <sl-button id="login" class="button" variant="neutral" @click="router.push('/login')">To login</sl-button>
</form>
</sl-card>
</div>

</template>

<!-- STYLE -->

<style scoped lang="scss">

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 5rem;
}

.button {
    width: 100%;
    margin-top: 1rem;
}

.error {
    color: var(--sl-color-red-200)
}

</style>