"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { forgotPasswordApi } from '@/lib/api';
import { Sparkles, ArrowLeft, Mail, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Validation functions
  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset messages
    setErrorMsg(null);
    setSuccessMsg(null);

    // Validate email
    if (!email) {
      setErrorMsg('Please enter your email address.');
      return;
    }

    if (!isValidEmail(email)) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    try {
      const msg = await forgotPasswordApi(email);
      setSuccessMsg(msg);
    } catch (err: unknown) {
      // Handle specific error messages from API
      const e = err as { response?: { data?: { message?: string } }; message?: string };
      if (e.response?.data?.message) {
        setErrorMsg(e.response.data.message);
      } else if (e.message) {
        setErrorMsg(e.message);
      } else {
        setErrorMsg('Password reset request failed. Please check your email and try again.');
      }
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
          <h1 className="text-2xl font-bold text-foreground-primary tracking-tight">Forgot Password</h1>
          <p className="text-sm text-foreground-muted">Enter your email to receive reset instructions</p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-error/10 border border-error/20 text-error/300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-4 rounded-xl bg-success/10 border border-success/20 text-success/300 text-sm flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-success/400" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Registered Email</label>
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
                  <span>Sending reset link...</span>
                </>
              ) : (
                <span>Send Reset Link</span>
              )}
            </Button>
          </form>

          <div className="pt-2 text-center">
            <Link href="/login" className="inline-flex items-center gap-2 text-xs text-foreground-muted hover:text-primary/600 transition-colors">
              <ArrowLeft className="w-4 h-4" /> Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}