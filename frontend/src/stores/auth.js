import { defineStore } from 'pinia'
import apiClient from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
    user: null,
    error: null,
  }),
  actions: {
    async login(email, password) {
      this.error = null
      try {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await apiClient.post('/token', params);

        console.log('Login response:', response);
        this.token = response.data.access_token
        this.refreshToken = response.data.refresh_token
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        await this.fetchUser()
      } catch (error) {
        console.error('Login error:', error);
        this.error = 'Invalid credentials'
        this.logout()
      }
    },
    async refreshTokenAction() {
      if (!this.refreshToken) throw new Error("No refresh token available");
      try {
        const response = await apiClient.post('/refresh', { refresh_token: this.refreshToken });
        this.token = response.data.access_token;
        this.refreshToken = response.data.refresh_token;
        localStorage.setItem('token', this.token);
        localStorage.setItem('refreshToken', this.refreshToken);
        return this.token;
      } catch (error) {
        console.error("Error refreshing token:", error);
        this.logout();
        throw error;
      }
    },
    async fetchUser() {
      if (!this.token) return
      try {
        const response = await apiClient.get('/users/me')
        this.user = response.data
      } catch (error) {
        console.error('Fetch user error:', error);
        this.logout()
      }
    },
    logout() {
      this.token = ''
      this.refreshToken = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },
  },
})
