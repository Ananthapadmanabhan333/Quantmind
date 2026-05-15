import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Transaction } from '../types';
import { format } from 'date-fns';
import { clsx } from 'clsx';
import { Search, Filter, ChevronLeft, ChevronRight, Eye, AlertTriangle, X } from 'lucide-react';

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  useEffect(() => {
    fetchTransactions();
  }, [page, statusFilter, riskFilter]);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const params: any = { page };
      if (statusFilter) params.status = statusFilter;
      if (riskFilter) params.risk_level = riskFilter;
      if (search) params.search = search;
      
      const data = await api.getTransactions(params);
      setTransactions(data.results);
      setTotalPages(Math.ceil(data.count / 20));
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-emerald-400 bg-emerald-500/20';
      case 'MEDIUM': return 'text-amber-400 bg-amber-500/20';
      case 'HIGH': return 'text-orange-400 bg-orange-500/20';
      case 'CRITICAL': return 'text-red-400 bg-red-500/20';
      default: return 'text-slate-400 bg-slate-500/20';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'badge-success';
      case 'FLAGGED': return 'badge-warning';
      case 'BLOCKED': return 'badge-danger';
      case 'PENDING': return 'badge-info';
      case 'INVESTIGATING': return 'badge-info';
      default: return 'badge-info';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Transactions</h1>
          <p className="text-slate-400 mt-1">Monitor and analyze all transactions</p>
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
              placeholder="Search by merchant, location..."
              className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="PENDING">Pending</option>
            <option value="COMPLETED">Completed</option>
            <option value="FLAGGED">Flagged</option>
            <option value="BLOCKED">Blocked</option>
            <option value="INVESTIGATING">Investigating</option>
          </select>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Risk</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Time</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Merchant</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">User</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Amount</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Risk Score</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Status</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">Loading...</td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">No transactions found</td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr key={tx.id} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                    <td className="px-6 py-4">
                      <p className="text-sm text-white">{format(new Date(tx.timestamp), 'MMM d, HH:mm')}</p>
                      <p className="text-xs text-slate-500">{format(new Date(tx.timestamp), 'yyyy')}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-white">{tx.merchant}</p>
                      <p className="text-xs text-slate-500">{tx.merchant_category || 'N/A'}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-white">{tx.user_email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-white">{formatCurrency(tx.amount)}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={clsx('px-2 py-1 rounded text-xs font-medium', getRiskColor(tx.risk_level))}>
                        {tx.fraud_score.toFixed(0)} - {tx.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={clsx('badge', getStatusBadge(tx.status))}>
                        {tx.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedTx(tx)}
                        className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors"
                      >
                        <Eye size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-700/50">
          <p className="text-sm text-slate-400">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-300 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-300 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {selectedTx && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-slate-700">
              <h2 className="text-lg font-semibold text-white">Transaction Details</h2>
              <button onClick={() => setSelectedTx(null)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Transaction ID</p>
                  <p className="text-sm text-white font-mono">{selectedTx.id}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Timestamp</p>
                  <p className="text-sm text-white">{format(new Date(selectedTx.timestamp), 'PPpp')}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Amount</p>
                  <p className="text-xl font-semibold text-white">{formatCurrency(selectedTx.amount)}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Type</p>
                  <p className="text-sm text-white">{selectedTx.transaction_type}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Merchant</p>
                  <p className="text-sm text-white">{selectedTx.merchant}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Location</p>
                  <p className="text-sm text-white">{selectedTx.location || 'N/A'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Fraud Score</p>
                  <p className={clsx('text-lg font-semibold', getRiskColor(selectedTx.risk_level))}>
                    {selectedTx.fraud_score.toFixed(1)}/100
                  </p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Risk Level</p>
                  <span className={clsx('badge', getStatusBadge(selectedTx.status))}>
                    {selectedTx.risk_level}
                  </span>
                </div>
              </div>
              {selectedTx.rule_triggers && selectedTx.rule_triggers.length > 0 && (
                <div>
                  <p className="text-sm text-slate-400 mb-2">Triggered Rules</p>
                  <div className="space-y-2">
                    {selectedTx.rule_triggers.map((rule, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 bg-slate-900/50 rounded">
                        <AlertTriangle size={16} className="text-amber-400" />
                        <span className="text-sm text-white">{rule.rule}</span>
                        <span className="text-xs text-slate-400">- {rule.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}