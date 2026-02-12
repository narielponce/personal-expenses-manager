<template>
  <div>
    <h2 class="mb-4">{{ isEditMode ? 'Editar Categoría' : 'Crear Nueva Categoría' }}</h2>
    <div v-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="categoryName" class="form-label">Nombre de la Categoría</label>
        <input
          type="text"
          class="form-control"
          id="categoryName"
          v-model="category.name"
          required
        />
      </div>
      <div class="mb-3">
        <label for="parentCategory" class="form-label">Categoría Padre (Opcional)</label>
        <select class="form-select" id="parentCategory" v-model="category.parent_id">
          <option :value="null">-- Ninguna --</option>
          <option v-for="cat in availableParentCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isEditMode ? 'Actualizar Categoría' : 'Crear Categoría' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineEmits, defineProps } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCategoryStore } from '../../stores/category';

const props = defineProps({
  isModalCreate: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['category-created']);

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();

const isEditMode = computed(() => !props.isModalCreate && route.params.id !== undefined);
const category = ref({
  name: '',
  parent_id: null, // New field
});
const loading = computed(() => categoryStore.loading);
const error = computed(() => categoryStore.error);
const allCategories = computed(() => categoryStore.categories);

const availableParentCategories = computed(() => {
  // Filter out the current category to prevent self-referencing and circular dependencies
  return allCategories.value.filter(cat => cat.id !== category.value.id);
});

onMounted(async () => {
  await categoryStore.fetchCategories();

  if (!props.isModalCreate && isEditMode.value) {
    const categoryId = parseInt(route.params.id);
    const fetchedCategory = allCategories.value.find(cat => cat.id === categoryId);
    if (fetchedCategory) {
      category.value = { ...fetchedCategory };
    } else {
      await categoryStore.fetchCategories(); // Re-fetch in case it wasn't there initially
      const foundCategory = allCategories.value.find(cat => cat.id === categoryId);
      if (foundCategory) {
        category.value = { ...foundCategory };
      } else {
        alert('Categoría no encontrada. Redirigiendo a la lista.');
        router.push('/categories');
      }
    }
  }
});

const handleSubmit = async () => {
  try {
    if (isEditMode.value) {
      await categoryStore.updateCategory(parseInt(route.params.id), category.value);
      router.push('/categories'); // Still route for standalone edit mode
    } else {
      const newCategory = await categoryStore.createCategory(category.value);
      emit('category-created', newCategory);
      // Reset form for next creation
      category.value = { name: '', parent_id: null };
    }
  } catch (err) {
    console.error('No se pudo guardar la categoría:', err);
    // Error message will be displayed by the template via the computed 'error'
  }
};
</script>