"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Project, toggleFavoriteApi, archiveProjectApi, restoreProjectApi, duplicateProjectApi, deleteProjectApi } from '@/lib/api';
import { Star, MoreVertical, Copy, Archive, RotateCcw, Trash2, ExternalLink, Film, Clock } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
  onRefresh?: () => void;
  viewMode?: 'grid' | 'list';
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, onRefresh, viewMode = 'grid' }) => {
  const [isFavorite, setIsFavorite] = useState(project.favorite);
  const [showMenu, setShowMenu] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleToggleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      setIsFavorite(!isFavorite);
      await toggleFavoriteApi(project.id);
      if (onRefresh) onRefresh();
    } catch (err) {
      setIsFavorite(isFavorite);
    }
  };

  const handleDuplicate = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowMenu(false);
    setIsProcessing(true);
    try {
      await duplicateProjectApi(project.id);
      if (onRefresh) onRefresh();
    } finally {
      setIsProcessing(false);
    }
  };

  const handleArchive = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowMenu(false);
    setIsProcessing(true);
    try {
      if (project.archived) {
        await restoreProjectApi(project.id);
      } else {
        await archiveProjectApi(project.id);
      }
      if (onRefresh) onRefresh();
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowMenu(false);
    if (!confirm(`Are you sure you want to delete "${project.title}"?`)) return;
    setIsProcessing(true);
    try {
      await deleteProjectApi(project.id);
      if (onRefresh) onRefresh();
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'DRAFT':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      case 'ARCHIVED':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'FAILED':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      default:
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
    }
  };

  if (viewMode === 'list') {
    return (
      <div className="glass-panel p-4 rounded-xl border border-white/10 hover:border-purple-500/40 transition-all flex items-center justify-between gap-4 group relative">
        <div className="flex items-center gap-4 min-w-0">
          <button onClick={handleToggleFavorite} className="text-gray-500 hover:text-amber-400 transition-colors">
            <Star className={`w-4 h-4 ${isFavorite ? 'fill-amber-400 text-amber-400' : ''}`} />
          </button>
          
          <div className="w-12 h-12 rounded-lg bg-black/60 overflow-hidden border border-white/10 shrink-0 flex items-center justify-center">
            {project.thumbnail_url ? (
              <img src={project.thumbnail_url} alt={project.title} className="w-full h-full object-cover" />
            ) : (
              <Film className="w-5 h-5 text-gray-500" />
            )}
          </div>

          <div className="min-w-0">
            <Link href={`/projects/${project.id}`} className="font-semibold text-white hover:text-purple-300 transition-colors truncate block">
              {project.title}
            </Link>
            <p className="text-xs text-gray-400 truncate">{project.prompt}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 shrink-0">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(project.status)}`}>
            {project.status}
          </span>

          <span className="text-xs text-gray-500 hidden md:inline">
            {project.aspect_ratio} • Age {project.target_age_group}
          </span>

          <span className="text-xs text-gray-500 hidden sm:inline flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(project.created_at).toLocaleDateString()}
          </span>

          <div className="relative">
            <button onClick={() => setShowMenu(!showMenu)} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400">
              <MoreVertical className="w-4 h-4" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-8 w-44 glass-panel rounded-xl border border-white/15 shadow-2xl py-1 z-50 text-xs text-gray-300">
                <Link href={`/projects/${project.id}`} className="px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                  <ExternalLink className="w-3.5 h-3.5" /> Open Details
                </Link>
                <button onClick={handleDuplicate} className="w-full text-left px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                  <Copy className="w-3.5 h-3.5" /> Duplicate
                </button>
                <button onClick={handleArchive} className="w-full text-left px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                  {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
                </button>
                <div className="border-t border-white/10 my-1" />
                <button onClick={handleDelete} className="w-full text-left px-3 py-2 hover:bg-rose-500/20 text-rose-400 flex items-center gap-2">
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl border border-white/10 hover:border-purple-500/40 transition-all flex flex-col overflow-hidden group relative">
      {/* Thumbnail Bar */}
      <div className="relative aspect-video bg-black/60 flex items-center justify-center border-b border-white/10 overflow-hidden">
        {project.thumbnail_url ? (
          <img src={project.thumbnail_url} alt={project.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <Film className="w-8 h-8 text-gray-600" />
        )}
        
        <button
          onClick={handleToggleFavorite}
          className="absolute top-3 left-3 p-1.5 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 text-gray-400 hover:text-amber-400 transition-colors"
        >
          <Star className={`w-4 h-4 ${isFavorite ? 'fill-amber-400 text-amber-400' : ''}`} />
        </button>

        <span className={`absolute top-3 right-3 px-2.5 py-0.5 rounded-full text-[10px] font-bold border backdrop-blur-md ${getStatusBadgeClass(project.status)}`}>
          {project.status}
        </span>
      </div>

      {/* Content Body */}
      <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
        <div>
          <Link href={`/projects/${project.id}`} className="font-bold text-white hover:text-purple-300 transition-colors text-base line-clamp-1">
            {project.title}
          </Link>
          <p className="text-xs text-gray-400 line-clamp-2 mt-1">{project.prompt}</p>
        </div>

        <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs text-gray-400">
          <span>{project.aspect_ratio} • Age {project.target_age_group}</span>
          <span>{new Date(project.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="px-5 py-3 bg-white/5 border-t border-white/10 flex items-center justify-between">
        <Link href={`/projects/${project.id}`} className="text-xs font-semibold text-purple-400 hover:underline flex items-center gap-1">
          Open Project <ExternalLink className="w-3 h-3" />
        </Link>

        <div className="relative">
          <button onClick={() => setShowMenu(!showMenu)} className="p-1 rounded-lg hover:bg-white/10 text-gray-400">
            <MoreVertical className="w-4 h-4" />
          </button>

          {showMenu && (
            <div className="absolute right-0 bottom-8 w-44 glass-panel rounded-xl border border-white/15 shadow-2xl py-1 z-50 text-xs text-gray-300">
              <Link href={`/projects/${project.id}`} className="px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                <ExternalLink className="w-3.5 h-3.5" /> View Details
              </Link>
              <button onClick={handleDuplicate} className="w-full text-left px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                <Copy className="w-3.5 h-3.5" /> Duplicate
              </button>
              <button onClick={handleArchive} className="w-full text-left px-3 py-2 hover:bg-white/10 flex items-center gap-2">
                {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
              </button>
              <div className="border-t border-white/10 my-1" />
              <button onClick={handleDelete} className="w-full text-left px-3 py-2 hover:bg-rose-500/20 text-rose-400 flex items-center gap-2">
                <Trash2 className="w-3.5 h-3.5" /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
