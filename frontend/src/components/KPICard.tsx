import { clsx } from 'clsx';
import { motion } from 'framer-motion';

interface KPICardProps {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'neutral' | 'warning';
  icon: React.ElementType;
  color: string;
  delay?: number;
}

export default function KPICard({ title, value, change, trend, icon: Icon, color, delay = 0 }: KPICardProps) {
  const isUp = trend === 'up';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="card p-6 group hover:border-white/20"
    >
      <div className="absolute top-0 right-0 p-24 bg-white/5 rounded-full blur-[60px] pointer-events-none group-hover:bg-theme-blue/10 transition duration-700" />
      
      <div className="relative flex items-center justify-between mb-4">
        <div className={clsx('p-3 rounded-[12px] bg-[#111827] border border-white/5 group-hover:scale-110 transition-transform duration-300 shadow-inner')}>
          <Icon size={22} className={clsx('text-theme-blue', color === 'purple' && 'text-theme-purple')} />
        </div>
        <div className={clsx(
          'flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold',
          isUp ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
          trend === 'warning' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
          trend === 'down' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
          'bg-slate-500/10 text-slate-400 border border-slate-500/20'
        )}>
          <span>{change}</span>
        </div>
      </div>
      
      <div className="relative">
        <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
        <p className="text-sm font-medium text-slate-400 mt-1 uppercase tracking-wider">{title}</p>
      </div>
    </motion.div>
  );
}
