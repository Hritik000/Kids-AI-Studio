import React from 'react';
import Link from 'next/link';
import { Sparkles, Video, Clapperboard, ShieldCheck, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/lib/theme-context';
import { Button } from '@/components/ui/button';

export const Navbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-4 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl gradient-button flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-foreground-primary flex items-center gap-2">
                KidsAI <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Studio</span>
              </h1>
              <p className="text-xs text-foreground-muted font-medium">Autonomous YouTube Kids Video Engine</p>
            </div>
          </Link>
        </div>

        {/* Navigation & Status */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20 text-success/400 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>AI Multi-Agent Pipeline Online</span>
          </div>

          <Button variant="outline" size="md" onClick={toggleTheme} className="text-foreground-primary hover:text-primary/80">
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            <span className="ml-2">Theme</span>
          </Button>
        </div>
      </div>
    </header>
  );
};