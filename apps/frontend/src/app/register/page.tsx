"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, ArrowRight, Lock, Mail, User, CheckCircle2, AlertCircle } from 'lucide-react';

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
    <div className="min-h-screen bg-[#090a0f] flex items-center justify-center p-6 selection:bg-purple-500 selection:text-white">
      <div className="w-full max-w-md space-y-8">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 text-xl font-bold text-white tracking-tight">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-white shadow-lg">
              <Sparkles className="w-4 h-4" />
            </div>
            <span>KidsAI Studio</span>
          </Link>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create Free Account</h1>
          <p className="text-sm text-gray-400">Start creating AI videos in 2 minutes</p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {isSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
              <span>Account created! Redirecting to studio workspace...</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Creator"
                  className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/15 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-purple-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="creator@kidsai.studio"
                  className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/15 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-purple-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/15 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-purple-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Confirm Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/15 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-purple-500"
                  required
                />
              </div>
            </div>

            <div className="flex items-start gap-2 pt-1 text-xs text-gray-400">
              <input
                type="checkbox"
                id="terms"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-0.5 rounded border-white/20 bg-black/40 text-purple-500 focus:ring-purple-500"
              />
              <label htmlFor="terms" className="leading-tight cursor-pointer">
                I agree to the <span className="text-purple-400 underline">Terms of Service</span> and{' '}
                <span className="text-purple-400 underline">YouTube Kids Safety Guidelines</span>.
              </label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || isSuccess}
              className="w-full py-3 rounded-xl gradient-button text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account & Start</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-gray-400">
          Already have an account?{' '}
          <Link href="/login" className="text-purple-400 font-semibold hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
