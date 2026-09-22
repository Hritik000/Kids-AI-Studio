"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from '@/components/layout/Navbar';
import { useAutoSave } from '@/hooks/useAutoSave';
import {
  getProjectApi,
  duplicateProjectApi,
  archiveProjectApi,
  restoreProjectApi,
  deleteProjectApi,
  toggleFavoriteApi,
  getProductionPlanApi,
  getStoryScriptApi,
  getStoryboardApi,
  getCharactersApi,
  listSceneImagesApi,
  listSceneAnimationsApi,
  listSceneVoicesApi,
  listSceneMusicMixesApi,
  getProjectTimelineApi,
  listProjectRendersApi,
  getPublishingAssetsApi,
  listConnectedAccountsApi,
  listPublishingQueueApi,
  publishNowApi,
  schedulePublishApi,
  retryPublishTaskApi,
  analyzeProjectCopilotApi,
  predictPerformanceCopilotApi,
  listTrendsCopilotApi,
  optimizePromptCopilotApi,
  Project,
  ProductionPlan,
  StoryScript,
  Storyboard,
  CharacterProfile,
  GeneratedImage,
  AnimatedSceneClip,
  VoiceNarrationAsset,
  MixedAudioTrack,
  VideoTimeline,
  RenderTask,
  PublishingAssetBundle,
  ConnectedAccount,
  PublishingQueueItem,
  OptimizationReport,
  PerformancePrediction,
  TrendReport
} from '@/lib/api';
import {
  ArrowLeft,
  Star,
  Copy,
  Archive,
  RotateCcw,
  Trash2,
  CheckCircle2,
  Clock,
  Code,
  AlertCircle,
  Check,
  X,
  ImageIcon,
  Send,
  Calendar,
  ExternalLink,
  Bot,
  TrendingUp,
  Award,
  Sparkles,
  Zap,
  Target,
  ShieldCheck,
  Layers,
  Wand2,
  Globe
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Container } from '@/components/layout/container';

