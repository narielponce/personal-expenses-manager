import { defineStore } from 'pinia';
import apiClient from '../api';

export const useRecipientStore = defineStore('recipient', {
  state: () => ({
    recipients: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchRecipients() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/recipients/');
        this.recipients = response.data;
      } catch (error) {
        this.error = error;
        console.error('Error fetching recipients:', error);
      } finally {
        this.loading = false;
      }
    },
    async createRecipient(recipient) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/recipients/', recipient);
        this.recipients.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error creating recipient:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async updateRecipient(id, recipient) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/recipients/${id}`, recipient);
        const index = this.recipients.findIndex(rec => rec.id === id);
        if (index !== -1) {
          this.recipients[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error updating recipient:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async deleteRecipient(id) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`/recipients/${id}`);
        this.recipients = this.recipients.filter(rec => rec.id !== id);
      } catch (error) {
        this.error = error;
        console.error('Error deleting recipient:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
