<template>
  <div class="container mt-2 mb-4 px-2" style="max-width: 500px;">
    <!-- Header estilo Home -->
    <div v-if="authStore.user" class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Registro <span class="text-primary">Manual</span></h5>
      <p class="text-muted tiny mb-0">Completa los detalles del movimiento</p>
    </div>

    <div v-if="error" class="alert alert-danger py-1 px-2 small mb-3" role="alert">
      {{ error.message }}
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-3">
      <!-- Drag Handle estilo Home -->
      <div class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>

      <div class="card-header bg-white border-0 pt-1 px-3">
        <h6 class="mb-0 fw-bold smaller text-center">{{ isEditMode ? 'Editar Movimiento' : 'Nuevo Movimiento' }}</h6>
      </div>

      <div class="card-body p-3">
        <form @submit.prevent="handleSubmit">
          <!-- Fila de Campos Esenciales -->
          <div class="row g-2 mb-3 align-items-end">
            <div class="col-4">
              <label for="date" class="form-label tiny text-muted fw-bold mb-1 text-uppercase">Fecha</label>
              <input type="date" class="form-control form-control-sm border-0 bg-light rounded-3 px-1" id="date" v-model="expense.date" required />
            </div>
            <div class="col-4">
              <label for="movementType" class="form-label tiny text-muted fw-bold mb-1 text-uppercase">Tipo</label>
              <select class="form-select form-select-sm border-0 bg-light rounded-3 px-1" id="movementType" v-model="expense.movement_type" required>
                <option value="expense">Gasto</option>
                <option value="income">Ingreso</option>
              </select>
            </div>
            <div class="col-4">
              <label for="amount" class="form-label tiny text-muted fw-bold mb-1 text-uppercase">Monto</label>
              <div class="input-group input-group-sm">
                <span class="input-group-text bg-light border-0 rounded-start-3 px-1 text-muted">$</span>
                <input type="number" class="form-control border-0 bg-light rounded-end-3 ps-0" id="amount" v-model="expense.amount" required step="0.01" inputmode="decimal" placeholder="0" />
              </div>
            </div>
          </div>

          <!-- Sección: Cuenta y Pago -->
          <div class="mb-2 bg-light rounded-4 overflow-hidden">
            <button type="button" class="btn btn-light w-100 text-start d-flex justify-content-between align-items-center py-2 px-3 bg-transparent border-0" @click="showAccount = !showAccount">
                <span class="fw-bold text-dark smaller">Cuenta y Pago</span>
                <i class="bi text-muted smaller" :class="showAccount ? 'bi-chevron-down' : 'bi-chevron-right'"></i>
            </button>

            <div v-show="showAccount" class="p-3 pt-0">
              <div class="row g-2 mb-2 align-items-center">
                <div class="col-4">
                  <label for="accountId" class="form-label mb-0 tiny text-muted fw-bold text-uppercase">Cuenta:</label>
                </div>
                <div class="col-8">
                  <div class="input-group input-group-sm">
                    <select class="form-select border-0 bg-white rounded-start-3 py-1" id="accountId" v-model="expense.account_id">
                      <option :value="null">Seleccionar...</option>
                      <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
                    </select>
                    <button class="btn btn-white border-0 bg-white rounded-end-3 py-1" type="button" data-bs-toggle="modal" data-bs-target="#accountModal">
                      <i class="bi bi-plus-circle text-primary"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="selectedAccountIsCreditCard" class="row g-2 align-items-center">
                <div class="col-4">
                  <label for="numInstallments" class="form-label mb-0 tiny text-muted fw-bold text-uppercase">Cuotas:</label>
                </div>
                <div class="col-8">
                  <select class="form-select form-select-sm border-0 bg-white rounded-3 py-1" id="numInstallments" v-model="expense.num_installments">
                    <option v-for="n in 24" :key="n" :value="n">{{ n }} {{ n === 1 ? 'Cuota' : 'Cuotas' }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Sección: Detalles Adicionales -->
          <div class="mb-3 bg-light rounded-4 overflow-hidden">
            <button type="button" class="btn btn-light w-100 text-start d-flex justify-content-between align-items-center py-2 px-3 bg-transparent border-0" @click="showDetails = !showDetails">
                <span class="fw-bold text-dark smaller">Detalles</span>
                <i class="bi text-muted smaller" :class="showDetails ? 'bi-chevron-down' : 'bi-chevron-right'"></i>
            </button>

            <div v-show="showDetails" class="p-3 pt-0">
              
              <div class="row g-2 mb-2 align-items-center">
                <div class="col-4">
                  <label for="categoryId" class="form-label mb-0 tiny text-muted fw-bold text-uppercase">Categoría:</label>
                </div>
                <div class="col-8">
                  <div class="input-group input-group-sm">
                    <select class="form-select border-0 bg-white rounded-start-3 py-1" id="categoryId" v-model="expense.category_id">
                      <option :value="null">Seleccionar...</option>
                      <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
                    </select>
                    <button class="btn btn-white border-0 bg-white rounded-end-3 py-1" type="button" data-bs-toggle="modal" data-bs-target="#categoryModal">
                      <i class="bi bi-plus-circle text-primary"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="row g-2 mb-2 align-items-center">
                <div class="col-4">
                  <label for="recipientId" class="form-label mb-0 tiny text-muted fw-bold text-uppercase">Para:</label>
                </div>
                <div class="col-8">
                  <div class="input-group input-group-sm">
                    <select class="form-select border-0 bg-white rounded-start-3 py-1" id="recipientId" v-model="expense.recipient_id">
                      <option :value="null">Seleccionar...</option>
                      <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
                    </select>
                    <button class="btn btn-white border-0 bg-white rounded-end-3 py-1" type="button" data-bs-toggle="modal" data-bs-target="#recipientModal">
                      <i class="bi bi-plus-circle text-primary"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="row g-2 align-items-center">
                <div class="col-4">
                  <label for="description" class="form-label mb-0 tiny text-muted fw-bold text-uppercase">Detalle:</label>
                </div>
                <div class="col-8">
                  <input type="text" class="form-control form-control-sm border-0 bg-white rounded-3 py-1" id="description" v-model="expense.description" placeholder="Ej: Compra super" required />
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100 fw-bold rounded-pill py-2 shadow-sm mb-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isEditMode ? 'Actualizar Movimiento' : 'Guardar Movimiento' }}
          </button>
          
          <div class="text-center">
              <button v-if="!isEditMode" type="button" @click="resetForm" class="btn btn-link text-decoration-none text-muted tiny fw-bold p-0">LIMPIAR TODO</button>
              <router-link v-else to="/expenses" class="text-decoration-none text-muted tiny fw-bold">CANCELAR</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Modales -->
    <div class="modal fade" id="categoryModal" tabindex="-1" aria-labelledby="categoryModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-1 px-2">
            <h5 class="modal-title h6" id="categoryModalLabel">Nueva Categoría</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2">
            <CategoryForm @category-created="handleCategoryCreated" :isModalCreate="true" />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="accountModal" tabindex="-1" aria-labelledby="accountModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-1 px-2">
            <h5 class="modal-title h6" id="accountModalLabel">Nueva Cuenta</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2">
            <AccountForm @account-created="handleAccountCreated" :isModalCreate="true" />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="recipientModal" tabindex="-1" aria-labelledby="recipientModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-1 px-2">
            <h5 class="modal-title h6" id="recipientModalLabel">Nuevo Destinatario</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2">
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
import { useAuthStore } from '../../stores/auth'; // Store de Auth

