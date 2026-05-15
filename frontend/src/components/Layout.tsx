import { useState, useEffect } from 'react';
import { useDashboardStore } from '../hooks/useStore';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    useDashboardStore.getState().fetchStats();
    const interval = setInterval(() => useDashboardStore.getState().fetchStats(), 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0F1A] relative overflow-hidden">
      {/* Background gradients for premium glass effect */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 -left-1/4 w-[150%] h-[500px] bg-theme-blue/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 -right-1/4 w-[150%] h-[500px] bg-theme-purple/5 blur-[120px] rounded-full" />
      </div>

      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      <div className="lg:pl-64 relative z-10 flex flex-col min-h-screen">
        <Topbar setSidebarOpen={setSidebarOpen} />

        <main className="flex-1 p-4 lg:p-8 w-full max-w-[1600px] mx-auto">
          {children}
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-[#0B0F1A]/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}