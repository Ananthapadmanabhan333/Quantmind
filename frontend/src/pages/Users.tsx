import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { User, RiskProfile } from '../types';
import { format } from 'date-fns';
import { clsx } from 'clsx';
import { Search, Filter, Shield, AlertTriangle, Users as UsersIcon } from 'lucide-react';

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  const [page, setPage] = useState(1);
  const [highRiskUsers, setHighRiskUsers] = useState<RiskProfile[]>([]);

  useEffect(() => {
    fetchUsers();
    fetchHighRisk();
  }, [page, segmentFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params: any = { page };
      if (segmentFilter) params.segment = segmentFilter;
      if (search) params.search = search;
      
      const data = await api.getUsers(params);
      setUsers(data.results);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHighRisk = async () => {
    try {
      const data = await api.getHighRiskUsers();
      setHighRiskUsers(data);
    } catch (error) {
      console.error('Failed to fetch high risk users:', error);
    }
  };

  const getRiskBadge = (score: number) => {
    if (score >= 80) return { color: 'text-red-400 bg-red-500/20', label: 'Critical' };
    if (score >= 60) return { color: 'text-orange-400 bg-orange-500/20', label: 'High' };
    if (score >= 40) return { color: 'text-amber-400 bg-amber-500/20', label: 'Medium' };
    return { color: 'text-emerald-400 bg-emerald-500/20', label: 'Low' };
  };

  const getSegmentColor = (segment: string) => {
    switch (segment) {
      case 'HIGH_RISK': return 'text-red-400';
      case 'SUSPICIOUS': return 'text-orange-400';
      case 'PREMIUM': return 'text-purple-400';
      case 'REGULAR': return 'text-blue-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Users</h1>
          <p className="text-slate-400 mt-1">Manage users and their risk profiles</p>
        </div>
        {highRiskUsers.length > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-lg">
            <AlertTriangle size={18} className="text-red-400" />
            <span className="text-sm text-red-400">{highRiskUsers.length} high risk users</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <UsersIcon size={20} className="text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">{users.length}</p>
              <p className="text-sm text-slate-400">Total Users</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle size={20} className="text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">{highRiskUsers.length}</p>
              <p className="text-sm text-slate-400">High Risk</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 rounded-lg">
              <Shield size={20} className="text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">
                {highRiskUsers.length > 0 
                  ? (highRiskUsers.reduce((acc, u) => acc + u.overall_score, 0) / highRiskUsers.length).toFixed(0)
                  : 0}
              </p>
              <p className="text-sm text-slate-400">Avg Risk Score</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <Shield size={20} className="text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">
                {users.length - highRiskUsers.length}
              </p>
              <p className="text-sm text-slate-400">Normal Users</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by email, name..."
              className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={segmentFilter}
            onChange={(e) => setSegmentFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Segments</option>
            <option value="PREMIUM">Premium</option>
            <option value="REGULAR">Regular</option>
            <option value="SUSPICIOUS">Suspicious</option>
            <option value="HIGH_RISK">High Risk</option>
            <option value="NEW">New User</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">User</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Segment</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Risk Score</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Transactions</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Fraud Prob.</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500">Loading...</td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500">No users found</td>
                </tr>
              ) : (
                users.map((user) => {
                  const risk = getRiskBadge(user.risk_score || 50);
                  return (
                    <tr key={user.id} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <span className="text-white font-medium">
                              {user.first_name?.[0] || user.email?.[0]?.toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white">
                              {user.first_name && user.last_name 
                                ? `${user.first_name} ${user.last_name}` 
                                : user.email}
                            </p>
                            <p className="text-xs text-slate-500">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={clsx('text-sm font-medium', getSegmentColor(user.segment || 'NEW'))}>
                          {user.segment || 'NEW'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={clsx('px-2 py-1 rounded text-xs font-medium', risk.color)}>
                          {user.risk_score?.toFixed(0) || 50}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm text-white">{user.transaction_count || 0}</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm text-white">
                          {user.risk_profile?.fraud_probability 
                            ? `${(user.risk_profile.fraud_probability * 100).toFixed(1)}%`
                            : '0%'}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <span className={clsx('badge', user.is_active ? 'badge-success' : 'badge-danger')}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-700/50">
          <p className="text-sm text-slate-400">Showing {users.length} users</p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-300 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={users.length < 20}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-300 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}