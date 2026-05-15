import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ArrowLeftRight, 
  Users, 
  AlertTriangle, 
  BarChart3,
  Settings,
  LogOut
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuthStore } from '../hooks/useStore';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/transactions', icon: ArrowLeftRight, label: 'Transactions' },
  { path: '/analytics', icon: BarChart3, label: 'Risk Analysis' },
  { path: '/users', icon: Users, label: 'Users' },
  { path: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export default function Sidebar({ sidebarOpen, setSidebarOpen }: SidebarProps) {
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <aside
      className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 glass-panel border-r border-white/5 transform transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]',
        sidebarOpen ? 'translate-x-0 shadow-[20px_0_40px_rgba(0,0,0,0.5)]' : '-translate-x-full lg:translate-x-0'
      )}
    >
      <div className="flex flex-col h-full bg-gradient-to-b from-white/[0.02] to-transparent">
        <div className="flex items-center gap-3 px-6 py-6 border-b border-white/5 relative">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-theme-blue to-theme-purple flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.4)]">
            <span className="text-white font-bold text-xl">Q</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">QuantMind</h1>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300 group relative overflow-hidden',
                  isActive
                    ? 'bg-theme-blue/10 text-theme-blue border border-theme-blue/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-100 border border-transparent'
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div 
                      layoutId="activeTab"
                      className="absolute inset-0 bg-theme-blue/5 z-0"
                      initial={false}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                  {isActive && (
                    <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-theme-blue rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.8)] z-10" />
                  )}
                  <item.icon size={20} className={clsx("relative z-10 transition-transform duration-300 group-hover:scale-110", isActive && "drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]")} />
                  <span className="relative z-10 font-semibold tracking-wide">{item.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-2xl text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-all border border-transparent hover:border-red-500/20"
          >
            <LogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
