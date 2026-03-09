import axios from 'axios'
import { useAuthStore } from '../stores/auth';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {}
});

// Interceptor para agregar el token a las peticiones
apiClient.interceptors.request.use(config => {
  const authStore = useAuthStore();
  const token = authStore.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores 401 (Sesión expirada)
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Si es 401 y no hemos reintentado ya
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const authStore = useAuthStore();
      
      try {
        console.log("Intentando refrescar token...");
        const newToken = await authStore.refreshTokenAction();
        
        // Actualizar el header de la petición original y reintentar
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Si el refresh también falla, al login
        console.warn("Refresh token expirado. Redirigiendo al login...");
        authStore.logout();
        localStorage.setItem('sessionExpired', 'true');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
