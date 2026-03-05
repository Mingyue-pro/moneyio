import { createRouter, createWebHistory } from 'vue-router';
import GlobalLayout from '../layouts/GlobalLayout.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import TransactionsPage from '../pages/TransactionsPage.vue';
import ReportsPage from '../pages/ReportsPage.vue';
import BudgetsPage from '../pages/BudgetsPage.vue';
import SettingsPage from '../pages/SettingsPage.vue';
import LoginPage from '@/pages/LoginPage.vue';
import RegisterPage from '@/pages/RegisterPage.vue';
import { useAuthStore } from '@/stores/auth';

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    subtitle?: string;
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: GlobalLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardPage,
          meta: { subtitle: "Here's what's happening with your money today" },
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: TransactionsPage,
          meta: { subtitle: 'View and manage all your transactions' },
        },
        {
          path: 'reports',
          name: 'reports',
          component: ReportsPage,
          meta: { subtitle: 'Analyze your spending and income trends' },
        },
        {
          path: 'budgets',
          name: 'budgets',
          component: BudgetsPage,
          meta: { subtitle: 'Set and track your budgets' },
        },
        {
          path: 'settings',
          name: 'settings',
          component: SettingsPage,
          meta: { subtitle: 'Manage your account and preferences' },
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: { requiresAuth: false },
    },
  ],
});

router.beforeEach((to): { name: string } | undefined => {
  const authStore = useAuthStore();

  // Redirect authenticated users away from auth pages
  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    return { name: 'dashboard' };
  }

  // Redirect unauthenticated users to login for protected routes
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    return { name: 'login' };
  }

  return undefined;
});

export default router;
