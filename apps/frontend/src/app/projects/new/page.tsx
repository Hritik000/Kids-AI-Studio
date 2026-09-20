"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createProjectApi } from '@/lib/api';
import {
  Wand2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Palette,
  Volume2,
  Globe,
  Clock,
  Film,
  CheckCircle2,
  Save,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';

export default function CreateProjectWizardPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);

  // Form State
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [targetAgeGroup, setTargetAgeGroup] = useState('3-5');
  const [language, setLanguage] = useState('English (US)');
  const [videoLength, setVideoLength] = useState('Standard (2-3 min)');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [voice, setVoice] = useState('Storyteller Emma');
  const [videoStyle, setVideoStyle] = useState('3D Pixar Render');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleNext = () => {
    if (currentStep === 1 && !title.trim()) {
      setErrorMsg('Please enter a project name.');
      return;
    }
    if (currentStep === 2 && !prompt.trim()) {
      setErrorMsg('Please enter a video topic prompt.');
      return;
    }
    setErrorMsg(null);
    setCurrentStep(prev => Math.min(10, prev + 1));
  };

  const handleBack = () => {
    setErrorMsg(null);
    setCurrentStep(prev => Math.max(1, prev - 1));
  };

  const handleCreate = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const project = await createProjectApi({
        title,
        prompt,
        target_age_group: targetAgeGroup,
        language,
        video_length: videoLength,
        aspect_ratio: aspectRatio,
        video_style: videoStyle,
        voice,
        save_as_draft: true
      });
      router.push(`/projects/${project.id}`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save project draft.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-primary flex flex-col font-sans">
      {/* Top Wizard Header */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between glass-panel">
        <Link href="/dashboard" className="flex items-center gap-2 text-xs text-foreground-muted hover:text-primary/600 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Cancel & Exit
        </Link>

        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary/400" />
          <span className="text-xs font-bold text-foreground-primary uppercase tracking-wider">Project Creation Wizard</span>
        </div>

        <span className="text-xs text-primary/400 font-semibold px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
          Step {currentStep} of 10
        </span>
      </header>

      {/* Progress Dots Bar */}
      <div className="w-full bg-surface-secondary/5 border-b border-white/10 px-6 py-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between relative">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(step => (
            <div
              key={step}
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                step === currentStep
                  ? 'bg-primary/20 text-primary/300 ring-4 ring-primary/500/20 scale-110'
                  : step < currentStep
                  ? 'bg-success/20 text-success/300'
                  : 'bg-surface-secondary/10 text-foreground-muted'
              }`}
            >
              {step < currentStep ? '✓' : step}
            </div>
          ))}
        </div>
      </div>

      {/* Main Wizard Form Body */}
      <main className="flex-1 max-w-2xl w-full mx-auto px-6 py-12 flex flex-col justify-between">
        <div className="space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-error/10 border border-error/20 text-error/300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* STEP 1: Project Name */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 1 — Identity</span>
              <h2 className="text-2xl font-bold text-foreground-primary">What is your project name?</h2>
              <p className="text-sm text-foreground-muted">Give your video project a recognizable title.</p>
              <Input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Dinosaurs Learn Colors #1"
                required
                autoFocus
                className="w-full"
              />
            </div>
          )}

          {/* STEP 2: Video Topic */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 2 — Prompt</span>
              <h2 className="text-2xl font-bold text-foreground-primary">What is the video story topic?</h2>
              <p className="text-sm text-foreground-muted">Describe the characters, plot, or educational lesson.</p>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder="e.g., Red dinosaur Sammy meets a friendly blue bird and explores a yellow sunflower garden..."
                required
                autoFocus
                className="w-full min-h-[100px] resize-none border border-white/15 bg-surface-secondary/5 rounded-xl px-4 py-3 text-sm placeholder-foreground-muted focus:outline-none focus:border-primary"
              />
            </div>
          )}

          {/* STEP 3: Age Group */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 3 — Audience</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Select Target Age Group</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {['2-4', '3-5', '6-8'].map(age => (
                  <Button
                    key={age}
                    variant="outline"
                    size="md"
                    onClick={() => setTargetAgeGroup(age)}
                    className={`
                      ${targetAgeGroup === age
                        ? 'bg-primary/20 text-primary/300 border-primary/40'
                        : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:bg-surface-secondary/10'}
                    `}
                  >
                    <span className="text-xs font-semibold text-primary/400">Ages {age}</span>
                    <span className="text-lg font-bold mt-2 block">
                      {age === '2-4' ? 'Toddlers' : age === '3-5' ? 'Preschool' : 'Early Elementary'}
                    </span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 4: Language */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 4 — Localization</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Select Narration Language</h2>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full"
              >
                <option value="English (US)">English (US)</option>
                <option value="English (UK)">English (UK)</option>
                <option value="Spanish">Spanish (Español)</option>
                <option value="French">French (Français)</option>
                <option value="German">German (Deutsch)</option>
                <option value="Hindi">Hindi (हिंदी)</option>
              </Select>
            </div>
          )}

          {/* STEP 5: Video Length */}
          {currentStep === 5 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 5 — Duration</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Target Video Length</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {['Short (30-60s)', 'Standard (2-3 min)', 'Extended (5 min)'].map(len => (
                  <Button
                    key={len}
                    variant="outline"
                    size="md"
                    onClick={() => setVideoLength(len)}
                    className={`
                      ${videoLength === len
                        ? 'bg-primary/20 text-primary/300 border-primary/40'
                        : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:bg-surface-secondary/10'}
                    `}
                  >
                    {len}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 6: Aspect Ratio */}
          {currentStep === 6 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 6 — Format</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Select Video Aspect Ratio</h2>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { ratio: '16:9', label: 'YouTube Standard (16:9 Landscape)' },
                  { ratio: '9:16', label: 'YouTube Shorts (9:16 Portrait)' },
                  { ratio: '1:1', label: 'Square Post (1:1)' }
                ].map(item => (
                  <Button
                    key={item.ratio}
                    variant="outline"
                    size="md"
                    onClick={() => setAspectRatio(item.ratio)}
                    className={`
                      ${aspectRatio === item.ratio
                        ? 'bg-primary/20 text-primary/300 border-primary/40'
                        : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:bg-surface-secondary/10'}
                    `}
                  >
                    <span className="text-xl font-bold">{item.ratio}</span>
                    <span className="text-[11px] text-foreground-muted mt-1 block">{item.label}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 7: Voice Style */}
          {currentStep === 7 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 7 — Narration Voice</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Choose Narrator Voice</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {['Storyteller Emma', 'Uncle Bob', 'Little Timmy'].map(v => (
                  <Button
                    key={v}
                    variant="outline"
                    size="md"
                    onClick={() => setVoice(v)}
                    className={`
                      ${voice === v
                        ? 'bg-primary/20 text-primary/300 border-primary/40'
                        : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:bg-surface-secondary/10'}
                    `}
                  >
                    <span className="text-xs text-primary/400 font-semibold flex items-center gap-1">
                      <Volume2 className="w-3.5 h-3.5" /> Narrator
                    </span>
                    <span className="text-sm font-bold mt-2">{v}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 8: Video Style */}
          {currentStep === 8 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 8 — Visual Style</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Choose Art & Render Style</h2>
              <div className="grid grid-cols-2 gap-4">
                {['3D Pixar Render', '2D Storybook', 'Claymation', 'Anime Cartoon'].map(style => (
                  <Button
                    key={style}
                    variant="outline"
                    size="md"
                    onClick={() => setVideoStyle(style)}
                    className={`
                      ${videoStyle === style
                        ? 'bg-primary/20 text-primary/300 border-primary/40'
                        : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:bg-surface-secondary/10'}
                    `}
                  >
                    <span className="text-sm font-bold block">{style}</span>
                    <span className="text-xs text-foreground-muted mt-1 block">High quality child-safe AI visual style</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 9: Review Summary */}
          {currentStep === 9 && (
            <div className="space-y-4">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider">Step 9 — Review</span>
              <h2 className="text-2xl font-bold text-foreground-primary">Review Project Settings</h2>

              <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3 text-xs">
                <div className="flex justify-between py-1 border-b border-white/10">
                  <span className="text-foreground-muted">Project Name:</span>
                  <span className="font-bold text-foreground-primary">{title}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/10">
                  <span className="text-foreground-muted">Topic Prompt:</span>
                  <span className="font-bold text-foreground-primary line-clamp-1 max-w-xs">{prompt}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/10">
                  <span className="text-foreground-muted">Target Age Group:</span>
                  <span className="font-bold text-foreground-primary">Ages {targetAgeGroup}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/10">
                  <span className="text-foreground-muted">Language:</span>
                  <span className="font-bold text-foreground-primary">{language}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/10">
                  <span className="text-foreground-muted">Format & Style:</span>
                  <span className="font-bold text-foreground-primary">{aspectRatio} • {videoStyle}</span>
                </div>
              </div>
            </div>
          )}

          {/* STEP 10: Create Project */}
          {currentStep === 10 && (
            <div className="space-y-6 text-center">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 text-primary/400 flex items-center justify-center mx-auto">
                <Save className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground-primary">Ready to Save Project Draft</h2>
                <p className="text-sm text-foreground-muted max-w-md mx-auto mt-2">
                  Your project configuration is ready. Save it to your workspace dashboard to continue customizing script and scenes.
                </p>
              </div>

              <Button
                type="button"
                variant="primary"
                size="md"
                onClick={handleCreate}
                className="w-full max-w-md mx-auto"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Saving Project Draft...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save Project Draft</span>
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Bottom Nav Actions */}
        {currentStep < 10 && (
          <div className="pt-8 border-t border-white/10 flex items-center justify-between">
            <Button
              variant="outline"
              size="md"
              onClick={handleBack}
              disabled={currentStep === 1}
              className="text-foreground-muted hover:text-foreground-primary"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>

            <Button
              variant="primary"
              size="md"
              onClick={handleNext}
              className="ml-4"
            >
              <span>Next Step</span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}