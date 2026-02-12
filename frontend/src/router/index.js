import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/accounts',
      name: 'account-list',
      component: () => import('../views/accounts/AccountList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/accounts/new',
      name: 'new-account',
      component: () => import('../views/accounts/AccountForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/accounts/:id/edit',
      name: 'edit-account',
      component: () => import('../views/accounts/AccountForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/accounts/:id',
      name: 'view-account',
      component: () => import('../views/accounts/AccountForm.vue'), // Using form for view as well
      meta: { requiresAuth: true }
    },
    {
      path: '/categories',
      name: 'category-list',
      component: () => import('../views/categories/CategoryList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/categories/new',
      name: 'new-category',
      component: () => import('../views/categories/CategoryForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/categories/:id/edit',
      name: 'edit-category',
      component: () => import('../views/categories/CategoryForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/categories/:id',
      name: 'view-category',
      component: () => import('../views/categories/CategoryForm.vue'), // Using form for view as well
      meta: { requiresAuth: true }
    },
    {
      path: '/recipients',
      name: 'recipient-list',
      component: () => import('../views/recipients/RecipientList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/recipients/new',
      name: 'new-recipient',
      component: () => import('../views/recipients/RecipientForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/recipients/:id/edit',
      name: 'edit-recipient',
      component: () => import('../views/recipients/RecipientForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/recipients/:id',
      name: 'view-recipient',
      component: () => import('../views/recipients/RecipientForm.vue'), // Using form for view as well
      meta: { requiresAuth: true }
    },
    {
      path: '/expenses',
      name: 'expense-list',
      component: () => import('../views/expenses/ExpenseList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/expenses/new',
      name: 'new-expense',
      component: () => import('../views/expenses/ExpenseForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/expenses/:id/edit',
      name: 'edit-expense',
      component: () => import('../views/expenses/ExpenseForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/expenses/:id',
      name: 'view-expense',
      component: () => import('../views/expenses/ExpenseForm.vue'), // Using form for view as well
      meta: { requiresAuth: true }
    },
    {
      path: '/reports/card-summary',
      name: 'card-summary-report',
      component: () => import('../views/reports/CardSummaryView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
