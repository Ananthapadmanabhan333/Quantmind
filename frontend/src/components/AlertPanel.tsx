import { AlertTriangle, Shield } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';

interface AlertPanelProps {
  activeAlerts: any[];
}

export default function AlertPanel({ activeAlerts }: AlertPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="card p-6 relative rounded-[24px]"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white relative">
          System Alerts
          <span className="absolute -bottom-2 left-0 w-8 h-1 bg-rose-500 rounded-full" />
        </h3>
        <a href="/alerts" className="text-sm font-semibold text-rose-400 hover:text-rose-300 transition-colors px-3 py-1 bg-rose-500/10 rounded-full border border-rose-500/20 hover:bg-rose-500/20">
          View all
        </a>
      </div>
      
      <div className="space-y-3">
        {activeAlerts.slice(0, 6).map((alert, idx) => (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.6 + idx * 0.1 }}
            key={alert.id}
            className="p-4 rounded-2xl bg-[#111827]/80 border border-white/5 hover:border-rose-500/30 transition-colors group relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 bottom-0 w-1 bg-rose-500/50 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className={clsx(
                  alert.severity === 'CRITICAL' ? 'text-red-400' :
                  alert.severity === 'HIGH' ? 'text-orange-400' :
                  alert.severity === 'MEDIUM' ? 'text-amber-400' :
                  'text-blue-400'
                )} />
                <span className={clsx(
                  'text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider',
                  alert.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                  alert.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                  alert.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                )}>
                  {alert.severity}
                </span>
              </div>
              <span className="text-xs font-semibold text-slate-500">
                {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
              </span>
            </div>
            <p className="text-sm font-semibold text-slate-200 mt-3 leading-snug">{alert.message}</p>
            <p className="text-xs font-medium text-slate-500 mt-2 bg-[#0B0F1A] px-2 py-1 rounded inline-block">
              <span className="text-slate-400">{alert.alert_type}</span> • {alert.user_email || 'System'}
            </p>
          </motion.div>
        ))}
        {activeAlerts.length === 0 && (
          <div className="text-center py-12">
            <Shield size={40} className="mx-auto text-emerald-500 mb-4 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
            <p className="text-slate-300 font-bold text-lg">System Secure</p>
            <p className="text-slate-500 text-sm mt-1">No active alerts to display at this time.</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
