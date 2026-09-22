"use client";

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Navbar } from '@/components/layout/Navbar';
import { User, Mail, Shield, Calendar, LogOut, CheckCircle2, AlertCircle, Save } from 'lucide-react';
import { useRouter } from 'next/navigation';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, updateProfile } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!user) {
    return (
      <div className="min-h-screen bg-[#090a0f] flex items-center justify-center p-6 text-white">
        <div className="text-center space-y-4">
          <p className="text-gray-400">Please sign in to view your profile.</p>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-2.5 rounded-xl gradient-button font-semibold text-sm"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await updateProfile(fullName);
      setSuccessMsg('Profile updated successfully!');
    } catch (error: unknown) {
      setErrorMsg(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-12 space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Account Profile</h1>
          <p className="text-sm text-gray-400 mt-1">Manage your creator credentials and workspace preferences</p>
        </div>

        {successMsg && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* User Overview Card */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col items-center text-center space-y-4">
            <div className="relative w-24 h-24 rounded-full overflow-hidden border-2 border-purple-500/50 p-1 bg-black/40">
              <img
                src={user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id}`}
                alt={user.full_name}
                className="w-full h-full rounded-full object-cover"
              />
            </div>

            <div>
              <h2 className="text-lg font-bold text-white">{user.full_name}</h2>
              <p className="text-xs text-gray-400">{user.email}</p>
            </div>

            <div className="w-full pt-4 border-t border-white/10 space-y-2 text-xs text-left">
              <div className="flex items-center justify-between text-gray-400">
                <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-purple-400" /> Role</span>
                <span className="font-semibold text-purple-300 uppercase px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">{user.role}</span>
              </div>
              <div className="flex items-center justify-between text-gray-400">
                <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5 text-blue-400" /> Joined</span>
                <span className="text-gray-200">{new Date(user.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="w-full mt-4 py-2.5 px-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Log Out</span>
            </button>
          </div>

          {/* Profile Edit Form */}
          <div className="md:col-span-2 glass-panel p-8 rounded-3xl border border-white/10 space-y-6">
            <h3 className="text-lg font-bold text-white">Edit Profile Details</h3>

            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Full Name</label>
                <div className="relative">
                  <User className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/15 text-white text-sm focus:outline-none focus:border-purple-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Email Address (Primary)</label>
                <div className="relative">
                  <Mail className="w-5 h-5 text-gray-500 absolute left-3.5 top-3" />
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-400 text-sm cursor-not-allowed"
                  />
                </div>
                <p className="text-[11px] text-gray-500 mt-1">Email changes require re-verification.</p>
              </div>

              <div className="pt-4 border-t border-white/10 flex justify-end">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-6 py-2.5 rounded-xl gradient-button text-white font-semibold text-sm flex items-center gap-2 shadow-lg disabled:opacity-50"
                >
                  {isSaving ? (
                    <span>Saving...</span>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
