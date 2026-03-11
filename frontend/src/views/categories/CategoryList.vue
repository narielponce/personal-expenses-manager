<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 600px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Gestión de <span class="text-primary">Categorías</span></h5>
      <p class="text-muted tiny mb-0">Organiza tus gastos por conceptos</p>
    </div>
    
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
        <router-link to="/categories/new" class="btn btn-primary fw-bold rounded-pill shadow-sm py-2">
          <i class="bi bi-plus-lg me-1"></i> NUEVA CATEGORÍA
        </router-link>
      </div>

      <!-- Unified View estilo Home -->
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
.summary-container {
  width: 100%;
  overflow-x: hidden;
}

.user-header {
  border-left: 4px solid #0d6efd;
  padding-left: 12px;
}

.tiny {
  font-size: 0.65rem;
}

.category-tree {
  margin-bottom: 2rem;
}

.btn-primary {
  background-color: #0d6efd;
  border: none;
}
</style>
