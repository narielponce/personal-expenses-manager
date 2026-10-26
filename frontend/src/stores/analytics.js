import { defineStore } from 'pinia';
import apiClient from '../api';

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    summary: null,
    advisor: null,
    budgets: [],
    loadingSummary: false,
    loadingAdvisor: false,
    loadingSimulation: false,
    simulationResult: null,
    error: null,
  }),
  actions: {
    async fetchSummary(month = null, year = null) {
      this.loadingSummary = true;
      this.error = null;
      try {
        const params = {};
        if (month) params.month = month;
        if (year) params.year = year;
        const res = await apiClient.get('/analytics/summary', { params });
        this.summary = res.data;
        return res.data;
      } catch (err) {
        this.error = err;
        console.error('Error fetching analytics summary:', err);
      } finally {
        this.loadingSummary = false;
      }
    },
    async fetchAdvisor(force = false) {
      this.loadingAdvisor = true;
      this.error = null;
      try {
        const res = await apiClient.get('/analytics/advisor', {
          params: { force }
        });
        this.advisor = res.data;
        return res.data;
      } catch (err) {
        this.error = err;
        console.error('Error fetching AI advisor diagnosis:', err);
      } finally {
        this.loadingAdvisor = false;
      }
    },
    async simulatePurchase(payload) {
      this.loadingSimulation = true;
      this.error = null;
      try {
        const res = await apiClient.post('/analytics/simulate', payload);
        this.simulationResult = res.data;
        return res.data;
      } catch (err) {
        this.error = err;
        console.error('Error simulating purchase:', err);
        throw err;
      } finally {
        this.loadingSimulation = false;
      }
    },
    async fetchBudgets(month = null, year = null) {
      try {
        const params = {};
        if (month) params.month = month;
        if (year) params.year = year;
        const res = await apiClient.get('/analytics/budgets', { params });
        this.budgets = res.data;
        return res.data;
      } catch (err) {
        console.error('Error fetching budgets:', err);
      }
    },
    async setBudget(budgetData) {
      try {
        const res = await apiClient.post('/analytics/budgets', budgetData);
        await this.fetchBudgets(budgetData.month, budgetData.year);
        return res.data;
      } catch (err) {
        console.error('Error setting budget:', err);
        throw err;
      }
    }
  }
});
