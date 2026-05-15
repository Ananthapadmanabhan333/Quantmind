import { DollarSign } from 'lucide-react';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';

interface TransactionTableProps {
  recentTransactions: any[];
  formatCurrency: (value: number) => string;
  getStatusColor: (status: string) => string;
  getRiskColor: (level: string) => string;
}

export default function TransactionTable({ recentTransactions, formatCurrency, getStatusColor, getRiskColor }: TransactionTableProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="card p-6 relative rounded-[24px]"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white relative">
          Live Transactions
          <span className="absolute -bottom-2 left-0 w-8 h-1 bg-theme-blue rounded-full" />
        </h3>
        <a href="/transactions" className="text-sm font-semibold text-theme-blue hover:text-blue-400 transition-colors px-3 py-1 bg-theme-blue/10 rounded-full border border-theme-blue/20 hover:bg-theme-blue/20">
          View all
        </a>
      </div>
      
      <div className="overflow-hidden rounded-xl border border-white/5 bg-[#0B0F1A]/50">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#111827] border-b border-white/5">
              <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Merchant / User</th>
              <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Amount</th>
              <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {recentTransactions.slice(0, 8).map((tx, idx) => {
              const isHighRisk = tx.risk_level === 'CRITICAL' || tx.risk_level === 'HIGH';
              return (
                <tr
                  key={tx.id}
                  className={clsx(
                    "border-b border-white/5 transition-colors group hover:bg-[#111827]",
                    isHighRisk && "hover:bg-rose-500/10 shadow-[inset_0_0_20px_rgba(244,63,94,0.05)]"
                  )}
                >
                  <td className="p-4 flex items-center gap-3">
                    <div className={clsx(
                      'w-10 h-10 rounded-xl flex items-center justify-center border border-white/5 shadow-sm transition-transform duration-300 group-hover:scale-110',
                      tx.risk_level === 'CRITICAL' ? 'bg-red-500/20' :
                      tx.risk_level === 'HIGH' ? 'bg-orange-500/20' :
                      tx.risk_level === 'MEDIUM' ? 'bg-amber-500/20' :
                      'bg-emerald-500/20'
                    )}>
                      <DollarSign size={18} className={getRiskColor(tx.risk_level)} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white tracking-wide">{tx.merchant}</p>
                      <p className="text-xs font-medium text-slate-500">{tx.user_email}</p>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <p className="text-sm font-bold text-slate-200">{formatCurrency(tx.amount)}</p>
                  </td>
                  <td className="p-4 text-center">
                    <span className={clsx('badge', getStatusColor(tx.status))}>
                      {tx.status}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        
        {recentTransactions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-500 font-medium">No recent transactions</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
