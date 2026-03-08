<template>
  <div class="container mt-2 mb-4 px-2" style="max-width: 600px;">
    <h2 class="h5 text-center mb-3 fw-bold text-dark">Cuentas</h2>
    
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small" role="alert">
      Error: {{ error.message }}
    </div>
    
    <div v-else>
      <div class="d-grid mb-3">
        <router-link to="/accounts/new" class="btn btn-primary fw-semibold rounded-3 shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> Agregar Nueva Cuenta
        </router-link>
      </div>

      <!-- Unified View for Accounts -->
      <div class="account-list">
        <div v-for="account in accounts" :key="account.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
            <div class="card-body p-2">
              <div class="d-flex align-items-center flex-wrap gap-2">
                
                <!-- Icono de Cuenta -->
                <div class="d-flex align-items-center me-2 text-primary" style="width: 1.2rem;">
                  <i class="bi" :class="account.is_credit_card ? 'bi-credit-card-fill' : 'bi-wallet2-fill'"></i>
                </div>

                <!-- Nombre y Badge -->
                <div class="flex-grow-1 min-width-0 d-flex flex-column align-items-start">
                  <span class="fw-medium text-dark d-block text-truncate w-100" :title="account.name">
                    {{ account.name }}
                  </span>
                  <span v-if="account.is_credit_card" class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 rounded-pill mt-1" style="font-size: 0.65rem;">
                    Tarjeta de Crédito
                  </span>
                </div>

                <!-- Acciones -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/accounts/${account.id}`" class="btn btn-light-blue btn-sm border-0 rounded-2 me-1" title="Ver">
                    <i class="bi bi-eye text-primary"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-primary">Ver</span>
                  </router-link>
                  
                  <router-link :to="`/accounts/${account.id}/edit`" class="btn btn-light-warning btn-sm border-0 rounded-2 me-1" title="Editar">
                    <i class="bi bi-pencil text-warning-emphasis"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-warning-emphasis">Editar</span>
                  </router-link>
                  
                  <button @click="deleteAccount(account.id)" class="btn btn-light-danger btn-sm border-0 rounded-2" title="Eliminar">
                    <i class="bi bi-trash text-danger"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-danger">Borrar</span>
                  </button>
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

<style scoped>
.account-list {
  margin-bottom: 2rem;
}

.smaller {
  font-size: 0.75rem;
  font-weight: 600;
}

.min-width-0 {
  min-width: 0;
}

/* Colores de botones sutiles similares a categorías/login */
.btn-light-blue {
  background-color: #e7f1ff;
}
.btn-light-blue:hover {
  background-color: #cfe2ff;
}

.btn-light-warning {
  background-color: #fff3cd;
}
.btn-light-warning:hover {
  background-color: #ffecb5;
}

.btn-light-danger {
  background-color: #f8d7da;
}
.btn-light-danger:hover {
  background-color: #f1aeb5;
}

.action-buttons .btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
}

/* Evitar que los botones se achiquen demasiado */
.action-buttons {
  flex-shrink: 0;
}

/* Estilo de la tarjeta */
.card {
  transition: transform 0.1s ease-in-out;
  border: 1px solid rgba(0,0,0,0.05) !important;
}
</style>
