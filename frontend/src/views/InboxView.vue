<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 800px; margin-left: auto; margin-right: auto;">
    <h2 class="h5 text-center mb-1 fw-bold text-dark">Bandeja de Entrada</h2>
    <p class="text-muted small text-center mb-3">Movimientos pendientes de revisión (IA)</p>
    
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small" role="alert">
      Error: {{ error.message }}
    </div>
    
    <div v-else>
      <div v-if="expenses.length === 0" class="text-center py-5">
        <i class="bi bi-check2-circle fs-1 text-success mb-2"></i>
        <p class="text-muted">¡Todo al día! No hay movimientos pendientes.</p>
        <router-link to="/expenses/new" class="btn btn-sm btn-outline-primary rounded-pill px-3">
          Registrar nuevo
        </router-link>
      </div>

      <div v-else class="expense-list">
        <div v-for="expense in expenses" :key="expense.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-3 overflow-hidden border-start border-warning border-4">
            <div class="card-body p-2 px-3">
              <div class="d-flex align-items-center gap-2">
                
                <!-- Info Principal -->
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex justify-content-between align-items-start">
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
                    <span v-if="expense.category_id" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;">
                      <i class="bi bi-tag me-1"></i>{{ getCategoryName(expense.category_id) }}
                    </span>
                    <span v-else class="ms-1 ms-sm-2 text-warning fw-medium italic"><i class="bi bi-tag me-1"></i>Sin categoría</span>
                    
                    <span v-if="expense.account_id" class="ms-1 ms-sm-2 text-truncate" style="max-width: 120px;">
                      <i class="bi bi-wallet2 me-1"></i>{{ getAccountName(expense.account_id) }}
                    </span>
                    <span v-else class="ms-1 ms-sm-2 text-warning fw-medium italic"><i class="bi bi-wallet2 me-1"></i>Sin cuenta</span>
                  </div>
                </div>

                <!-- Acciones -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/expenses/${expense.id}/edit`" class="btn btn-primary btn-sm border-0 rounded-pill px-3 fw-bold smaller" title="Confirmar">
                    Revisar
                  </router-link>
                  
                  <button @click="deleteExpense(expense.id)" class="btn btn-light-danger btn-sm border-0 rounded-circle ms-2" title="Eliminar">
                    <i class="bi bi-trash text-danger"></i>
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
import { useExpenseStore } from '../stores/expense';
import { useAccountStore } from '../stores/account';
import { useCategoryStore } from '../stores/category';

const expenseStore = useExpenseStore();
const accountStore = useAccountStore();
const categoryStore = useCategoryStore();

const expenses = computed(() => expenseStore.expenses);
const loading = computed(() => expenseStore.loading);
const error = computed(() => expenseStore.error);

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

const getCategoryName = (id) => {
  const cat = categoryStore.categories.find(c => c.id === id);
  return cat ? cat.name : '';
};

const getAccountName = (id) => {
  const acc = accountStore.accounts.find(a => a.id === id);
  return acc ? acc.name : '';
};

onMounted(() => {
  accountStore.fetchAccounts();
  categoryStore.fetchCategories();
  expenseStore.fetchExpenses(0, 100, null, null, null, null, null, null, null, null, 'pending');
});

const deleteExpense = async (id) => {
  if (confirm('¿Estás seguro de que quieres descartar este movimiento pendiente?')) {
    try {
      await expenseStore.deleteExpense(id);
      expenseStore.fetchExpenses(0, 100, null, null, null, null, null, null, null, null, 'pending');
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

.italic {
  font-style: italic;
}

.btn-light-danger { background-color: #f8d7da; }
.btn-light-danger:hover { background-color: #f1aeb5; }

.action-buttons {
  flex-shrink: 0;
}

.card {
  border: 1px solid rgba(0,0,0,0.05) !important;
  width: 100%;
}
</style>
