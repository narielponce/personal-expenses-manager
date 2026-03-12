<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Listado de <span class="text-primary">Movimientos</span></h5>
      <p class="text-muted tiny mb-0">Historial completo de tus finanzas</p>
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
            <div class="col-md-4">
              <label class="tiny text-muted fw-bold mb-1 text-uppercase">Descripción</label>
              <input type="text" class="form-control form-control-sm border-0 bg-light rounded-3 px-2" v-model="filterDescription" @keyup.enter="applyFilters" placeholder="Buscar...">
            </div>
            <div class="col-6 col-md-4">
              <label class="tiny text-muted fw-bold mb-1 text-uppercase">Desde</label>
              <input type="date" class="form-control form-control-sm border-0 bg-light rounded-3 px-2" v-model="filterStartDate">
            </div>
            <div class="col-6 col-md-4">
              <label class="tiny text-muted fw-bold mb-1 text-uppercase">Hasta</label>
              <input type="date" class="form-control form-control-sm border-0 bg-light rounded-3 px-2" v-model="filterEndDate">
            </div>
            <div class="col-md-4">
              <label class="tiny text-muted fw-bold mb-1 text-uppercase">Categoría</label>
              <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="filterCategoryId">
                <option :value="null">Todas</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="tiny text-muted fw-bold mb-1 text-uppercase">Cuenta</label>
              <select class="form-select form-select-sm border-0 bg-light rounded-3 px-2" v-model="filterAccountId">
                <option :value="null">Todas</option>
                <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
              </select>
            </div>
            <div class="col-md-4 text-end d-flex align-items-end justify-content-end gap-2 mt-2 mt-md-0">
              <button class="btn btn-sm btn-link text-decoration-none text-muted tiny fw-bold p-0" @click="resetFilters">LIMPIAR</button>
              <button class="btn btn-sm btn-primary rounded-pill px-3 fw-bold tiny" @click="applyFilters">APLICAR</button>
            </div>
          </div>
        </div>
      </div>

      <div class="d-grid mb-3">
        <router-link to="/expenses/new" class="btn btn-primary fw-bold rounded-pill shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> NUEVO MOVIMIENTO
        </router-link>
      </div>

      <!-- Lista de Movimientos estilo Home -->
      <div class="expense-list">
        <div v-for="expense in expenses" :key="expense.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
            <div class="card-body p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                
                <!-- Icono Tipo simplificado -->
                <div class="flex-shrink-0">
                  <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center" :class="expense.movement_type === 'expense' ? 'bg-danger-subtle' : 'bg-success-subtle'" style="width: 28px; height: 28px;">
                    <i class="bi tiny" :class="[expense.movement_type === 'expense' ? 'bi-arrow-down-left text-danger' : 'bi-arrow-up-right text-success']"></i>
                  </div>
                </div>

                <!-- Info Principal -->
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="min-width-0 overflow-hidden">
                      <span class="fw-bold text-dark d-block text-truncate mb-0 smaller" :title="expense.description">
                        {{ expense.description }}
                      </span>
                    </div>
                    <span class="fw-bold tiny" :class="expense.movement_type === 'expense' ? 'text-danger' : 'text-success'">
                      {{ expense.movement_type === 'expense' ? '-' : '+' }}{{ formatCurrency(expense.amount) }}
                    </span>
                  </div>
                  <div class="d-flex align-items-center tiny text-muted mt-0 flex-wrap gap-x-2">
                    <span class="text-nowrap"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(expense.date) }}</span>
                    <span v-if="expense.category_name" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;"><i class="bi bi-tag me-1"></i>{{ expense.category_name }}</span>
                    <span v-if="expense.account_name" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;"><i class="bi bi-wallet2 me-1"></i>{{ expense.account_name }}</span>
                  </div>
                </div>

                <!-- Acciones discretas -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/expenses/${expense.id}/edit`" class="btn btn-link text-warning p-1" title="Editar">
                    <i class="bi bi-pencil-square fs-6"></i>
                  </router-link>
                  
                  <button @click="deleteExpense(expense.id)" class="btn btn-link text-danger p-1" title="Eliminar">
                    <i class="bi bi-trash fs-6"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paginación Compacta estilo Home -->
      <nav aria-label="Page navigation" v-if="totalPages > 1">
        <ul class="pagination pagination-sm justify-content-center mt-4 border-0 align-items-center">
          <!-- Flecha Izquierda -->
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link border-0 rounded-circle mx-1 shadow-sm" href="#" @click.prevent="changePage(currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </a>
          </li>

          <!-- Primera Página si no está en el rango -->
          <template v-if="visiblePages[0] > 1">
            <li class="page-item">
              <a class="page-link border-0 rounded-circle mx-1 shadow-sm" href="#" @click.prevent="changePage(1)">1</a>
            </li>
            <li class="page-item disabled" v-if="visiblePages[0] > 2">
              <span class="page-link border-0 bg-transparent">...</span>
            </li>
          </template>

          <!-- Páginas Dinámicas -->
          <li class="page-item" v-for="page in visiblePages" :key="page" :class="{ active: currentPage === page }">
            <a class="page-link border-0 rounded-circle mx-1 shadow-sm" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>

          <!-- Última Página si no está en el rango -->
          <template v-if="visiblePages[visiblePages.length - 1] < totalPages">
            <li class="page-item disabled" v-if="visiblePages[visiblePages.length - 1] < totalPages - 1">
              <span class="page-link border-0 bg-transparent">...</span>
            </li>
            <li class="page-item">
              <a class="page-link border-0 rounded-circle mx-1 shadow-sm" href="#" @click.prevent="changePage(totalPages)">{{ totalPages }}</a>
            </li>
          </template>

          <!-- Flecha Derecha -->
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link border-0 rounded-circle mx-1 shadow-sm" href="#" @click.prevent="changePage(currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useExpenseStore } from '../../stores/expense';
import { useAccountStore } from '../../stores/account';
import { useCategoryStore } from '../../stores/category';
import { useRecipientStore } from '../../stores/recipient';

const expenseStore = useExpenseStore();
const accountStore = useAccountStore();
const categoryStore = useCategoryStore();
const recipientStore = useRecipientStore();

const expenses = computed(() => expenseStore.expenses);
const totalExpensesCount = computed(() => expenseStore.totalExpensesCount);
const loading = computed(() => expenseStore.loading);
const error = computed(() => expenseStore.error);

const showFilters = ref(false);
const filterDescription = ref('');
const filterStartDate = ref(null);
const filterEndDate = ref(null);
const filterCategoryId = ref(null);
const filterAccountId = ref(null);
const filterRecipientId = ref(null);

const accounts = computed(() => accountStore.accounts);
const categories = computed(() => categoryStore.categories);
const recipients = computed(() => recipientStore.recipients);

const currentPage = ref(1);
const itemsPerPage = ref(10);

const totalPages = computed(() => Math.ceil(totalExpensesCount.value / itemsPerPage.value));

// Lógica para Páginas Visibles (Ventana Deslizante)
const visiblePages = computed(() => {
  const range = 2; // Número de páginas a mostrar a los lados de la actual
  let start = Math.max(1, currentPage.value - range);
  let end = Math.min(totalPages.value, currentPage.value + range);

  // Ajustar si estamos cerca de los extremos
  if (currentPage.value <= range) {
    end = Math.min(totalPages.value, range * 2 + 1);
  } else if (currentPage.value > totalPages.value - range) {
    start = Math.max(1, totalPages.value - range * 2);
  }

  const pages = [];
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
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
  // Si viene con T (ISO string), tomar solo la parte de la fecha
  const pureDate = dateStr.includes('T') ? dateStr.split('T')[0] : dateStr;
  const [year, month, day] = pureDate.split('-');
  return new Date(year, month - 1, day).toLocaleDateString();
};

const fetchExpensesWithPagination = () => {
  const skip = (currentPage.value - 1) * itemsPerPage.value;
  const limit = itemsPerPage.value;
  expenseStore.fetchExpenses(
    skip,
    limit,
    filterDescription.value || null,
    filterStartDate.value || null,
    filterEndDate.value || null,
    filterAccountId.value || null,
    filterCategoryId.value || null,
    filterRecipientId.value || null
  );
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    fetchExpensesWithPagination();
    // Scroll suave hacia arriba al cambiar de página
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const applyFilters = () => {
  currentPage.value = 1;
  fetchExpensesWithPagination();
};

const resetFilters = () => {
  filterDescription.value = '';
  filterStartDate.value = null;
  filterEndDate = null;
  filterCategoryId.value = null;
  filterAccountId.value = null;
  filterRecipientId.value = null;
  currentPage.value = 1;
  fetchExpensesWithPagination();
};

onMounted(() => {
  accountStore.fetchAccounts();
  categoryStore.fetchCategories();
  recipientStore.fetchRecipients();
  fetchExpensesWithPagination();
});

const deleteExpense = async (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar este movimiento?')) {
    try {
      await expenseStore.deleteExpense(id);
      fetchExpensesWithPagination();
    } catch (err) {
      console.error('No se pudo eliminar el movimiento:', err);
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

.gap-x-2 {
  column-gap: 0.5rem;
}

.bg-danger-subtle { background-color: #f8d7da !important; }
.bg-success-subtle { background-color: #d1e7dd !important; }

.action-buttons .btn-link {
  text-decoration: none;
  opacity: 0.7;
}
.action-buttons .btn-link:hover {
  opacity: 1;
}

.page-link {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  background-color: #fff;
  font-weight: 600;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.page-item.active .page-link {
  background-color: #0d6efd;
  color: #fff;
  transform: scale(1.1);
}

.page-item.disabled .page-link {
  opacity: 0.5;
  background-color: transparent;
  box-shadow: none;
}

.card {
  width: 100%;
}
</style>
