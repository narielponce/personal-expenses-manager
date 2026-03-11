<template>
  <div class="category-item mb-2" :class="{ 'ms-3': level > 0 }">
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-body p-2 px-3">
        <div class="d-flex align-items-center gap-2">
          
          <!-- Icono Expansión / Nivel -->
          <div class="d-flex align-items-center">
            <button 
              v-if="category.children && category.children.length" 
              @click="toggleExpand" 
              class="btn btn-link text-primary p-0 me-2"
              style="font-size: 1.1rem; line-height: 1;"
            >
              <i :class="isExpanded ? 'bi bi-dash-square-fill' : 'bi bi-plus-square-fill'"></i>
            </button>
            <div v-else class="me-2 text-secondary opacity-25" style="width: 1.1rem;">
              <i class="bi bi-dot fs-4"></i>
            </div>
          </div>

          <!-- Info Principal -->
          <div class="flex-grow-1 min-width-0">
            <span class="fw-bold text-dark d-block text-truncate mb-0 smaller" :title="category.name">
              {{ category.name }}
            </span>
          </div>

          <!-- Acciones discretas -->
          <div class="d-flex align-items-center ms-auto action-buttons">
            <router-link :to="`/categories/${category.id}/edit`" class="btn btn-link text-warning p-1" title="Editar">
              <i class="bi bi-pencil-square fs-5"></i>
            </router-link>
            
            <button @click="$emit('delete-category', category.id)" class="btn btn-link text-danger p-1" title="Eliminar">
              <i class="bi bi-trash fs-5"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Subcategorías Recursivas -->
      <div v-if="category.children && category.children.length && isExpanded" class="bg-light-subtle border-top py-2 px-1">
        <CategoryCardItem
          v-for="child in category.children"
          :key="child.id"
          :category="child"
          :level="level + 1"
          @delete-category="$emit('delete-category', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';

defineProps({
  category: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
});

defineEmits(['delete-category']);

const isExpanded = ref(false);

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};
</script>

<style scoped>
.smaller {
  font-size: 0.75rem;
}

.min-width-0 {
  min-width: 0;
}

.bg-light-subtle {
  background-color: rgba(0, 0, 0, 0.02) !important;
}

.action-buttons .btn-link {
  text-decoration: none;
  opacity: 0.7;
}
.action-buttons .btn-link:hover {
  opacity: 1;
}

.card {
  width: 100%;
}
</style>
