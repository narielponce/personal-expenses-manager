<template>
  <div class="container mt-4">
    <h2 class="mb-4">{{ isEditMode ? 'Editar Movimiento' : 'Registrar Movimiento' }}</h2>
    <div v-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="date" class="form-label">Fecha</label>
        <input type="date" class="form-control" id="date" v-model="expense.date" required />
      </div>
      <div class="mb-3">
        <label for="movementType" class="form-label">Tipo de Movimiento</label>
        <select class="form-select" id="movementType" v-model="expense.movement_type" required>
          <option value="expense">Gasto</option>
          <option value="income">Ingreso</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="categoryId" class="form-label">Categoría</label>
        <div class="input-group">
          <select class="form-select" id="categoryId" v-model="expense.category_id">
            <option :value="null">Seleccionar Categoría</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
          </select>
          <button class="btn btn-outline-secondary" type="button" data-bs-toggle="modal" data-bs-target="#categoryModal">
            <i class="bi bi-plus-lg"></i> Agregar nuevo
          </button>
        </div>
      </div>
      <div class="mb-3">
        <label for="accountId" class="form-label">Cuenta</label>
        <div class="input-group">
          <select class="form-select" id="accountId" v-model="expense.account_id">
            <option :value="null">Seleccionar Cuenta</option>
            <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
          </select>
          <button class="btn btn-outline-secondary" type="button" data-bs-toggle="modal" data-bs-target="#accountModal">
            <i class="bi bi-plus-lg"></i> Agregar nuevo
          </button>
        </div>
      </div>
      <div v-if="selectedAccountIsCreditCard">
        <div class="mb-3">
          <label for="numInstallments" class="form-label">Número de Cuotas</label>
          <input type="number" class="form-control" id="numInstallments" v-model="expense.num_installments" />
        </div>
      </div>
      <div class="mb-3">
        <label for="recipientId" class="form-label">Destinatario</label>
        <div class="input-group">
          <select class="form-select" id="recipientId" v-model="expense.recipient_id">
            <option :value="null">Seleccionar Destinatario</option>
            <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
          </select>
          <button class="btn btn-outline-secondary" type="button" data-bs-toggle="modal" data-bs-target="#recipientModal">
            <i class="bi bi-plus-lg"></i> Agregar nuevo
          </button>
        </div>
      </div>
      <div class="mb-3">
        <label for="description" class="form-label">Descripción</label>
        <input type="text" class="form-control" id="description" v-model="expense.description" required />
      </div>
      <div class="mb-3">
        <label for="amount" class="form-label">Monto</label>
        <input type="number" class="form-control" id="amount" v-model="expense.amount" required step="0.01" />
      </div>

      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isEditMode ? 'Actualizar Movimiento' : 'Registrar Movimiento' }}
      </button>
      <router-link to="/expenses" class="btn btn-secondary ms-2">Cancelar</router-link>
    </form>

    <!-- Category Modal -->
    <div class="modal fade" id="categoryModal" tabindex="-1" aria-labelledby="categoryModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="categoryModalLabel">Crear Nueva Categoría</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <CategoryForm @category-created="handleCategoryCreated" :isModalCreate="true" />
          </div>
        </div>
      </div>
    </div>

    <!-- Account Modal -->
    <div class="modal fade" id="accountModal" tabindex="-1" aria-labelledby="accountModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="accountModalLabel">Crear Nueva Cuenta</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AccountForm @account-created="handleAccountCreated" :isModalCreate="true" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recipient Modal -->
    <div class="modal fade" id="recipientModal" tabindex="-1" aria-labelledby="recipientModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="recipientModalLabel">Crear Nuevo Destinatario</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <RecipientForm @recipient-created="handleRecipientCreated" :isModalCreate="true" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useExpenseStore } from '../../stores/expense';
import { useCategoryStore } from '../../stores/category';
import { useAccountStore } from '../../stores/account';
import { useRecipientStore } from '../../stores/recipient';

// Import the modal forms
import CategoryForm from '../categories/CategoryForm.vue';
import AccountForm from '../accounts/AccountForm.vue';
import RecipientForm from '../recipients/RecipientForm.vue';

// Bootstrap needs to be imported for modal to work
import * as bootstrap from 'bootstrap';

const route = useRoute();
const router = useRouter();
const expenseStore = useExpenseStore();
const categoryStore = useCategoryStore();
const accountStore = useAccountStore();
const recipientStore = useRecipientStore();

const isEditMode = computed(() => route.params.id !== undefined);
const expense = ref({
  description: '',
  amount: 0.0,
  date: new Date().toISOString().split('T')[0],
  application_date: new Date().toISOString().split('T')[0], // New field
  movement_type: 'expense',
  category_id: null,
  account_id: null,
  recipient_id: null,
  is_installment: false,
  num_installments: null,
  installment_amount: null,
});

