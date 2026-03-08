<template>
  <div class="container mt-2 mb-4 px-2" style="max-width: 600px;">
    <h2 class="h5 text-center mb-3 fw-bold text-dark">Categorías</h2>
    
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
        <router-link to="/categories/new" class="btn btn-primary fw-semibold rounded-3 shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> Agregar Nueva Categoría
        </router-link>
      </div>

      <!-- Unified View (Better for both but optimized for mobile feel) -->
      <div class="category-tree">
        <CategoryCardItem
          v-for="category in categoryTree"
          :key="category.id"
          :category="category"
          :level="0"
          @delete-category="handleDeleteCategory"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useCategoryStore } from '../../stores/category';
import CategoryCardItem from '../../components/CategoryCardItem.vue';

const categoryStore = useCategoryStore();
const allCategories = computed(() => categoryStore.categories);
const loading = computed(() => categoryStore.loading);
const error = computed(() => categoryStore.error);

const buildCategoryTree = (categories) => {
  const categoryMap = new Map();
  categories.forEach(cat => categoryMap.set(cat.id, { ...cat, children: [] }));

  const tree = [];
  categories.forEach(cat => {
    if (cat.parent_id === null) {
      tree.push(categoryMap.get(cat.id));
    } else {
      const parent = categoryMap.get(cat.parent_id);
      if (parent) {
        parent.children.push(categoryMap.get(cat.id));
      } else {
        tree.push(categoryMap.get(cat.id));
      }
    }
  });

  const sortTree = (nodes) => {
    nodes.sort((a, b) => a.name.localeCompare(b.name));
    nodes.forEach(node => {
      if (node.children) {
        sortTree(node.children);
      }
    });
  };
  sortTree(tree);
  return tree;
};

const categoryTree = computed(() => buildCategoryTree(allCategories.value));

onMounted(() => {
  categoryStore.fetchCategories();
});

const handleDeleteCategory = async (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar esta categoría y todas sus subcategorías?')) {
    try {
      await categoryStore.deleteCategory(id);
      categoryStore.fetchCategories();
    } catch (err) {
      console.error('No se pudo eliminar la categoría:', err);
    }
  }
};
</script>

<style scoped>
.category-tree {
  margin-bottom: 2rem;
}
</style>
