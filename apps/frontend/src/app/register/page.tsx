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

  // Validation functions
  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const checkPasswordStrength = (password: string) => {
    if (password.length < 8) return 0;
    let strength = 1;
    if (password.length >= 12) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getPasswordStrengthText = (strength: number) => {
    switch (strength) {
      case 0: return "Too Short";
      case 1: return "Very Weak";
      case 2: return "Weak";
      case 3: return "Fair";
      case 4: return "Good";
      case 5: return "Strong";
      default: return "Very Strong";
    }
  };

  const getPasswordStrengthColor = (strength: number) => {
    switch (strength) {
      case 0: return "bg-error/20 text-error";
      case 1: return "bg-error/20 text-error";
      case 2: return "bg-warning/20 text-warning";
      case 3: return "bg-warning/20 text-warning";
      case 4: return "bg-success/20 text-success";
      case 5: return "bg-success/20 text-success";
      default: return "bg-success/20 text-success";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setErrorMsg(null);

    // Validate full name
    if (!fullName.trim()) {
      setErrorMsg('Please enter your full name.');
      return;
    }

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
      setErrorMsg('Please enter a password.');
      return;
    }

    if (password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    const passwordStrength = checkPasswordStrength(password);
    if (passwordStrength < 3) {
      setErrorMsg('Password should be stronger. Include uppercase, lowercase, numbers, and special characters.');
      return;
    }

    // Validate confirm password
    if (!confirmPassword) {
      setErrorMsg('Please confirm your password.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    // Validate terms
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
      // Handle specific error messages from API
      if (err.response?.data?.message) {
        setErrorMsg(err.response.data.message);
      } else if (err.message) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Registration failed. Please try again.');
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
              {/* Password Strength Indicator */}
              <div className="mt-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold">Password Strength:</span>
                  <span>{getPasswordStrengthText(checkPasswordStrength(password))}</span>
                </div>
                <div className="w-full bg-surface-secondary/5 rounded-full h-1.5 mt-1 overflow-hidden">
                  <div
                    className={`${getPasswordStrengthColor(checkPasswordStrength(password))} h-full transition-all duration-300`}
                    style={{ width: `${checkPasswordStrength(password) * 20}%` }}
                  ></div>
                </div>
                <p className="text-xs text-foreground-muted mt-1">
                  Use at least 8 characters, including uppercase, lowercase, numbers, and symbols
                </p>
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