<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 650px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Gestión de <span class="text-primary">Cuentas y Saldos</span></h5>
      <p class="text-muted tiny mb-0">Control de dinero disponible, descubiertos y tarjetas</p>
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
      <!-- Resumen Superior de Liquidez y Deuda -->
      <div class="row g-2 mb-3">
        <div class="col-6">
          <div class="card border-0 shadow-sm rounded-4 p-3 h-100" :class="totalLiquidity < 0 ? 'bg-danger text-white' : 'bg-primary text-white'">
            <div class="d-flex justify-content-between align-items-center">
              <span class="tiny opacity-75 fw-bold text-uppercase">Disponible Líquido</span>
              <i class="bi bi-wallet2 opacity-75 tiny"></i>
            </div>
            <h5 class="fw-bold mb-0 mt-1">{{ formatCurrency(totalLiquidity) }}</h5>
            <span v-if="totalLiquidity < 0" class="badge bg-white text-danger fw-bold mt-1 tiny text-uppercase" style="width: fit-content;">
              Descubierto Total
            </span>
            <span v-else class="tiny opacity-75 mt-1">Efectivo, bancos y billeteras</span>
          </div>
        </div>

        <div class="col-6">
          <div class="card border-0 shadow-sm rounded-4 p-3 h-100 bg-white border">
            <div class="d-flex justify-content-between align-items-center">
              <span class="tiny text-muted fw-bold text-uppercase">Deuda en Tarjetas</span>
              <i class="bi bi-credit-card-2-front text-muted tiny"></i>
            </div>
            <h5 class="fw-bold mb-0 mt-1 text-danger">{{ formatCurrency(totalCreditDebt) }}</h5>
            <span class="tiny text-muted mt-1">Consumos pendientes de pago</span>
          </div>
        </div>
      </div>

      <!-- Botón Nueva Cuenta y Transferir -->
      <div class="row g-2 mb-3">
        <div class="col-7">
          <router-link to="/accounts/new" class="btn btn-primary fw-bold rounded-pill shadow-sm py-2 w-100">
            <i class="bi bi-plus-lg me-1"></i> NUEVA CUENTA
          </router-link>
        </div>
        <div class="col-5">
          <router-link to="/expenses/new?type=transfer" class="btn btn-outline-primary fw-bold rounded-pill shadow-sm py-2 w-100">
            <i class="bi bi-arrow-left-right me-1"></i> TRANSFERIR
          </router-link>
        </div>
      </div>

      <!-- Lista de Cuentas -->
      <div class="account-list">
        <div v-for="account in accountsWithBalances" :key="account.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-4 overflow-hidden" :class="{ 'border-start border-4 border-danger': account.is_overdrawn }">
            <div class="card-body p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                
                <!-- Icono Tipo -->
                <div class="flex-shrink-0">
                  <div 
                    class="rounded-circle d-flex align-items-center justify-content-center" 
                    :class="account.is_credit_card ? 'bg-primary-subtle text-primary' : (account.is_overdrawn ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success')" 
                    style="width: 36px; height: 36px;"
                  >
                    <i class="bi" :class="account.is_credit_card ? 'bi-credit-card-fill' : 'bi-bank2'"></i>
                  </div>
                </div>

                <!-- Info Principal -->
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="min-width-0 overflow-hidden">
                      <span class="fw-bold text-dark d-block text-truncate mb-0 smaller" :title="account.name">
                        {{ account.name }}
                      </span>
                      <div class="d-flex align-items-center gap-1 tiny text-muted mt-0">
                        <span v-if="account.is_credit_card" class="text-primary fw-bold text-uppercase" style="font-size: 0.58rem;">
                          <i class="bi bi-star-fill me-1"></i>Tarjeta de Crédito
                        </span>
                        <span v-else class="text-uppercase" style="font-size: 0.58rem;">
                          <i class="bi bi-cash-stack me-1"></i>Bancaria / Débito
                        </span>

                        <span v-if="account.is_overdrawn && !account.is_credit_card" class="badge bg-danger text-white fw-bold px-1 py-0 ms-1" style="font-size: 0.55rem;">
                          DESCUBIERTO
                        </span>
                      </div>
                    </div>

                    <!-- Saldo Actual -->
                    <div class="text-end ps-2 flex-shrink-0">
                      <div 
                        class="fw-bold smaller" 
                        :class="account.is_overdrawn ? 'text-danger' : (account.current_balance > 0 ? 'text-success' : 'text-dark')"
                      >
                        {{ formatCurrency(account.current_balance) }}
                      </div>
                      <div class="tiny text-muted" style="font-size: 0.6rem;">
                        <span v-if="account.is_credit_card">Saldo tarjeta</span>
                        <span v-else-if="account.is_overdrawn" class="text-danger fw-bold">En descubierto</span>
                        <span v-else>Saldo actual</span>
                      </div>
                    </div>
                  </div>

                  <!-- Desglose compacto de movimientos -->
                  <div class="d-flex align-items-center gap-2 tiny text-muted mt-1 pt-1 border-top" style="font-size: 0.62rem;">
                    <span title="Saldo inicial configurado">Ini: {{ formatCurrency(account.initial_balance) }}</span>
                    <span>•</span>
                    <span class="text-success" title="Ingresos recibidos">+{{ formatCurrency(account.total_incomes) }}</span>
                    <span>•</span>
                    <span class="text-danger" title="Gastos realizados">-{{ formatCurrency(account.total_expenses) }}</span>
                    <template v-if="account.total_transfers_in > 0 || account.total_transfers_out > 0">
                      <span>•</span>
                      <span class="text-info" title="Transferencias netas">
                        ⇄ +{{ formatCurrency(account.total_transfers_in) }} / -{{ formatCurrency(account.total_transfers_out) }}
                      </span>
                    </template>
                  </div>
                </div>

                <!-- Acciones discretas -->
                <div class="d-flex flex-column align-items-center ms-auto action-buttons ps-1">
                  <router-link :to="`/accounts/${account.id}/edit`" class="btn btn-link text-warning p-1" title="Editar">
                    <i class="bi bi-pencil-square fs-6"></i>
                  </router-link>
                  
                  <button @click="deleteAccount(account.id)" class="btn btn-link text-danger p-1" title="Eliminar">
                    <i class="bi bi-trash fs-6"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="accountsWithBalances.length === 0" class="text-center py-4 bg-white rounded-4 shadow-sm">
          <i class="bi bi-wallet2 text-muted fs-1 opacity-25"></i>
          <p class="text-muted tiny mt-2">Aún no tienes cuentas registradas.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useAccountStore } from '../../stores/account';

const accountStore = useAccountStore();
const accountsWithBalances = computed(() => accountStore.accountsWithBalances);
const totalLiquidity = computed(() => accountStore.totalLiquidity);
const totalCreditDebt = computed(() => accountStore.totalCreditDebt);
const loading = computed(() => accountStore.loading);
const error = computed(() => accountStore.error);

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0,00';
  return new Intl.NumberFormat('es-AR', { 
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2, 
  }).format(Number(value));
};

onMounted(() => {
  accountStore.fetchAccountsWithBalances();
});

const deleteAccount = async (id) => {
  if (confirm('¿Estás seguro de que deseas eliminar esta cuenta?')) {
    try {
      await accountStore.deleteAccount(id);
      await accountStore.fetchAccountsWithBalances(); 
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
  font-size: 0.82rem;
}

.tiny {
  font-size: 0.68rem;
}

.min-width-0 {
  min-width: 0;
}

.bg-primary-subtle { background-color: #e7f1ff !important; }
.bg-success-subtle { background-color: #e8f7ee !important; }
.bg-danger-subtle { background-color: #fde8e8 !important; }

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
