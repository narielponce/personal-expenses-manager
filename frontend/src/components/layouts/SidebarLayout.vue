<template>
  <div class="main-layout" :class="{ 'mobile-layout': isMobile }">
    <!-- Desktop Sidebar -->
    <div v-if="!isMobile" id="sidebarMenu" class="bg-light border-right d-flex flex-column shadow-sm">
      <div class="sidebar-header p-3 border-bottom bg-white">
        <h5 class="sidebar-heading mb-0 fw-bold text-primary text-center">Gestor Gastos</h5>
      </div>
      <div class="list-group list-group-flush flex-grow-1 overflow-auto">
        <router-link to="/home" class="list-group-item list-group-item-action bg-light py-3 border-0">
          <i class="bi bi-house-door me-2"></i> Inicio
        </router-link>
        <router-link to="/inbox" class="list-group-item list-group-item-action bg-light py-3 border-0">
          <i class="bi bi-inbox me-2"></i> Inbox
        </router-link>
        <router-link to="/expenses" class="list-group-item list-group-item-action bg-light py-3 border-0">
          <i class="bi bi-receipt me-2"></i> Movimientos
        </router-link>
        
        <div class="border-top mt-2 pt-2 px-3 mb-2">
          <small class="text-muted fw-bold text-uppercase" style="font-size: 0.65rem;">Análisis</small>
        </div>
        <router-link to="/reports/card-summary" class="list-group-item list-group-item-action bg-light py-2 border-0 ps-4">
          <i class="bi bi-bar-chart-line me-2"></i> Reportes
        </router-link>

        <div class="border-top mt-2 pt-2 px-3 mb-2">
          <small class="text-muted fw-bold text-uppercase" style="font-size: 0.65rem;">Configuración</small>
        </div>
        <router-link to="/settings" class="list-group-item list-group-item-action bg-light py-3 border-0">
          <i class="bi bi-gear me-2"></i> Ajustes
        </router-link>
      </div>
      <div class="sidebar-footer p-3 border-top mt-auto bg-white">
        <button @click="handleLogout" class="btn btn-outline-danger w-100 btn-sm">
          <i class="bi bi-box-arrow-right me-1"></i> Salir
        </button>
      </div>
    </div>

    <!-- Mobile Top Header (Minimal) -->
    <nav v-if="isMobile" class="navbar navbar-light bg-white border-bottom fixed-top px-3 py-2 shadow-sm">
      <h6 class="mb-0 fw-bold text-primary">Gestor Gastos</h6>
      <div class="d-flex align-items-center">
        <button class="btn btn-link text-danger p-0 ms-2" @click="handleLogout" title="Cerrar Sesión">
          <i class="bi bi-box-arrow-right fs-5"></i>
        </button>
      </div>
    </nav>

    <!-- Page Content -->
    <div id="page-content-wrapper" class="flex-grow-1" :class="{ 'pb-5 mb-4': isMobile }">
      <div class="container-fluid py-3 px-3 px-md-4 mt-2">
        <slot></slot>
      </div>
    </div>

    <!-- Mobile Bottom Navigation Bar -->
    <nav v-if="isMobile" class="mobile-bottom-nav fixed-bottom bg-white border-top d-flex justify-content-around align-items-center">
      <router-link to="/home" class="nav-item d-flex flex-column align-items-center py-2 px-3 text-decoration-none" :class="{ active: currentRoute === '/home' }">
        <i class="bi" :class="currentRoute === '/home' ? 'bi-house-door-fill' : 'bi-house-door'"></i>
        <span class="smaller">Home</span>
      </router-link>
      <router-link to="/inbox" class="nav-item d-flex flex-column align-items-center py-2 px-3 text-decoration-none" :class="{ active: currentRoute === '/inbox' }">
        <i class="bi" :class="currentRoute === '/inbox' ? 'bi-inbox-fill' : 'bi-inbox'"></i>
        <span class="smaller">Inbox</span>
      </router-link>
      <router-link to="/expenses" class="nav-item d-flex flex-column align-items-center py-2 px-3 text-decoration-none" :class="{ active: currentRoute === '/expenses' }">
        <i class="bi" :class="currentRoute === '/expenses' ? 'bi-receipt-cutoff' : 'bi-receipt'"></i>
        <span class="smaller">Movs</span>
      </router-link>
      <router-link to="/reports/card-summary" class="nav-item d-flex flex-column align-items-center py-2 px-3 text-decoration-none" :class="{ active: currentRoute.startsWith('/reports') }">
        <i class="bi" :class="currentRoute.startsWith('/reports') ? 'bi-bar-chart-line-fill' : 'bi-bar-chart-line'"></i>
        <span class="smaller">Reportes</span>
      </router-link>
      <router-link to="/settings" class="nav-item d-flex flex-column align-items-center py-2 px-3 text-decoration-none" :class="{ active: currentRoute === '/settings' }">
        <i class="bi" :class="currentRoute === '/settings' ? 'bi-gear-fill' : 'bi-gear'"></i>
        <span class="smaller">Ajustes</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useBreakpoints } from '@/composables/useBreakpoints';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const { isMobile } = useBreakpoints();

const currentRoute = computed(() => route.path);

const handleLogout = () => {
  authStore.logout();
  router.push('/');
}
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* Sidebar Desktop */
#sidebarMenu {
  width: 240px;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 1020;
}

.list-group-item {
  color: #6c757d;
  font-weight: 500;
  transition: all 0.2s;
}

.list-group-item:hover {
  background-color: #eef2f7 !important;
  color: #0d6efd;
}

.router-link-active {
  background-color: #e7f1ff !important;
  color: #0d6efd !important;
  border-right: 3px solid #0d6efd !important;
}

/* Mobile Layout */
.mobile-layout {
  flex-direction: column;
}

.mobile-layout #page-content-wrapper {
  margin-top: 56px; /* Space for top navbar */
}

/* Bottom Nav */
.mobile-bottom-nav {
  height: 65px;
  z-index: 1030;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

.nav-item {
  color: #6c757d;
  flex: 1;
  transition: color 0.2s;
}

.nav-item i {
  font-size: 1.25rem;
}

.nav-item.active {
  color: #0d6efd;
}

.smaller {
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 2px;
}

/* FAB Button */
.nav-item-center {
  width: 60px;
  position: relative;
  display: flex;
  justify-content: center;
}

.fab-btn {
  width: 50px;
  height: 50px;
  position: absolute;
  top: -35px;
  border: 4px solid white;
}

/* Adjustments */
#page-content-wrapper {
  transition: all 0.3s;
}
</style>
