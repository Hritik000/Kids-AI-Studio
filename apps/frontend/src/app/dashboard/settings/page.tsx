"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Navbar } from '@/components/layout/Navbar';
import {
  listSubscriptionPlansApi,
  getUserSubscriptionApi,
  subscribeToPlanApi,
  listWorkspacesApi,
  createWorkspaceApi,
  listApiKeysApi,
  createApiKeyApi,
  revokeApiKeyApi,
  getAnalyticsSummaryApi,
  listNotificationsApi,
  SubscriptionPlan,
  UserSubscription,
  Workspace,
  APIKeyItem,
  NotificationItem,
  AnalyticsSummary
} from '@/lib/api';
import {
  CreditCard,
  Key,
  Users,
  BarChart3,
  Bell,
  ShieldCheck,
  Check,
  Plus,
  Trash2,
  Sparkles,
  Zap,
  Globe,
  ArrowLeft
} from 'lucide-react';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

export default function SaaSManagementPage() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKeyItem[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const [activeTab, setActiveTab] = useState<'billing' | 'workspaces' | 'apikeys' | 'analytics' | 'notifications'>('billing');
  const [isLoading, setIsLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState('');
  const [newWsName, setNewWsName] = useState('');

  const loadSaaSData = async () => {
    setIsLoading(true);
    try {
      try { const p = await listSubscriptionPlansApi(); setPlans(p); } catch (error: unknown) {
        console.warn('Failed to load subscription plans', error);
      }
      try { const sub = await getUserSubscriptionApi(); setSubscription(sub); } catch (error: unknown) {
        console.warn('Failed to get user subscription', error);
      }
      try { const ws = await listWorkspacesApi(); setWorkspaces(ws); } catch (error: unknown) {
        console.warn('Failed to list workspaces', error);
      }
      try { const keys = await listApiKeysApi(); setApiKeys(keys); } catch (error: unknown) {
        console.warn('Failed to list API keys', error);
      }
      try { const summary = await getAnalyticsSummaryApi(); setAnalytics(summary); } catch (error: unknown) {
        console.warn('Failed to get analytics summary', error);
      }
      try { const notes = await listNotificationsApi(); setNotifications(notes); } catch (error: unknown) {
        console.warn('Failed to load notifications', error);
      }
    } catch (error: unknown) {
      console.error("Error loading SaaS data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSaaSData();
  }, []);

  const handleSubscribe = async (planId: string) => {
    try {
      const updatedSub = await subscribeToPlanApi(planId);
      setSubscription(updatedSub);
    } catch (error: unknown) {
      alert(getErrorMessage(error) || 'Subscription upgrade failed');
    }
  };

  const handleCreateApiKey = async () => {
    if (!newKeyName) return;
    try {
      await createApiKeyApi(newKeyName);
      setNewKeyName('');
      const keys = await listApiKeysApi();
      setApiKeys(keys);
    } catch (error: unknown) {
      console.warn('Failed to create API key', error);
    }
  };

  const handleRevokeApiKey = async (keyId: string) => {
    try {
      await revokeApiKeyApi(keyId);
      const keys = await listApiKeysApi();
      setApiKeys(keys);
    } catch (error: unknown) {
      console.warn('Failed to revoke API key', error);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newWsName) return;
    try {
      await createWorkspaceApi(newWsName, 'TEAM');
      setNewWsName('');
      const ws = await listWorkspacesApi();
      setWorkspaces(ws);
    } catch (error: unknown) {
      console.warn('Failed to create workspace', error);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Link href="/dashboard" className="text-xs text-gray-400 hover:text-white flex items-center gap-1">
                <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
              </Link>
            </div>
            <h1 className="text-2xl font-bold text-white">SaaS Platform & Workspace Settings</h1>
            <p className="text-xs text-gray-400">Manage subscriptions, credits, developer API keys, team workspaces, and platform analytics.</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-white/10 pb-3">
          <button onClick={() => setActiveTab('billing')} className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${activeTab === 'billing' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
            <CreditCard className="w-4 h-4" /> Subscription & Credits
          </button>
          <button onClick={() => setActiveTab('workspaces')} className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${activeTab === 'workspaces' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
            <Users className="w-4 h-4" /> Team Workspaces ({workspaces.length})
          </button>
          <button onClick={() => setActiveTab('apikeys')} className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${activeTab === 'apikeys' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
            <Key className="w-4 h-4" /> Developer API Keys ({apiKeys.length})
          </button>
          <button onClick={() => setActiveTab('analytics')} className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${activeTab === 'analytics' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
            <BarChart3 className="w-4 h-4" /> Platform Analytics
          </button>
          <button onClick={() => setActiveTab('notifications')} className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${activeTab === 'notifications' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
            <Bell className="w-4 h-4" /> Notifications ({notifications.length})
          </button>
        </div>

        {/* Billing Tab */}
        {activeTab === 'billing' && (
          <div className="space-y-8">
            <div className="glass-panel p-6 rounded-3xl border border-white/10 flex items-center justify-between">
              <div>
                <div className="text-xs text-purple-400 font-bold uppercase tracking-wider">Active Subscription</div>
                <div className="text-xl font-bold text-white mt-1">Current Plan: {subscription?.plan_id.toUpperCase()}</div>
                <div className="text-xs text-gray-400 mt-1">Credits Remaining: <strong className="text-emerald-400">{subscription?.credits_remaining} / 3,500</strong></div>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold border border-emerald-500/30 flex items-center gap-1">
                <ShieldCheck className="w-4 h-4" /> Subscription Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {plans.map((p) => (
                <div key={p.plan_id} className={`glass-panel p-6 rounded-3xl border flex flex-col justify-between transition-all ${subscription?.plan_id === p.plan_id ? 'border-purple-500 bg-purple-500/10' : 'border-white/10 hover:border-white/20'}`}>
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <h3 className="text-lg font-bold text-white">{p.name} Plan</h3>
                      <div className="text-2xl font-extrabold text-purple-300">${p.monthly_price_usd} <span className="text-xs text-gray-400 font-normal">/ mo</span></div>
                    </div>

                    <div className="space-y-2 text-xs text-gray-300">
                      {p.features.map((feat, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => handleSubscribe(p.plan_id)}
                    disabled={subscription?.plan_id === p.plan_id}
                    className={`w-full mt-6 py-2.5 rounded-xl text-xs font-bold transition-all border ${
                      subscription?.plan_id === p.plan_id ? 'bg-purple-500 text-white border-purple-400' : 'bg-white/10 hover:bg-white/20 text-white border-white/20'
                    }`}
                  >
                    {subscription?.plan_id === p.plan_id ? 'Current Plan' : 'Upgrade Plan'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Workspaces Tab */}
        {activeTab === 'workspaces' && (
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-3xl border border-white/10 flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="text-base font-bold text-white">Create New Team Workspace</h3>
                <p className="text-xs text-gray-400">Invite team members to edit stories, generate assets, and approve video timelines.</p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Workspace Name (e.g., Studio Alpha)"
                  value={newWsName}
                  onChange={(e) => setNewWsName(e.target.value)}
                  className="px-3 py-2 rounded-xl bg-black/60 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                />
                <button onClick={handleCreateWorkspace} className="px-4 py-2 rounded-xl gradient-button text-xs font-bold text-white flex items-center gap-1">
                  <Plus className="w-4 h-4" /> Create Workspace
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workspaces.map((ws) => (
                <div key={ws.workspace_id} className="glass-panel p-4 rounded-2xl border border-white/10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300 font-bold">
                      {ws.name[0]}
                    </div>
                    <div>
                      <div className="text-white text-xs font-bold">{ws.name}</div>
                      <div className="text-gray-400 text-[11px] uppercase">Type: {ws.type}</div>
                    </div>
                  </div>

                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    Owner
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'apikeys' && (
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-3xl border border-white/10 flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="text-base font-bold text-white">Generate Developer API Key</h3>
                <p className="text-xs text-gray-400">Integrate KidsAI Studio APIs directly into external applications.</p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Key Label (e.g., Mobile App)"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="px-3 py-2 rounded-xl bg-black/60 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                />
                <button onClick={handleCreateApiKey} className="px-4 py-2 rounded-xl gradient-button text-xs font-bold text-white flex items-center gap-1">
                  <Plus className="w-4 h-4" /> Create Key
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {apiKeys.map((key) => (
                <div key={key.key_id} className="glass-panel p-4 rounded-2xl border border-white/10 flex items-center justify-between text-xs">
                  <div>
                    <div className="text-white font-bold">{key.name}</div>
                    <div className="text-gray-400 font-mono text-[11px] mt-0.5">{key.secret_key}</div>
                  </div>

                  <button onClick={() => handleRevokeApiKey(key.key_id)} className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2">
              <div className="text-xs text-gray-400 font-bold uppercase">Total Render Minutes</div>
              <div className="text-2xl font-extrabold text-purple-300">{analytics.total_render_minutes} mins</div>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2">
              <div className="text-xs text-gray-400 font-bold uppercase">Render Success Rate</div>
              <div className="text-2xl font-extrabold text-emerald-400">{analytics.render_success_rate}%</div>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2">
              <div className="text-xs text-gray-400 font-bold uppercase">AI Provider Health</div>
              <div className="text-xs font-bold text-emerald-300 truncate">{analytics.ai_provider_health}</div>
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="space-y-3">
            {notifications.map((n) => (
              <div key={n.notification_id} className="glass-panel p-4 rounded-2xl border border-white/10 flex items-center justify-between text-xs">
                <div>
                  <div className="text-white font-bold">{n.title}</div>
                  <div className="text-gray-400 mt-0.5">{n.message}</div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {n.type}
                </span>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
