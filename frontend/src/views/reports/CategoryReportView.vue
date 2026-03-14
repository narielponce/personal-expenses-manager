<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1 d-flex justify-content-between align-items-start">
      <div>
        <h5 class="fw-bold mb-0">Gastos por <span class="text-primary">Categoría</span></h5>
        <p class="text-muted tiny mb-0">Distribución de tus consumos mensuales</p>
      </div>
      <button 
        v-if="reportData.length > 0" 
        @click="exportToCSV" 
        class="btn btn-outline-primary btn-sm rounded-pill border-0 shadow-sm tiny fw-bold"
        title="Exportar a CSV"
        :disabled="isExporting"
      >
        <i v-if="!isExporting" class="bi bi-download me-1"></i>
        <span v-else class="spinner-border spinner-border-sm me-1"></span>
        CSV
      </button>
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
            <button @click="resetToRoot" class="btn btn-sm btn-primary rounded-pill px-4 fw-bold tiny shadow-sm">
              GENERAR REPORTE
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Navegación (Breadcrumbs) -->
    <div v-if="history.length > 0" class="d-flex align-items-center mb-3 px-1">
      <button @click="goBack" class="btn btn-light btn-sm rounded-circle me-2 shadow-sm" style="width: 30px; height: 30px; padding: 0;">
        <i class="bi bi-arrow-left"></i>
      </button>
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0 tiny">
          <li class="breadcrumb-item"><a href="#" @click.prevent="resetToRoot" class="text-decoration-none fw-bold">Todas</a></li>
          <li v-for="(step, index) in history" :key="step.id" class="breadcrumb-item" :class="{ active: index === history.length - 1 }">
            <a v-if="index < history.length - 1" href="#" @click.prevent="goToStep(index)" class="text-decoration-none fw-bold">{{ step.name }}</a>
            <span v-else class="text-primary fw-bold">{{ step.name }}</span>
          </li>
        </ol>
      </nav>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small rounded-4" role="alert">
      {{ error }}
    </div>

    <div v-else>
      <div v-if="reportData.length === 0" class="text-center py-5">
        <i class="bi bi-pie-chart text-muted opacity-25 fs-1"></i>
        <p class="text-muted tiny mt-2">No hay gastos registrados en este nivel.</p>
      </div>

      <div v-else>
        <!-- Resumen Total del nivel actual -->
        <div class="card border-0 bg-primary text-white rounded-4 shadow-sm p-3 mb-4">
          <div class="d-flex justify-content-between align-items-center">
            <span class="tiny opacity-75 fw-bold text-uppercase">Total {{ currentCategoryName }}</span>
            <i class="bi bi-info-circle opacity-50 tiny"></i>
          </div>
          <h4 class="fw-bold mb-0 mt-1">{{ formatCurrency(grandTotal) }}</h4>
        </div>

        <!-- Listado de Categorías con Drill-down -->
        <div class="category-list">
          <div 
            v-for="item in reportData" 
            :key="item.category_id" 
            class="card border-0 shadow-sm rounded-4 mb-2 overflow-hidden"
            :class="{ 'clickable-card': item.has_children }"
            @click="item.has_children ? drillDown(item) : null"
          >
            <div class="card-body p-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                  <span class="fw-bold text-dark smaller">{{ item.category_name }}</span>
                  <i v-if="item.has_children" class="bi bi-chevron-right ms-2 text-primary tiny"></i>
                </div>
                <div class="text-end">
                  <span class="fw-bold text-dark smaller d-block">{{ formatCurrency(item.total) }}</span>
                  <!-- Indicador de Variación -->
                  <span v-if="item.variance_percent !== 0" class="tiny fw-bold" :class="item.variance_percent > 0 ? 'text-danger' : 'text-success'">
                    <i class="bi" :class="item.variance_percent > 0 ? 'bi-caret-up-fill' : 'bi-caret-down-fill'"></i>
                    {{ Math.abs(item.variance_percent) }}%
                  </span>
                  <span v-else class="tiny text-muted fw-bold">0%</span>
                </div>
              </div>
              
              <!-- Barra de Progreso CSS -->
              <div class="progress-container rounded-pill bg-light" style="height: 8px;">
                <div 
                  class="progress-bar rounded-pill bg-primary" 
                  :style="{ width: calculatePercentage(item.total) + '%' }"
                ></div>
              </div>
              
              <div class="d-flex justify-content-end mt-1">
                <span class="tiny text-muted fw-bold">{{ calculatePercentage(item.total) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <Transition name="fade">
      <div v-if="showSuccessToast" class="success-toast shadow-sm rounded-pill py-2 px-4 bg-success text-white d-flex align-items-center gap-2">
        <i class="bi bi-check-circle-fill"></i>
        <span class="fw-bold tiny">{{ successMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/api';

const loading = ref(false);
const isExporting = ref(false);
const error = ref(null);
const reportData = ref([]);
const showFilters = ref(true);
const history = ref([]); // Historial para breadcrumbs: [{id, name}]
const showSuccessToast = ref(false);
const successMessage = ref('');

const selectedMonth = ref(new Date().getMonth() + 1);
const selectedYear = ref(new Date().getFullYear());

const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return [currentYear, currentYear - 1, currentYear - 2];
});

const currentParentId = computed(() => {
  return history.value.length > 0 ? history.value[history.value.length - 1].id : null;
});

const currentCategoryName = computed(() => {
  return history.value.length > 0 ? history.value[history.value.length - 1].name : 'del Período';
});

const grandTotal = computed(() => {
  return reportData.value.reduce((sum, item) => sum + item.total, 0);
});

const calculatePercentage = (amount) => {
  if (grandTotal.value === 0) return 0;
  return ((amount / grandTotal.value) * 100).toFixed(1);
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: true }).format(Number(value)) + ' $';
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/expenses/reports/by-category', {
      params: {
        month: selectedMonth.value,
        year: selectedYear.value,
        parent_id: currentParentId.value
      }
    });
    reportData.value = response.data;
  } catch (err) {
    console.error('Error fetching category report:', err);
    error.value = 'No se pudo cargar el reporte.';
  } finally {
    loading.value = false;
  }
};

const drillDown = (category) => {
  history.value.push({ id: category.category_id, name: category.category_name });
  fetchData();
};

const goBack = () => {
  history.value.pop();
  fetchData();
};

const goToStep = (index) => {
  history.value = history.value.slice(0, index + 1);
  fetchData();
};

const resetToRoot = () => {
  history.value = [];
  showFilters.value = false;
  fetchData();
};

const exportToCSV = async () => {
  if (isExporting.value) return;
  isExporting.value = true;
  try {
    const response = await apiClient.get('/expenses/reports/by-category/export', {
      params: {
        month: selectedMonth.value,
        year: selectedYear.value,
        parent_id: currentParentId.value
      },
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_categorias_${selectedYear.value}_${selectedMonth.value}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    successMessage.value = "Reporte CSV descargado";
    showSuccessToast.value = true;
    setTimeout(() => { showSuccessToast.value = false; }, 2500);
  } catch (err) {
    console.error('Error exporting CSV:', err);
    alert('No se pudo generar el archivo CSV.');
  } finally {
    isExporting.value = false;
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
.progress-bar { transition: width 0.6s ease; }
.card { width: 100%; }
.clickable-card { cursor: pointer; transition: background-color 0.2s; }
.clickable-card:active { background-color: #f8f9fa; }
.breadcrumb-item + .breadcrumb-item::before { content: ">"; }

/* Estilos para el Toast */
.success-toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