const loading = computed(() => expenseStore.loading || categoryStore.loading || accountStore.loading || recipientStore.loading);
const error = computed(() => expenseStore.error || categoryStore.error || accountStore.error || recipientStore.error);
const categories = computed(() => categoryStore.categories);
const accounts = computed(() => accountStore.accounts);
const recipients = computed(() => recipientStore.recipients);

const selectedAccountIsCreditCard = computed(() => {
  const accountId = expense.value.account_id;
  if (accountId) {
    const account = accounts.value.find(acc => acc.id === accountId);
    return account ? account.is_credit_card : false;
  }
  return false;
});

watch(selectedAccountIsCreditCard, (newVal) => {
  if (newVal) {
    expense.value.is_installment = true;
    if (!expense.value.num_installments) {
      expense.value.num_installments = 1; // Default to 1 installment for credit card
    }
  } else {
    // If account changes from credit card to non-credit card, reset installment options
    if (!isEditMode.value) { // Only reset if not in edit mode to avoid overwriting existing expense
        expense.value.is_installment = false;
        expense.value.num_installments = null;
    }
  }
});

onMounted(async () => {
  await categoryStore.fetchCategories();
  await accountStore.fetchAccounts();
  await recipientStore.fetchRecipients();

  if (isEditMode.value) {
    const expenseId = parseInt(route.params.id);
    const fetchedExpense = expenseStore.expenses.find(exp => exp.id === expenseId);
    if (fetchedExpense) {
      expense.value = { ...fetchedExpense };
    } else {
      await expenseStore.fetchExpenses();
      const foundExpense = expenseStore.expenses.find(exp => exp.id === expenseId);
      if (foundExpense) {
        expense.value = { ...foundExpense };
      } else {
        alert('Movimiento no encontrado. Redirigiendo a la lista.');
        router.push('/expenses');
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    if (isEditMode.value) {
      await expenseStore.updateExpense(parseInt(route.params.id), expense.value);
    } else {
      await expenseStore.createExpense(expense.value);
    }
    router.push('/expenses');
  } catch (err) {
    console.error('No se pudo guardar el movimiento:', err);
  }
};

const handleCategoryCreated = async (newCategory) => {
  console.log('Category Created:', newCategory);
  await categoryStore.fetchCategories(); // Refresh categories
  expense.value.category_id = newCategory.id; // Select the newly created category
  const categoryModalElement = document.getElementById('categoryModal');
  console.log('categoryModalElement:', categoryModalElement);
  const categoryModal = bootstrap.Modal.getInstance(categoryModalElement) || new bootstrap.Modal(categoryModalElement);
  console.log('categoryModal instance:', categoryModal);
  if (categoryModal) {
    categoryModal.hide();
    console.log('Category Modal hide() called.');

    // Explicitly remove backdrop and clean up body classes, with a small delay
    setTimeout(() => {
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => {
        backdrop.remove();
        console.log('Removed modal-backdrop explicitly.');
      });
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }, 300);
  } else {
    console.warn('Could not get Bootstrap Modal instance for categoryModal.');
  }
};

const handleAccountCreated = async (newAccount) => {
  console.log('Account Created:', newAccount);
  await accountStore.fetchAccounts(); // Refresh accounts
  expense.value.account_id = newAccount.id; // Select the newly created account
  const accountModalElement = document.getElementById('accountModal');
  console.log('accountModalElement:', accountModalElement);
  const accountModal = bootstrap.Modal.getInstance(accountModalElement) || new bootstrap.Modal(accountModalElement);
  console.log('accountModal instance:', accountModal);
  if (accountModal) {
    accountModal.hide();
    console.log('Account Modal hide() called.');

    // Explicitly remove backdrop and clean up body classes, with a small delay
    setTimeout(() => {
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => {
        backdrop.remove();
        console.log('Removed modal-backdrop explicitly.');
      });
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }, 300);
  } else {
    console.warn('Could not get Bootstrap Modal instance for accountModal.');
  }
};

const handleRecipientCreated = async (newRecipient) => {
  console.log('Recipient Created:', newRecipient);
  await recipientStore.fetchRecipients(); // Refresh recipients
  expense.value.recipient_id = newRecipient.id; // Select the newly created recipient
  const recipientModalElement = document.getElementById('recipientModal');
  console.log('recipientModalElement:', recipientModalElement);
  const recipientModal = bootstrap.Modal.getInstance(recipientModalElement) || new bootstrap.Modal(recipientModalElement);
  console.log('recipientModal instance:', recipientModal);
  if (recipientModal) {
    recipientModal.hide();
    console.log('Recipient Modal hide() called.');

    // Explicitly remove backdrop and clean up body classes, with a small delay
    setTimeout(() => {
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => {
        backdrop.remove();
        console.log('Removed modal-backdrop explicitly.');
      });
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }, 300);
  } else {
    console.warn('Could not get Bootstrap Modal instance for recipientModal.');
  }
};
</script>
