import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Alert } from '../types';
import { format, formatDistanceToNow } from 'date-fns';
import { clsx } from 'clsx';
import { AlertTriangle, CheckCircle, Clock, Search, Filter, X, MessageSquare } from 'lucide-react';

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [resolving, setResolving] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;
      
      const data = await api.getAlerts(params);
      setAlerts(data.results);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (alertId: string, isFalsePositive: boolean) => {
    setResolving(true);
    try {
      await api.resolveAlert(alertId, 'Resolved', isFalsePositive);
      fetchAlerts();
      setSelectedAlert(null);
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    } finally {
      setResolving(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'HIGH': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      case 'MEDIUM': return 'text-amber-400 bg-amber-500/20 border-amber-500/30';
      case 'LOW': return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      default: return 'text-slate-400 bg-slate-500/20 border-slate-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RESOLVED': return <CheckCircle size={16} className="text-emerald-400" />;
      case 'INVESTIGATING': return <Clock size={16} className="text-amber-400" />;
      case 'FALSE_POSITIVE': return <X size={16} className="text-slate-400" />;
      default: return <AlertTriangle size={16} className="text-red-400" />;
    }
  };

  const activeAlerts = alerts.filter(a => !['RESOLVED', 'FALSE_POSITIVE'].includes(a.status));
  const resolvedAlerts = alerts.filter(a => ['RESOLVED', 'FALSE_POSITIVE'].includes(a.status));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Alerts</h1>
          <p className="text-slate-400 mt-1">Monitor and resolve fraud alerts</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/20 rounded-lg">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm text-red-400">{activeAlerts.length} active</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle size={20} className="text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">
                {alerts.filter(a => a.severity === 'CRITICAL' && a.status === 'NEW').length}
              </p>
              <p className="text-sm text-slate-400">Critical</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-500/10 rounded-lg">
              <AlertTriangle size={20} className="text-orange-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">
                {alerts.filter(a => a.status === 'NEW').length}
              </p>
              <p className="text-sm text-slate-400">New</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 rounded-lg">
              <Clock size={20} className="text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">
                {alerts.filter(a => a.status === 'INVESTIGATING').length}
              </p>
              <p className="text-sm text-slate-400">Investigating</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <CheckCircle size={20} className="text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-white">{resolvedAlerts.length}</p>
              <p className="text-sm text-slate-400">Resolved</p>
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
              placeholder="Search alerts..."
              className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="NEW">New</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Severity</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading...</div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No alerts found</div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={clsx(
                'bg-slate-800/50 backdrop-blur border rounded-xl p-4 hover:border-slate-600/50 transition-colors cursor-pointer',
                alert.severity === 'CRITICAL' ? 'border-red-500/30' :
                alert.severity === 'HIGH' ? 'border-orange-500/30' :
                'border-slate-700/50'
              )}
              onClick={() => setSelectedAlert(alert)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={clsx('p-2 rounded-lg', getSeverityColor(alert.severity))}>
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={clsx('text-xs font-medium px-2 py-0.5 rounded', getSeverityColor(alert.severity))}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-slate-500">{alert.alert_type}</span>
                    </div>
                    <p className="text-sm text-white mt-2">{alert.message}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                      <span>{alert.user_email || 'System'}</span>
                      <span>{formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(alert.status)}
                  <span className="text-sm text-slate-400">{alert.status}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-6 border-b border-slate-700">
              <h2 className="text-lg font-semibold text-white">Alert Details</h2>
              <button onClick={() => setSelectedAlert(null)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <span className={clsx('text-sm font-medium px-3 py-1 rounded', getSeverityColor(selectedAlert.severity))}>
                  {selectedAlert.severity}
                </span>
                <span className="text-sm text-slate-400">{selectedAlert.alert_type}</span>
              </div>
              <div>
                <p className="text-sm text-slate-400">Message</p>
                <p className="text-sm text-white mt-1">{selectedAlert.message}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">User</p>
                  <p className="text-sm text-white">{selectedAlert.user_email || 'System'}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Created</p>
                  <p className="text-sm text-white">{format(new Date(selectedAlert.created_at), 'PPpp')}</p>
                </div>
              </div>
              {selectedAlert.status === 'NEW' && (
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => handleResolve(selectedAlert.id, true)}
                    disabled={resolving}
                    className="flex-1 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-300 transition-colors"
                  >
                    False Positive
                  </button>
                  <button
                    onClick={() => handleResolve(selectedAlert.id, false)}
                    disabled={resolving}
                    className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
                  >
                    {resolving ? 'Resolving...' : 'Resolve'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}