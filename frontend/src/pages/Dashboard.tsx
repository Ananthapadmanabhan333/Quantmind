import { useEffect, useState } from 'react';
import { 
  AlertTriangle, 
  Shield, 
  Users, 
  TrendingUp,
  Activity,
  DollarSign,
  RefreshCw
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useDashboardStore, useAuthStore } from '../hooks/useStore';
import { api } from '../services/api';
import { clsx } from 'clsx';
import KPICard from '../components/KPICard';
import Charts from '../components/Charts';
import TransactionTable from '../components/TransactionTable';
import AlertPanel from '../components/AlertPanel';

export default function Dashboard() {
  const { stats, recentTransactions, activeAlerts, isLoading, refresh } = useDashboardStore();
  const [volumeData, setVolumeData] = useState<any[]>([]);
  const [riskDistribution, setRiskDistribution] = useState<any[]>([]);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    useDashboardStore.getState().refresh();
    loadChartData();
  }, []);

  const loadChartData = async () => {
    try {
      const [volume, risk] = await Promise.all([
        api.getTransactionVolume(7),
        api.getRiskDistribution(),
      ]);
      setVolumeData(volume);
      setRiskDistribution(risk);
    } catch (error) {
      console.error('Failed to load chart data:', error);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-emerald-400';
      case 'MEDIUM': return 'text-amber-400';
      case 'HIGH': return 'text-orange-400';
      case 'CRITICAL': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'badge-success';
      case 'FLAGGED': return 'badge-warning';
      case 'BLOCKED': return 'badge-danger';
      case 'PENDING': return 'badge-info';
      default: return 'badge-info';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const statCards = [
    {
      title: 'Total Transactions',
      value: stats?.total_transactions?.toLocaleString() || '0',
      change: '+12.5%',
      trend: 'up' as const,
      icon: Activity,
      color: 'blue',
    },
    {
      title: 'Total Volume',
      value: formatCurrency(stats?.total_volume || 0),
      change: '+8.3%',
      trend: 'up' as const,
      icon: DollarSign,
      color: 'blue',
    },
    {
      title: 'Fraud Detected',
      value: `${stats?.fraud_rate || 0}%`,
      change: '-2.1%',
      trend: 'down' as const,
      icon: Shield,
      color: 'purple',
    },
    {
      title: 'High Risk Users',
      value: stats?.high_risk_users?.toLocaleString() || '0',
      change: stats?.high_risk_users > 0 ? '+3' : '0',
      trend: stats?.high_risk_users > 0 ? 'warning' : 'neutral' as const,
      icon: AlertTriangle,
      color: 'purple',
    },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 relative z-10">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
            Overview
          </h1>
          <p className="text-slate-400 mt-2 text-sm font-medium">Real-time risk intelligence and transaction monitoring.</p>
        </div>
        <button
          onClick={() => refresh()}
          disabled={isLoading}
          className="btn-secondary flex items-center gap-2 group border-white/10"
        >
          <RefreshCw size={18} className={clsx(isLoading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500')} />
          Refresh Data
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
        {statCards.map((stat, index) => (
          <KPICard key={index} {...stat} delay={index * 0.1} />
        ))}
      </div>

      <div className="relative z-10">
        <Charts volumeData={volumeData} riskDistribution={riskDistribution} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10">
        <div className="lg:col-span-2">
          <TransactionTable 
            recentTransactions={recentTransactions} 
            formatCurrency={formatCurrency}
            getStatusColor={getStatusColor}
            getRiskColor={getRiskColor}
          />
        </div>
        <div>
          <AlertPanel activeAlerts={activeAlerts} />
        </div>
      </div>
    </motion.div>
  );
}