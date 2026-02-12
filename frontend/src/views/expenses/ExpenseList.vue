<template>
  <div class="container mt-4">
    <h2 class="mb-4">Movimientos</h2>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <div v-else>
      <div class="mb-4 p-3 border rounded">
        <h4 class="mb-3">Filtros de Movimientos</h4>
        <div class="row g-3">
          <div class="col-md-6 col-lg-4">
            <label for="filterDescription" class="form-label">Descripción</label>
            <input type="text" class="form-control" id="filterDescription" v-model="filterDescription" @keyup.enter="applyFilters" placeholder="Buscar por descripción">
          </div>
          <div class="col-md-6 col-lg-4">
            <label for="filterStartDate" class="form-label">Fecha Inicio</label>
            <input type="date" class="form-control" id="filterStartDate" v-model="filterStartDate">
          </div>
          <div class="col-md-6 col-lg-4">
            <label for="filterEndDate" class="form-label">Fecha Fin</label>
            <input type="date" class="form-control" id="filterEndDate" v-model="filterEndDate">
          </div>
          <div class="col-md-6 col-lg-4">
            <label for="filterCategory" class="form-label">Categoría</label>
            <select class="form-select" id="filterCategory" v-model="filterCategoryId">
              <option :value="null">Todas las Categorías</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
            </select>
          </div>
          <div class="col-md-6 col-lg-4">
            <label for="filterAccount" class="form-label">Cuenta</label>
            <select class="form-select" id="filterAccount" v-model="filterAccountId">
              <option :value="null">Todas las Cuentas</option>
              <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
            </select>
          </div>
          <div class="col-md-6 col-lg-4">
            <label for="filterRecipient" class="form-label">Destinatario</label>
            <select class="form-select" id="filterRecipient" v-model="filterRecipientId">
              <option :value="null">Todos los Destinatarios</option>
              <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
            </select>
          </div>
          <div class="col-12 text-end">
            <button class="btn btn-secondary me-2" @click="resetFilters">Limpiar Filtros</button>
            <button class="btn btn-primary" @click="applyFilters">Aplicar Filtros</button>
          </div>
        </div>
      </div>
      <router-link to="/expenses/new" class="btn btn-primary mb-3">Registrar Movimiento</router-link>
      <!-- Desktop View (List) -->
      <div class="d-none d-md-block">
        <ul class="list-group">
          <li v-for="expense in expenses" :key="expense.id" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <strong>{{ expense.description }}</strong> - {{ formatCurrency(expense.amount) }} ({{ expense.movement_type === 'expense' ? 'Gasto' : 'Ingreso' }})
              <br>
              <small>Fecha: {{ new Date(expense.date).toLocaleDateString() }}
                <span v-if="expense.is_installment && expense.application_date"> | Aplicación: {{ new Date(expense.application_date).toLocaleDateString() }}</span>
              </small>
              <span v-if="expense.is_installment && expense.num_installments && expense.installment_amount">
                <br>
                <small>Cuotas: {{ expense.num_installments }} de {{ formatCurrency(expense.installment_amount) }}</small>
              </span>
            </div>
            <div>
              <router-link :to="`/expenses/${expense.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
              <router-link :to="`/expenses/${expense.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
              <button @click="deleteExpense(expense.id)" class="btn btn-danger btn-sm">Eliminar</button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Mobile View (Cards) -->
      <div class="d-block d-md-none">
        <div class="row">
          <div v-for="expense in expenses" :key="expense.id" class="col-12 mb-3">
            <div class="card">
              <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="card-title"><strong>{{ expense.description }}</strong></h5>
                  <p class="card-text">{{ formatCurrency(expense.amount) }} ({{ expense.movement_type === 'expense' ? 'Gasto' : 'Ingreso' }})</p>
                  <small>Fecha: {{ new Date(expense.date).toLocaleDateString() }}
                    <span v-if="expense.is_installment && expense.application_date"> | Aplicación: {{ new Date(expense.application_date).toLocaleDateString() }}</span>
                  </small>
                  <span v-if="expense.is_installment && expense.num_installments && expense.installment_amount">
                    <br>
                    <small>Cuotas: {{ expense.num_installments }} de {{ formatCurrency(expense.installment_amount) }}</small>
                  </span>
                </div>
                <div>
                  <router-link :to="`/expenses/${expense.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
                  <router-link :to="`/expenses/${expense.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
                  <button @click="deleteExpense(expense.id)" class="btn btn-danger btn-sm">Eliminar</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination Controls -->
      <nav aria-label="Page navigation" v-if="totalPages > 1">
        <ul class="pagination justify-content-center mt-3">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Anterior</a>
          </li>
          <li class="page-item" v-for="page in totalPages" :key="page" :class="{ active: currentPage === page }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Siguiente</a>
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
  return value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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
  currentPage.value = 1; // Reset to first page when filters are applied
  fetchExpensesWithPagination();
};

const resetFilters = () => {
  filterDescription.value = '';
  filterStartDate.value = null;
  filterEndDate.value = null;
  filterCategoryId.value = null;
  filterAccountId.value = null;
  filterRecipientId.value = null;
  currentPage.value = 1; // Reset to first page
  fetchExpensesWithPagination(); // Fetch expenses with cleared filters
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
      fetchExpensesWithPagination(); // Re-fetch expenses after deletion
    } catch (err) {
      console.error('No se pudo eliminar el movimiento:', err);
      alert('No se pudo eliminar el movimiento.');
    }
  }
};
</script>
