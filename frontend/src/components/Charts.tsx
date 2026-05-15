import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { format } from 'date-fns';
import { motion } from 'framer-motion';

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'];

interface ChartsProps {
  volumeData: any[];
  riskDistribution: any[];
}

export default function Charts({ volumeData, riskDistribution }: ChartsProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="card p-6 rounded-[24px]"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white relative">
            Transaction Volume
            <span className="absolute -bottom-2 left-0 w-8 h-1 bg-theme-blue rounded-full" />
          </h3>
          <span className="text-xs font-semibold text-slate-400 bg-[#111827] px-3 py-1 rounded-full border border-white/5">
            7 Days
          </span>
        </div>
        
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={volumeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="#64748B" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => format(new Date(value), 'MMM d')}
              />
              <YAxis 
                stroke="#64748B" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#111827', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)'
                }}
                labelStyle={{ color: '#94A3B8', marginBottom: '4px' }}
                itemStyle={{ color: '#F8FAFC', fontWeight: 600 }}
                formatter={(value: number) => [formatCurrency(value), 'Volume']}
              />
              <Area 
                type="monotone" 
                dataKey="volume" 
                stroke="#3B82F6" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorVolume)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="card p-6 rounded-[24px]"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white relative">
            Risk Distribution
            <span className="absolute -bottom-2 left-0 w-8 h-1 bg-theme-purple rounded-full" />
          </h3>
        </div>
        
        <div className="h-[300px] flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={110}
                paddingAngle={5}
                dataKey="count"
                nameKey="risk_level"
                stroke="none"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[index % COLORS.length]}
                    style={{ filter: `drop-shadow(0px 0px 8px ${COLORS[index % COLORS.length]}80)` }}
                  />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#111827', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
                itemStyle={{ color: '#F8FAFC', fontWeight: 600 }}
                formatter={(value: number, name: string) => [value, name]}
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="flex flex-col gap-3 ml-4 min-w-[120px]">
            {riskDistribution.map((item, index) => (
              <div key={item.risk_level} className="flex items-center justify-between p-2 rounded-lg bg-[#111827]/50 border border-white/5">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: COLORS[index % COLORS.length], boxShadow: `0 0 8px ${COLORS[index % COLORS.length]}` }} />
                  <span className="text-sm font-semibold text-slate-200">{item.risk_level}</span>
                </div>
                <span className="text-xs font-bold text-slate-500">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
