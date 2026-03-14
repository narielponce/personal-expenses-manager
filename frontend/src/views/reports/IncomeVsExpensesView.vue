<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Ingresos vs <span class="text-primary">Gastos</span></h5>
      <p class="text-muted tiny mb-0">Balance mensual de tus movimientos</p>
    </div>

    <!-- Filtros estilo Home -->
    <div class="card border-0 shadow-sm rounded-4 mb-3 overflow-hidden">
      <div class="d-flex justify-content-center pt-2 pb-1" @click="showFilters = !showFilters" style="cursor: pointer;">
        <div class="drag-handle"></div>
      </div>
      
      <div class="card-header bg-white border-0 py-1 px-3 d-flex justify-content-between align-items-center" @click="showFilters = !showFilters" style="cursor: pointer;">
        <h6 class="mb-0 fw-bold text-secondary smaller"><i class="bi bi-funnel me-1"></i> Período</h6>
        <i class="bi text-muted smaller" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </div>
      
      <div v-show="showFilters" class="card-body p-3 bg-white">
        <div class="row g-2">
          <div class="col-6">
            <label class="tiny text-muted fw-bold mb-1 text-uppercase">Mes</label>
            <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="selectedMonth">
              <option v-for="(monthName, index) in months" :key="index" :value="index + 1">{{ monthName }}</option>
            </select>
          </div>
          <div class="col-6">
            <label class="tiny text-muted fw-bold mb-1 text-uppercase">Año</label>
            <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="selectedYear">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="col-12 text-end mt-2">
            <button @click="fetchData" class="btn btn-sm btn-primary rounded-pill px-4 fw-bold tiny shadow-sm">
              BUSCAR
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small rounded-4" role="alert">
      {{ error }}
    </div>

    <div v-else>
      <!-- Cards de Resumen -->
      <div class="row g-2 mb-4">
        <div class="col-6">
          <div class="card border-0 bg-success text-white rounded-4 shadow-sm p-3">
            <span class="tiny opacity-75 fw-bold text-uppercase">Ingresos</span>
            <h5 class="fw-bold mb-0 mt-1">{{ formatCurrency(balanceData.total_income) }}</h5>
          </div>
        </div>
        <div class="col-6">
          <div class="card border-0 bg-danger text-white rounded-4 shadow-sm p-3">
            <span class="tiny opacity-75 fw-bold text-uppercase">Gastos</span>
            <h5 class="fw-bold mb-0 mt-1">{{ formatCurrency(balanceData.total_expense) }}</h5>
          </div>
        </div>
      </div>

      <!-- Balance Card -->
      <div class="card border-0 shadow-sm rounded-4 mb-4 overflow-hidden" :class="balanceData.balance >= 0 ? 'bg-primary-subtle' : 'bg-danger-subtle'">
        <div class="card-body p-3 text-center">
          <span class="tiny fw-bold text-uppercase" :class="balanceData.balance >= 0 ? 'text-primary' : 'text-danger'">Balance Neto</span>
          <h3 class="fw-bold mb-0" :class="balanceData.balance >= 0 ? 'text-primary' : 'text-danger'">{{ formatCurrency(balanceData.balance) }}</h3>
          <p class="tiny mb-0 mt-1 fw-medium" :class="balanceData.balance >= 0 ? 'text-primary' : 'text-danger'">
            {{ balanceData.balance >= 0 ? '¡Vas por buen camino!' : 'Tus gastos superaron tus ingresos' }}
          </p>
        </div>
      </div>

      <!-- Comparativa Visual -->
      <div class="card border-0 shadow-sm rounded-4 p-4 mb-2">
        <h6 class="fw-bold smaller text-dark mb-4 text-center">Comparativa Proporcional</h6>
        
        <div class="d-flex flex-column gap-4">
          <!-- Barra Ingresos -->
          <div>
            <div class="d-flex justify-content-between mb-1">
              <span class="tiny fw-bold text-muted">INGRESOS</span>
              <span class="tiny fw-bold text-success">{{ incomePercentage }}%</span>
            </div>
            <div class="progress-container rounded-pill bg-light" style="height: 12px;">
              <div class="progress-bar rounded-pill bg-success" :style="{ width: incomePercentage + '%' }"></div>
            </div>
          </div>

          <!-- Barra Gastos -->
          <div>
            <div class="d-flex justify-content-between mb-1">
              <span class="tiny fw-bold text-muted">GASTOS</span>
              <span class="tiny fw-bold text-danger">{{ expensePercentage }}%</span>
            </div>
            <div class="progress-container rounded-pill bg-light" style="height: 12px;">
              <div class="progress-bar rounded-pill bg-danger" :style="{ width: expensePercentage + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/api';

const loading = ref(false);
const error = ref(null);
const balanceData = ref({ total_income: 0, total_expense: 0, balance: 0 });
const showFilters = ref(false);

const selectedMonth = ref(new Date().getMonth() + 1);
const selectedYear = ref(new Date().getFullYear());

const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return [currentYear, currentYear - 1, currentYear - 2];
});

const grandTotalVolume = computed(() => {
  return balanceData.value.total_income + balanceData.value.total_expense;
});

const incomePercentage = computed(() => {
  if (grandTotalVolume.value === 0) return 0;
  return ((balanceData.value.total_income / grandTotalVolume.value) * 100).toFixed(0);
});

const expensePercentage = computed(() => {
  if (grandTotalVolume.value === 0) return 0;
  return ((balanceData.value.total_expense / grandTotalVolume.value) * 100).toFixed(0);
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: true }).format(Number(value)) + ' $';
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/expenses/reports/income-vs-expenses', {
      params: {
        month: selectedMonth.value,
        year: selectedYear.value
      }
    });
    balanceData.value = response.data;
    showFilters.value = false;
  } catch (err) {
    console.error('Error fetching balance report:', err);
    error.value = 'No se pudo cargar el reporte.';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);
</script>

<style scoped>
.summary-container { width: 100%; overflow-x: hidden; }
.user-header { border-left: 4px solid #0d6efd; padding-left: 12px; }
.drag-handle { width: 36px; height: 4px; background-color: #e9ecef; border-radius: 2px; position: relative; }
.drag-handle::before, .drag-handle::after { content: ""; position: absolute; width: 4px; height: 4px; background-color: #e9ecef; border-radius: 50%; top: 0; }
.drag-handle::before { left: -8px; }
.drag-handle::after { right: -8px; }
.smaller { font-size: 0.75rem; }
.tiny { font-size: 0.65rem; }
.progress-bar { transition: width 0.8s ease; }
.bg-primary-subtle { background-color: #e7f1ff !important; }
.bg-danger-subtle { background-color: #f8d7da !important; }
.bg-success-subtle { background-color: #d1e7dd !important; }
.card { width: 100%; }
</style>
