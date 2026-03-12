<template>
  <div class="tree-item-node">
    <div 
      class="d-flex align-items-center py-1 px-2 rounded-2 hover-bg" 
      :class="{ 'bg-primary-subtle': selectedId === node.id }"
    >
      <!-- Icono de expansión -->
      <div 
        class="flex-shrink-0 me-1 d-flex align-items-center justify-content-center" 
        style="width: 24px; height: 24px; cursor: pointer;" 
        @click.stop="toggle"
      >
        <i v-if="hasChildren" class="bi text-primary" :class="isExpanded ? 'bi-chevron-down' : 'bi-chevron-right'" style="font-size: 0.7rem;"></i>
      </div>
      
      <!-- Nombre de la categoría -->
      <div 
        class="flex-grow-1 tiny fw-semibold text-dark text-truncate" 
        style="cursor: pointer; padding: 2px 0;" 
        @click="handleSelect"
      >
        {{ node.name }}
      </div>
    </div>

    <!-- Hijos recursivos -->
    <div v-if="isExpanded && hasChildren" class="ms-3 border-start ps-1">
      <CategoryTreeItemSelect 
        v-for="child in node.children" 
        :key="child.id" 
        :node="child" 
        :selected-id="selectedId" 
        @select="$emit('select', $event)" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  selectedId: {
    type: [Number, null],
    default: null
  }
});

const emit = defineEmits(['select']);

const isExpanded = ref(false);
const hasChildren = computed(() => props.node.children && props.node.children.length > 0);

const toggle = () => {
  isExpanded.value = !isExpanded.value;
};

const handleSelect = () => {
  emit('select', props.node.id);
};
</script>

<style scoped>
.hover-bg:hover {
  background-color: rgba(13, 110, 253, 0.05);
}

.tiny {
  font-size: 0.75rem;
}

.bg-primary-subtle {
  background-color: #e7f1ff !important;
}

.tree-item-node {
  user-select: none;
}
</style>
