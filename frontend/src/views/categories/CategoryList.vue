<template>
  <div class="container mt-4">
    <h2 class="mb-4">Categorías</h2>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      Error: {{ error.message }}
    </div>
    <div v-else>
      <router-link to="/categories/new" class="btn btn-primary mb-3">Agregar Nueva Categoría</router-link>
      <!-- Desktop View (List) -->
      <div class="d-none d-md-block">
        <ul class="list-group">
          <CategoryTreeItem
            v-for="category in categoryTree"
            :key="category.id"
            :category="category"
            :level="0"
            @delete-category="handleDeleteCategory"
          />
        </ul>
      </div>

      <!-- Mobile View (Cards) -->
      <div class="d-block d-md-none">
        <div class="row">
          <div v-for="category in categoryTree" :key="category.id" class="col-12 mb-3">
            <CategoryCardItem
              :category="category"
              :level="0"
              @delete-category="handleDeleteCategory"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useCategoryStore } from '../../stores/category';
import CategoryTreeItem from '../../components/CategoryTreeItem.vue';
import CategoryCardItem from '../../components/CategoryCardItem.vue';

const categoryStore = useCategoryStore();
const allCategories = computed(() => categoryStore.categories);
const loading = computed(() => categoryStore.loading);
const error = computed(() => categoryStore.error);

// Function to build the hierarchical tree from a flat list
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
        // If parent not found (e.g., deleted or invalid parent_id), treat as top-level
        tree.push(categoryMap.get(cat.id));
      }
    }
  });

  // Sort top-level and children by name for consistent display
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
      categoryStore.fetchCategories(); // Re-fetch categories after deletion
    } catch (err) {
      console.error('No se pudo eliminar la categoría:', err);
      alert('No se pudo eliminar la categoría.');
    }
  }
};
</script>