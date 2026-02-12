<template>
  <div class="container mt-4">
    <h2 class="mb-4">Resumen Tarjetas</h2>

    <div class="row mb-4">
      <div class="col-md-4">
        <label for="cardSelect" class="form-label">Seleccionar Tarjeta</label>
        <select id="cardSelect" class="form-select" v-model="selectedCardId">
          <option value="">Todas las Tarjetas</option>
          <option v-for="card in cards" :key="card.id" :value="card.id">{{ card.name }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <label for="monthSelect" class="form-label">Mes</label>
        <select id="monthSelect" class="form-select" v-model="selectedMonth">
          <option v-for="(monthName, index) in months" :key="index" :value="index + 1">{{ monthName }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <label for="yearSelect" class="form-label">Año</label>
        <select id="yearSelect" class="form-select" v-model="selectedYear">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
      <div class="col-md-2 d-flex align-items-end">
        <button @click="fetchCardSummary" class="btn btn-primary w-100">Buscar</button>
      </div>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <div v-else>
      <div v-if="cardSummary.length === 0" class="alert alert-info" role="alert">
        No hay movimientos para los filtros seleccionados.
      </div>
      <div v-else>
        <!-- Desktop View (Table) -->
        <div class="d-none d-md-block">
          <div class="table-responsive">
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Descripción</th>
                  <th>Monto</th>
                  <th>Tipo</th>
                  <th>Tarjeta</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in cardSummary" :key="item.id">
                  <td>{{ new Date(item.date).toLocaleDateString() }}</td>
                  <td>{{ item.description }}</td>
                  <td>{{ formatNumber(item.amount) }}</td>
                  <td>{{ item.movement_type === 'expense' ? 'Gasto' : 'Ingreso' }}</td>
                  <td>{{ item.account_name }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-3 p-3 bg-light rounded d-flex justify-content-between align-items-center">
            <h5>Total:</h5>
            <h5>{{ formatNumber(totalAmount) }}</h5>
          </div>
        </div>

        <!-- Mobile View (Cards) -->
        <div class="d-block d-md-none">
          <div v-for="item in cardSummary" :key="item.id" class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">{{ item.description }}</h5>
              <h6 class="card-subtitle mb-2 text-muted">{{ formatNumber(item.amount) }} ({{ item.movement_type === 'expense' ? 'Gasto' : 'Ingreso' }})</h6>
              <p class="card-text">
                <small class="text-muted">Fecha: {{ new Date(item.date).toLocaleDateString() }}</small><br>
                <small class="text-muted">Tarjeta: {{ item.account_name }}</small>
              </p>
            </div>
          </div>
          <div class="mt-3 p-3 bg-light rounded d-flex justify-content-between align-items-center">
            <h5>Total:</h5>
            <h5>{{ formatNumber(totalAmount) }}</h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAccountStore } from '@/stores/account'; // Assuming accounts are cards
import { useExpenseStore } from '@/stores/expense'; // To fetch expenses

const accountStore = useAccountStore();
const expenseStore = useExpenseStore();

const cards = computed(() => accountStore.accounts.filter(acc => acc.is_credit_card));

const selectedCardId = ref('');
const selectedMonth = ref(new Date().getMonth() + 1); // Current month
const selectedYear = ref(new Date().getFullYear()); // Current year

const loading = ref(false);
const error = ref(null);

const months = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  const yearsArray = [];
  for (let i = currentYear; i >= currentYear - 5; i--) { // Last 5 years
    yearsArray.push(i);
  }
  return yearsArray;
});

const formatNumber = (value) => {
  if (value === null || value === undefined) return '';
  return value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const cardSummary = computed(() => {
  return expenseStore.expenses.map(expense => ({
    ...expense,
    account_name: accountStore.accounts.find(acc => acc.id === expense.account_id)?.name || 'N/A'
  })).sort((a, b) => new Date(a.date) - new Date(b.date));
});

const totalAmount = computed(() => {
  return cardSummary.value.reduce((sum, item) => sum + item.amount, 0);
});

const fetchCardSummary = async () => {
  loading.value = true;
  error.value = null;
  try {
    await expenseStore.fetchExpenses(
      0, // skip
      100, // limit
      null, // description
      null, // startDate
      null, // endDate
      selectedCardId.value === '' ? null : selectedCardId.value, // accountId
      null, // categoryId
      null, // recipientId
      selectedMonth.value, // month
      selectedYear.value   // year
    );
    await accountStore.fetchAccounts(); // Still need accounts for card names
  } catch (err) {
    error.value = err;
    console.error('Error fetching card summary:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCardSummary();
});
</script>

<style scoped>
/* Add any specific styling for this view */
</style>
