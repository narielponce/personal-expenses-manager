<template>
  <div class="container py-2">
    <h5 class="fw-bold mb-4">Configuración</h5>
    
    <div class="list-group list-group-flush shadow-sm rounded-3 overflow-hidden border">
      <router-link to="/accounts" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center">
        <div>
          <i class="bi bi-credit-card me-3 text-primary"></i>
          <span>Mis Cuentas</span>
        </div>
        <i class="bi bi-chevron-right text-muted small"></i>
      </router-link>
      
      <router-link to="/categories" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center">
        <div>
          <i class="bi bi-tags me-3 text-success"></i>
          <span>Categorías</span>
        </div>
        <i class="bi bi-chevron-right text-muted small"></i>
      </router-link>
      
      <router-link to="/recipients" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center">
        <div>
          <i class="bi bi-people me-3 text-info"></i>
          <span>Destinatarios</span>
        </div>
        <i class="bi bi-chevron-right text-muted small"></i>
      </router-link>
    </div>

    <div class="mt-4 pt-2">
      <h6 class="text-muted small fw-bold text-uppercase px-1 mb-3">Preferencias</h6>
      <div class="list-group list-group-flush shadow-sm rounded-3 overflow-hidden border">
        <div class="list-group-item py-3 d-flex justify-content-between align-items-center opacity-50">
          <div>
            <i class="bi bi-moon-stars me-3"></i>
            <span>Modo Oscuro (Próximamente)</span>
          </div>
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" disabled>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Lógica de configuración futura
</script>
