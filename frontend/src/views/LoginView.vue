<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100 bg-light-subtle">
    <div class="card p-4 shadow-lg" style="width: 25rem;">
      <h1 class="card-title text-center mb-4">Login</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="emailInput" class="form-label">Email address</label>
          <input type="email" class="form-control" id="emailInput" v-model="email" required />
        </div>
        <div class="mb-3">
          <label for="passwordInput" class="form-label">Password</label>
          <input type="password" class="form-control" id="passwordInput" v-model="password" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
      <p v-if="authStore.error" class="text-danger mt-3 text-center">{{ authStore.error }}</p>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { mapStores } from 'pinia'

export default {
  data() {
    return {
      email: '',
      password: '',
    };
  },
  computed: {
    ...mapStores(useAuthStore)
  },
  methods: {
    async handleLogin() {
      await this.authStore.login(this.email, this.password)
      if (!this.authStore.error) {
        this.$router.push('/home')
      }
    },
  },
};
</script>
