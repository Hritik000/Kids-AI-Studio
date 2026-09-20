"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Sparkles, Lock, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function ResetPasswordPage() {
  const router = useRouter();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Validation functions
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

    // Reset messages
    setErrorMsg(null);
    setSuccessMsg(null);

    // Validate new password
    if (!newPassword) {
      setErrorMsg('Please enter a new password.');
      return;
    }

    if (newPassword.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    const passwordStrength = checkPasswordStrength(newPassword);
    if (passwordStrength < 3) {
      setErrorMsg('Password should be stronger. Include uppercase, lowercase, numbers, and special characters.');
      return;
    }

    // Validate confirm password
    if (!confirmPassword) {
      setErrorMsg('Please confirm your new password.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      // In a real implementation, you would call the reset password API here
      // For now, we'll simulate success
      setSuccessMsg('Your password has been successfully reset. Redirecting to login...');
      setTimeout(() => {
        router.push('/login');
      }, 1500);
    } catch (err: any) {
      // Handle specific error messages from API
      if (err.response?.data?.message) {
        setErrorMsg(err.response.data.message);
      } else if (err.message) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Password reset failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-primary flex items-center justify-center p-6">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 text-xl font-bold text-foreground-primary tracking-tight">
            <div className="w-8 h-8 rounded-xl gradient-button flex items-center justify-center shadow-lg">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span>KidsAI <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Studio</span></span>
          </Link>
          <h1 className="text-2xl font-bold text-foreground-primary tracking-tight">Reset Password</h1>
          <p className="text-sm text-foreground-muted">Set a new password for your account</p>
        </div>

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
              <label className="block text-xs font-semibold text-foreground-muted mb-2">New Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  className="w-full pl-10 pr-4"
                />
              </div>
              {/* Password Strength Indicator */}
              <div className="mt-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold">Password Strength:</span>
                  <span>{getPasswordStrengthText(checkPasswordStrength(newPassword))}</span>
                </div>
                <div className="w-full bg-surface-secondary/5 rounded-full h-1.5 mt-1 overflow-hidden">
                  <div
                    className={`${getPasswordStrengthColor(checkPasswordStrength(newPassword))} h-full transition-all duration-300`}
                    style={{ width: `${checkPasswordStrength(newPassword) * 20}%` }}
                  ></div>
                </div>
                <p className="text-xs text-foreground-muted mt-1">
                  Use at least 8 characters, including uppercase, lowercase, numbers, and symbols
                </p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground-muted mb-2">Confirm New Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-foreground-muted/50 absolute left-3 top-3" />
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat new password"
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
                  <span>Updating Password...</span>
                </>
              ) : (
                <span>Update Password</span>
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}