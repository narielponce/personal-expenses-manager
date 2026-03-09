<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <h2 class="h5 text-center mb-3 fw-bold text-dark">Movimientos</h2>
    
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small" role="alert">
      Error: {{ error.message }}
    </div>
    
    <div v-else>
      <!-- Filtros Modernizados -->
      <div class="card border-0 shadow-sm rounded-3 mb-3 overflow-hidden">
        <div class="card-header bg-white border-0 py-2 px-3 d-flex justify-content-between align-items-center" @click="showFilters = !showFilters" style="cursor: pointer;">
          <h6 class="mb-0 fw-bold text-secondary small"><i class="bi bi-funnel me-1"></i> Filtros de Movimientos</h6>
          <i class="bi text-muted small" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
        </div>
        <div v-show="showFilters" class="card-body p-3 bg-light-subtle border-top">
          <div class="row g-2">
            <div class="col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Descripción</label>
              <input type="text" class="form-control form-control-sm border-0 shadow-sm" v-model="filterDescription" @keyup.enter="applyFilters" placeholder="Buscar...">
            </div>
            <div class="col-6 col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Desde</label>
              <input type="date" class="form-control form-control-sm border-0 shadow-sm" v-model="filterStartDate">
            </div>
            <div class="col-6 col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Hasta</label>
              <input type="date" class="form-control form-control-sm border-0 shadow-sm" v-model="filterEndDate">
            </div>
            <div class="col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Categoría</label>
              <select class="form-select form-select-sm border-0 shadow-sm" v-model="filterCategoryId">
                <option :value="null">Todas</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Cuenta</label>
              <select class="form-select form-select-sm border-0 shadow-sm" v-model="filterAccountId">
                <option :value="null">Todas</option>
                <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="smaller text-muted fw-bold mb-1">Destinatario</label>
              <select class="form-select form-select-sm border-0 shadow-sm" v-model="filterRecipientId">
                <option :value="null">Todos</option>
                <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
              </select>
            </div>
            <div class="col-12 text-end mt-2">
              <button class="btn btn-sm btn-outline-secondary border-0 me-2 fw-bold smaller" @click="resetFilters">Limpiar</button>
              <button class="btn btn-sm btn-primary rounded-2 px-3 fw-bold smaller" @click="applyFilters">Aplicar Filtros</button>
            </div>
          </div>
        </div>
      </div>

      <div class="d-grid mb-3">
        <router-link to="/expenses/new" class="btn btn-primary fw-semibold rounded-3 shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> Registrar Movimiento
        </router-link>
      </div>

      <!-- Lista de Movimientos Unificada con protección de desbordamiento -->
      <div class="expense-list">
        <div v-for="expense in expenses" :key="expense.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
            <div class="card-body p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                
                <!-- Tipo (Pill) - Oculto en móviles extra pequeños si es necesario -->
                <div class="flex-shrink-0 d-none d-sm-block">
                  <span class="movement-pill" :class="expense.movement_type === 'expense' ? 'bg-danger' : 'bg-success'">
                    <i class="bi" :class="expense.movement_type === 'expense' ? 'bi-arrow-down-left' : 'bi-arrow-up-right'"></i>
                  </span>
                </div>

                <!-- Info Principal -->
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex flex-column flex-sm-row justify-content-sm-between align-items-sm-start">
                    <div class="min-width-0 overflow-hidden">
                      <span class="fw-bold text-dark d-block text-truncate mb-0" :title="expense.description">
                        {{ expense.description }}
                      </span>
                    </div>
                    <span class="fw-bold fs-6 text-nowrap" :class="expense.movement_type === 'expense' ? 'text-danger' : 'text-success'">
                      {{ expense.movement_type === 'expense' ? '-' : '+' }}{{ formatCurrency(expense.amount) }}
                    </span>
                  </div>
                  <div class="d-flex align-items-center smaller text-muted mt-1 flex-wrap gap-x-2">
                    <span class="text-nowrap"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(expense.date) }}</span>
                    <span v-if="expense.category_name" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;"><i class="bi bi-tag me-1"></i>{{ expense.category_name }}</span>
                    <span v-if="expense.account_name" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;"><i class="bi bi-wallet2 me-1"></i>{{ expense.account_name }}</span>
                  </div>
                </div>

                <!-- Acciones -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/expenses/${expense.id}`" class="btn btn-light-blue btn-sm border-0 rounded-2 me-1" title="Ver">
                    <i class="bi bi-eye text-primary"></i>
                  </router-link>
                  
                  <router-link :to="`/expenses/${expense.id}/edit`" class="btn btn-light-warning btn-sm border-0 rounded-2 me-1" title="Editar">
                    <i class="bi bi-pencil text-warning-emphasis"></i>
                  </router-link>
                  
                  <button @click="deleteExpense(expense.id)" class="btn btn-light-danger btn-sm border-0 rounded-2" title="Eliminar">
                    <i class="bi bi-trash text-danger"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paginación Modernizada -->
      <nav aria-label="Page navigation" v-if="totalPages > 1">
        <ul class="pagination pagination-sm justify-content-center mt-4 border-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link border-0 rounded-3 me-1 shadow-sm" href="#" @click.prevent="changePage(currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </a>
          </li>
          <li class="page-item" v-for="page in totalPages" :key="page" :class="{ active: currentPage === page }">
            <a class="page-link border-0 rounded-3 mx-1 shadow-sm" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link border-0 rounded-3 ms-1 shadow-sm" href="#" @click.prevent="changePage(currentPage + 1)">
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

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '';
  return value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' $';
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
  }
};

const applyFilters = () => {
  currentPage.value = 1;
  fetchExpensesWithPagination();
};

const resetFilters = () => {
  filterDescription.value = '';
  filterStartDate.value = null;
  filterEndDate.value = null;
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

.smaller {
  font-size: 0.75rem;
}

.min-width-0 {
  min-width: 0;
}

.gap-x-2 {
  column-gap: 0.5rem;
}

.movement-pill {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-size: 1rem;
}

.bg-light-subtle {
  background-color: rgba(0, 0, 0, 0.02) !important;
}

/* Colores de botones sutiles */
.btn-light-blue { background-color: #e7f1ff; }
.btn-light-blue:hover { background-color: #cfe2ff; }
.btn-light-warning { background-color: #fff3cd; }
.btn-light-warning:hover { background-color: #ffecb5; }
.btn-light-danger { background-color: #f8d7da; }
.btn-light-danger:hover { background-color: #f1aeb5; }

.action-buttons .btn {
  padding: 0.25rem 0.45rem;
}

.action-buttons {
  flex-shrink: 0;
}

.page-link {
  color: #6c757d;
  background-color: #fff;
}

.page-item.active .page-link {
  background-color: #0d6efd;
  color: #fff;
}

.card {
  border: 1px solid rgba(0,0,0,0.05) !important;
  width: 100%;
}
</style>
