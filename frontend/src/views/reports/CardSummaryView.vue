<template>
  <div class="summary-container mt-2 mb-4 px-2" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <h2 class="h5 text-center mb-3 fw-bold text-dark">Resumen de Tarjetas</h2>

    <!-- Filtros Modernizados (Acordeón) -->
    <div class="card border-0 shadow-sm rounded-3 mb-3 overflow-hidden">
      <div class="card-header bg-white border-0 py-2 px-3 d-flex justify-content-between align-items-center" @click="showFilters = !showFilters" style="cursor: pointer;">
        <h6 class="mb-0 fw-bold text-secondary small"><i class="bi bi-funnel me-1"></i> Filtros del Informe</h6>
        <i class="bi text-muted small" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </div>
      <div v-show="showFilters" class="card-body p-3 bg-light-subtle border-top">
        <div class="row g-2">
          <div class="col-md-6">
            <label class="smaller text-muted fw-bold mb-1">Tarjeta</label>
            <select class="form-select form-select-sm border-0 shadow-sm" v-model="selectedCardId">
              <option value="">Todas las Tarjetas</option>
              <option v-for="card in cards" :key="card.id" :value="card.id">{{ card.name }}</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="smaller text-muted fw-bold mb-1">Mes</label>
            <select class="form-select form-select-sm border-0 shadow-sm" v-model="selectedMonth">
              <option v-for="(monthName, index) in months" :key="index" :value="index + 1">{{ monthName }}</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="smaller text-muted fw-bold mb-1">Año</label>
            <select class="form-select form-select-sm border-0 shadow-sm" v-model="selectedYear">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="col-12 text-end mt-2">
            <button @click="fetchCardSummary" class="btn btn-sm btn-primary rounded-2 px-4 fw-bold smaller shadow-sm">
              <i class="bi bi-search me-1"></i> Buscar
            </button>
          </div>
        </div>
      </div>
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
      <div v-if="cardSummary.length === 0" class="alert alert-info py-2 small text-center rounded-3 border-0 shadow-sm" role="alert">
        <i class="bi bi-info-circle me-1"></i> No hay movimientos para los filtros seleccionados.
      </div>
      <div v-else>
        
        <!-- Lista de Movimientos de Tarjeta -->
        <div class="card-summary-list">
          <div v-for="item in cardSummary" :key="item.id" class="mb-2">
            <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
              <div class="card-body p-2 px-3">
                <div class="d-flex align-items-center gap-2">
                  
                  <!-- Info Principal -->
                  <div class="flex-grow-1 min-width-0">
                    <div class="d-flex flex-column justify-content-start align-items-start">
                      <div class="w-100 overflow-hidden">
                        <span class="fw-bold text-dark d-block text-truncate mb-0" style="max-width: 100%;" :title="item.description">
                          {{ item.description }}
                        </span>
                      </div>
                      <span class="fw-bold text-danger fs-6">
                        -{{ formatCurrency(item.amount) }}
                      </span>
                    </div>
                    <div class="d-flex align-items-center smaller text-muted mt-1 flex-wrap">
                      <span class="me-2 text-nowrap"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(item.date) }}</span>
                      <span class="text-truncate" style="max-width: 150px;"><i class="bi bi-wallet2 me-1"></i>{{ item.account_name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Compacto -->
        <div class="card border-0 shadow-sm rounded-3 mt-4 bg-dark text-white p-3 d-flex justify-content-between align-items-center">
          <h6 class="mb-0 fw-bold small">TOTAL CONSUMOS:</h6>
          <h5 class="mb-0 fw-bold fs-5">{{ formatCurrency(totalAmount) }}</h5>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAccountStore } from '@/stores/account';
import { useExpenseStore } from '@/stores/expense';

const accountStore = useAccountStore();
const expenseStore = useExpenseStore();

const showFilters = ref(false);
const cards = computed(() => accountStore.accounts.filter(acc => acc.is_credit_card));

const selectedCardId = ref('');
const selectedMonth = ref(new Date().getMonth() + 1);
const selectedYear = ref(new Date().getFullYear());

const loading = ref(false);
const error = ref(null);

const months = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  const yearsArray = [];
  for (let i = currentYear; i >= currentYear - 5; i--) {
    yearsArray.push(i);
  }
  return yearsArray;
});

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '';
  return value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' $';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const pureDate = dateStr.includes('T') ? dateStr.split('T')[0] : dateStr;
  const [year, month, day] = pureDate.split('-');
  return new Date(year, month - 1, day).toLocaleDateString();
};

const cardSummary = computed(() => {
  // Solo incluir gastos cuyas cuentas sean tarjetas de crédito
  return expenseStore.expenses
    .filter(expense => {
      const account = accountStore.accounts.find(acc => acc.id === expense.account_id);
      return account ? account.is_credit_card : false;
    })
    .map(expense => ({
      ...expense,
      account_name: accountStore.accounts.find(acc => acc.id === expense.account_id)?.name || 'N/A'
    }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));
});

const totalAmount = computed(() => {
  return cardSummary.value.reduce((sum, item) => sum + item.amount, 0);
});

const fetchCardSummary = async () => {
  loading.value = true;
  error.value = null;
  try {
    await expenseStore.fetchExpenses(
      0,
      200, 
      null,
      null,
      null,
      selectedCardId.value === '' ? null : selectedCardId.value,
      null,
      null,
      selectedMonth.value,
      selectedYear.value
    );
    await accountStore.fetchAccounts();
  } catch (err) {
    error.value = err;
    console.error('Error fetching card summary:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await accountStore.fetchAccounts();
  fetchCardSummary();
});
</script>

<style scoped>
.summary-container {
  width: 100%;
  overflow-x: hidden;
}

.smaller {
  font-size: 0.75rem;
}

.min-width-0 {
  min-width: 0;
}

.bg-light-subtle {
  background-color: rgba(0, 0, 0, 0.02) !important;
}

.card {
  border: 1px solid rgba(0,0,0,0.05) !important;
  width: 100%;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
