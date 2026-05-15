import axios, { AxiosInstance, AxiosError } from 'axios';
import type { AuthTokens, User, Transaction, DashboardStats, Alert, RiskDistribution, TransactionVolume, UserSegment, RiskProfile } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiService {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' },
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
          (originalRequest as any)._retry = true;
          try {
            await this.refreshToken();
            return this.client(originalRequest);
          } catch {
            this.logout();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const { data } = await this.client.post<AuthTokens>('/auth/login/', { email, password });
    this.setTokens(data);
    return data;
  }

  async register(email: string, username: string, password: string, firstName?: string, lastName?: string): Promise<AuthTokens> {
    const { data } = await this.client.post<AuthTokens>('/auth/register/', {
      email,
      username,
      password,
      password_confirm: password,
      first_name: firstName,
      last_name: lastName,
    });
    this.setTokens(data);
    return data;
  }

  async refreshToken(): Promise<void> {
    if (this.refreshPromise) return this.refreshPromise;

    this.refreshPromise = (async () => {
      const refresh = localStorage.getItem('refresh_token');
      const { data } = await this.client.post<{ access: string }>('/auth/refresh/', { refresh });
      localStorage.setItem('access_token', data.access);
      this.refreshPromise = null;
      return data.access;
    })();
    return this.refreshPromise;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  private setTokens(tokens: AuthTokens): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(tokens.user));
  }

  getUser(): User | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const { data } = await this.client.get<DashboardStats>('/dashboard/');
    return data;
  }

  async getTransactions(params?: { page?: number; status?: string; risk_level?: string; search?: string }): Promise<{ results: Transaction[]; count: number }> {
    const { data } = await this.client.get('/transactions/', { params });
    return data;
  }

  async getTransactionFeed(limit = 50): Promise<Transaction[]> {
    const { data } = await this.client.get<Transaction[]>('/transactions/feed/', { params: { limit } });
    return data;
  }

  async getTransactionStats(): Promise<any> {
    const { data } = await this.client.get('/transactions/stats/');
    return data;
  }

  async getAlerts(params?: { status?: string; severity?: string }): Promise<{ results: Alert[]; count: number }> {
    const { data } = await this.client.get('/dashboard/alerts/', { params });
    return data;
  }

  async getActiveAlerts(): Promise<Alert[]> {
    const { data } = await this.client.get('/dashboard/alerts/active_alerts/');
    return data;
  }

  async resolveAlert(alertId: string, resolution: string, isFalsePositive: boolean): Promise<Alert> {
    const { data } = await this.client.post(`/dashboard/alerts/${alertId}/resolve/`, {
      resolution,
      is_false_positive: isFalsePositive,
    });
    return data;
  }

  async getRiskDistribution(): Promise<RiskDistribution[]> {
    const { data } = await this.client.get('/dashboard/risk-distribution/');
    return data;
  }

  async getTransactionVolume(days = 7): Promise<TransactionVolume[]> {
    const { data } = await this.client.get('/dashboard/transaction-volume/', { params: { days } });
    return data;
  }

  async getUserSegments(): Promise<UserSegment[]> {
    const { data } = await this.client.get('/dashboard/user-segments/');
    return data;
  }

  async getUsers(params?: { segment?: string; risk_score_min?: number; search?: string }): Promise<{ results: User[]; count: number }> {
    const { data } = await this.client.get('/users/', { params });
    return data;
  }

  async getUserRiskProfile(userId: string): Promise<RiskProfile> {
    const { data } = await this.client.get(`/users/${userId}/risk-profile/`);
    return data;
  }

  async getHighRiskUsers(): Promise<RiskProfile[]> {
    const { data } = await this.client.get('/users/high-risk/');
    return data;
  }

  async createTransaction(transaction: Partial<Transaction>): Promise<Transaction> {
    const { data } = await this.client.post('/transactions/', transaction);
    return data;
  }
}

export const api = new ApiService();