// Modales
import CategoryForm from '../categories/CategoryForm.vue';
import AccountForm from '../accounts/AccountForm.vue';
import RecipientForm from '../recipients/RecipientForm.vue';

import * as bootstrap from 'bootstrap';
import apiClient from '../../api'; // Importar para llamar al backend

const route = useRoute();
const router = useRouter();
const expenseStore = useExpenseStore();
const categoryStore = useCategoryStore();
const accountStore = useAccountStore();
const recipientStore = useRecipientStore();
const authStore = useAuthStore(); // Usar store de auth

const isEditMode = computed(() => route.params.id !== undefined);

// Estado de UI de los collapsibles (Abiertos por defecto para reducir taps)
const showAccount = ref(true);
const showDetails = ref(true);

const expense = ref({
  description: '',
  amount: null,
  date: new Date().toLocaleDateString('en-CA'), // Formato YYYY-MM-DD local
  application_date: new Date().toLocaleDateString('en-CA'),
  movement_type: 'expense',
  category_id: null,
  account_id: null,
  recipient_id: null,
  is_installment: false,
  num_installments: null,
  installment_amount: null,
  status: 'completed'
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

// Auto-expandir cuenta si es tarjeta de crédito o si ya tiene algo seleccionado
watch(() => expense.value.account_id, (newVal) => {
  if (newVal) showAccount.value = true;
});

watch(selectedAccountIsCreditCard, (newVal) => {
  if (newVal) {
    expense.value.is_installment = true;
    if (!expense.value.num_installments) {
      expense.value.num_installments = 1; 
    }
    showAccount.value = true;
  } else {
    if (!isEditMode.value) {
        expense.value.is_installment = false;
        expense.value.num_installments = null;
    }
  }
});

onMounted(async () => {
  // Asegurar que el usuario esté cargado
  if (!authStore.user) {
    await authStore.fetchUser();
  }
  
  await categoryStore.fetchCategories();
  await accountStore.fetchAccounts();
  await recipientStore.fetchRecipients();

  if (isEditMode.value) {
    const expenseId = parseInt(route.params.id);
    const fetchedExpense = expenseStore.expenses.find(exp => exp.id === expenseId);
    if (fetchedExpense) {
      expense.value = { ...fetchedExpense };
      showAccount.value = true;
      showDetails.value = true;
    } else {
      // If filtering by status in store, it might not be there if we came from list or direct link
      await expenseStore.fetchExpenses(); 
      const foundExpense = expenseStore.expenses.find(exp => exp.id === expenseId);
      if (foundExpense) {
        expense.value = { ...foundExpense };
        showAccount.value = true;
        showDetails.value = true;
      } else {
        alert('Movimiento no encontrado. Redirigiendo a la lista.');
        router.push('/expenses');
      }
    }
  }
});

const resetForm = () => {
  expense.value = {
    description: '',
    amount: null,
    date: new Date().toLocaleDateString('en-CA'),
    application_date: new Date().toLocaleDateString('en-CA'),
    movement_type: 'expense',
    category_id: null,
    account_id: null,
    recipient_id: null,
    is_installment: false,
    num_installments: null,
    installment_amount: null,
    status: 'completed',
  };
};

const handleSubmit = async () => {
  try {
    // Remove derived/internal fields that are not in the backend schemas
    const { id, user_id, tenant_id, installment_amount, ...payload } = expense.value;
    
    // Always set status to completed when saving from the form
    payload.status = 'completed';

    if (isEditMode.value) {
      await expenseStore.updateExpense(parseInt(route.params.id), payload);
    } else {
      await expenseStore.createExpense(payload);
    }
    if (isEditMode.value) {
      // Redirect back to where we came from or default to expenses
      const redirectTo = expense.value.status === 'pending' || route.query.from === 'inbox' ? '/inbox' : '/expenses';
      router.push(redirectTo);
    } else {
      resetForm(); // Limpiar después de guardar si es carga rápida
      alert("Movimiento guardado con éxito.");
    }
  } catch (err) {
    console.error('No se pudo guardar el movimiento:', err);
  }
};

const handleCategoryCreated = async (newCategory) => {
  await categoryStore.fetchCategories(); 
  expense.value.category_id = newCategory.id; 
  closeModal('categoryModal');
};

const handleAccountCreated = async (newAccount) => {
  await accountStore.fetchAccounts(); 
  expense.value.account_id = newAccount.id; 
  closeModal('accountModal');
};

const handleRecipientCreated = async (newRecipient) => {
  await recipientStore.fetchRecipients(); 
  expense.value.recipient_id = newRecipient.id; 
  closeModal('recipientModal');
};

const closeModal = (modalId) => {
  const modalElement = document.getElementById(modalId);
  const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
  if (modalInstance) {
    modalInstance.hide();
    setTimeout(() => {
      document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }, 300);
  }
};
</script>

<style scoped>
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

.form-control-sm, .form-select-sm, .input-group-text {
  font-size: 0.85rem;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}

.btn-white {
  background-color: white;
  color: #0d6efd;
}

/* Sombras suaves para inputs tipo Home */
input:focus, select:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
  background-color: white !important;
}
</style>
