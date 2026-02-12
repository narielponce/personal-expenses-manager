<template>
  <div class="container mt-4">
    <h2 class="mb-4">Destinatarios</h2>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <div v-else>
      <router-link to="/recipients/new" class="btn btn-primary mb-3">Agregar Nuevo Destinatario</router-link>
      <!-- Desktop View (List) -->
      <div class="d-none d-md-block">
        <ul class="list-group">
          <li v-for="recipient in recipients" :key="recipient.id" class="list-group-item d-flex justify-content-between align-items-center">
            {{ recipient.name }}
            <div>
              <router-link :to="`/recipients/${recipient.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
              <router-link :to="`/recipients/${recipient.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
              <button @click="deleteRecipient(recipient.id)" class="btn btn-danger btn-sm">Eliminar</button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Mobile View (Cards) -->
      <div class="d-block d-md-none">
        <div class="row">
          <div v-for="recipient in recipients" :key="recipient.id" class="col-12 mb-3">
            <div class="card">
              <div class="card-body d-flex justify-content-between align-items-center">
                <h5 class="card-title">{{ recipient.name }}</h5>
                <div>
                  <router-link :to="`/recipients/${recipient.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
                  <router-link :to="`/recipients/${recipient.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
                  <button @click="deleteRecipient(recipient.id)" class="btn btn-danger btn-sm">Eliminar</button>
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
      alert('No se pudo eliminar el destinatario.');
    }
  }
};
</script>