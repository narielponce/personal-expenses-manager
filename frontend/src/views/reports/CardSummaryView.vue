<template>
  <div class="summary-container mt-2 mb-4 px-2" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Resumen de <span class="text-primary">Tarjetas</span></h5>
      <p class="text-muted tiny mb-0">Consumos y cuotas por período</p>
    </div>

    <!-- Filtros Modernizados estilo Home -->
    <div class="card border-0 shadow-sm rounded-4 mb-3 overflow-hidden">
      <!-- Drag Handle -->
      <div class="d-flex justify-content-center pt-2 pb-1" @click="showFilters = !showFilters" style="cursor: pointer;">
        <div class="drag-handle"></div>
      </div>

      <div class="card-header bg-white border-0 py-1 px-3 d-flex justify-content-between align-items-center" @click="showFilters = !showFilters" style="cursor: pointer;">
        <h6 class="mb-0 fw-bold text-secondary smaller"><i class="bi bi-funnel me-1"></i> Filtros</h6>
        <i class="bi text-muted smaller" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </div>
      <div v-show="showFilters" class="card-body p-3 bg-white">
        <div class="row g-2">
          <div class="col-md-6">
            <label class="tiny text-muted fw-bold mb-1 text-uppercase">Tarjeta</label>
            <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="selectedCardId">
              <option value="">Todas las Tarjetas</option>
              <option v-for="card in cards" :key="card.id" :value="card.id">{{ card.name }}</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="tiny text-muted fw-bold mb-1 text-uppercase">Mes</label>
            <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="selectedMonth">
              <option v-for="(monthName, index) in months" :key="index" :value="index + 1">{{ monthName }}</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="tiny text-muted fw-bold mb-1 text-uppercase">Año</label>
            <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="selectedYear">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="col-12 text-end mt-2">
            <button @click="fetchCardSummary" class="btn btn-sm btn-primary rounded-pill px-4 fw-bold tiny shadow-sm">
              BUSCAR
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
      <div v-if="cardSummary.length === 0" class="alert alert-info py-2 tiny text-center rounded-4 border-0 shadow-sm" role="alert">
        <i class="bi bi-info-circle me-1"></i> No hay movimientos para estos filtros.
      </div>
      <div v-else>
        
        <!-- Lista de Movimientos de Tarjeta -->
        <div class="card-summary-list">
          <div v-for="item in cardSummary" :key="item.id" class="mb-2">
            <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
              <div class="card-body p-2 px-3">
                <div class="d-flex align-items-center gap-2">
                  <!-- Info Principal -->
                  <div class="flex-grow-1 min-width-0">
                    <!-- Primer Renglón: Descripción -->
                    <div class="min-width-0 overflow-hidden">
                      <span class="fw-bold text-dark d-block text-truncate mb-0 smaller" :title="item.description">
                        {{ item.description }}
                      </span>
                    </div>
                    <!-- Segundo Renglón: Fecha e Importe -->
                    <div class="d-flex justify-content-between align-items-center mt-1">
                      <span class="tiny text-muted text-nowrap">
                        <i class="bi bi-calendar3 me-1"></i>{{ formatDate(item.date) }}
                      </span>
                      <span class="fw-bold text-danger tiny">
                        {{ formatCurrency(item.amount) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Compacto estilo Home -->
        <div class="card border-0 bg-primary text-white rounded-4 shadow-sm p-3 mt-4 d-flex justify-content-between align-items-center">
          <span class="tiny opacity-75 fw-bold text-uppercase">Total Consumos</span>
          <h5 class="fw-bold mb-0">{{ formatCurrency(totalAmount) }}</h5>
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
  return new Intl.NumberFormat('es-ES', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2, 
    useGrouping: true 
  }).format(Number(value)) + ' $';
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

.user-header {
  border-left: 4px solid #0d6efd;
  padding-left: 12px;
}

.drag-handle {
  width: 36px;
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  position: relative;
}

.drag-handle::before, .drag-handle::after {
  content: "";
  position: absolute;
  width: 4px;
  height: 4px;
  background-color: #e9ecef;
  border-radius: 50%;
  top: 0;
}
.drag-handle::before { left: -8px; }
.drag-handle::after { right: -8px; }

.smaller {
  font-size: 0.75rem;
}

.tiny {
  font-size: 0.65rem;
}

.min-width-0 {
  min-width: 0;
}

.card {
  width: 100%;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}
</style>
