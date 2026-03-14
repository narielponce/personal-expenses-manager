<template>
  <div class="summary-container mt-2 mb-4 px-2 px-md-3" style="max-width: 600px; margin-left: auto; margin-right: auto;">
    <!-- Header estilo Home -->
    <div class="user-header mb-4 mt-1 px-1">
      <h5 class="fw-bold mb-0">Centro de <span class="text-primary">Reportes</span></h5>
      <p class="text-muted tiny mb-0">Analiza tus finanzas con detalle</p>
    </div>

    <div class="list-group list-group-flush shadow-sm rounded-4 overflow-hidden border">
      <!-- Reporte 1: Categorías -->
      <router-link to="/reports/by-category" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0 border-bottom">
        <div class="d-flex align-items-center">
          <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-primary-subtle me-3" style="width: 40px; height: 40px;">
            <i class="bi bi-pie-chart text-primary fs-5"></i>
          </div>
          <div>
            <span class="fw-bold text-dark d-block smaller">Gastos por Categoría</span>
            <span class="text-muted tiny">Distribución porcentual y comparativa</span>
          </div>
        </div>
        <i class="bi bi-chevron-right text-muted smaller"></i>
      </router-link>
      
      <!-- Reporte 2: Tarjetas -->
      <router-link to="/reports/card-summary" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0 border-bottom">
        <div class="d-flex align-items-center">
          <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-success-subtle me-3" style="width: 40px; height: 40px;">
            <i class="bi bi-credit-card-2-front text-success fs-5"></i>
          </div>
          <div>
            <span class="fw-bold text-dark d-block smaller">Resumen de Tarjetas</span>
            <span class="text-muted tiny">Consumos y cuotas mensuales</span>
          </div>
        </div>
        <i class="bi bi-chevron-right text-muted smaller"></i>
      </router-link>

      <!-- Reporte 3: Ingresos vs Gastos -->
      <router-link to="/reports/income-vs-expenses" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center border-0">
        <div class="d-flex align-items-center">
          <div class="inbox-icon rounded-circle d-flex align-items-center justify-content-center bg-info-subtle me-3" style="width: 40px; height: 40px;">
            <i class="bi bi-arrow-left-right text-info fs-5"></i>
          </div>
          <div>
            <span class="fw-bold text-dark d-block smaller">Ingresos vs Gastos</span>
            <span class="text-muted tiny">Balance mensual y comparativa</span>
          </div>
        </div>
        <i class="bi bi-chevron-right text-muted smaller"></i>
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.summary-container {
  width: 100%;
}
.user-header {
  border-left: 4px solid #0d6efd;
  padding-left: 12px;
}
.tiny { font-size: 0.65rem; }
.smaller { font-size: 0.75rem; }
.bg-primary-subtle { background-color: #e7f1ff !important; }
.bg-success-subtle { background-color: #d1e7dd !important; }
.bg-info-subtle { background-color: #cff4fc !important; }
</style>
