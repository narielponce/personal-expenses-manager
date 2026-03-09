<template>
  <div class="container mt-3 mb-4 px-2" style="max-width: 500px;">
    <!-- Header con Bienvenida - Margen ajustado -->
    <div v-if="authStore.user" class="text-center mt-2 mb-2">
      <p class="text-muted small mb-0">Bienvenido, <span class="fw-bold text-dark">{{ authStore.user.email }}</span></p>
    </div>

    <h2 class="h5 text-center mt-3 mb-4 fw-bold text-dark">{{ isEditMode ? 'Editar Movimiento' : 'Registrar Movimiento' }}</h2>
    
    <div v-if="error" class="alert alert-danger py-1 px-2 small mb-3" role="alert">
      {{ error.message }}
    </div>

    <!-- Botones de Entrada Rápida - Más grandes/cuadrados -->
    <div class="row g-2 mb-4">
      <div class="col-6">
        <button 
          type="button" 
          @click="toggleRecording"
          class="btn w-100 h-100 py-3 rounded-4 d-flex flex-column align-items-center justify-content-center text-white shadow-sm border-0 position-relative" 
          :style="{ backgroundColor: isRecording ? '#d32f2f' : '#2E64FE', minHeight: '110px' }"
          :disabled="isProcessingVoice"
        >
          <div v-if="isRecording" class="recording-ripple"></div>
          <i class="bi fs-1 mb-2" :class="isRecording ? 'bi-stop-fill' : 'bi-mic-fill'"></i>
          <span class="fw-bold">{{ isRecording ? 'Detener' : (isProcessingVoice ? 'Procesando...' : 'Grabar Gasto') }}</span>
        </button>
      </div>
      <div class="col-6">
        <button type="button" class="btn w-100 h-100 py-3 rounded-4 d-flex flex-column align-items-center justify-content-center text-white shadow-sm" style="background-color: #388E3C; border: none; minHeight: 110px;">
          <i class="bi bi-camera-fill fs-1 mb-2"></i>
          <span class="fw-bold text-wrap lh-sm">Foto Ticket</span>
        </button>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="bg-white p-2 rounded-4 shadow-sm border">
      <!-- Fila de Campos Esenciales - Margen mb-2 -->
      <div class="row g-2 mb-2 align-items-end">
        <div class="col-4">
          <label for="date" class="form-label smaller text-muted mb-0">Fecha</label>
          <input type="date" class="form-control form-control-sm border-secondary-subtle px-1" id="date" v-model="expense.date" required />
        </div>
        <div class="col-4">
          <label for="movementType" class="form-label smaller text-muted mb-0">Tipo</label>
          <select class="form-select form-select-sm border-secondary-subtle px-1" id="movementType" v-model="expense.movement_type" required>
            <option value="expense">Gasto</option>
            <option value="income">Ingreso</option>
          </select>
        </div>
        <div class="col-4">
          <label for="amount" class="form-label smaller text-muted mb-0">Monto</label>
          <div class="input-group input-group-sm">
            <span class="input-group-text bg-white border-end-0 border-secondary-subtle px-1 text-muted">$</span>
            <input type="number" class="form-control border-start-0 ps-0 border-secondary-subtle" id="amount" v-model="expense.amount" required step="0.01" inputmode="decimal" placeholder="0" />
          </div>
        </div>
      </div>

      <!-- Sección: Cuenta y Pago - Margen mb-1 -->
      <div class="mb-1 border border-secondary-subtle rounded-3 overflow-hidden">
        <button type="button" class="btn btn-light w-100 text-start d-flex justify-content-between align-items-center py-1 px-2 bg-light border-0" @click="showAccount = !showAccount">
            <span class="fw-semibold text-dark smaller">Cuenta y Pago</span>
            <i class="bi bi-chevron-down text-muted smaller" v-if="showAccount"></i>
            <i class="bi bi-chevron-right text-muted smaller" v-else></i>
        </button>

        <div v-show="showAccount" class="p-2 bg-white border-top border-secondary-subtle">
          <div class="row g-2 mb-1 align-items-center">
            <div class="col-4 text-end">
              <label for="accountId" class="form-label mb-0 smaller text-muted text-truncate">Cuenta:</label>
            </div>
            <div class="col-8">
              <div class="input-group input-group-sm">
                <select class="form-select border-secondary-subtle py-0" id="accountId" v-model="expense.account_id">
                  <option :value="null">Seleccionar...</option>
                  <option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option>
                </select>
                <button class="btn btn-outline-secondary border-secondary-subtle py-0" type="button" data-bs-toggle="modal" data-bs-target="#accountModal">
                  <i class="bi bi-plus"></i>
                </button>
              </div>
            </div>
          </div>

          <div v-if="selectedAccountIsCreditCard" class="row g-2 align-items-center">
            <div class="col-4 text-end">
              <label for="numInstallments" class="form-label mb-0 smaller text-muted">Cuotas:</label>
            </div>
            <div class="col-8">
              <select class="form-select form-select-sm border-secondary-subtle py-0" id="numInstallments" v-model="expense.num_installments">
                <option v-for="n in 24" :key="n" :value="n">{{ n }} {{ n === 1 ? 'Cuota' : 'Cuotas' }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Sección: Detalles Adicionales - Margen mb-2 -->
      <div class="mb-2 border border-secondary-subtle rounded-3 overflow-hidden">
        <button type="button" class="btn btn-light w-100 text-start d-flex justify-content-between align-items-center py-1 px-2 bg-light border-0" @click="showDetails = !showDetails">
            <span class="fw-semibold text-dark smaller">Detalles Adicionales</span>
            <i class="bi bi-chevron-down text-muted smaller" v-if="showDetails"></i>
            <i class="bi bi-chevron-right text-muted smaller" v-else></i>
        </button>

        <div v-show="showDetails" class="p-2 bg-white border-top border-secondary-subtle">
          
          <div class="row g-2 mb-1 align-items-center">
            <div class="col-4 text-end">
              <label for="categoryId" class="form-label mb-0 smaller text-muted text-truncate">Categoría:</label>
            </div>
            <div class="col-8">
              <div class="input-group input-group-sm">
                <select class="form-select border-secondary-subtle py-0" id="categoryId" v-model="expense.category_id">
                  <option :value="null">Seleccionar...</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
                </select>
                <button class="btn btn-outline-secondary border-secondary-subtle py-0" type="button" data-bs-toggle="modal" data-bs-target="#categoryModal">
                  <i class="bi bi-plus"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="row g-2 mb-1 align-items-center">
            <div class="col-4 text-end">
              <label for="recipientId" class="form-label mb-0 smaller text-muted text-truncate">Destinatario:</label>
            </div>
            <div class="col-8">
              <div class="input-group input-group-sm">
                <select class="form-select border-secondary-subtle py-0" id="recipientId" v-model="expense.recipient_id">
                  <option :value="null">Seleccionar...</option>
                  <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
                </select>
                <button class="btn btn-outline-secondary border-secondary-subtle py-0" type="button" data-bs-toggle="modal" data-bs-target="#recipientModal">
                  <i class="bi bi-plus"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="row g-2 align-items-center">
            <div class="col-4 text-end">
              <label for="description" class="form-label mb-0 smaller text-muted">Descripción:</label>
            </div>
            <div class="col-8">
              <input type="text" class="form-control form-control-sm border-secondary-subtle py-0" id="description" v-model="expense.description" placeholder="Ej: Super" required />
            </div>
          </div>
        </div>
      </div>

      <button type="submit" class="btn btn-lg w-100 fw-bold text-white mb-1 shadow-sm rounded-3 py-1" style="background-color: #E66A1D; border: none;" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isEditMode ? 'Actualizar' : 'Guardar' }}
      </button>
      <div class="text-center">
          <button v-if="!isEditMode" type="button" @click="resetForm" class="btn btn-link text-decoration-none text-secondary smaller fw-medium p-0">Limpiar Formulario</button>
          <router-link v-else to="/expenses" class="text-decoration-none text-secondary smaller fw-medium">Cancelar</router-link>
      </div>
    </form>

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