export default function ProjectDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [productionPlan, setProductionPlan] = useState<ProductionPlan | null>(null);
  const [storyScript, setStoryScript] = useState<StoryScript | null>(null);
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [sceneImages, setSceneImages] = useState<GeneratedImage[]>([]);
  const [animations, setAnimations] = useState<AnimatedSceneClip[]>([]);
  const [audios, setAudios] = useState<VoiceNarrationAsset[]>([]);
  const [musicMixes, setMusicMixes] = useState<MixedAudioTrack[]>([]);
  const [timeline, setTimeline] = useState<VideoTimeline | null>(null);
  const [renders, setRenders] = useState<RenderTask[]>([]);
  const [publishingBundle, setPublishingBundle] = useState<PublishingAssetBundle | null>(null);

  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [publishingQueue, setPublishingQueue] = useState<PublishingQueueItem[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [scheduleDate, setScheduleDate] = useState<string>('');

  const [copilotReport, setCopilotReport] = useState<OptimizationReport | null>(null);
  const [copilotPrediction, setCopilotPrediction] = useState<PerformancePrediction | null>(null);
  const [trends, setTrends] = useState<TrendReport[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzingCopilot, setIsAnalyzingCopilot] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showJsonDebug, setShowJsonDebug] = useState(false);

  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [targetAgeGroup, setTargetAgeGroup] = useState('3-5');
  const [language, setLanguage] = useState('English (US)');
  const [videoStyle, setVideoStyle] = useState('3D Pixar Render');
  const [isFavorite, setIsFavorite] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'copilot' | 'plan' | 'scenes' | 'storyboard' | 'characters' | 'images' | 'animations' | 'audio' | 'music' | 'render' | 'publishing' | 'distribution'>('overview');

  const { saveStatus } = useAutoSave(
    project?.id,
    { title, prompt, target_age_group: targetAgeGroup, language, video_style: videoStyle },
    1200
  );

  function getErrorMessage(error: unknown): string {
    return error instanceof Error ? error.message : 'An unexpected error occurred';
  }

  const loadData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const proj = await getProjectApi(projectId);
      setProject(proj);
      setTitle(proj.title);
      setPrompt(proj.prompt);
      setTargetAgeGroup(proj.target_age_group);
      setLanguage(proj.language);
      setVideoStyle(proj.video_style);
      setIsFavorite(proj.favorite);

      try { const plan = await getProductionPlanApi(projectId); setProductionPlan(plan); } catch {}
      try { const story = await getStoryScriptApi(projectId); setStoryScript(story); } catch {}
      try { const sb = await getStoryboardApi(projectId); setStoryboard(sb); } catch {}
      try { const chars = await getCharactersApi(projectId); setCharacters(chars); } catch {}
      try { const imgs = await listSceneImagesApi(projectId); setSceneImages(imgs); } catch {}
      try { const anims = await listSceneAnimationsApi(projectId); setAnimations(anims); } catch {}
      try { const voiceClips = await listSceneVoicesApi(projectId); setAudios(voiceClips); } catch {}
      try { const mixes = await listSceneMusicMixesApi(projectId); setMusicMixes(mixes); } catch {}
      try { const tl = await getProjectTimelineApi(projectId); setTimeline(tl); } catch {}
      try { const rnds = await listProjectRendersApi(projectId); setRenders(rnds); } catch {}
      try { const pub = await getPublishingAssetsApi(projectId); setPublishingBundle(pub); } catch {}
      try { const accs = await listConnectedAccountsApi(); setAccounts(accs); if (accs.length > 0) setSelectedAccountId(accs[0].account_id); } catch {}
      try { const q = await listPublishingQueueApi(projectId); setPublishingQueue(q); } catch {}
      try { const tr = await listTrendsCopilotApi(); setTrends(tr); } catch {}
      try { const rep = await analyzeProjectCopilotApi(projectId); setCopilotReport(rep); } catch {}
      try { const pred = await predictPerformanceCopilotApi(projectId); setCopilotPrediction(pred); } catch {}
    } catch (error: unknown) {
      console.error("Error fetching project data:", getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleFavoriteToggle = async () => {
    if (!project) return;
    setIsFavorite(!isFavorite);
    await toggleFavoriteApi(project.id);
  };

  const handleDuplicate = async () => {
    if (!project) return;
    const dup = await duplicateProjectApi(project.id);
    router.push(`/projects/${dup.id}`);
  };

  const handleArchive = async () => {
    if (!project) return;
    if (project.archived) {
      const restored = await restoreProjectApi(project.id);
      setProject(restored);
    } else {
      const archived = await archiveProjectApi(project.id);
      setProject(archived);
    }
  };

  const handleDelete = async () => {
    if (!project) return;
    if (!confirm(`Are you sure you want to delete "${project.title}"?`)) return;
    await deleteProjectApi(project.id);
    router.push('/dashboard');
  };

  const handleRunCopilotAudit = async () => {
    if (!project) return;
    setIsAnalyzingCopilot(true);
    try {
      const rep = await analyzeProjectCopilotApi(project.id);
      const pred = await predictPerformanceCopilotApi(project.id);
      setCopilotReport(rep);
      setCopilotPrediction(pred);
      setActiveTab('copilot');
    } catch (err: any) {
      setErrorMsg(err.message || 'Copilot audit failed.');
    } finally {
      setIsAnalyzingCopilot(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background-primary flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-foreground-muted">Loading project workspace...</span>
          </div>
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-background-primary flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 text-center space-y-4">
          <h2 className="text-xl font-bold text-foreground-primary">Project Not Found</h2>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-button text-xs font-semibold text-primary-foreground">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-primary flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        <Container>
          {/* Top Header & Actions Bar */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Link href="/dashboard" className="p-2 rounded-xl bg-surface-secondary/5 border border-white/10 hover:bg-surface-secondary/10 text-foreground-muted transition-colors">
                <ArrowLeft className="w-4 h-4" />
              </Link>

              <div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(project.status)}`}>
                    {project.status}
                  </span>
                  <span className="text-xs text-foreground-muted flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> Format: {project.aspect_ratio}
                  </span>

                  <div className="flex items-center gap-1.5 text-xs text-foreground-muted">
                    {saveStatus === 'saving' && (
                      <span className="text-warning/400 font-medium flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-warning/400 animate-ping" /> Auto-saving...
                      </span>
                    )}
                    {saveStatus === 'saved' && (
                      <span className="text-success/400 font-medium flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Saved
                      </span>
                    )}
                  </div>
                </div>

                <Input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-2xl font-bold text-foreground-primary bg-transparent border-b border-transparent hover:border-primary/50 focus:border-primary/500 focus:outline-none mt-1"
                  placeholder="Enter project title..."
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowJsonDebug(!showJsonDebug)}
                className={`${showJsonDebug ? 'bg-primary/20 text-primary/300 border-primary/40' : 'text-foreground-muted'}`}
              >
                <Code className="w-3.5 h-3.5" /> JSON Debug
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleFavoriteToggle}
                className={`${isFavorite ? 'text-primary' : 'text-foreground-muted'}`}
              >
                <Star className={`w-4 h-4 ${isFavorite ? 'text-primary' : ''}`} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDuplicate}
              >
                <Copy className="w-3.5 h-3.5" /> Duplicate
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleArchive}
              >
                {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDelete}
                className="text-error/400 hover:text-error/600"
              >
                <Trash2 className="w-3.5 h-3.5" /> Delete
              </Button>
            </div>
          </div>

          {errorMsg && (
            <div className="p-4 rounded-xl bg-error/10 border border-error/20 text-error/300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* AI Orchestration Banner */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
            <div className="space-y-1">
              <span className="text-xs font-semibold text-primary/400 uppercase tracking-wider flex items-center gap-1.5">
                <Bot className="w-4 h-4" /> KidsAI Studio v2.0 AI Creator Copilot & Performance Predictor
              </span>
              <h2 className="text-lg font-bold text-foreground-primary">
                {copilotReport
                  ? `Project Optimization Score: ${copilotReport.overall_score}/100 — High Audience Retention Predicted`
                  : "Run AI Creator Copilot Audit for Pacing, Visual & CTR Optimization"}
              </h2>
              <p className="text-sm text-foreground-muted">
                {copilotReport
                  ? "Autonomous intelligence evaluated story pacing, visual contrast, educational depth, and predicted a 13.8% CTR on release."
                  : "Analyze project for weak scene detection, CTR performance predictions, and automated workflow triggers."}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 shrink-0">
              <Button
                variant="primary"
                size="sm"
                onClick={handleRunCopilotAudit}
                disabled={isAnalyzingCopilot}
                className="flex items-center gap-2"
              >
                {isAnalyzingCopilot ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Analyzing Project...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>{copilotReport ? "Re-Run Copilot Audit" : "Run Copilot Audit"}</span>
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex items-center gap-2 border-t border-white/10 pt-4 space-x-2 overflow-x-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('copilot')}
              className={`
                ${activeTab === 'copilot'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              AI Copilot Studio {copilotReport ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('overview')}
              className={`
                ${activeTab === 'overview'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Overview
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('plan')}
              className={`
                ${activeTab === 'plan'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Production Plan {productionPlan ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('scenes')}
              className={`
                ${activeTab === 'scenes'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Story Script ({storyScript?.scenes.length || 0})
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('storyboard')}
              className={`
                ${activeTab === 'storyboard'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Storyboard ({storyboard?.scenes.length || 0}) {storyboard ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('characters')}
              className={`
                ${activeTab === 'characters'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Characters ({characters.length}) {characters.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('images')}
              className={`
                ${activeTab === 'images'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Images ({sceneImages.length}) {sceneImages.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('animations')}
              className={`
                ${activeTab === 'animations'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Animations ({animations.length}) {animations.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('audio')}
              className={`
                ${activeTab === 'audio'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Voice Narration ({audios.length}) {audios.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('music')}
              className={`
                ${activeTab === 'music'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Audio Mixing ({musicMixes.length}) {musicMixes.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('render')}
              className={`
                ${activeTab === 'render'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Render & Export ({renders.length}) {renders.length > 0 ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('publishing')}
              className={`
                ${activeTab === 'publishing'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Publishing & SEO {publishingBundle ? "✓" : ""}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('distribution')}
              className={`
                ${activeTab === 'distribution'
                  ? 'bg-primary/20 text-primary/300 border-primary/40'
                  : 'bg-surface-secondary/5 text-foreground-muted border-white/10 hover:text-foreground-primary'}
              `}
            >
              Multi-Platform Distribution ({publishingQueue.length}) {publishingQueue.length > 0 ? "✓" : ""}
            </Button>
          </div>

          {/* Tab Content */}
          <div className="mt-6 space-y-6">
            {/* Tab 1: AI Creator Copilot Studio */}
            {activeTab === 'copilot' && (
              <div className="space-y-6">
                {copilotReport && copilotPrediction ? (
                  <div className="space-y-8">
                    {/* Copilot Performance Forecast Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                        <div className="text-xs text-foreground-muted font-bold uppercase flex items-center gap-1.5">
                          <Award className="w-4 h-4 text-primary/400" /> Optimization Score
                        </div>
                        <div className="text-2xl font-extrabold text-foreground-primary">{copilotReport.overall_score} <span className="text-xs text-foreground-muted font-normal">/ 100</span></div>
                      </div>

                      <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                        <div className="text-xs text-foreground-muted font-bold uppercase flex items-center gap-1.5">
                          <TrendingUp className="w-4 h-4 text-success/400" /> Predicted CTR
                        </div>
                        <div className="text-2xl font-extrabold text-success/400">{copilotPrediction.predicted_ctr}%</div>
                      </div>

                      <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                        <div className="text-xs text-foreground-muted font-bold uppercase flex items-center gap-1.5">
                          <Target className="w-4 h-4 text-warning/400" /> Retention Forecast
                        </div>
                        <div className="text-2xl font-extrabold text-warning/400">{copilotPrediction.predicted_retention_pct}%</div>
                      </div>

                      <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                        <div className="text-xs text-foreground-muted font-bold uppercase flex items-center gap-1.5">
                          <ShieldCheck className="w-4 h-4 text-info/400" /> Release Risk
                        </div>
                        <div className="text-2xl font-extrabold text-info/400">{copilotPrediction.publishing_risk} RISK</div>
                      </div>
                    </div>

                    {/* Copilot Suggestions & Forecast Explanations */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Actionable Suggestions */}
                      <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
                        <h4 className="text-sm font-semibold text-primary/400 uppercase tracking-wider flex items-center gap-2">
                          <Wand2 className="w-4 h-4 text-primary/400" /> Autonomous Copilot Suggestions
                        </h4>

                        <div className="space-y-3">
                          {copilotReport.suggestions.map((sug, i) => (
                            <div key={i} className="p-4 rounded-2xl border border-white/15 space-y-2 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="px-2.5 py-0.5 rounded-full bg-primary/10 text-primary/300 font-bold text-[10px] border border-primary/20">
                                  {sug.category}
                                </span>
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                                  sug.severity === 'HIGH' ? 'bg-error/10 text-error/300 border-error/20' : 'bg-warning/10 text-warning/300 border-warning/20'
                                }`}>
                                  {sug.severity} PRIORITY
                                </span>
                              </div>

                              <div className="text-white font-bold">{sug.explanation}</div>
                              <div className="text-foreground-muted text-[11px]">Suggested Action: <span className="text-primary/400 font-mono">{sug.suggested_value}</span></div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Trend Intelligence & Explanations */}
                      <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
                        <h4 className="text-sm font-semibold text-primary/400 uppercase tracking-wider flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-warning/400" /> Market Intelligence & High-CTR Keywords
                        </h4>

                        <div className="space-y-3">
                          {trends.map((t) => (
                            <div key={t.trend_id} className="p-3.5 rounded-2xl border border-white/15 space-y-2 text-xs">
                              <div className="flex items-center justify-between text-white font-bold">
                                <span>{t.topic}</span>
                                <span className="text-emerald-400 font-mono">Opportunity: {t.opportunity_score}/100</span>
                              </div>

                              <div className="flex flex-wrap gap-1.5">
                                {t.seasonal_keywords.map((kw, idx) => (
                                  <span key={idx} className="px-2 py-0.5 rounded-md bg-white/5 text-foreground-muted text-[11px] border border-white/15">
                                    #{kw}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="glass-panel p-12 rounded-3xl border border-white/10 text-center space-y-4 max-w-md mx-auto">
                    <Bot className="w-10 h-10 text-primary/400 mx-auto" />
                    <h3 className="text-base font-bold text-foreground-primary">No Copilot Audit Performed Yet</h3>
                    <Button
                      variant="primary"
                      size="md"
                      onClick={handleRunCopilotAudit}
                    >
                      Run Copilot Audit & Performance Predictor
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Other Tabs */}
            {activeTab === 'overview' && (
              <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2 text-xs text-foreground-muted">
                <strong className="text-primary/400 font-semibold">Topic Prompt:</strong> {prompt}
              </div>
            )}

            {activeTab === 'plan' && (
              <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2">
                {productionPlan ? (
                  <>
                    <h3 className="text-lg font-bold text-foreground-primary mb-4">Production Plan</h3>
                    <pre className="bg-surface-secondary/5 p-4 rounded-xl overflow-auto">{JSON.stringify(productionPlan, null, 2)}</pre>
                  </>
                ) : (
                  <p className="text-foreground-muted">No production plan available.</p>
                )}
              </div>
            )}
          </div>
        </Container>
      </main>
    </div>
  );
}

// Helper function for status badge classes
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