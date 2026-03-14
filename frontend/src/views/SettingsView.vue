<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 600px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-3 mt-1 px-1">
      <h5 class="fw-bold mb-0">Ajustes y <span class="text-primary">Configuración</span></h5>
      <p class="text-muted tiny mb-0">Personaliza tu experiencia y gestiona tus datos</p>
    </div>

    <!-- Sección: Gestión de Tablas -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="list-group list-group-flush">
        <router-link to="/accounts" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0 border-bottom">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-primary-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-credit-card text-primary tiny"></i>
            </div>
            <span class="fw-bold text-dark smaller">Mis Cuentas</span>
          </div>
          <i class="bi bi-chevron-right text-muted smaller"></i>
        </router-link>
        
        <router-link to="/categories" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0 border-bottom">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-success-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-tags text-success tiny"></i>
            </div>
            <span class="fw-bold text-dark smaller">Categorías</span>
          </div>
          <i class="bi bi-chevron-right text-muted smaller"></i>
        </router-link>
        
        <router-link to="/recipients" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-info-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-people text-info tiny"></i>
            </div>
            <span class="fw-bold text-dark smaller">Destinatarios</span>
          </div>
          <i class="bi bi-chevron-right text-muted smaller"></i>
        </router-link>
      </div>
    </div>

    <!-- Sección: Seguridad y Datos -->
    <h6 class="text-muted tiny fw-bold text-uppercase px-1 mb-2">Seguridad y Datos</h6>
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="list-group list-group-flush">
        <button @click="downloadBackup" :disabled="isDownloading" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0 border-bottom">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-warning-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-download text-warning tiny"></i>
            </div>
            <div>
              <span class="fw-bold text-dark d-block smaller">Exportar Respaldo</span>
              <span class="text-muted tiny">Descarga todos tus datos en un ZIP (CSV)</span>
            </div>
          </div>
          <div v-if="isDownloading" class="spinner-border spinner-border-sm text-warning" role="status"></div>
          <i v-else class="bi bi-chevron-right text-muted smaller"></i>
        </button>

        <button @click="showResetModal" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-danger-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-trash3 text-danger tiny"></i>
            </div>
            <div>
              <span class="fw-bold text-danger d-block smaller">Reiniciar Cuenta</span>
              <span class="text-muted tiny">Borra todos los datos y restablece categorías</span>
            </div>
          </div>
          <i class="bi bi-exclamation-triangle text-danger smaller"></i>
        </button>
      </div>
    </div>

    <!-- Sección: Apariencia -->
    <h6 class="text-muted tiny fw-bold text-uppercase px-1 mb-2">Apariencia</h6>
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="list-group list-group-flush">
        <div class="list-group-item py-3 d-flex justify-content-between align-items-center border-0 opacity-50">
          <div class="d-flex align-items-center">
            <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-secondary-subtle me-3" style="width: 35px; height: 32px;">
              <i class="bi bi-moon-stars text-secondary tiny"></i>
            </div>
            <span class="fw-bold text-dark smaller">Modo Oscuro (Próximamente)</span>
          </div>
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" disabled>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación de Reinicio -->
    <div class="modal fade" id="resetConfirmModal" data-bs-backdrop="static" tabindex="-1" aria-hidden="true" ref="resetModalRef">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header border-0 pb-0">
            <h6 class="modal-title fw-bold text-danger">¿Reiniciar cuenta?</h6>
            <button type="button" class="btn-close tiny" @click="closeResetModal" :disabled="isResetting"></button>
          </div>
          <div class="modal-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-exclamation-octagon text-danger fs-1"></i>
            </div>
            <p class="text-dark fw-bold mb-1">Esta acción es irreversible.</p>
            <p class="text-muted small mb-0">Se eliminarán todos tus movimientos, cuentas y destinatarios. Tus categorías se restablecerán a los valores por defecto.</p>
          </div>
          <div class="modal-footer border-0 pt-0 d-flex flex-column gap-2">
            <button type="button" class="btn btn-danger w-100 rounded-pill fw-bold" @click="handleResetAccount" :disabled="isResetting">
              <span v-if="isResetting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              SÍ, REINICIAR TODO
            </button>
            <button type="button" class="btn btn-light w-100 rounded-pill fw-bold text-muted" @click="closeResetModal" :disabled="isResetting">
              CANCELAR
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <Transition name="fade">
      <div v-if="showSuccessToast" class="success-toast shadow-sm rounded-pill py-2 px-4 bg-success text-white d-flex align-items-center gap-2">
        <i class="bi bi-check-circle-fill"></i>
        <span class="fw-bold tiny">{{ successMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import apiClient from '@/api';
import * as bootstrap from 'bootstrap';

const authStore = useAuthStore();
const isDownloading = ref(false);
const isResetting = ref(false);
const showSuccessToast = ref(false);
const successMessage = ref('');

const resetModalRef = ref(null);
let resetModalInstance = null;

const downloadBackup = async () => {
  if (isDownloading.value) return;
  
  isDownloading.value = true;
  try {
    const response = await apiClient.get('/backup/export', {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const timestamp = new Date().toISOString().split('T')[0];
    link.setAttribute('download', `respaldo_gastos_${timestamp}.zip`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    successMessage.value = "Respaldo generado con éxito";
    showSuccessToast.value = true;
    setTimeout(() => { showSuccessToast.value = false; }, 2500);
  } catch (error) {
    console.error('Error al descargar el respaldo:', error);
    alert('Hubo un error al generar el respaldo.');
  } finally {
    isDownloading.value = false;
  }
};

const showResetModal = () => {
  if (!resetModalInstance) {
    resetModalInstance = new bootstrap.Modal(resetModalRef.value);
  }
  resetModalInstance.show();
};

const closeResetModal = () => {
  if (resetModalInstance) resetModalInstance.hide();
};

const handleResetAccount = async () => {
  isResetting.value = true;
  try {
    await apiClient.post('/backup/reset');
    
    closeResetModal();
    successMessage.value = "Cuenta restablecida correctamente";
    showSuccessToast.value = true;
    setTimeout(() => { showSuccessToast.value = false; }, 3000);
    
  } catch (error) {
    console.error('Error al reiniciar la cuenta:', error);
    alert('No se pudo reiniciar la cuenta. Intenta de nuevo.');
  } finally {
    isResetting.value = false;
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

.smaller {
  font-size: 0.75rem;
}

.bg-primary-subtle { background-color: #e7f1ff !important; }
.bg-success-subtle { background-color: #d1e7dd !important; }
.bg-info-subtle { background-color: #cff4fc !important; }
.bg-warning-subtle { background-color: #fff3cd !important; }
.bg-danger-subtle { background-color: #f8d7da !important; }
.bg-secondary-subtle { background-color: #e2e3e5 !important; }

.list-group-item {
  transition: background-color 0.2s;
}

/* Estilos para el Toast */
.success-toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
