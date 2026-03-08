<template>
  <div class="login-bg d-flex justify-content-center align-items-center min-vh-100 position-relative">
    <div class="card p-4 p-md-5 shadow-lg border-0 rounded-4" style="width: 90%; max-width: 400px; background-color: #f8f9fa;">
      <h1 class="h5 text-center text-secondary fw-bold text-uppercase mb-1" style="letter-spacing: 2px;">Gestión Gastos Personales</h1>
      <h2 class="h4 text-center mb-4 fw-bold text-dark mt-2">Inicio de sesión</h2>
      <form @submit.prevent="handleLogin">
        
        <div class="input-group mb-3">
          <span class="input-group-text bg-white border-end-0 rounded-start-3 text-secondary px-3">
            <i class="bi bi-envelope"></i>
          </span>
          <input type="email" class="form-control border-start-0 rounded-end-3 py-2" id="emailInput" v-model="email" placeholder="Correo electrónico" required />
        </div>

        <div class="input-group mb-4">
          <span class="input-group-text bg-white border-end-0 rounded-start-3 text-secondary px-3">
            <i class="bi bi-lock-fill"></i>
          </span>
          <input type="password" class="form-control border-start-0 rounded-end-3 py-2" id="passwordInput" v-model="password" placeholder="Contraseña" required />
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2 rounded-3 fw-medium fs-5 mb-4 shadow-sm" style="background-color: #0d6efd; border: none;">Ingresar</button>

        <div v-if="authStore.error" class="alert alert-danger py-2 px-3 small text-center mb-3" role="alert">
          {{ authStore.error }}
        </div>

        <hr class="text-muted opacity-25 mb-3">
        <div class="text-center">
          <a href="#" class="text-decoration-none text-secondary small">¿Olvidaste la contraseña?</a>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { mapStores } from 'pinia'

export default {
  data() {
    return {
      email: '',
      password: '',
    };
  },
  computed: {
    ...mapStores(useAuthStore)
  },
  methods: {
    async handleLogin() {
      await this.authStore.login(this.email, this.password)
      if (!this.authStore.error) {
        this.$router.push('/home')
      }
    },
  },
};
</script>

<style scoped>
.login-bg {
  /* Imagen de fondo de escritorio/finanzas similar al mockup */
  background-image: url('https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Capa oscura superpuesta para que la tarjeta resalte más */
.login-bg::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.15); /* Sutil oscurecimiento */
  z-index: 0;
}

.card {
  z-index: 1;
}

/* Ajustes para los inputs para que no se vea el borde entre el icono y el campo */
.form-control:focus {
  box-shadow: none;
  border-color: #dee2e6;
}

.input-group-text, .form-control {
  border-color: #dee2e6;
}

/* Cuando el input tiene el foco, darle color al borde del icono también para que parezca un solo elemento */
.input-group:focus-within .input-group-text,
.input-group:focus-within .form-control {
  border-color: #86b7fe;
}
</style>