// Estado de grabación de voz
const isRecording = ref(false);
const isProcessingVoice = ref(false);
let recognition = null;

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
  };
};

const handleSubmit = async () => {
  try {
    if (isEditMode.value) {
      await expenseStore.updateExpense(parseInt(route.params.id), expense.value);
    } else {
      await expenseStore.createExpense(expense.value);
    }
    if (isEditMode.value) {
      router.push('/expenses');
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

// --- Lógica de Voz ---
const toggleRecording = () => {
  if (isRecording.value) {
    recognition.stop();
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Lo siento, tu navegador no soporta reconocimiento de voz.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'es-ES';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isRecording.value = true;
  };

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    console.log("Texto detectado:", text);
    processVoiceText(text);
  };

  recognition.onerror = (event) => {
    console.error("Error en reconocimiento:", event.error);
    isRecording.value = false;
  };

  recognition.onend = () => {
    isRecording.value = false;
  };

  recognition.start();
};

const processVoiceText = async (text) => {
  isProcessingVoice.value = true;
  try {
    const response = await apiClient.post('/process-voice', { text: text });
    const data = response.data;
    
    // Autocompletar el formulario básico
    if (data.amount) expense.value.amount = data.amount;
    if (data.description) expense.value.description = data.description;
    if (data.date) expense.value.date = data.date;
    if (data.movement_type) expense.value.movement_type = data.movement_type;

    // Lógica de coincidencia difusa para listas (Ignora mayúsculas y acentos)
    const normalize = (str) => str ? str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : "";

    // 1. Asignar Cuenta
    if (data.account_hint) {
      const hint = normalize(data.account_hint);
      const matchedAccount = accounts.value.find(acc => normalize(acc.name).includes(hint) || hint.includes(normalize(acc.name)));
      if (matchedAccount) {
        expense.value.account_id = matchedAccount.id;
        // 2. Asignar Cuotas si la cuenta es de crédito
        if (data.installments && matchedAccount.is_credit_card) {
          expense.value.is_installment = true;
          expense.value.num_installments = data.installments;
        }
      }
    }

    // 3. Asignar Destinatario
    if (data.recipient_hint) {
      const hint = normalize(data.recipient_hint);
      const matchedRecipient = recipients.value.find(rec => normalize(rec.name).includes(hint) || hint.includes(normalize(rec.name)));
      if (matchedRecipient) {
        expense.value.recipient_id = matchedRecipient.id;
      }
    }

    // 4. Asignar Categoría
    if (data.category_hint) {
      const hint = normalize(data.category_hint);
      const matchedCategory = categories.value.find(cat => normalize(cat.name).includes(hint) || hint.includes(normalize(cat.name)));
      if (matchedCategory) {
        expense.value.category_id = matchedCategory.id;
      }
    }

    // Expandir secciones si se llenaron datos
    showDetails.value = true;
    showAccount.value = true;
    
    console.log("Formulario actualizado por Gemini:", data);
  } catch (err) {
    console.error("Error al procesar voz con Gemini:", err);
    alert("Hubo un error al procesar tu voz con la IA. Por favor, inténtalo de nuevo.");
  } finally {
    isProcessingVoice.value = false;
  }
};
</script>

<style scoped>
.recording-ripple {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.3);
  animation: ripple 1.5s infinite;
}

@keyframes ripple {
  0% { transform: scale(0.9); opacity: 1; }
  100% { transform: scale(1.1); opacity: 0; }
}

.smaller {
  font-size: 0.75rem;
}
.form-control-sm, .form-select-sm, .input-group-text {
  font-size: 0.85rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
.btn-lg {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
</style>
