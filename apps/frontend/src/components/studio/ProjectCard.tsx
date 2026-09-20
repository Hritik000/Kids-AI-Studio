"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Project, toggleFavoriteApi, archiveProjectApi, restoreProjectApi, duplicateProjectApi, deleteProjectApi } from '@/lib/api';
import { Star, MoreVertical, Copy, Archive, RotateCcw, Trash2, ExternalLink, Film, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

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
        return 'bg-success/20 text-success border-success/30';
      case 'DRAFT':
        return 'bg-dim/20 text-dim border-dim/30';
      case 'ARCHIVED':
        return 'bg-warning/20 text-warning border-warning/30';
      case 'FAILED':
        return 'bg-error/20 text-error border-error/30';
      default:
        return 'bg-primary/20 text-primary border-primary/30';
    }
  };

  if (viewMode === 'list') {
    return (
      <div className="glass-panel p-4 rounded-xl border border-white/10 hover:border-primary/40 transition-all flex items-center justify-between gap-4 group relative">
        <div className="flex items-center gap-4 min-w-0">
          <Button variant="ghost" size="sm" onClick={handleToggleFavorite} className="p-1">
            <Star className={`w-4 h-4 ${isFavorite ? 'text-primary' : ''}`} />
          </Button>

          <div className="w-12 h-12 rounded-lg bg-surface-secondary/60 overflow-hidden border border-white/10 shrink-0 flex items-center justify-center">
            {project.thumbnail_url ? (
              <img src={project.thumbnail_url} alt={project.title} className="w-full h-full object-cover" />
            ) : (
              <Film className="w-5 h-5 text-foreground-muted/50" />
            )}
          </div>

          <div className="min-w-0">
            <Link href={`/projects/${project.id}`} className="font-semibold text-foreground-primary hover:text-primary/80 transition-colors truncate block">
              {project.title}
            </Link>
            <p className="text-xs text-foreground-muted truncate">{project.prompt}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 shrink-0">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(project.status)}`}>
            {project.status}
          </span>

          <span className="text-xs text-foreground-hidden md:inline-flex items-center gap-1">
            {project.aspect_ratio} • Age {project.target_age_group}
          </span>

          <span className="text-xs text-foreground-muted hidden sm:inline-flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(project.created_at).toLocaleDateString()}
          </span>

          <div className="relative">
            <Button variant="outline" size="sm" onClick={() => setShowMenu(!showMenu)} className="p-1 text-foreground-muted hover:text-foreground-primary">
              <MoreVertical className="w-4 h-4" />
            </Button>

            {showMenu && (
              <div className="absolute right-0 top-8 w-48 glass-panel rounded-xl border border-white/15 shadow-lg py-2 z-50 text-xs text-foreground-muted">
                <Link href={`/projects/${project.id}`} className="block px-4 py-2 hover:bg-surface-secondary/10 flex items-center gap-2">
                  <ExternalLink className="w-3.5 h-3.5" /> Open Details
                </Link>
                <Button variant="outline" size="sm" onClick={handleDuplicate} className="w-full text-left px-4 py-2 hover:bg-surface-secondary/10">
                  <Copy className="w-3.5 h-3.5" /> Duplicate
                </Button>
                <Button variant="outline" size="sm" onClick={handleArchive} className="w-full text-left px-4 py-2 hover:bg-surface-secondary/10">
                  {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
                </Button>
                <div className="border-t border-white/10 my-1" />
                <Button variant="outline" size="sm" onClick={handleDelete} className="w-full text-left px-4 py-2 hover:bg-error/20 text-error">
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl border border-white/10 hover:border-primary/40 transition-all flex flex-col overflow-hidden group relative">
      {/* Thumbnail Bar */}
      <div className="relative aspect-video bg-surface-secondary/60 flex items-center justify-center border-b border-white/10 overflow-hidden">
        {project.thumbnail_url ? (
          <img src={project.thumbnail_url} alt={project.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <Film className="w-8 h-8 text-foreground-muted/50" />
        )}

        <Button variant="ghost" size="sm" onClick={handleToggleFavorite} className="absolute top-3 left-3 p-1">
          <Star className={`w-4 h-4 ${isFavorite ? 'text-primary' : ''}`} />
        </Button>

        <span className={`absolute top-3 right-3 px-2.5 py-0.5 rounded-full text-[10px] font-bold border backdrop-blur-md ${getStatusBadgeClass(project.status)}`}>
          {project.status}
        </span>
      </div>

      {/* Content Body */}
      <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
        <div>
          <Link href={`/projects/${project.id}`} className="font-bold text-foreground-primary hover:text-primary/80 transition-colors text-base line-clamp-1">
            {project.title}
          </Link>
          <p className="text-xs text-foreground-muted line-clamp-2 mt-1">{project.prompt}</p>
        </div>

        <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs text-foreground-muted">
          <span>{project.aspect_ratio} • Age {project.target_age_group}</span>
          <span>{new Date(project.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="px-5 py-3 bg-surface-secondary/5 border-t border-white/10 flex items-center justify-between">
        <Link href={`/projects/${project.id}`} className="text-xs font-semibold text-primary/400 hover:underline flex items-center gap-1">
          Open Project <ExternalLink className="w-3 h-3" />
        </Link>

        <div className="relative">
          <Button variant="outline" size="sm" onClick={() => setShowMenu(!showMenu)} className="p-1 text-foreground-muted hover:text-foreground-primary">
            <MoreVertical className="w-4 h-4" />
          </Button>

          {showMenu && (
            <div className="absolute right-0 bottom-8 w-48 glass-panel rounded-xl border border-white/15 shadow-lg py-2 z-50 text-xs text-foreground-muted">
              <Link href={`/projects/${project.id}`} className="block px-4 py-2 hover:bg-surface-secondary/10 flex items-center gap-2">
                <ExternalLink className="w-3.5 h-3.5" /> View Details
              </Link>
              <Button variant="outline" size="sm" onClick={handleDuplicate} className="w-full text-left px-4 py-2 hover:bg-surface-secondary/10">
                <Copy className="w-3.5 h-3.5" /> Duplicate
              </Button>
              <Button variant="outline" size="sm" onClick={handleArchive} className="w-full text-left px-4 py-2 hover:bg-surface-secondary/10">
                {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
              </Button>
              <div className="border-t border-white/10 my-1" />
              <Button variant="outline" size="sm" onClick={handleDelete} className="w-full text-left px-4 py-2 hover:bg-error/20 text-error">
                <Trash2 className="w-3.5 h-3.5" /> Delete
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};