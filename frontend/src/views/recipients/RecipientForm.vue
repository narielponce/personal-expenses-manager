<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" :style="{ maxWidth: isModalCreate ? '100%' : '500px', marginLeft: 'auto', marginRight: 'auto' }">
    <!-- Header estilo Home -->
    <div v-if="!isModalCreate" class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">{{ isEditMode ? 'Editar' : 'Nuevo' }} <span class="text-primary">Destinatario</span></h5>
      <p class="text-muted tiny mb-0">Registra a quién diriges tus movimientos</p>
    </div>

    <div v-if="error" class="alert alert-danger py-1 px-2 small mb-3" role="alert">
      {{ error.message }}
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-3">
      <!-- Drag Handle estilo Home -->
      <div v-if="!isModalCreate" class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>

      <div class="card-header bg-white border-0 pt-1 px-3">
        <h6 class="mb-0 fw-bold smaller text-center">{{ isEditMode ? 'Detalles de Destinatario' : 'Ingresa los datos' }}</h6>
      </div>

      <div class="card-body p-3">
        <form @submit.prevent="handleSubmit">
          <div class="mb-4">
            <label for="name" class="form-label tiny text-muted fw-bold mb-1 text-uppercase">Nombre del Destinatario</label>
            <input 
              type="text" 
              class="form-control form-control-sm border-0 bg-light rounded-3 py-2 px-3" 
              id="name" 
              v-model="recipient.name" 
              placeholder="Ej: Supermercado, Juan Pérez, Alquiler..." 
              required 
            />
          </div>

          <button type="submit" class="btn btn-primary w-100 fw-bold rounded-pill py-2 shadow-sm mb-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isEditMode ? 'ACTUALIZAR DESTINATARIO' : 'GUARDAR DESTINATARIO' }}
          </button>
          
          <div v-if="!isModalCreate" class="text-center mt-2">
              <router-link to="/recipients" class="text-decoration-none text-muted tiny fw-bold">VOLVER AL LISTADO</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useRecipientStore } from '../../stores/recipient';

const props = defineProps({
  isModalCreate: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['recipient-created']);

const route = useRoute();
const router = useRouter();
const recipientStore = useRecipientStore();

const isEditMode = computed(() => !props.isModalCreate && route.params.id !== undefined);

const recipient = ref({
  name: '',
});

const loading = computed(() => recipientStore.loading);
const error = computed(() => recipientStore.error);

onMounted(async () => {
  if (isEditMode.value) {
    const recipientId = parseInt(route.params.id);
    const fetchedRecipient = recipientStore.recipients.find(rec => rec.id === recipientId);
    if (fetchedRecipient) {
      recipient.value = { ...fetchedRecipient };
    } else {
      await recipientStore.fetchRecipients();
      const foundRecipient = recipientStore.recipients.find(rec => rec.id === recipientId);
      if (foundRecipient) {
        recipient.value = { ...foundRecipient };
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    let result;
    if (isEditMode.value) {
      result = await recipientStore.updateRecipient(parseInt(route.params.id), recipient.value);
    } else {
      result = await recipientStore.createRecipient(recipient.value);
    }
    
    if (props.isModalCreate) {
      emit('recipient-created', result);
    } else {
      router.push('/recipients');
    }
  } catch (err) {
    console.error('Error saving recipient:', err);
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

.form-control-sm {
  font-size: 0.85rem;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}

/* Sombras suaves para inputs tipo Home */
input:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
  background-color: white !important;
}
</style>
