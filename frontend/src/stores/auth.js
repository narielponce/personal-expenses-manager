import { defineStore } from 'pinia'
import apiClient from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
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
        localStorage.setItem('token', this.token)
        await this.fetchUser()
      } catch (error) {
        console.error('Login error:', error);
        this.error = 'Invalid credentials'
        this.token = ''
        localStorage.removeItem('token')
        this.user = null
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
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
