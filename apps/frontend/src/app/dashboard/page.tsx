"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Navbar } from '@/components/layout/Navbar';
import { ProjectCard } from '@/components/studio/ProjectCard';
import { listProjectsApi, Project, PaginatedProjects } from '@/lib/api';
import {
  Plus,
  Search,
  Grid,
  List,
  Filter,
  Star,
  FolderKanban,
  FileText,
  CheckCircle2,
  Clock,
  Sparkles,
  Archive,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [pagination, setPagination] = useState<PaginatedProjects | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'drafts' | 'favorites' | 'completed'>('all');
  const [sortOption, setSortOption] = useState('newest');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const isFav = activeTab === 'favorites' ? true : undefined;
      const statusFilter = activeTab === 'drafts' ? 'DRAFT' : activeTab === 'completed' ? 'COMPLETED' : undefined;

      const data = await listProjectsApi({
        q: searchQuery,
        status: statusFilter,
        is_favorite: isFav,
        is_archived: false,
        sort: sortOption,
        page: currentPage,
        limit: 6
      });
      setProjects(data.items);
      setPagination(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [searchQuery, activeTab, sortOption, currentPage]);

  const totalCount = pagination?.total || projects.length;
  const completedCount = projects.filter(p => p.status === 'COMPLETED').length;
  const draftCount = projects.filter(p => p.status === 'DRAFT').length;
  const favoriteCount = projects.filter(p => p.favorite).length;

  return (
    <div className="min-h-screen bg-background-primary text-foreground-primary flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 space-y-10">
        {/* Top Hero Banner & Quick Actions */}
        <div className="glass-panel p-8 rounded-3xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="space-y-2 z-10">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 border border-primary/20 text-primary/300 inline-flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-primary/400" /> Creator Dashboard v2.0
            </span>
            <h1 className="text-3xl font-extrabold text-foreground-primary tracking-tight">
              Welcome back, {user?.full_name || 'Creator'} 👋
            </h1>
            <p className="text-sm text-foreground-muted max-w-xl">
              Manage your video project scripts, storyboards, drafts, and rendered assets in one place.
            </p>
          </div>

          <div className="flex items-center gap-3 z-10">
            <Link
              href="/projects/new"
              className="px-6 py-3 rounded-xl gradient-button text-primary-foreground font-semibold text-sm flex items-center gap-2 shadow-lg hover:scale-105 transition-all"
            >
              <Plus className="w-5 h-5" />
              <span>New Video Project</span>
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-panel p-5 rounded-2xl border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-xl bg-primary/10 border border-primary/20 text-primary/400">
              <FolderKanban className="w-6 h-6" />
            </div>
            <div>
              <span className="text-foreground-muted block font-medium">Total Projects</span>
              <span className="text-2xl font-bold text-foreground-primary">{totalCount}</span>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-xl bg-success/10 border border-success/20 text-success/400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <span className="text-foreground-muted block font-medium">Completed</span>
              <span className="text-2xl font-bold text-foreground-primary">{completedCount}</span>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-xl bg-warning/10 border border-warning/20 text-warning/400">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <span className="text-foreground-muted block font-medium">Active Drafts</span>
              <span className="text-2xl font-bold text-foreground-primary">{draftCount}</span>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-xl bg-accent-pink/10 border border-accent-pink/20 text-accent-pink/400">
              <Star className="w-6 h-6" />
            </div>
            <div>
              <span className="text-foreground-muted block font-medium">Favorites</span>
              <span className="text-2xl font-bold text-foreground-primary">{favoriteCount}</span>
            </div>
          </div>
        </div>

        {/* Toolbar: Search, Tabs, Sorting, View Toggle */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 pt-4 border-t border-white/10">
          {/* Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0">
            <button
              onClick={() => { setActiveTab('all'); setCurrentPage(1); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                activeTab === 'all'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'
              }`}
            >
              All Projects ({totalCount})
            </button>
            <button
              onClick={() => { setActiveTab('drafts'); setCurrentPage(1); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                activeTab === 'drafts'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'
              }`}
            >
              Drafts ({draftCount})
            </button>
            <button
              onClick={() => { setActiveTab('favorites'); setCurrentPage(1); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                activeTab === 'favorites'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'
              }`}
            >
              Favorites ({favoriteCount})
            </button>
            <button
              onClick={() => { setActiveTab('completed'); setCurrentPage(1); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                activeTab === 'completed'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'
              }`}
            >
              Completed ({completedCount})
            </button>
          </div>

          {/* Search, Sort & View Toggle */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[220px]">
              <Search className="w-4 h-4 text-foreground-muted/50 absolute left-3 top-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                placeholder="Search projects..."
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-surface-secondary/40 border border-white/15 text-xs text-foreground-primary placeholder-foreground-muted focus:outline-none focus:border-primary"
              />
            </div>

            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              className="bg-surface-secondary/40 border border-white/15 rounded-xl px-3 py-2 text-xs text-foreground-muted focus:outline-none focus:border-primary"
            >
              <option value="newest">Sort: Newest First</option>
              <option value="oldest">Sort: Oldest First</option>
              <option value="title">Sort: Alphabetical</option>
              <option value="recently_opened">Sort: Recently Opened</option>
            </select>

            <div className="flex items-center p-1 rounded-xl bg-surface-secondary/5 border border-white/10">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-primary/20 text-primary/300' : 'text-foreground-muted'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-primary/20 text-primary/300' : 'text-foreground-muted'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Project Grid / List Display */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="glass-panel h-64 rounded-2xl border border-white/10 animate-pulse bg-surface-secondary/5" />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="glass-panel p-12 rounded-3xl border border-white/10 text-center space-y-4 max-w-md mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 text-primary/400 flex items-center justify-center mx-auto">
              <FolderKanban className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-foreground-primary">No Projects Found</h3>
            <p className="text-xs text-foreground-muted">
              {searchQuery ? `No results matching "${searchQuery}"` : "Create your first video project to get started."}
            </p>
            <Link
              href="/projects/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-button text-xs font-semibold text-primary-foreground"
            >
              <Plus className="w-4 h-4" /> Create Video Project
            </Link>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-3 gap-6" : "space-y-3"}>
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} onRefresh={fetchProjects} viewMode={viewMode} />
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {pagination && pagination.pages > 1 && (
          <div className="pt-6 border-t border-white/10 flex items-center justify-between text-xs text-foreground-muted">
            <span>Showing page {pagination.page} of {pagination.pages} ({pagination.total} total items)</span>

            <div className="flex items-center gap-2">
              <button
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                className="p-2 rounded-xl bg-surface-secondary/5 border border-white/10 disabled:opacity-30 hover:bg-surface-secondary/10 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-3 py-1 font-semibold text-foreground-primary">{currentPage}</span>
              <button
                disabled={currentPage >= pagination.pages}
                onClick={() => setCurrentPage(prev => Math.min(pagination.pages, prev + 1))}
                className="p-2 rounded-xl bg-surface-secondary/5 border border-white/10 disabled:opacity-30 hover:bg-surface-secondary/10 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
