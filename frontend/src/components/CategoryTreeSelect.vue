<template>
  <div class="category-tree-select">
    <!-- Botón que abre el Modal -->
    <button 
      type="button" 
      class="form-select form-select-sm border-0 bg-white rounded-start-3 py-1 d-flex align-items-center justify-content-between text-start"
      @click="openModal"
    >
      <span class="text-truncate me-2" :class="{ 'text-muted': !selectedCategoryName }">
        {{ selectedCategoryName || 'Seleccionar...' }}
      </span>
    </button>

    <!-- Modal de Selección de Categoría -->
    <div class="modal fade" ref="modalRef" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header border-0 pb-0">
            <h6 class="modal-title fw-bold text-primary">Seleccionar Categoría</h6>
            <button type="button" class="btn-close tiny" @click="closeModal"></button>
          </div>
          <div class="modal-body pt-2">
            <div v-if="!categoryTree.length" class="text-center py-4 tiny text-muted">
              No hay categorías disponibles
            </div>
            <div v-else class="tree-container">
              <div v-for="node in categoryTree" :key="node.id" class="mb-1">
                <CategoryTreeItemSelect 
                  :node="node" 
                  :selected-id="modelValue" 
                  @select="selectCategory" 
                />
              </div>
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-light btn-sm rounded-pill px-3 tiny fw-bold" @click="closeModal">CANCELAR</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import CategoryTreeItemSelect from './CategoryTreeItemSelect.vue';
import * as bootstrap from 'bootstrap';

const props = defineProps({
  modelValue: {
    type: [Number, null],
    default: null
  },
  categories: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const modalRef = ref(null);
let modalInstance = null;

const openModal = () => {
  if (!modalInstance) {
    modalInstance = new bootstrap.Modal(modalRef.value);
  }
  modalInstance.show();
};

const closeModal = () => {
  if (modalInstance) {
    modalInstance.hide();
  }
};

const selectCategory = (id) => {
  emit('update:modelValue', id);
  closeModal();
};

// Construir el árbol a partir de la lista plana
const categoryTree = computed(() => {
  const categoryMap = new Map();
  props.categories.forEach(cat => categoryMap.set(cat.id, { ...cat, children: [] }));

  const tree = [];
  props.categories.forEach(cat => {
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

  return tree.sort((a, b) => a.name.localeCompare(b.name));
});

const selectedCategoryName = computed(() => {
  const found = props.categories.find(c => c.id === props.modelValue);
  return found ? found.name : '';
});
</script>

<style scoped>
.tiny {
  font-size: 0.75rem;
}

.tree-container {
  max-height: 60vh;
  overflow-y: auto;
}

.tree-container::-webkit-scrollbar {
  width: 4px;
}
.tree-container::-webkit-scrollbar-thumb {
  background: #e9ecef;
  border-radius: 10px;
}

.modal-content {
  max-width: 90vw;
  margin: 0 auto;
}
</style>
