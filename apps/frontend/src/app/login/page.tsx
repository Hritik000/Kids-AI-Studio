"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, ArrowRight, Lock, Mail, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validation functions
  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setErrorMsg(null);

    // Validate email
    if (!email) {
      setErrorMsg('Please enter your email address.');
      return;
    }

    if (!isValidEmail(email)) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }

    // Validate password
    if (!password) {
      setErrorMsg('Please enter your password.');
      return;
    }

    if (password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email, password, rememberMe);
      router.push('/dashboard');
    } catch (error: unknown) {
      setErrorMsg(getErrorMessage(error) || 'Invalid credentials. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleLogin = () => {
    // Supabase Auth Google OAuth trigger
    window.location.href = 'http://localhost:8000/api/v1/auth/google';
  };

  return (
    <div className="min-h-screen bg-background-primary flex items-center justify-center p-6">
      <div className="w-full max-w-md space-y-8">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 text-xl font-bold text-foreground-primary tracking-tight">
            <div className="w-8 h-8 rounded-xl gradient-button flex items-center justify-center shadow-lg">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span>KidsAI <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Studio</span></span>
          </Link>
          <h1 className="text-2xl font-bold text-foreground-primary tracking-tight">Welcome Back</h1>
          <p className="text-sm text-foreground-muted">Sign in to your studio creator account</p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-error/10 border border-error/20 text-error/300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* OAuth Buttons */}
          <Button variant="outline" size="md" onClick={handleGoogleLogin} className="w-full text-foreground-primary hover:text-primary/80">
            <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 2 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span className="ml-2">Continue with Google</span>
          </Button>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-white/10 w-full" />
            <span className="bg-background-primary px-3 text-xs text-foreground-muted uppercase tracking-wider font-semibold absolute">
              or
            </span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Email Address</label>
              <div className="relative">
                <Mail className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="creator@kidsai.studio"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-semibold text-foreground-muted mb-1">Password</label>
                <Link href="/forgot-password" className="text-xs text-primary/400 hover:text-primary/600">
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-foreground-muted">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-white/20 bg-background-secondary/50 text-primary/600 focus:ring-primary/500"
                />
                <span>Remember me for 30 days</span>
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Signing In...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </form>
        </div>

        <p className="text-center text-xs text-foreground-muted">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="font-semibold text-primary/400 hover:text-primary/600">
            Sign up for free
          </Link>
        </p>
      </div>
    </div>
  );
}
