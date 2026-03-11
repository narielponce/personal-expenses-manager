<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 600px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Gestión de <span class="text-primary">Cuentas</span></h5>
      <p class="text-muted tiny mb-0">Administra tus billeteras y tarjetas</p>
    </div>
    
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
        <router-link to="/accounts/new" class="btn btn-primary fw-bold rounded-pill shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> NUEVA CUENTA
        </router-link>
      </div>

      <!-- Lista de Cuentas estilo Home -->
      <div class="account-list">
        <div v-for="account in accounts" :key="account.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
            <div class="card-body p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                
                <!-- Icono Tipo simplificado -->
                <div class="flex-shrink-0">
                  <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-primary-subtle" style="width: 32px; height: 32px;">
                    <i class="bi tiny text-primary" :class="account.is_credit_card ? 'bi-credit-card-fill' : 'bi-wallet2'"></i>
                  </div>
                </div>

                <!-- Info Principal -->
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="min-width-0 overflow-hidden">
                      <span class="fw-bold text-dark d-block text-truncate mb-0 smaller" :title="account.name">
                        {{ account.name }}
                      </span>
                    </div>
                  </div>
                  <div class="d-flex align-items-center tiny text-muted mt-0">
                    <span v-if="account.is_credit_card" class="text-primary fw-bold text-uppercase" style="font-size: 0.55rem;">
                      <i class="bi bi-star-fill me-1"></i>Tarjeta de Crédito
                    </span>
                    <span v-else class="text-uppercase" style="font-size: 0.55rem;">
                      <i class="bi bi-cash-stack me-1"></i>Efectivo / Débito
                    </span>
                  </div>
                </div>

                <!-- Acciones discretas -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/accounts/${account.id}/edit`" class="btn btn-link text-warning p-1" title="Editar">
                    <i class="bi bi-pencil-square fs-5"></i>
                  </router-link>
                  
                  <button @click="deleteAccount(account.id)" class="btn btn-link text-danger p-1" title="Eliminar">
                    <i class="bi bi-trash fs-5"></i>
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
      accountStore.fetchAccounts(); 
    } catch (err) {
      console.error('No se pudo eliminar la cuenta:', err);
    }
  }
};
</script>

<style scoped>
.summary-container {
  width: 100%;
  overflow-x: hidden;
}

.user-header {
  border-left: 4px solid #0d6efd;
  padding-left: 12px;
}

.smaller {
  font-size: 0.75rem;
}

.tiny {
  font-size: 0.65rem;
}

.min-width-0 {
  min-width: 0;
}

.bg-primary-subtle { background-color: #e7f1ff !important; }

.action-buttons .btn-link {
  text-decoration: none;
  opacity: 0.7;
}
.action-buttons .btn-link:hover {
  opacity: 1;
}

.card {
  width: 100%;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}
</style>
