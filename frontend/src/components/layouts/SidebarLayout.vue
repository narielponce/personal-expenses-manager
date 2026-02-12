<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <div class="offcanvas offcanvas-start bg-light border-right d-flex flex-column" tabindex="-1" id="sidebarMenu" aria-labelledby="sidebarMenuLabel">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title sidebar-heading" id="sidebarMenuLabel">Administrador de Gastos</h5>
        <button type="button" class="btn-close text-reset d-block d-md-none" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body d-md-flex flex-column p-0">
        <div class="list-group list-group-flush">
          <a href="#" @click.prevent="navigateTo('/home')" class="list-group-item list-group-item-action bg-light" data-bs-dismiss="offcanvas">Inicio</a>
          <a href="#" @click.prevent="navigateTo('/accounts')" class="list-group-item list-group-item-action bg-light" data-bs-dismiss="offcanvas">Cuentas</a>
          <a href="#" @click.prevent="navigateTo('/categories')" class="list-group-item list-group-item-action bg-light" data-bs-dismiss="offcanvas">Categorías</a>
          <a href="#" @click.prevent="navigateTo('/recipients')" class="list-group-item list-group-item-action bg-light" data-bs-dismiss="offcanvas">Destinatarios</a>
          <a href="#" @click.prevent="navigateTo('/expenses')" class="list-group-item list-group-item-action bg-light" data-bs-dismiss="offcanvas">Movimientos</a>

          <!-- Reports Dropdown -->
          <a href="#submenuReports" data-bs-toggle="collapse" aria-expanded="false" class="list-group-item list-group-item-action bg-light dropdown-toggle">
            Informes
          </a>
          <div class="collapse" id="submenuReports">
            <a href="#" @click.prevent="navigateTo('/reports/card-summary')" class="list-group-item list-group-item-action bg-light ps-4" data-bs-dismiss="offcanvas">Resumen tarjetas</a>
          </div>

          <a href="#" @click.prevent="handleLogoutAndDismiss" class="list-group-item list-group-item-action bg-light">Salir</a>
        </div>
      </div>
    </div>
    <!-- /#sidebar-wrapper -->

    <!-- Page Content -->
    <div id="page-content-wrapper" class="flex-grow-1">
      <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom fixed-top">
        <div class="container-fluid">
          <button class="navbar-toggler d-md-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <h5 class="ms-3 me-auto d-none d-md-block">Panel de Administrador de Gastos</h5>
          <h5 class="ms-3 me-auto d-md-none">Administrador de Gastos</h5>
        </div>
      </nav>

      <div class="container-fluid mt-5 pt-3">
        <slot></slot> <!-- Main content goes here -->
      </div>
    </div>
    <!-- /#page-content-wrapper -->
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as bootstrap from 'bootstrap'; // Import Bootstrap JS

const authStore = useAuthStore()
const router = useRouter()

const navigateTo = (path) => {
  // Dismiss offcanvas if open
  const sidebarOffcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('sidebarMenu'));
  if (sidebarOffcanvas) {
    sidebarOffcanvas.hide();
  }
  router.push(path);
};

const handleLogoutAndDismiss = () => {
  // Dismiss offcanvas if open
  const sidebarOffcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('sidebarMenu'));
  if (sidebarOffcanvas) {
    sidebarOffcanvas.hide();
  }
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
/* Custom styles to adjust for offcanvas behavior on desktop */
#sidebarMenu {
  width: 15rem; /* Set explicit width for sidebar */
}

/* For desktop, make the offcanvas always visible and part of the layout */
@media (min-width: 768px) {
  #sidebarMenu {
    transform: none; /* Override offcanvas transform to always show */
    visibility: visible !important;
    position: sticky; /* Keep it in the flow */
    top: 0;
    height: 100vh; /* Full height */
    margin-right: 0;
    border-right: 1px solid #dee2e6; /* Border */
    z-index: 0; /* Less z-index than fixed navbar */
  }

  #page-content-wrapper {
    margin-left: 15rem; /* Make space for the sidebar */
  }

  .navbar.fixed-top {
    left: 15rem; /* Adjust fixed navbar position */
    width: calc(100% - 15rem);
  }
}

/* Adjust main content padding for fixed navbar */
.container-fluid.mt-5.pt-3 {
  padding-top: calc(3rem + 56px) !important; /* Adjust for navbar height (approx 56px) */
}
</style>
