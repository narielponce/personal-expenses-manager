import { defineStore } from 'pinia';
import apiClient from '../api';

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchCategories() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/categories/');
        this.categories = response.data;
      } catch (error) {
        this.error = error;
        console.error('Error fetching categories:', error);
      } finally {
        this.loading = false;
      }
    },
    async createCategory(category) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/categories/', category);
        this.categories.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error creating category:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async updateCategory(id, category) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/categories/${id}`, category);
        const index = this.categories.findIndex(cat => cat.id === id);
        if (index !== -1) {
          this.categories[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error;
        console.error('Error updating category:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async deleteCategory(id) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`/categories/${id}`);
        this.categories = this.categories.filter(cat => cat.id !== id);
      } catch (error) {
        this.error = error;
        console.error('Error deleting category:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
