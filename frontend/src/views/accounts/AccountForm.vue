<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 500px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">{{ isEditMode ? 'Editar' : 'Nueva' }} <span class="text-primary">Cuenta</span></h5>
      <p class="text-muted tiny mb-0">Configura tus medios de pago</p>
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
        <h6 class="mb-0 fw-bold smaller text-center">{{ isEditMode ? 'Detalles de Cuenta' : 'Ingresa los datos' }}</h6>
      </div>

      <div class="card-body p-3">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="name" class="form-label tiny text-muted fw-bold mb-1 text-uppercase">Nombre de la Cuenta</label>
            <input 
              type="text" 
              class="form-control form-control-sm border-0 bg-light rounded-3 py-2 px-3" 
              id="name" 
              v-model="account.name" 
              placeholder="Ej: Efectivo, Visa, Santander..." 
              required 
            />
          </div>

          <div class="mb-4">
            <div class="form-check form-switch d-flex align-items-center gap-2 ps-0 bg-light p-2 rounded-3">
              <label class="form-check-label tiny text-muted fw-bold mb-0 text-uppercase flex-grow-1 ms-2" for="isCreditCard">
                ¿Es una tarjeta de crédito?
              </label>
              <input 
                class="form-check-input ms-0 border-0 shadow-none" 
                type="checkbox" 
                role="switch" 
                id="isCreditCard" 
                v-model="account.is_credit_card"
              />
            </div>
            <div class="mt-2 px-2">
              <p class="text-muted italic mb-0" style="font-size: 0.6rem;">
                * Las tarjetas de crédito permiten el registro de gastos en cuotas.
              </p>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100 fw-bold rounded-pill py-2 shadow-sm mb-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isEditMode ? 'ACTUALIZAR CUENTA' : 'GUARDAR CUENTA' }}
          </button>
          
          <div class="text-center mt-2">
              <router-link to="/accounts" class="text-decoration-none text-muted tiny fw-bold">VOLVER AL LISTADO</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAccountStore } from '../../stores/account';

const props = defineProps({
  isModalCreate: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['account-created']);

const route = useRoute();
const router = useRouter();
const accountStore = useAccountStore();

const isEditMode = computed(() => !props.isModalCreate && route.params.id !== undefined);

const account = ref({
  name: '',
  is_credit_card: false,
});

const loading = computed(() => accountStore.loading);
const error = computed(() => accountStore.error);

onMounted(async () => {
  if (isEditMode.value) {
    const accountId = parseInt(route.params.id);
    const fetchedAccount = accountStore.accounts.find(acc => acc.id === accountId);
    if (fetchedAccount) {
      account.value = { ...fetchedAccount };
    } else {
      await accountStore.fetchAccounts();
      const foundAccount = accountStore.accounts.find(acc => acc.id === accountId);
      if (foundAccount) {
        account.value = { ...foundAccount };
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    let result;
    if (isEditMode.value) {
      result = await accountStore.updateAccount(parseInt(route.params.id), account.value);
    } else {
      result = await accountStore.createAccount(account.value);
    }
    
    if (props.isModalCreate) {
      emit('account-created', result);
    } else {
      router.push('/accounts');
    }
  } catch (err) {
    console.error('Error saving account:', err);
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

.italic {
  font-style: italic;
}

.form-control-sm {
  font-size: 0.85rem;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

/* Sombras suaves para inputs tipo Home */
input:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
  background-color: white !important;
}
</style>
