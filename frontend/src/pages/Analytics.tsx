import { useEffect, useState } from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import { api } from '../services/api';
import { format } from 'date-fns';
import { clsx } from 'clsx';
import { TrendingUp, Users, DollarSign, AlertTriangle, Activity, RefreshCw } from 'lucide-react';

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6'];

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [volumeData, setVolumeData] = useState<any[]>([]);
  const [riskDistribution, setRiskDistribution] = useState<any[]>([]);
  const [userSegments, setUserSegments] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [volume, risk, segments, statsData] = await Promise.all([
        api.getTransactionVolume(14),
        api.getRiskDistribution(),
        api.getUserSegments(),
        api.getDashboardStats(),
      ]);
      setVolumeData(volume);
      setRiskDistribution(risk);
      setUserSegments(segments);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
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

  const volumeWithCount = volumeData.map(item => ({
    ...item,
    formattedDate: format(new Date(item.date), 'MMM d'),
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Analytics</h1>
          <p className="text-slate-400 mt-1">Insights and trends from your data</p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors"
        >
          <RefreshCw size={18} className={clsx(loading && 'animate-spin')} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Activity size={20} className="text-blue-400" />
            </div>
            <span className="text-xs text-emerald-400">+12.5%</span>
          </div>
          <p className="text-2xl font-semibold text-white">{stats?.total_transactions?.toLocaleString()}</p>
          <p className="text-sm text-slate-400 mt-1">Total Transactions</p>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <DollarSign size={20} className="text-emerald-400" />
            </div>
            <span className="text-xs text-emerald-400">+8.3%</span>
          </div>
          <p className="text-2xl font-semibold text-white">{formatCurrency(stats?.total_volume || 0)}</p>
          <p className="text-sm text-slate-400 mt-1">Total Volume</p>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Users size={20} className="text-purple-400" />
            </div>
            <span className="text-xs text-emerald-400">+5.2%</span>
          </div>
          <p className="text-2xl font-semibold text-white">{stats?.active_users?.toLocaleString()}</p>
          <p className="text-sm text-slate-400 mt-1">Active Users</p>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle size={20} className="text-red-400" />
            </div>
            <span className="text-xs text-red-400">+3</span>
          </div>
          <p className="text-2xl font-semibold text-white">{stats?.fraud_rate?.toFixed(1)}%</p>
          <p className="text-sm text-slate-400 mt-1">Fraud Rate</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Transaction Volume (14 Days)</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={volumeWithCount}>
                <defs>
                  <linearGradient id="volumeGradient2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="formattedDate" 
                  stroke="#64748B" 
                  fontSize={12}
                />
                <YAxis 
                  stroke="#64748B" 
                  fontSize={12}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1E293B', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#F8FAFC' }}
                  formatter={(value: number, name: string) => [
                    name === 'volume' ? formatCurrency(value) : value,
                    name === 'volume' ? 'Volume' : 'Count'
                  ]}
                />
                <Area 
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#volumeGradient2)" 
                  name="volume"
                />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#10B981" 
                  fill="none"
                  strokeWidth={2}
                  name="count"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          <div className="h-80 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="risk_level"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: '#64748B' }}
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1E293B', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">User Segments</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={userSegments} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#64748B" fontSize={12} />
                <YAxis 
                  type="category" 
                  dataKey="segment" 
                  stroke="#64748B" 
                  fontSize={12}
                  width={80}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1E293B', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="count" fill="#3B82F6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Transaction Type Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { type: 'Debit', count: Math.floor(Math.random() * 5000) + 2000 },
                  { type: 'Credit', count: Math.floor(Math.random() * 3000) + 1000 },
                  { type: 'Transfer', count: Math.floor(Math.random() * 2000) + 500 },
                  { type: 'Withdrawal', count: Math.floor(Math.random() * 1500) + 300 },
                  { type: 'Deposit', count: Math.floor(Math.random() * 2000) + 800 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="type" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1E293B', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Daily Transaction Summary</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left px-4 py-3 text-sm font-medium text-slate-400">Date</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Volume</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Transactions</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Avg Amount</th>
              </tr>
            </thead>
            <tbody>
              {volumeWithCount.slice(-7).map((item, index) => (
                <tr key={index} className="border-b border-slate-700/30">
                  <td className="px-4 py-3 text-sm text-white">{item.formattedDate}</td>
                  <td className="px-4 py-3 text-sm text-white text-right">{formatCurrency(item.volume)}</td>
                  <td className="px-4 py-3 text-sm text-white text-right">{item.count}</td>
                  <td className="px-4 py-3 text-sm text-white text-right">
                    {formatCurrency(item.count > 0 ? item.volume / item.count : 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}