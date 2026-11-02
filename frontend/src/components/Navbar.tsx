import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, LayoutDashboard, Zap, History, Building2, LogOut, BookOpen, Brain } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Analyze Match', path: '/analysis', icon: Zap },
    { label: 'History', path: '/analysis-history', icon: History },
    { label: 'Companies', path: '/companies', icon: Building2 },
    { label: 'Learning', path: '/learning', icon: BookOpen },
    { label: 'Assess Skills', path: '/skill-assessment', icon: Brain },
  ];

  return (
    <header className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 px-6 md:px-10 py-3.5 flex justify-between items-center sticky top-0 z-50 shadow-2xs">
      <Link to="/dashboard" className="flex items-center gap-3 group">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent leading-none">
            AI Placement Copilot
          </h1>
          <p className="text-[10px] text-slate-400 font-medium mt-0.5">Resume & Job Description Analyzer</p>
        </div>
      </Link>

      <div className="flex items-center space-x-1 sm:space-x-4">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.path || (link.path === '/analysis-history' && location.pathname === '/history') || (link.path === '/learning' && location.pathname.startsWith('/learning'));
          return (
            <Link
              key={link.path}
              to={link.path}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                isActive
                  ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-2xs'
                  : 'text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{link.label}</span>
            </Link>
          );
        })}

        <div className="flex items-center space-x-2.5 ml-2 border-l border-slate-200 dark:border-slate-700 pl-3 sm:pl-4">
          {user?.picture ? (
            <img src={user.picture} alt="Profile" className="w-7 h-7 rounded-full border border-slate-300" />
          ) : (
            <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 text-xs font-bold flex items-center justify-center">
              {user?.name ? user.name[0].toUpperCase() : 'U'}
            </div>
          )}

          <button
            onClick={logout}
            className="flex items-center gap-1 text-xs font-semibold text-slate-400 hover:text-red-500 transition-colors cursor-pointer p-1 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
