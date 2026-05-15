import { create } from 'zustand';
import { api } from '../services/api';
import type { User, Transaction, DashboardStats, Alert } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: api.getUser(),
  isAuthenticated: api.isAuthenticated(),
  isLoading: false,

  login: async (email, password) => {
    set({ isLoading: true });
    const tokens = await api.login(email, password);
    set({ user: tokens.user, isAuthenticated: true, isLoading: false });
  },

  register: async (email, username, password, firstName, lastName) => {
    set({ isLoading: true });
    const tokens = await api.register(email, username, password, firstName, lastName);
    set({ user: tokens.user, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    api.logout();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: () => {
    set({ user: api.getUser(), isAuthenticated: api.isAuthenticated() });
  },
}));

interface DashboardState {
  stats: DashboardStats | null;
  recentTransactions: Transaction[];
  activeAlerts: Alert[];
  isLoading: boolean;
  error: string | null;
  fetchStats: () => Promise<void>;
  fetchRecentTransactions: () => Promise<void>;
  fetchActiveAlerts: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  recentTransactions: [],
  activeAlerts: [],
  isLoading: false,
  error: null,

  fetchStats: async () => {
    try {
      const stats = await api.getDashboardStats();
      set({ stats });
    } catch (error) {
      set({ error: 'Failed to fetch dashboard stats' });
    }
  },

  fetchRecentTransactions: async () => {
    try {
      const transactions = await api.getTransactionFeed(20);
      set({ recentTransactions: transactions });
    } catch (error) {
      set({ error: 'Failed to fetch transactions' });
    }
  },

  fetchActiveAlerts: async () => {
    try {
      const alerts = await api.getActiveAlerts();
      set({ activeAlerts: alerts });
    } catch (error) {
      set({ error: 'Failed to fetch alerts' });
    }
  },

  refresh: async () => {
    set({ isLoading: true });
    await Promise.all([
      useDashboardStore.getState().fetchStats(),
      useDashboardStore.getState().fetchRecentTransactions(),
      useDashboardStore.getState().fetchActiveAlerts(),
    ]);
    set({ isLoading: false });
  },
}));