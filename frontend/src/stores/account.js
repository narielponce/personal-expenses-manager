import { defineStore } from 'pinia';
import apiClient from '../api';

export const useAccountStore = defineStore('account', {
  state: () => ({
    accounts: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchAccounts() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/accounts/');
        this.accounts = response.data;
      } catch (error) {
        this.error = error;
        console.error('Error fetching accounts:', error);
      } finally {
        this.loading = false;
      }
    },
    async createAccount(account) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/accounts/', account);
        this.accounts.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error creating account:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async updateAccount(id, account) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/accounts/${id}`, account);
        const index = this.accounts.findIndex(acc => acc.id === id);
        if (index !== -1) {
          this.accounts[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error updating account:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async deleteAccount(id) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`/accounts/${id}`);
        this.accounts = this.accounts.filter(acc => acc.id !== id);
      } catch (error) {
        this.error = error;
        console.error('Error deleting account:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
