"use client";

import React from 'react';
import { Project, Scene, ProjectStatus } from '@/lib/api';
import { Sparkles, Film, Image as ImageIcon, Volume2, CheckCircle2, Clock, PlayCircle, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SceneTimelineProps {
  project: Project;
}

export const SceneTimeline: React.FC<SceneTimelineProps> = ({ project }) => {
  const getStatusBadge = (status: ProjectStatus) => {
    switch (status) {
      case 'DRAFT':
        return { label: '📝 Project Created', color: 'bg-dim/20 text-dim border-dim/30' };
      case 'PLANNING':
        return { label: '🎬 Director Agent Analyzing Prompt...', color: 'bg-primary/20 text-primary border-primary/30' };
      case 'STORY_READY':
        return { label: '🧠 Story Agent Script Writing...', color: 'bg-primary/20 text-primary border-primary/30' };
      case 'STORYBOARD_READY':
        return { label: '🎨 Storyboard Agent Breaking Scenes...', color: 'bg-secondary/20 text-secondary border-secondary/30' };
      case 'IMAGES_READY':
        return { label: '🖼️ Visual Artist Generating Assets...', color: 'bg-success/20 text-success border-success/30' };
      case 'ANIMATION_READY':
        return { label: '✨ Motion Agent Applying Camera Pans...', color: 'bg-success/20 text-success border-success/30' };
      case 'VOICE_READY':
        return { label: '🗣️ Voice Agent Synthesizing Speech...', color: 'bg-accent-pink/20 text-accent-pink border-accent-pink/30' };
      case 'MUSIC_READY':
        return { label: '🎵 Music Agent Adding Soundtrack...', color: 'bg-warning/20 text-warning border-warning/30' };
      case 'RENDERING':
        return { label: '🎞️ FFmpeg Engine Compositing MP4...', color: 'bg-warning/20 text-warning border-warning/30' };
      case 'QUALITY_CHECK':
        return { label: '🔍 Quality Checker Validating Assets...', color: 'bg-primary/20 text-primary border-primary/30' };
      case 'COMPLETED':
        return { label: '✅ Video Ready for Download', color: 'bg-success/20 text-success border-success/30' };
      case 'FAILED':
        return { label: '❌ Generation Error', color: 'bg-error/20 text-error border-error/30' };
      default:
        return { label: 'Processing...', color: 'bg-dim/20 text-dim border-dim/30' };
    }
  };

  const currentStatus = getStatusBadge(project.status);

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8">
      {/* Project Status Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${currentStatus.color}`}>
              {currentStatus.label}
            </span>
            <span className="text-xs text-foreground-muted flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              Target: Age {project.target_age_group}
            </span>
            <span className="text-xs text-foreground-muted flex items-center gap-1">
              Aspect Ratio: {project.aspect_ratio}
            </span>
          </div>
          <h2 className="text-xl font-bold text-foreground-primary mt-2">{project.title || project.prompt}</h2>
          {project.description && <p className="text-sm text-foreground-muted mt-1 max-w-2xl">{project.description}</p>}
        </div>

        {/* Video Download / Player Action */}
        {project.final_video_url && project.status === 'COMPLETED' && (
          <a
            href={project.final_video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-2.5 rounded-xl gradient-button text-primary-foreground font-semibold flex items-center gap-2 shadow-lg hover:scale-105 transition-transform"
          >
            <PlayCircle className="w-5 h-5" />
            <span>Download MP4 Video</span>
          </a>
        )}
      </div>

      {/* Metrics Bar */}
      {project.metrics && project.status === 'COMPLETED' && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-surface-secondary/5 border border-white/10 text-xs">
          <div>
            <span className="text-foreground-muted block">Total Pipeline Time</span>
            <span className="text-foreground-primary font-bold text-sm">{project.metrics.generation_time_seconds}s</span>
          </div>
          <div>
            <span className="text-foreground-muted block">Video Duration</span>
            <span className="text-foreground-primary font-bold text-sm">{project.metrics.video_duration_seconds}s</span>
          </div>
          <div>
            <span className="text-foreground-muted block">Scenes Generated</span>
            <span className="text-foreground-primary font-bold text-sm">{project.metrics.image_count} scenes</span>
          </div>
          <div>
            <span className="text-foreground-muted block">Estimated Cost</span>
            <span className="text-success font-bold text-sm">$${project.metrics.estimated_cost_usd}</span>
          </div>
        </div>
      )}

      {/* SEO Tags */}
      {project.tags && project.tags.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-foreground-muted mr-2">YouTube SEO Tags:</span>
          {project.tags.map((tag, i) => (
            <span key={i} className="px-2.5 py-1 rounded-lg bg-surface-secondary/5 border border-white/10 text-xs text-primary/300">
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Scenes Timeline Grid */}
      {project.scenes && project.scenes.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-lg font-bold text-foreground-primary flex items-center gap-2">
            <Film className="w-5 h-5 text-primary/400" />
            <span>Generated Scene Breakdown ({project.scenes.length} Scenes)</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {project.scenes.map((scene) => (
              <div key={scene.scene_number} className="glass-panel rounded-2xl border border-white/10 overflow-hidden flex flex-col">
                {/* Scene Preview Image */}
                <div className="relative aspect-video bg-surface-secondary/60 flex items-center justify-center border-b border-white/10">
                  {scene.image_url ? (
                    <img
                      src={scene.image_url}
                      alt={`Scene ${scene.scene_number}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex flex-col items-center gap-2 text-foreground-muted">
                      <ImageIcon className="w-8 h-8 animate-pulse text-primary/50" />
                      <span className="text-xs">Visual Artist Generating...</span>
                    </div>
                  )}
                  <span className="absolute top-3 left-3 px-2 py-1 rounded-md bg-background-secondary/70 backdrop-blur-md text-xs font-bold text-foreground-primary border border-white/10">
                    Scene #{scene.scene_number}
                  </span>
                </div>

                {/* Scene Content */}
                <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-primary/400 mb-1 flex items-center gap-1.5">
                      <Volume2 className="w-3.5 h-3.5" />
                      Narration Script
                    </h4>
                    <p className="text-sm font-medium text-foreground-secondary bg-surface-secondary/5 p-3 rounded-xl border border-white/5 italic">
                      "{scene.narration_text}"
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-secondary/400 mb-1 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Visual Prompt
                    </h4>
                    <p className="text-xs text-foreground-muted line-clamp-3">
                      {scene.visual_prompt}
                    </p>
                  </div>

                  {/* Audio Track Indicator */}
                  {scene.audio_url && (
                    <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs text-success/400">
                      <span className="flex items-center gap-1 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Voice Narration Ready
                      </span>
                      <span className="text-foreground-muted">{scene.duration_seconds}s</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};