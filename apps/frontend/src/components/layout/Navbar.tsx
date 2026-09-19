import React from 'react';
import { Sparkles, Video, Clapperboard, ShieldCheck, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/lib/theme-context';

export const Navbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-4 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl gradient-button flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              KidsAI <span className="gradient-text">Studio</span>
            </h1>
            <p className="text-xs text-gray-400 font-medium">Autonomous YouTube Kids Video Engine</p>
          </div>
        </div>

        {/* Navigation & Status */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>AI Multi-Agent Pipeline Online</span>
          </div>

          <button 
            className="px-4 py-2 rounded-xl glass-panel-interactive text-sm font-semibold text-white flex items-center gap-2 hover:glass-panel-interactive:hover"
            onClick={toggleTheme}
          >
            <Moon className="w-4 h-4 text-purple-400" />
            <span>Theme</span>
          </button>
        </div>
      </div>
    </header>
  );
};
