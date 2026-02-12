<template>
  <div>
    <h2 class="mb-4">{{ isEditMode ? 'Editar Destinatario' : 'Crear Nuevo Destinatario' }}</h2>
    <div v-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="recipientName" class="form-label">Nombre del Destinatario</label>
        <input
          type="text"
          class="form-control"
          id="recipientName"
          v-model="recipient.name"
          required
        />
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isEditMode ? 'Actualizar Destinatario' : 'Crear Destinatario' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineEmits, defineProps } from 'vue';
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
  await recipientStore.fetchRecipients(); // Fetch all recipients first

  if (!props.isModalCreate && isEditMode.value) {
    const recipientId = parseInt(route.params.id);
    const fetchedRecipient = recipientStore.recipients.find(rec => rec.id === recipientId);
    if (fetchedRecipient) {
      recipient.value = { ...fetchedRecipient };
    } else {
      await recipientStore.fetchRecipients(); // Re-fetch in case it wasn't there initially
      const foundRecipient = recipientStore.recipients.find(rec => rec.id === recipientId);
      if (foundRecipient) {
        recipient.value = { ...foundRecipient };
      } else {
        alert('Destinatario no encontrado. Redirigiendo a la lista.');
        router.push('/recipients');
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    if (isEditMode.value) {
      await recipientStore.updateRecipient(parseInt(route.params.id), recipient.value);
      router.push('/recipients'); // Still route for standalone edit mode
    } else {
      const newRecipient = await recipientStore.createRecipient(recipient.value);
      emit('recipient-created', newRecipient);
      // Reset form for next creation
      recipient.value = { name: '' };
    }
  } catch (err) {
    console.error('No se pudo guardar el destinatario:', err);
    // Error message will be displayed by the template via the computed 'error'
  }
};
</script>