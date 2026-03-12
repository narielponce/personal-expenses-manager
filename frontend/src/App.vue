<template>
  <div id="app">
    <template v-if="authStore.token">
      <SidebarLayout>
        <RouterView />
      </SidebarLayout>
    </template>
    <template v-else>
      <RouterView />
    </template>

    <!-- Modal de Sesión Expirada -->
    <div class="modal fade" id="sessionTimeoutModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="sessionTimeoutModalLabel" aria-hidden="true" ref="timeoutModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-clock-history text-warning fs-1"></i>
            </div>
            <h5 class="fw-bold mb-2">Sesión expirada</h5>
            <p class="text-muted small mb-4">Tu sesión ha finalizado por inactividad. Por seguridad, debes volver a ingresar.</p>
            <button type="button" class="btn btn-primary w-100 rounded-pill fw-bold" @click="handleSessionTimeout">
              ACEPTAR
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SidebarLayout from '@/components/layouts/SidebarLayout.vue';
import * as bootstrap from 'bootstrap';

const authStore = useAuthStore()
const router = useRouter()
const timeoutModal = ref(null)
let modalInstance = null
let inactivityTimer = null

// Tiempo de inactividad: 5 minutos
const INACTIVITY_TIME = 5 * 60 * 1000 

const resetInactivityTimer = () => {
  if (inactivityTimer) clearTimeout(inactivityTimer)
  
  // Solo iniciar timer si el usuario está autenticado
  if (authStore.token) {
    inactivityTimer = setTimeout(showTimeoutModal, INACTIVITY_TIME)
  }
}

const showTimeoutModal = () => {
  if (!modalInstance && timeoutModal.value) {
    modalInstance = new bootstrap.Modal(timeoutModal.value)
  }
  if (modalInstance) {
    modalInstance.show()
  }
}

const handleSessionTimeout = () => {
  if (modalInstance) {
    modalInstance.hide()
  }
  authStore.logout()
  router.push('/')
}

// Eventos a escuchar para detectar actividad
const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']

onMounted(() => {
  events.forEach(event => {
    window.addEventListener(event, resetInactivityTimer)
  })
  
  // Iniciar timer si ya está logueado
  if (authStore.token) {
    resetInactivityTimer()
  }
})

onUnmounted(() => {
  events.forEach(event => {
    window.removeEventListener(event, resetInactivityTimer)
  })
  if (inactivityTimer) clearTimeout(inactivityTimer)
})

// Reiniciar timer cuando cambie el estado de autenticación (login)
watch(() => authStore.token, (newToken) => {
  if (newToken) {
    resetInactivityTimer()
  } else {
    if (inactivityTimer) clearTimeout(inactivityTimer)
  }
})
</script>

<style>
/* Estilos globales */
#app {
  min-height: 100vh;
}
</style>
