"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, ArrowRight, Lock, Mail, User, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      setErrorMsg('Please fill in all required fields.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }
    if (!termsAccepted) {
      setErrorMsg('You must accept the Terms of Service & Child Safety Guidelines.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await register(fullName, email, password, confirmPassword);
      setIsSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
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
          <h1 className="text-2xl font-bold text-foreground-primary tracking-tight">Create Free Account</h1>
          <p className="text-sm text-foreground-muted">Start creating AI videos in 2 minutes</p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-error/10 border border-error/20 text-error/300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {isSuccess && (
            <div className="p-4 rounded-xl bg-success/10 border border-success/20 text-success/300 text-sm flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-success/400" />
              <span>Account created! Redirecting to studio workspace...</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Full Name</label>
              <div className="relative">
                <User className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Creator"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
            </div>

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
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Confirm Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
            </div>

            <div className="flex items-start gap-2 pt-1 text-xs text-foreground-muted">
              <input
                type="checkbox"
                id="terms"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-0.5 rounded border-white/20 bg-background-secondary/50 text-primary/600 focus:ring-primary/500"
              />
              <label htmlFor="terms" className="leading-tight cursor-pointer">
                I agree to the <span className="text-primary/400 underline">Terms of Service</span> and{' '}
                <span className="text-primary/400 underline">YouTube Kids Safety Guidelines</span>.
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isSubmitting || isSuccess}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account & Start</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </form>
        </div>

        <p className="text-center text-xs text-foreground-muted">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-primary/400 hover:text-primary/600">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}