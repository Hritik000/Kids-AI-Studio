"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { forgotPasswordApi } from '@/lib/api';
import { Sparkles, ArrowLeft, Mail, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const msg = await forgotPasswordApi(email);
      setSuccessMsg(msg);
    } catch (err: any) {
      setErrorMsg(err.message || 'Password reset request failed.');
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Forgot Password</h1>
          <p className="text-sm text-gray-400">Enter your email to receive reset instructions</p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Registered Email</label>
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

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 rounded-xl gradient-button text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Sending reset link...</span>
                </>
              ) : (
                <span>Send Reset Link</span>
              )}
            </button>
          </form>

          <div className="pt-2 text-center">
            <Link href="/login" className="inline-flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Login</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
