<template>
  <div class="container mt-4">
    <h2 class="mb-4">Cuentas</h2>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <div v-else>
      <router-link to="/accounts/new" class="btn btn-primary mb-3">Agregar Nueva Cuenta</router-link>
      <!-- Desktop View (List) -->
      <div class="d-none d-md-block">
        <ul class="list-group">
          <li v-for="account in accounts" :key="account.id" class="list-group-item d-flex justify-content-between align-items-center">
            {{ account.name }}
            <span v-if="account.is_credit_card" class="badge bg-info ms-2">Tarjeta de Crédito</span>
            <div>
              <router-link :to="`/accounts/${account.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
              <router-link :to="`/accounts/${account.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
              <button @click="deleteAccount(account.id)" class="btn btn-danger btn-sm">Eliminar</button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Mobile View (Cards) -->
      <div class="d-block d-md-none">
        <div class="row">
          <div v-for="account in accounts" :key="account.id" class="col-12 mb-3">
            <div class="card">
              <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="card-title">{{ account.name }}</h5>
                  <span v-if="account.is_credit_card" class="badge bg-info">Tarjeta de Crédito</span>
                </div>
                <div>
                  <router-link :to="`/accounts/${account.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
                  <router-link :to="`/accounts/${account.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
                  <button @click="deleteAccount(account.id)" class="btn btn-danger btn-sm">Eliminar</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useAccountStore } from '../../stores/account';

const accountStore = useAccountStore();
const accounts = computed(() => accountStore.accounts);
const loading = computed(() => accountStore.loading);
const error = computed(() => accountStore.error);

onMounted(() => {
  accountStore.fetchAccounts();
});

const deleteAccount = async (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar esta cuenta?')) {
    try {
      await accountStore.deleteAccount(id);
      accountStore.fetchAccounts(); // Re-fetch accounts after deletion
    } catch (err) {
      console.error('No se pudo eliminar la cuenta:', err);
      alert('No se pudo eliminar la cuenta.');
    }
  }
};
</script>