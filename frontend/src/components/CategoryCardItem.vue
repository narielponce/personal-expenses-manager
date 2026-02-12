<template>
  <div class="card mb-2">
    <div class="card-body">
      <div class="d-flex align-items-center" :style="{ 'padding-left': (level * 20) + 'px' }">
        <button v-if="category.children && category.children.length" @click="toggleExpand" class="btn btn-sm btn-light me-2">
          <i :class="isExpanded ? 'bi bi-dash-circle' : 'bi bi-plus-circle'"></i>
        </button>
        <span v-else class="me-2" :style="{ 'width': (level * 20) + 'px' }"></span> <!-- Placeholder for alignment -->

        <span>{{ category.name }}</span>

        <div class="ms-auto">
          <router-link :to="`/categories/${category.id}`" class="btn btn-info btn-sm me-2">Ver</router-link>
          <router-link :to="`/categories/${category.id}/edit`" class="btn btn-warning btn-sm me-2">Editar</router-link>
          <button @click="$emit('delete-category', category.id)" class="btn btn-danger btn-sm">Eliminar</button>
        </div>
      </div>

      <ul v-if="category.children && category.children.length && isExpanded" class="mt-2">
        <CategoryCardItem
          v-for="child in category.children"
          :key="child.id"
          :category="child"
          :level="level + 1"
          @delete-category="$emit('delete-category', $event)"
        />
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import { RouterLink } from 'vue-router'; // Explicitly import RouterLink

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
/* Add any specific styling for tree items here */
.list-group-item {
  border: none;
  border-bottom: 1px solid rgba(0,0,0,.125);
}
.list-group-item:last-child {
  border-bottom: none;
}
</style>