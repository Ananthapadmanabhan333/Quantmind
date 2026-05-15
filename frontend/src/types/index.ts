export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'ANALYST' | 'VIEWER';
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface Transaction {
  id: string;
  user: string;
  user_email: string;
  user_name: string;
  amount: number;
  currency: string;
  transaction_type: 'DEBIT' | 'CREDIT' | 'TRANSFER' | 'WITHDRAWAL' | 'DEPOSIT';
  merchant: string;
  merchant_category?: string;
  merchant_country?: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  timestamp: string;
  status: 'PENDING' | 'COMPLETED' | 'FLAGGED' | 'BLOCKED' | 'INVESTIGATING';
  fraud_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  fraud_probability: number;
  is_anomaly: boolean;
  rule_triggers: Array<{ rule: string; message: string; severity: string }>;
  created_at: string;
}

export interface RiskProfile {
  id: string;
  user: string;
  user_email: string;
  overall_score: number;
  fraud_probability: number;
  last_transaction_count: number;
  last_24h_volume: number;
  last_7d_volume: number;
  avg_transaction_amount: number;
  avg_transaction_frequency: number;
  segment: string;
  is_high_risk: boolean;
}

export interface Alert {
  id: string;
  transaction: string;
  user?: string;
  user_email?: string;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'NEW' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE' | 'CONFIRMED_FRAUD';
  message: string;
  created_at: string;
  resolved_by?: string;
  resolved_at?: string;
}

export interface DashboardStats {
  total_transactions: number;
  total_volume: number;
  total_users: number;
  active_users: number;
  fraud_rate: number;
  avg_risk_score: number;
  high_risk_users: number;
  total_alerts: number;
  pending_alerts: number;
  critical_alerts: number;
}

export interface RiskDistribution {
  risk_level: string;
  count: number;
  percentage: number;
}

export interface TransactionVolume {
  date: string;
  volume: number;
  count: number;
}

export interface UserSegment {
  segment: string;
  count: number;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: User;
}