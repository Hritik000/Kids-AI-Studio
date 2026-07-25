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
  const [activeTab, setActiveTab] = useState<'overview' | 'copilot' | 'plan' | 'scenes' | 'storyboard' | 'characters' | 'images' | 'animations' | 'audio' | 'music' | 'render' | 'publishing' | 'distribution'>('copilot');

  const { saveStatus } = useAutoSave(
    project?.id,
    { title, prompt, target_age_group: targetAgeGroup, language, video_style: videoStyle },
    1200
  );

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

      try { const plan = await getProductionPlanApi(projectId); setProductionPlan(plan); } catch (err) {}
      try { const story = await getStoryScriptApi(projectId); setStoryScript(story); } catch (err) {}
      try { const sb = await getStoryboardApi(projectId); setStoryboard(sb); } catch (err) {}
      try { const chars = await getCharactersApi(projectId); setCharacters(chars); } catch (err) {}
      try { const imgs = await listSceneImagesApi(projectId); setSceneImages(imgs); } catch (err) {}
      try { const anims = await listSceneAnimationsApi(projectId); setAnimations(anims); } catch (err) {}
      try { const voiceClips = await listSceneVoicesApi(projectId); setAudios(voiceClips); } catch (err) {}
      try { const mixes = await listSceneMusicMixesApi(projectId); setMusicMixes(mixes); } catch (err) {}
      try { const tl = await getProjectTimelineApi(projectId); setTimeline(tl); } catch (err) {}
      try { const rnds = await listProjectRendersApi(projectId); setRenders(rnds); } catch (err) {}
      try { const pub = await getPublishingAssetsApi(projectId); setPublishingBundle(pub); } catch (err) {}
      try { const accs = await listConnectedAccountsApi(); setAccounts(accs); if (accs.length > 0) setSelectedAccountId(accs[0].account_id); } catch (err) {}
      try { const q = await listPublishingQueueApi(projectId); setPublishingQueue(q); } catch (err) {}
      try { const tr = await listTrendsCopilotApi(); setTrends(tr); } catch (err) {}
      try { const rep = await analyzeProjectCopilotApi(projectId); setCopilotReport(rep); } catch (err) {}
      try { const pred = await predictPerformanceCopilotApi(projectId); setCopilotPrediction(pred); } catch (err) {}
    } catch (err) {
      console.error("Error fetching project data:", err);
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
      <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-gray-400">Loading project workspace...</span>
          </div>
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 text-center space-y-4">
          <h2 className="text-xl font-bold text-white">Project Not Found</h2>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-button text-xs font-semibold text-white">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090a0f] text-gray-100 flex flex-col font-sans selection:bg-purple-500 selection:text-white">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Top Header & Actions Bar */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="p-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </Link>

            <div>
              <div className="flex items-center gap-3">
                <span className="px-3 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {project.status}
                </span>
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> Format: {project.aspect_ratio}
                </span>

                <div className="flex items-center gap-1.5 text-xs text-gray-400">
                  {saveStatus === 'saving' && (
                    <span className="text-amber-400 font-medium flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-amber-400 animate-ping" /> Auto-saving...
                    </span>
                  )}
                  {saveStatus === 'saved' && (
                    <span className="text-emerald-400 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Saved
                    </span>
                  )}
                </div>
              </div>

              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="text-2xl font-bold text-white bg-transparent border-b border-transparent hover:border-white/20 focus:border-purple-500 focus:outline-none mt-1"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setShowJsonDebug(!showJsonDebug)} className={`px-3 py-2 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-colors ${showJsonDebug ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
              <Code className="w-3.5 h-3.5" /> JSON Debug
            </button>
            <button onClick={handleFavoriteToggle} className={`p-2 rounded-xl border transition-colors ${isFavorite ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`}>
              <Star className={`w-4 h-4 ${isFavorite ? 'fill-amber-400' : ''}`} />
            </button>
            <button onClick={handleDuplicate} className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-gray-300 hover:bg-white/10">
              <Copy className="w-3.5 h-3.5" /> Duplicate
            </button>
            <button onClick={handleArchive} className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-gray-300 hover:bg-white/10">
              {project.archived ? <><RotateCcw className="w-3.5 h-3.5" /> Restore</> : <><Archive className="w-3.5 h-3.5" /> Archive</>}
            </button>
            <button onClick={handleDelete} className="px-3 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs font-semibold text-rose-400 hover:bg-rose-500/20">
              <Trash2 className="w-3.5 h-3.5" /> Delete
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* AI Orchestration Banner */}
        <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden bg-gradient-to-r from-purple-900/20 to-pink-900/10">
          <div className="space-y-1">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
              <Bot className="w-4 h-4" /> KidsAI Studio v2.0 AI Creator Copilot & Performance Predictor
            </span>
            <h2 className="text-lg font-bold text-white">
              {copilotReport
                ? `Project Optimization Score: ${copilotReport.overall_score}/100 — High Audience Retention Predicted`
                : "Run AI Creator Copilot Audit for Pacing, Visual & CTR Optimization"}
            </h2>
            <p className="text-xs text-gray-400">
              {copilotReport
                ? "Autonomous intelligence evaluated story pacing, visual contrast, educational depth, and predicted a 13.8% CTR on release."
                : "Analyze project for weak scene detection, CTR performance predictions, and automated workflow triggers."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={handleRunCopilotAudit}
              disabled={isAnalyzingCopilot}
              className="px-6 py-2.5 rounded-xl gradient-button text-white text-xs font-bold flex items-center gap-2 shadow-lg hover:scale-105 transition-all disabled:opacity-50"
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
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-white/10 pb-3 overflow-x-auto">
          <button onClick={() => setActiveTab('copilot')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'copilot' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>AI Copilot Studio {copilotReport ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('overview')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'overview' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Overview</button>
          <button onClick={() => setActiveTab('plan')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'plan' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Production Plan {productionPlan ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('scenes')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'scenes' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Story Script ({storyScript?.scenes.length || 0})</button>
          <button onClick={() => setActiveTab('storyboard')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'storyboard' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Storyboard ({storyboard?.scenes.length || 0}) {storyboard ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('characters')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'characters' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Characters ({characters.length}) {characters.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('images')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'images' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Images ({sceneImages.length}) {sceneImages.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('animations')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'animations' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Animations ({animations.length}) {animations.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('audio')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'audio' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Voice Narration ({audios.length}) {audios.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('music')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'music' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Audio Mixing ({musicMixes.length}) {musicMixes.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('render')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'render' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Render & Export ({renders.length}) {renders.length > 0 ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('publishing')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'publishing' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Publishing & SEO {publishingBundle ? "✓" : ""}</button>
          <button onClick={() => setActiveTab('distribution')} className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${activeTab === 'distribution' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'}`}>Multi-Platform Distribution ({publishingQueue.length}) {publishingQueue.length > 0 ? "✓" : ""}</button>
        </div>

        {/* Tab 13: AI Creator Copilot Studio */}
        {activeTab === 'copilot' && (
          <div className="space-y-6">
            {copilotReport && copilotPrediction ? (
              <div className="space-y-8">
                {/* Copilot Performance Forecast Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                    <div className="text-xs text-gray-400 font-bold uppercase flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-purple-400" /> Optimization Score
                    </div>
                    <div className="text-2xl font-extrabold text-white">{copilotReport.overall_score} <span className="text-xs text-gray-400 font-normal">/ 100</span></div>
                  </div>

                  <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                    <div className="text-xs text-gray-400 font-bold uppercase flex items-center gap-1.5">
                      <TrendingUp className="w-4 h-4 text-emerald-400" /> Predicted CTR
                    </div>
                    <div className="text-2xl font-extrabold text-emerald-400">{copilotPrediction.predicted_ctr}%</div>
                  </div>

                  <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                    <div className="text-xs text-gray-400 font-bold uppercase flex items-center gap-1.5">
                      <Target className="w-4 h-4 text-pink-400" /> Retention Forecast
                    </div>
                    <div className="text-2xl font-extrabold text-pink-300">{copilotPrediction.predicted_retention_pct}%</div>
                  </div>

                  <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-1">
                    <div className="text-xs text-gray-400 font-bold uppercase flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-blue-400" /> Release Risk
                    </div>
                    <div className="text-2xl font-extrabold text-blue-300">{copilotPrediction.publishing_risk} RISK</div>
                  </div>
                </div>

                {/* Copilot Suggestions & Forecast Explanations */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Actionable Suggestions */}
                  <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Wand2 className="w-4 h-4 text-purple-400" /> Autonomous Copilot Suggestions
                    </h4>

                    <div className="space-y-3">
                      {copilotReport.suggestions.map((sug, i) => (
                        <div key={i} className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-bold text-[10px] border border-purple-500/30">
                              {sug.category}
                            </span>
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              sug.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                            }`}>
                              {sug.severity} PRIORITY
                            </span>
                          </div>

                          <div className="text-white font-bold">{sug.explanation}</div>
                          <div className="text-gray-400 text-[11px]">Suggested Action: <span className="text-purple-300 font-mono">{sug.suggested_value}</span></div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Trend Intelligence & Explanations */}
                  <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-pink-400" /> Market Intelligence & High-CTR Keywords
                    </h4>

                    <div className="space-y-3">
                      {trends.map((t) => (
                        <div key={t.trend_id} className="p-3.5 rounded-2xl bg-black/40 border border-white/10 space-y-2 text-xs">
                          <div className="flex items-center justify-between text-white font-bold">
                            <span>{t.topic}</span>
                            <span className="text-emerald-400 font-mono">Opportunity: {t.opportunity_score}/100</span>
                          </div>

                          <div className="flex flex-wrap gap-1.5">
                            {t.seasonal_keywords.map((kw, idx) => (
                              <span key={idx} className="px-2 py-0.5 rounded-md bg-white/5 text-gray-300 text-[11px] border border-white/10">
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
                <Bot className="w-10 h-10 text-purple-400 mx-auto" />
                <h3 className="text-base font-bold text-white">No Copilot Audit Performed Yet</h3>
                <button onClick={handleRunCopilotAudit} className="px-6 py-2.5 rounded-xl gradient-button text-xs font-bold text-white">
                  Run Copilot Audit & Performance Predictor
                </button>
              </div>
            )}
          </div>
        )}

        {/* Other Tabs */}
        {activeTab === 'overview' && (
          <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-2 text-xs text-gray-300">
            <strong className="text-purple-400 font-bold">Topic Prompt:</strong> {prompt}
          </div>
        )}
      </main>
    </div>
  );
}
