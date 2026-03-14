import { defineStore } from 'pinia';
import apiClient from '../api';

export const useExpenseStore = defineStore('expense', {
  state: () => ({
    expenses: [],
    totalExpensesCount: 0, // New state property
    loading: false,
    error: null,
  }),
  actions: {
    async fetchExpenses(
      skip = 0,
      limit = 100,
      description = null,
      startDate = null,
      endDate = null,
      accountId = null,
      categoryId = null,
      recipientId = null,
      month = null,
      year = null,
      status = null
    ) {
      this.loading = true;
      this.error = null;
      try {
        const params = { skip, limit };
        if (description) params.description = description;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (accountId) params.account_id = accountId;
        if (categoryId) params.category_id = categoryId;
        if (recipientId) params.recipient_id = recipientId;
        if (month) params.month = month;
        if (year) params.year = year;
        if (status) params.status = status;

        const response = await apiClient.get('/expenses/', {
          params: params
        });
        console.log('JSON recibido del backend:', response.data.expenses);
        this.expenses = response.data.expenses;
        this.totalExpensesCount = response.data.total_count;
      } catch (error) {
        this.error = error;
        console.error('Error fetching expenses:', error);
      } finally {
        this.loading = false;
      }
    },
    async processVoiceAndSave(text) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/process-voice-and-save', { text });
        this.expenses.unshift(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error processing voice and saving:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async processImageAndSave(file) {
      this.loading = true;
      this.error = null;
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await apiClient.post('/process-image-and-save', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        this.expenses.unshift(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error processing image and saving:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async createExpense(expense) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/expenses/', expense);
        this.expenses.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error creating expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async updateExpense(id, expense) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/expenses/${id}`, expense);
        const index = this.expenses.findIndex(exp => exp.id === id);
        if (index !== -1) {
          this.expenses[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error updating expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async deleteExpense(id) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`/expenses/${id}`);
        this.expenses = this.expenses.filter(exp => exp.id !== id);
      } catch (error) {
        this.error = error;
        console.error('Error deleting expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
