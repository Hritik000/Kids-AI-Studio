"use client";

import React, { useState } from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { PromptGenerator } from '@/components/studio/PromptGenerator';
import { SceneTimeline } from '@/components/studio/SceneTimeline';
import { createProject, getProject, Project } from '@/lib/api';
import { Sparkles, Video, Play, CheckCircle2, Zap, AlertCircle } from 'lucide-react';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = async (prompt: string, ageGroup: string, aspectRatio: string) => {
    setIsGenerating(true);
    setErrorMsg(null);
    try {
      // Step 1: Create project in FastAPI backend
      const newProject = await createProject(prompt, ageGroup, aspectRatio);
      setActiveProject(newProject);

      // Step 2: Poll status until generation completes or fails
      const pollInterval = setInterval(async () => {
        try {
          const updated = await getProject(newProject.id);
          setActiveProject(updated);
          if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            if (updated.status === 'FAILED') {
              setErrorMsg('Project pipeline generation failed. Please check backend logs.');
            }
          }
        } catch (error: unknown) {
          console.error("Polling error:", error);
          clearInterval(pollInterval);
          setIsGenerating(false);
          setErrorMsg(getErrorMessage(error));
        }
      }, 1000);

    } catch (error: unknown) {
      console.error("Project creation failed:", error);
      setIsGenerating(false);
      setErrorMsg(getErrorMessage(error));
    }
  };

  return (
    <div className="min-h-screen bg-background-primary text-foreground-primary flex flex-col font-sans selection:bg-primary/20 selection:text-primary-foreground">
      {/* Top Glass Navbar */}
      <Navbar />

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 space-y-16">
        {/* Intro Title */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary/300 text-xs font-semibold">
            <Zap className="w-4 h-4 text-primary-400" />
            <span>Autonomous YouTube Kids Video Creation SaaS v2.0</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-foreground-primary leading-tight">
            Turn Any Prompt into a <br />
            <span className="gradient-text-hero">Complete YouTube Kids Video</span>
          </h1>

          <p className="text-foreground-secondary text-lg">
            Director Agent, Script, Storyboard, Visuals, Narration, and FFmpeg Render — fully automated.
          </p>
        </div>

        {/* Error Notification */}
        {errorMsg && (
          <div className="max-w-xl mx-auto p-4 rounded-xl bg-error/10 border border-error/30 text-error-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Input Prompt Generator Wizard */}
        <PromptGenerator onGenerate={handleGenerate} isGenerating={isGenerating} />

        {/* Active Generated Project Timeline */}
        {activeProject && (
          <div className="pt-8 border-t border-white/10">
            <SceneTimeline project={activeProject} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-6 text-center text-xs text-foreground-muted">
        <p>KidsAI Studio © 2026 — Built with Next.js 15, FastAPI, Supabase, Cloudflare R2 & AI Adapters</p>
      </footer>
    </div>
  );
}
