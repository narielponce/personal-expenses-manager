<template>
  <div class="container mt-2 mb-4 px-2" style="max-width: 600px;">
    <h2 class="h5 text-center mb-3 fw-bold text-dark">Destinatarios</h2>
    
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2 small" role="alert">
      Error: {{ error.message }}
    </div>
    
    <div v-else>
      <div class="d-grid mb-3">
        <router-link to="/recipients/new" class="btn btn-primary fw-semibold rounded-3 shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> Agregar Nuevo Destinatario
        </router-link>
      </div>

      <!-- Unified View for Recipients -->
      <div class="recipient-list">
        <div v-for="recipient in recipients" :key="recipient.id" class="mb-2">
          <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
            <div class="card-body p-2">
              <div class="d-flex align-items-center flex-wrap gap-2">
                
                <!-- Icono de Persona -->
                <div class="d-flex align-items-center me-2 text-primary" style="width: 1.2rem;">
                  <i class="bi bi-person-fill fs-5"></i>
                </div>

                <!-- Nombre -->
                <div class="flex-grow-1 min-width-0">
                  <span class="fw-medium text-dark d-block text-truncate w-100" :title="recipient.name">
                    {{ recipient.name }}
                  </span>
                </div>

                <!-- Acciones -->
                <div class="d-flex align-items-center ms-auto action-buttons">
                  <router-link :to="`/recipients/${recipient.id}`" class="btn btn-light-blue btn-sm border-0 rounded-2 me-1" title="Ver">
                    <i class="bi bi-eye text-primary"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-primary">Ver</span>
                  </router-link>
                  
                  <router-link :to="`/recipients/${recipient.id}/edit`" class="btn btn-light-warning btn-sm border-0 rounded-2 me-1" title="Editar">
                    <i class="bi bi-pencil text-warning-emphasis"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-warning-emphasis">Editar</span>
                  </router-link>
                  
                  <button @click="deleteRecipient(recipient.id)" class="btn btn-light-danger btn-sm border-0 rounded-2" title="Eliminar">
                    <i class="bi bi-trash text-danger"></i>
                    <span class="d-none d-sm-inline ms-1 smaller text-danger">Borrar</span>
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
import { useRecipientStore } from '../../stores/recipient';

const recipientStore = useRecipientStore();
const recipients = computed(() => recipientStore.recipients);
const loading = computed(() => recipientStore.loading);
const error = computed(() => recipientStore.error);

onMounted(() => {
  recipientStore.fetchRecipients();
});

const deleteRecipient = async (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar este destinatario?')) {
    try {
      await recipientStore.deleteRecipient(id);
      recipientStore.fetchRecipients(); // Re-fetch recipients after deletion
    } catch (err) {
      console.error('No se pudo eliminar el destinatario:', err);
    }
  }
};
</script>

<style scoped>
.recipient-list {
  margin-bottom: 2rem;
}

.smaller {
  font-size: 0.75rem;
  font-weight: 600;
}

.min-width-0 {
  min-width: 0;
}

/* Colores de botones sutiles similares a categorías/login */
.btn-light-blue {
  background-color: #e7f1ff;
}
.btn-light-blue:hover {
  background-color: #cfe2ff;
}

.btn-light-warning {
  background-color: #fff3cd;
}
.btn-light-warning:hover {
  background-color: #ffecb5;
}

.btn-light-danger {
  background-color: #f8d7da;
}
.btn-light-danger:hover {
  background-color: #f1aeb5;
}

.action-buttons .btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
}

/* Evitar que los botones se achiquen demasiado */
.action-buttons {
  flex-shrink: 0;
}

/* Estilo de la tarjeta */
.card {
  transition: transform 0.1s ease-in-out;
  border: 1px solid rgba(0,0,0,0.05) !important;
}
</style>
