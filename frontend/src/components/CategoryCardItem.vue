<template>
  <div class="category-item mb-2" :class="{ 'ms-3': level > 0 }">
    <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
      <div class="card-body p-2">
        <div class="d-flex align-items-center flex-wrap gap-2">
          
          <!-- Icono Expansión / Nivel -->
          <div class="d-flex align-items-center">
            <button 
              v-if="category.children && category.children.length" 
              @click="toggleExpand" 
              class="btn btn-link text-primary p-0 me-2"
              style="font-size: 1.2rem; line-height: 1;"
            >
              <i :class="isExpanded ? 'bi bi-dash-square-fill' : 'bi bi-plus-square-fill'"></i>
            </button>
            <div v-else class="me-2 text-secondary opacity-25" style="width: 1.2rem;">
              <i class="bi bi-dot fs-4"></i>
            </div>
          </div>

          <!-- Nombre Categoría -->
          <div class="flex-grow-1 min-width-0">
            <span class="fw-medium text-dark d-block text-truncate" :title="category.name">
              {{ category.name }}
            </span>
          </div>

          <!-- Acciones - Ajuste flexible -->
          <div class="d-flex align-items-center ms-auto action-buttons">
            <router-link :to="`/categories/${category.id}`" class="btn btn-light-blue btn-sm border-0 rounded-2 me-1" title="Ver">
              <i class="bi bi-eye text-primary"></i>
              <span class="d-none d-sm-inline ms-1 smaller text-primary">Ver</span>
            </router-link>
            
            <router-link :to="`/categories/${category.id}/edit`" class="btn btn-light-warning btn-sm border-0 rounded-2 me-1" title="Editar">
              <i class="bi bi-pencil text-warning-emphasis"></i>
              <span class="d-none d-sm-inline ms-1 smaller text-warning-emphasis">Editar</span>
            </router-link>
            
            <button @click="$emit('delete-category', category.id)" class="btn btn-light-danger btn-sm border-0 rounded-2" title="Eliminar">
              <i class="bi bi-trash text-danger"></i>
              <span class="d-none d-sm-inline ms-1 smaller text-danger">Borrar</span>
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
import { ref, defineProps, defineEmits } from 'vue';
import { RouterLink } from 'vue-router';

const props = defineProps({
  category: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['delete-category']);

const isExpanded = ref(false);

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};
</script>

<style scoped>
.smaller {
  font-size: 0.75rem;
  font-weight: 600;
}

.min-width-0 {
  min-width: 0;
}

/* Colores de botones sutiles similares al login */
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

/* Animación sutil para la entrada de subcategorías */
.bg-light-subtle {
  background-color: rgba(0, 0, 0, 0.02) !important;
}

/* Estilo de la tarjeta similar al login */
.card {
  transition: transform 0.1s ease-in-out;
  border: 1px solid rgba(0,0,0,0.05) !important;
}
</style>
