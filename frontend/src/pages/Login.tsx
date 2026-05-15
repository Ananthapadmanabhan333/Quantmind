import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../hooks/useStore';
import { Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0B0F1A] p-4 relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 -left-1/4 w-[150%] h-[500px] bg-theme-blue/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 -right-1/4 w-[150%] h-[500px] bg-theme-purple/10 blur-[120px] rounded-full" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="card p-10 rounded-[24px]">
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-theme-blue to-theme-purple flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.5)]">
              <span className="text-white font-bold text-3xl">Q</span>
            </div>
          </div>
          
          <h1 className="text-3xl font-bold text-center text-white mb-2 tracking-tight">Welcome back</h1>
          <p className="text-center font-medium text-slate-400 mb-8">Sign in to QuantMind</p>

          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
              className="flex items-center gap-2 p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/20"
            >
              <AlertCircle size={18} className="text-red-400" />
              <span className="text-sm font-semibold text-red-400">{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">Email</label>
              <div className="relative">
                <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 bg-[#0B0F1A]/80 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-theme-blue/50 focus:border-theme-blue transition-all"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">Password</label>
              <div className="relative">
                <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-12 py-3.5 bg-[#0B0F1A]/80 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-theme-blue/50 focus:border-theme-blue transition-all"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-4 mt-4 text-lg font-bold shadow-[0_0_20px_rgba(59,130,246,0.3)]"
            >
              {isLoading ? 'Authenticating...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-8 text-center text-sm font-medium text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-theme-blue hover:text-blue-400 transition-colors">
              Contact admin
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}