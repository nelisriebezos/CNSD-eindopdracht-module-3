<script setup lang="ts">
  import {useRoute, useRouter} from "vue-router";
  import {ref, watch} from "vue";

  function isUserSignedIn() {
    return localStorage.getItem("jwtToken") != null;
  }

  const router = useRouter();
  const route = useRoute();
  const userSignedIn = ref<boolean>(isUserSignedIn());

  watch(() => route.path, () => {
    userSignedIn.value = isUserSignedIn();
    if (!userSignedIn.value && !["/login", "/register"].includes(route.path)) {
      router.push("/login");
    }
  })

  function logOut() {
    localStorage.removeItem("jwtToken");
    userSignedIn.value = false;
    router.push("/login");
  }
</script>

<template>
  <header id="title-wrapper">
    <h1>Dragons MTG Card Collection System</h1>
    <img
        src="/mtg_logo.png"
        alt="MTG Logo"
    >
    <nav v-if="userSignedIn">
      <router-link to="/collection">Collection</router-link>
      <router-link to="/decks">Decks</router-link>
      <router-link to="/search">Search</router-link>
      <button id="logout-button" @click="logOut">Logout</button>
    </nav>
    <nav v-else>
      <router-link to="/register">Register</router-link>
      <router-link to="/login">Login</router-link>
    </nav>
  </header>
</template>

<style scoped lang="scss">
#title-wrapper {
  display: flex;
  margin: 1rem 2rem;
  align-items: center;

  h1 {
    margin: 0;
  }
  img {
    height: 3em;
  }
  nav {
    margin-left: auto;
    display: flex;
    gap: 1rem;
  }
  #logout-button {
    all: unset;
    text-decoration: underline;
    cursor: pointer;
  }
}
</style>
