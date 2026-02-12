<template>
  <div>
    <h2 class="mb-4">{{ isEditMode ? 'Editar Cuenta' : 'Crear Nueva Cuenta' }}</h2>
    <div v-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="accountName" class="form-label">Nombre de la Cuenta</label>
        <input
          type="text"
          class="form-control"
          id="accountName"
          v-model="account.name"
          required
        />
      </div>
      <div class="mb-3 form-check">
        <input type="checkbox" class="form-check-input" id="isCreditCard" v-model="account.is_credit_card" />
        <label class="form-check-label" for="isCreditCard">¿Es Tarjeta de Crédito?</label>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isEditMode ? 'Actualizar Cuenta' : 'Crear Cuenta' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineEmits, defineProps } from 'vue';
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
  is_credit_card: false, // New field
});
const loading = computed(() => accountStore.loading);
const error = computed(() => accountStore.error);

onMounted(async () => {
  await accountStore.fetchAccounts(); // Fetch all accounts first

  if (!props.isModalCreate && isEditMode.value) {
    const accountId = parseInt(route.params.id);
    const fetchedAccount = accountStore.accounts.find(acc => acc.id === accountId);
    if (fetchedAccount) {
      account.value = { ...fetchedAccount };
    } else {
      await accountStore.fetchAccounts(); // Re-fetch in case it wasn't there initially
      const foundAccount = accountStore.accounts.find(acc => acc.id === accountId);
      if (foundAccount) {
        account.value = { ...foundAccount };
      } else {
        alert('Cuenta no encontrada. Redirigiendo a la lista.');
        router.push('/accounts');
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    if (isEditMode.value) {
      await accountStore.updateAccount(parseInt(route.params.id), account.value);
      router.push('/accounts'); // Still route for standalone edit mode
    } else {
      const newAccount = await accountStore.createAccount(account.value);
      emit('account-created', newAccount);
      // Reset form for next creation
      account.value = { name: '', is_credit_card: false };
    }
  } catch (err) {
    console.error('No se pudo guardar la cuenta:', err);
    // Error message will be displayed by the template via the computed 'error'
  }
};
</script>
