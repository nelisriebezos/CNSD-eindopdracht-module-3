<script setup lang="ts">
import "@shoelace-style/shoelace/dist/components/input/input";
import '@shoelace-style/shoelace/dist/components/card/card';
import type SlInput from "@shoelace-style/shoelace/dist/components/input/input";

import { ref, type Ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const email = ref('');
const password = ref('');

const emailInput: Ref<null> | Ref<HTMLObjectElement> = ref(null);
const passwordInput: Ref<null> | Ref<HTMLObjectElement> = ref(null);

const errorMessage = ref('');

const router = useRouter();

function login() {
  if (!isFormValid()) {
    return
  }
  sendData(email.value, password.value)
      .then((response) => {
        if (response.ok) {
          response.json()
            .then((body) => {
              storeSessionToken(body.token);

              const returnUrl = !!router.currentRoute.value.query.redirect_url
                ? router.currentRoute.value.query.redirect_url as string
                : "/collection";

              router.push(returnUrl);
            });
        } else if (response.status === 403) {
          showErrorMessage('Invalid credentials!')
        } else if (response.status === 400) {
          showErrorMessage('Please verify your account with the confirmation email!')
        } else {
          showErrorMessage('Something went wrong!');
        }
      });
}

function storeSessionToken(token: string) {
  localStorage.setItem("jwtToken", `Bearer ${token}`);
}

function showErrorMessage(error: string) {
  console.error(error);
  errorMessage.value = error;
}

function isFormValid(): boolean {
  // @ts-ignore typescript detecteerd het bestaan van getAttribute() niet
  if (emailInput.value.getAttribute('data-invalid') === '') {
    return false;
  }
  // @ts-ignore typescript detecteerd het bestaan van getAttribute() niet
  if (passwordInput.value.getAttribute('data-invalid') === '') {
    return false;
  }

  return true;
}

async function sendData(email: string, password: string) {
  return await fetch("/api/users/login", {
        "method": "post",
        "mode": "no-cors", //Kan potentieel een pijnpunt zijn. Als er cors problemen zijn kijk hier.
        "headers": {
          "Content-Type": "application/json"
        },
        "body": JSON.stringify({
          "email": email,
          "password": password
        })
      }
  )
}
</script>

<template>
  <div class="container">
    <sl-card class="login-card">
      <h1>Login</h1>
      <form id="login-form" @submit.prevent.submit="login">
        <sl-input label="Email" id="email" type="email" placeholder="Email" required v-model="email"
                  ref="emailInput" data-test-id="email"></sl-input>
        <sl-input label="Password" id="password" password-toggle placeholder="Password" type="password" required
                  v-model="password" ref="passwordInput" data-test-id="password"></sl-input>
        <p class="error" id="error-message" v-if="errorMessage">{{ errorMessage }}</p>
        <sl-button id="login" class="button" variant="primary" type="submit" data-test-id="submit">Login</sl-button>
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
  color: var(--sl-color-red-200);
}
</style>
