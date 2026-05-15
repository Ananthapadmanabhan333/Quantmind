import { Bell, Search, Menu } from 'lucide-react';
import { useAuthStore, useDashboardStore } from '../hooks/useStore';

interface TopbarProps {
  setSidebarOpen: (open: boolean) => void;
}

export default function Topbar({ setSidebarOpen }: TopbarProps) {
  const { user } = useAuthStore();
  const { stats } = useDashboardStore();

  return (
    <header className="sticky top-0 z-40 bg-[#0B0F1A]/80 backdrop-blur-xl border-b border-white/5 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 lg:px-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2.5 rounded-xl text-slate-400 hover:bg-white/5 transition-colors"
          >
            <Menu size={24} />
          </button>
          
          <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-[#111827] rounded-full border border-white/5 focus-within:border-theme-blue/50 focus-within:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all">
            <Search size={18} className="text-slate-500" />
            <input
              type="text"
              placeholder="Search transactions..."
              className="bg-transparent border-none outline-none text-sm font-medium text-slate-200 placeholder-slate-500 w-72"
            />
          </div>
        </div>

        <div className="flex items-center gap-5">
          <button className="relative p-2.5 rounded-full text-slate-400 bg-white/5 hover:bg-theme-blue/10 hover:text-theme-blue transition-all duration-300 group border border-white/5">
            <Bell size={20} className="group-hover:animate-bounce" />
            {stats?.pending_alerts && stats.pending_alerts > 0 && (
              <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-[2.5px] border-[#0B0F1A]" />
            )}
          </button>

          <div className="flex items-center gap-3 pl-5 border-l border-white/10">
            <div className="hidden sm:block text-right cursor-pointer group">
              <p className="text-sm font-bold text-slate-200 group-hover:text-theme-blue transition-colors">
                {user?.first_name || user?.email}
              </p>
              <p className="text-xs font-semibold text-slate-500 tracking-wide uppercase">
                {user?.role}
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-theme-blue to-theme-purple flex items-center justify-center border-2 border-[#111827] ring-2 ring-white/5 cursor-pointer hover:scale-105 transition-transform duration-300">
              <span className="text-white font-bold text-sm">
                {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
