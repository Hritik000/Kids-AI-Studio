"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Navbar } from '@/components/layout/Navbar';
import { ProjectCard } from '@/components/studio/ProjectCard';
import { listProjectsApi, Project } from '@/lib/api';
import { Archive, ArrowLeft } from 'lucide-react';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

export default function ArchivedProjectsPage() {
  const [archivedProjects, setArchivedProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchArchived = async () => {
    setIsLoading(true);
    try {
      const data = await listProjectsApi({ is_archived: true, limit: 50 });
      setArchivedProjects(data.items);
    } catch (error: unknown) {
      console.error("Error fetching archived projects:", getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const id = setTimeout(fetchArchived, 0);
    return () => clearTimeout(id);
     
  }, []);

  return (
    <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 space-y-8">
        <div className="flex items-center justify-between border-b border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="p-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <Archive className="w-6 h-6 text-amber-400" />
                Archived Projects Vault
              </h1>
              <p className="text-xs text-gray-400 mt-0.5">Projects stored in archive can be restored anytime or permanently removed.</p>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2].map(i => (
              <div key={i} className="glass-panel h-64 rounded-2xl border border-white/10 animate-pulse bg-white/5" />
            ))}
          </div>
        ) : archivedProjects.length === 0 ? (
          <div className="glass-panel p-12 rounded-3xl border border-white/10 text-center space-y-4 max-w-md mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
              <Archive className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-white">No Archived Projects</h3>
            <p className="text-xs text-gray-400">Your archive vault is currently empty.</p>
            <Link href="/dashboard" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-button text-xs font-semibold text-white">
              Return to Dashboard
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {archivedProjects.map((project) => (
              <ProjectCard key={project.id} project={project} onRefresh={fetchArchived} viewMode="grid" />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
