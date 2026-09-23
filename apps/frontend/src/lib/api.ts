export type UserRole = 'USER' | 'ADMIN' | 'MODERATOR';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export type ProjectStatus =
  | 'DRAFT'
  | 'PLANNING'
  | 'STORY_READY'
  | 'STORYBOARD_READY'
  | 'IMAGES_READY'
  | 'ANIMATION_READY'
  | 'VOICE_READY'
  | 'MUSIC_READY'
  | 'RENDERING'
  | 'QUALITY_CHECK'
  | 'COMPLETED'
  | 'PUBLISHED'
  | 'FAILED'
  | 'ARCHIVED';

export interface Scene {
  scene_number: number;
  narration_text: string;
  visual_prompt: string;
  image_url?: string;
  audio_url?: string;
  duration_seconds: number;
  camera_direction?: string;
  emotion?: string;
  transition?: string;
  educational_goal?: string;
}

export interface ProjectMetrics {
  generation_time_seconds: number;
  model_used: string;
  tokens_used: number;
  image_count: number;
  video_duration_seconds: number;
  render_time_seconds: number;
  estimated_cost_usd: number;
}

export interface Project {
  id: string;
  title: string;
  description?: string;
  prompt: string;
  target_age_group: string;
  language: string;
  video_length: string;
  aspect_ratio: string;
  video_style: string;
  voice: string;
  status: ProjectStatus;
  thumbnail_url?: string;
  tags: string[];
  scenes: Scene[];
  final_video_url?: string;
  metrics?: ProjectMetrics;
  favorite: boolean;
  archived: boolean;
  owner_id: string;
  created_at: string;
  updated_at: string;
  last_opened_at?: string;
}

export interface ProductionPlan {
  project_id: string;
  topic: string;
  educational_objective: string;
  target_age_group: string;
  estimated_duration_seconds: number;
  scene_count: number;
  narration_style: string;
  visual_style: string;
  character_requirements: Array<{ name: string; description: string; role: string }>;
  music_mood_plan: string;
  animation_style_plan: string;
  thumbnail_concept_plan: string;
  seo_strategy_plan: { target_keywords: string[]; category: string };
  quality_rules: string[];
  retry_strategy: { max_retries: number; fallback_provider: string };
}

export interface StoryScript {
  story_title: string;
  story_summary: string;
  educational_goal: string;
  ending_call_to_action?: string;
  characters: Array<{ name: string; species_or_type: string; visual_features: string; personality: string }>;
  scenes: Array<{
    scene_number: number;
    narration_text: string;
    visual_description: string;
    educational_goal: string;
    estimated_duration: number;
    camera_direction: string;
    emotion: string;
    transition: string;
  }>;
}

export interface StoryboardScene {
  scene_number: number;
  scene_title: string;
  purpose: string;
  learning_goal: string;
  estimated_duration: number;
  energy_level: string;
  scene_importance: string;
  narrative_arc: { beginning: string; middle: string; ending: string };
  narration_text: string;
  visual_plan: {
    environment: string;
    time_of_day: string;
    weather: string;
    background: string;
    foreground: string;
    key_objects: string[];
    color_palette: string[];
    lighting_style: string;
    mood: string;
    atmosphere: string;
    composition: string;
  };
  camera_plan: {
    shot_type: string;
    angle: string;
    movement: string;
    camera_direction: string;
    camera_speed: string;
    focal_point: string;
  };
  transition: { type: string; duration_seconds: number };
  character_references: Array<{
    character_name: string;
    expression: string;
    pose: string;
    eye_direction: string;
    interaction: string;
    visibility: string;
    importance: string;
  }>;
}

export interface Storyboard {
  project_id: string;
  story_title: string;
  total_scenes: number;
  total_duration_seconds: number;
  visual_style: string;
  global_color_palette: string[];
  scenes: StoryboardScene[];
  approved: boolean;
}

export interface CharacterProfile {
  character_id: string;
  project_id: string;
  name: string;
  species: string;
  age_group: string;
  gender: string;
  personality: string;
  role: string;
  backstory?: string;
  height: string;
  body_shape: string;
  eye_shape: string;
  eye_color: string;
  hair_style: string;
  hair_color: string;
  skin_color: string;
  clothing: string;
  shoes: string;
  accessories: string[];
  primary_colors: string[];
  expressions: string[];
  signature_pose: string;
  reference_prompt: string;
  negative_prompt: string;
  reference_image_url?: string;
  visual_style: string;
  created_at: string;
}

export interface GeneratedImage {
  image_id: string;
  project_id: string;
  scene_number: number;
  prompt_version: string;
  composed_prompt: string;
  negative_prompt: string;
  provider: string;
  seed: number;
  width: number;
  height: number;
  aspect_ratio: string;
  generation_time_seconds: number;
  status: string;
  storage_url: string;
  thumbnail_url: string;
  created_at: string;
}

export interface MotionPlan {
  motion_type: string;
  camera_path: string;
  camera_speed: string;
  character_motion: string;
  environment_motion: string;
  duration_seconds: number;
  frame_rate: number;
  speed: string;
  transition_style: string;
  complexity: string;
}

export interface AnimatedSceneClip {
  animation_id: string;
  project_id: string;
  scene_number: number;
  motion_plan: MotionPlan;
  composed_motion_prompt: string;
  provider: string;
  seed: number;
  width: number;
  height: number;
  aspect_ratio: string;
  duration_seconds: number;
  frame_rate: number;
  generation_time_seconds: number;
  status: string;
  storage_url: string;
  thumbnail_url: string;
  created_at: string;
}

export interface DialogueSegment {
  segment_id: string;
  scene_number: number;
  speaker_name: string;
  speaker_role: string;
  text: string;
  emotional_tone: string;
  speech_speed: number;
  pause_duration_seconds: number;
  emphasis_words: string[];
}

export interface VisemeMarker {
  timestamp_seconds: number;
  mouth_shape: string;
  duration_seconds: number;
}

export interface LipSyncMetadata {
  visemes: VisemeMarker[];
  blink_timestamps: number[];
}

export interface VoiceNarrationAsset {
  audio_id: string;
  project_id: string;
  scene_number: number;
  dialogue_segments: DialogueSegment[];
  lip_sync: LipSyncMetadata;
  voice_name: string;
  voice_type: string;
  emotion: string;
  language: string;
  duration_seconds: number;
  sample_rate: number;
  audio_format: string;
  provider: string;
  status: string;
  storage_url: string;
  generation_time_seconds: number;
  created_at: string;
}

export interface MusicPlan {
  track_id: string;
  genre: string;
  mood: string;
  bpm: number;
  key: string;
  instruments: string[];
  duration_seconds: number;
  loop_enabled: boolean;
}

export interface SoundEffectItem {
  sfx_id: string;
  name: string;
  category: string;
  timestamp_seconds: number;
  volume_level: number;
}

export interface AmbientAudioPlan {
  ambient_id: string;
  environment_type: string;
  volume_level: number;
}

export interface MixedAudioTrack {
  mix_id: string;
  project_id: string;
  scene_number: number;
  music_plan: MusicPlan;
  sound_effects: SoundEffectItem[];
  ambient_plan: AmbientAudioPlan;
  narration_volume: number;
  music_ducked_volume: number;
  ambient_volume: number;
  sfx_volume: number;
  master_loudness_lufs: number;
  duration_seconds: number;
  sample_rate: number;
  audio_format: string;
  provider: string;
  status: string;
  storage_url: string;
  generation_time_seconds: number;
  created_at: string;
}

export interface SubtitlePlaceholder {
  enabled: boolean;
  caption_style: string;
  font_family: string;
  font_color: string;
  highlight_color: string;
  position: string;
}

export interface TimelineSceneItem {
  scene_number: number;
  duration_seconds: number;
  animation_url: string;
  voice_url?: string;
  music_mix_url?: string;
  transition_type: string;
  transition_duration_seconds: number;
  subtitle_placeholder: SubtitlePlaceholder;
}

export interface VideoTimeline {
  timeline_id: string;
  project_id: string;
  aspect_ratio: string;
  resolution: string;
  frame_rate: number;
  total_duration_seconds: number;
  scenes: TimelineSceneItem[];
  created_at: string;
}

export interface RenderTask {
  render_id: string;
  project_id: string;
  timeline_id: string;
  status: string;
  resolution: string;
  codec: string;
  output_format: string;
  file_size_bytes: number;
  preview_url: string;
  final_video_url: string;
  generation_time_seconds: number;
  created_at: string;
}

export interface ThumbnailVariant {
  variant_id: string;
  version_name: string;
  style_type: string;
  prompt: string;
  storage_url: string;
  ctr_score: number;
  selected: boolean;
}

export interface TitleOption {
  title_id: string;
  title_text: string;
  category: string;
  ctr_score: number;
  character_count: number;
}

export interface ChapterItem {
  timestamp: string;
  title: string;
  summary: string;
}

export interface SEOPackage {
  seo_id: string;
  project_id: string;
  selected_title: string;
  title_options: TitleOption[];
  short_description: string;
  long_description: string;
  chapters: ChapterItem[];
  primary_keywords: string[];
  secondary_keywords: string[];
  hashtags: string[];
  category: string;
  coppa_compliant: boolean;
  created_at: string;
}

export interface PublishingAssetBundle {
  bundle_id: string;
  project_id: string;
  thumbnails: ThumbnailVariant[];
  seo: SEOPackage;
  status: string;
  created_at: string;
}

export interface ConnectedAccount {
  account_id: string;
  platform: string;
  display_name: string;
  channel_name: string;
  avatar_url: string;
  connection_status: string;
  permissions: string[];
  last_synced_at: string;
}

export interface PlatformPublishPlan {
  plan_id: string;
  project_id: string;
  platform: string;
  scheduled_time?: string;
  publish_mode: string;
  custom_title: string;
  custom_description: string;
  custom_tags: string[];
  visibility: string;
}

export interface PublishingQueueItem {
  queue_id: string;
  project_id: string;
  account_id: string;
  platform: string;
  plan: PlatformPublishPlan;
  status: string;
  progress_percentage: number;
  platform_post_id?: string;
  post_url?: string;
  error_message?: string;
  attempt_count: number;
  published_at?: string;
  created_at: string;
}

export interface SubscriptionPlan {
  plan_id: string;
  name: string;
  monthly_price_usd: number;
  credits_per_month: number;
  max_team_members: number;
  storage_limit_gb: number;
  features: string[];
}

export interface UserSubscription {
  subscription_id: string;
  user_id: string;
  plan_id: string;
  status: string;
  credits_remaining: number;
  current_period_end: string;
  created_at: string;
}

export interface Workspace {
  workspace_id: string;
  name: string;
  owner_id: string;
  type: string;
  created_at: string;
}

export interface APIKeyItem {
  key_id: string;
  user_id: string;
  name: string;
  secret_key: string;
  scopes: string[];
  last_used_at?: string;
  created_at: string;
}

export interface NotificationItem {
  notification_id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  read: boolean;
  created_at: string;
}

export interface AnalyticsSummary {
  total_projects: number;
  total_stories_generated: number;
  total_images_generated: number;
  total_video_clips_generated: number;
  total_audio_tracks_generated: number;
  total_render_minutes: number;
  render_success_rate: number;
  ai_provider_health: string;
  credits_remaining: number;
  active_subscription: string;
}

export interface OptimizationSuggestion {
  category: string;
  severity: string;
  current_value: string;
  suggested_value: string;
  explanation: string;
}

export interface OptimizationReport {
  project_id: string;
  overall_score: number;
  pacing_score: number;
  educational_score: number;
  visual_score: number;
  audio_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: OptimizationSuggestion[];
  created_at: string;
}

export interface PerformancePrediction {
  project_id: string;
  predicted_ctr: number;
  predicted_retention_pct: number;
  expected_watch_time_sec: number;
  publishing_risk: string;
  confidence_score: number;
  explanations: string[];
  created_at: string;
}

export interface TrendReport {
  trend_id: string;
  topic: string;
  category: string;
  search_volume_score: number;
  competition_level: string;
  opportunity_score: number;
  target_age_group: string;
  seasonal_keywords: string[];
}

export interface WorkflowAutomationItem {
  workflow_id: string;
  name: string;
  trigger_event: string;
  actions: string[];
  is_active: boolean;
  created_at: string;
}

export interface ContentTemplateItem {
  template_id: string;
  name: string;
  category: string;
  description: string;
  tags: string[];
  payload: Record<string, unknown>;
  downloads_count: number;
  created_at: string;
}

export interface AIModelConfigItem {
  model_id: string;
  provider: string;
  model_type: string;
  display_name: string;
  latency_ms: number;
  cost_per_unit: number;
  status: string;
  is_default: boolean;
}

export interface PipelineStatus {
  project_id: string;
  status: ProjectStatus;
  has_production_plan: boolean;
  has_story_script: boolean;
  current_step: number;
  total_steps: number;
}

export interface CreateProjectPayload {
  title?: string;
  prompt: string;
  target_age_group?: string;
  language?: string;
  video_length?: string;
  aspect_ratio?: string;
  video_style?: string;
  voice?: string;
  save_as_draft?: boolean;
}

export interface UpdateProjectPayload {
  title?: string;
  description?: string;
  prompt?: string;
  target_age_group?: string;
  language?: string;
  video_length?: string;
  aspect_ratio?: string;
  video_style?: string;
  voice?: string;
  status?: ProjectStatus;
  tags?: string[];
  favorite?: boolean;
  archived?: boolean;
}

export interface PaginatedProjects {
  items: Project[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders(token?: string | null): HeadersInit {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('kidsai_auth_token') : null) || 'demo_token_user_demo_123';
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
}

export async function loginApi(email: string, password: string, rememberMe: boolean = false): Promise<{ token: string; user: UserProfile }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, remember_me: rememberMe }),
  });
  const res: APIResponse<{ access_token: string; user: UserProfile }> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Login failed');
  }
  return { token: res.data.access_token, user: res.data.user };
}

export async function registerApi(fullName: string, email: string, password: string, confirmPassword: string): Promise<{ token: string; user: UserProfile }> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      full_name: fullName,
      email,
      password,
      confirm_password: confirmPassword,
      terms_accepted: true,
    }),
  });
  const res: APIResponse<{ access_token: string; user: UserProfile }> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Registration failed');
  }
  return { token: res.data.access_token, user: res.data.user };
}

export async function getMeApi(token?: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders(token),
  });
  const res: APIResponse<UserProfile> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to authenticate session');
  }
  return res.data;
}

export async function updateProfileApi(fullName: string, avatarUrl?: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE}/users/profile`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ full_name: fullName, avatar_url: avatarUrl }),
  });
  const res: APIResponse<UserProfile> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to update profile');
  }
  return res.data;
}

export async function forgotPasswordApi(email: string): Promise<string> {
  const response = await fetch(`${API_BASE}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  const res: APIResponse<{ message: string }> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Password reset request failed');
  }
  return res.data.message;
}

// Project Management CRUD APIs
export async function createProjectApi(payload: CreateProjectPayload | string, targetAgeGroup: string = "3-5", aspectRatio: string = "16:9"): Promise<Project> {
  const bodyPayload = typeof payload === 'string' ? {
    title: `Project ${payload.slice(0, 15)}...`,
    prompt: payload,
    target_age_group: targetAgeGroup,
    aspect_ratio: aspectRatio,
    save_as_draft: true
  } : {
    title: payload.title || `Project ${payload.prompt.slice(0, 15)}...`,
    ...payload
  };

  const response = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(bodyPayload),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to create project');
  }
  return res.data;
}

export async function listProjectsApi(params?: {
  q?: string;
  status?: string;
  is_favorite?: boolean;
  is_archived?: boolean;
  sort?: string;
  page?: number;
  limit?: number;
}): Promise<PaginatedProjects> {
  const urlParams = new URLSearchParams();
  if (params?.q) urlParams.append('q', params.q);
  if (params?.status) urlParams.append('status', params.status);
  if (params?.is_favorite !== undefined) urlParams.append('is_favorite', String(params.is_favorite));
  if (params?.is_archived !== undefined) urlParams.append('is_archived', String(params.is_archived));
  if (params?.sort) urlParams.append('sort', params.sort);
  if (params?.page) urlParams.append('page', String(params.page));
  if (params?.limit) urlParams.append('limit', String(params.limit));

  const response = await fetch(`${API_BASE}/projects?${urlParams.toString()}`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PaginatedProjects> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list projects');
  }
  return res.data;
}

export async function getProjectApi(id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch project');
  }
  return res.data;
}

export async function updateProjectApi(id: string, payload: UpdateProjectPayload): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to update project');
  }
  return res.data;
}

export async function deleteProjectApi(id: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ message: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to delete project');
  }
  return true;
}

export async function duplicateProjectApi(id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/duplicate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to duplicate project');
  }
  return res.data;
}

export async function archiveProjectApi(id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/archive`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to archive project');
  }
  return res.data;
}

export async function restoreProjectApi(id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/restore`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to restore project');
  }
  return res.data;
}

export async function toggleFavoriteApi(id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/favorite`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Project> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to toggle favorite');
  }
  return res.data;
}

// Phase 6 AI Director & Story Generation APIs
export async function generateProductionPlanApi(projectId: string): Promise<ProductionPlan> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/generate-plan`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<ProductionPlan> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate production plan');
  }
  return res.data;
}

export async function generateStoryApi(projectId: string): Promise<StoryScript> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/generate-story`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<StoryScript> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate story script');
  }
  return res.data;
}

export async function getProductionPlanApi(projectId: string): Promise<ProductionPlan> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/plan`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<ProductionPlan> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch production plan');
  }
  return res.data;
}

export async function getStoryScriptApi(projectId: string): Promise<StoryScript> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/story`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<StoryScript> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch story script');
  }
  return res.data;
}

export async function regenerateStoryApi(projectId: string): Promise<StoryScript> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/regenerate-story`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<StoryScript> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate story script');
  }
  return res.data;
}

export async function getPipelineStatusApi(projectId: string): Promise<PipelineStatus> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/pipeline-status`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PipelineStatus> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch pipeline status');
  }
  return res.data;
}

// Phase 7 Storyboard APIs
export async function generateStoryboardApi(projectId: string): Promise<Storyboard> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/generate-storyboard`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Storyboard> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate storyboard');
  }
  return res.data;
}

export async function getStoryboardApi(projectId: string): Promise<Storyboard> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/storyboard`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Storyboard> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch storyboard');
  }
  return res.data;
}

export async function regenerateSceneApi(projectId: string, sceneNumber: number): Promise<Storyboard> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/storyboard/regenerate-scene/${sceneNumber}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Storyboard> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate scene storyboard');
  }
  return res.data;
}

export async function approveStoryboardApi(projectId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/storyboard/approve`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ approved: boolean }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve storyboard');
  }
  return true;
}

export async function getStoryboardStatusApi(projectId: string): Promise<{ has_storyboard: boolean; approved: boolean; scene_count: number }> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/storyboard/status`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ has_storyboard: boolean; approved: boolean; scene_count: number }> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch storyboard status');
  }
  return res.data;
}

// Phase 8 Character & Image Pipeline APIs
export async function generateCharactersApi(projectId: string): Promise<CharacterProfile[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/characters/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<CharacterProfile[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate character profiles');
  }
  return res.data;
}

export async function getCharactersApi(projectId: string): Promise<CharacterProfile[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/characters`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<CharacterProfile[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch character profiles');
  }
  return res.data;
}

export async function generateSceneImagesApi(projectId: string): Promise<GeneratedImage[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/images/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<GeneratedImage[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate scene images');
  }
  return res.data;
}

export async function listSceneImagesApi(projectId: string): Promise<GeneratedImage[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/images`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<GeneratedImage[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch scene images');
  }
  return res.data;
}

export async function regenerateSceneImageApi(projectId: string, sceneNumber: number): Promise<GeneratedImage> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/images/regenerate-scene/${sceneNumber}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<GeneratedImage> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate scene image');
  }
  return res.data;
}

export async function approveImageApi(projectId: string, imageId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/images/approve/${imageId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve image');
  }
  return true;
}

export async function rejectImageApi(projectId: string, imageId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/images/reject/${imageId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject image');
  }
  return true;
}

// Phase 9 Animation Engine APIs
export async function generateSceneAnimationsApi(projectId: string): Promise<AnimatedSceneClip[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/animations/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<AnimatedSceneClip[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate scene animations');
  }
  return res.data;
}

export async function listSceneAnimationsApi(projectId: string): Promise<AnimatedSceneClip[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/animations`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<AnimatedSceneClip[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch scene animations');
  }
  return res.data;
}

export async function regenerateSceneAnimationApi(projectId: string, sceneNumber: number): Promise<AnimatedSceneClip> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/animations/regenerate-scene/${sceneNumber}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<AnimatedSceneClip> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate scene animation');
  }
  return res.data;
}

export async function approveAnimationApi(projectId: string, animationId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/animations/approve/${animationId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve animation');
  }
  return true;
}

export async function rejectAnimationApi(projectId: string, animationId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/animations/reject/${animationId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject animation');
  }
  return true;
}

// Phase 10 Voice & Audio Pipeline APIs
export async function generateSceneVoicesApi(projectId: string): Promise<VoiceNarrationAsset[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/audio/generate-voices`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<VoiceNarrationAsset[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate voice narration');
  }
  return res.data;
}

export async function listSceneVoicesApi(projectId: string): Promise<VoiceNarrationAsset[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/audio`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<VoiceNarrationAsset[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch voice narration');
  }
  return res.data;
}

export async function regenerateSceneVoiceApi(projectId: string, sceneNumber: number): Promise<VoiceNarrationAsset> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/audio/regenerate-scene/${sceneNumber}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<VoiceNarrationAsset> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate scene voice');
  }
  return res.data;
}

export async function approveAudioApi(projectId: string, audioId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/audio/approve/${audioId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve audio');
  }
  return true;
}

export async function rejectAudioApi(projectId: string, audioId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/audio/reject/${audioId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject audio');
  }
  return true;
}

// Phase 11 Music & Audio Enhancement APIs
export async function generateSceneMusicMixesApi(projectId: string): Promise<MixedAudioTrack[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/music/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<MixedAudioTrack[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate background music and audio mix');
  }
  return res.data;
}

export async function listSceneMusicMixesApi(projectId: string): Promise<MixedAudioTrack[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/music`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<MixedAudioTrack[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch music mixes');
  }
  return res.data;
}

export async function regenerateSceneMusicApi(projectId: string, sceneNumber: number): Promise<MixedAudioTrack> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/music/regenerate-scene/${sceneNumber}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<MixedAudioTrack> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to regenerate scene music mix');
  }
  return res.data;
}

export async function approveMusicMixApi(projectId: string, mixId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/music/approve/${mixId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve audio mix');
  }
  return true;
}

export async function rejectMusicMixApi(projectId: string, mixId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/music/reject/${mixId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject audio mix');
  }
  return true;
}

// Phase 12 Video Composition & Render Engine APIs
export async function buildProjectTimelineApi(projectId: string): Promise<VideoTimeline> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/timeline/build`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<VideoTimeline> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to build video timeline');
  }
  return res.data;
}

export async function getProjectTimelineApi(projectId: string): Promise<VideoTimeline> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/timeline`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<VideoTimeline> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch video timeline');
  }
  return res.data;
}

export async function renderProjectVideoApi(projectId: string): Promise<RenderTask> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/render/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<RenderTask> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to render project video');
  }
  return res.data;
}

export async function listProjectRendersApi(projectId: string): Promise<RenderTask[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/render`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<RenderTask[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch render tasks');
  }
  return res.data;
}

export async function approveRenderApi(projectId: string, renderId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/render/approve/${renderId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve render task');
  }
  return true;
}

export async function rejectRenderApi(projectId: string, renderId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/render/reject/${renderId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject render task');
  }
  return true;
}

export async function exportProjectPackageApi(projectId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/render/export`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Record<string, unknown>> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to export project package');
  }
  return res.data;
}

// Phase 13 Publishing Assets & SEO Engine APIs
export async function generatePublishingAssetsApi(projectId: string): Promise<PublishingAssetBundle> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publishing/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingAssetBundle> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to generate publishing assets');
  }
  return res.data;
}

export async function getPublishingAssetsApi(projectId: string): Promise<PublishingAssetBundle> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publishing`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingAssetBundle> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch publishing assets');
  }
  return res.data;
}

export async function selectThumbnailVariantApi(projectId: string, variantId: string): Promise<ThumbnailVariant> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publishing/select-thumbnail/${variantId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<ThumbnailVariant> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to select thumbnail variant');
  }
  return res.data;
}

export async function approvePublishingAssetsApi(projectId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publishing/approve`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to approve publishing assets');
  }
  return true;
}

export async function rejectPublishingAssetsApi(projectId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publishing/reject`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ status: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to reject publishing assets');
  }
  return true;
}

// Phase 14 Multi-Platform Distribution APIs
export async function listConnectedAccountsApi(): Promise<ConnectedAccount[]> {
  const response = await fetch(`${API_BASE}/distribution/accounts`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<ConnectedAccount[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list connected accounts');
  }
  return res.data;
}

export async function connectAccountApi(platform: string, channelName: string): Promise<ConnectedAccount> {
  const response = await fetch(`${API_BASE}/distribution/accounts/connect`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ platform, channel_name: channelName }),
  });
  const res: APIResponse<ConnectedAccount> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to connect account');
  }
  return res.data;
}

export async function disconnectAccountApi(accountId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/distribution/accounts/${accountId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ message: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to disconnect account');
  }
  return true;
}

export async function publishNowApi(
  projectId: string,
  accountId: string,
  platform: string,
  videoUrl?: string,
  title?: string,
  description?: string,
  tags?: string[]
): Promise<PublishingQueueItem> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/publish-now`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      account_id: accountId,
      platform,
      video_url: videoUrl,
      title,
      description,
      tags
    }),
  });
  const res: APIResponse<PublishingQueueItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to publish video');
  }
  return res.data;
}

export async function schedulePublishApi(
  projectId: string,
  accountId: string,
  platform: string,
  scheduledTime: string,
  videoUrl?: string,
  title?: string,
  description?: string,
  tags?: string[]
): Promise<PublishingQueueItem> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/schedule`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      account_id: accountId,
      platform,
      scheduled_time: scheduledTime,
      video_url: videoUrl,
      title,
      description,
      tags
    }),
  });
  const res: APIResponse<PublishingQueueItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to schedule publish task');
  }
  return res.data;
}

export async function listPublishingQueueApi(projectId: string): Promise<PublishingQueueItem[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/queue`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingQueueItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch publishing queue');
  }
  return res.data;
}

export async function listPublishingHistoryApi(projectId: string): Promise<PublishingQueueItem[]> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/history`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingQueueItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch publishing history');
  }
  return res.data;
}

export async function cancelPublishTaskApi(projectId: string, queueId: string): Promise<PublishingQueueItem> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/cancel/${queueId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingQueueItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to cancel publish task');
  }
  return res.data;
}

export async function retryPublishTaskApi(projectId: string, queueId: string): Promise<PublishingQueueItem> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/distribution/retry/${queueId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PublishingQueueItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to retry publish task');
  }
  return res.data;
}

// Phase 15 SaaS Platform APIs
export async function listSubscriptionPlansApi(): Promise<SubscriptionPlan[]> {
  const response = await fetch(`${API_BASE}/saas/billing/plans`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<SubscriptionPlan[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch subscription plans');
  }
  return res.data;
}

export async function getUserSubscriptionApi(): Promise<UserSubscription> {
  const response = await fetch(`${API_BASE}/saas/billing/subscription`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<UserSubscription> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch subscription');
  }
  return res.data;
}

export async function subscribeToPlanApi(planId: string): Promise<UserSubscription> {
  const response = await fetch(`${API_BASE}/saas/billing/subscribe`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ plan_id: planId }),
  });
  const res: APIResponse<UserSubscription> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to update subscription');
  }
  return res.data;
}

export async function listWorkspacesApi(): Promise<Workspace[]> {
  const response = await fetch(`${API_BASE}/saas/workspaces`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<Workspace[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list workspaces');
  }
  return res.data;
}

export async function createWorkspaceApi(name: string, type: string = "TEAM"): Promise<Workspace> {
  const response = await fetch(`${API_BASE}/saas/workspaces`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name, type }),
  });
  const res: APIResponse<Workspace> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to create workspace');
  }
  return res.data;
}

export async function listApiKeysApi(): Promise<APIKeyItem[]> {
  const response = await fetch(`${API_BASE}/saas/api-keys`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<APIKeyItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list API keys');
  }
  return res.data;
}

export async function createApiKeyApi(name: string): Promise<APIKeyItem> {
  const response = await fetch(`${API_BASE}/saas/api-keys`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name }),
  });
  const res: APIResponse<APIKeyItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to create API key');
  }
  return res.data;
}

export async function revokeApiKeyApi(keyId: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/saas/api-keys/${keyId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<{ message: string }> = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.error?.message || 'Failed to revoke API key');
  }
  return true;
}

export async function listNotificationsApi(): Promise<NotificationItem[]> {
  const response = await fetch(`${API_BASE}/saas/notifications`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<NotificationItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch notifications');
  }
  return res.data;
}

export async function getAnalyticsSummaryApi(): Promise<AnalyticsSummary> {
  const response = await fetch(`${API_BASE}/saas/analytics/summary`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<AnalyticsSummary> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to fetch analytics summary');
  }
  return res.data;
}

// Phase 16 AI Creator Copilot APIs
export async function analyzeProjectCopilotApi(projectId: string): Promise<OptimizationReport> {
  const response = await fetch(`${API_BASE}/copilot/analyze-project/${projectId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<OptimizationReport> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to analyze project with Copilot');
  }
  return res.data;
}

export async function predictPerformanceCopilotApi(projectId: string): Promise<PerformancePrediction> {
  const response = await fetch(`${API_BASE}/copilot/predict-performance/${projectId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  const res: APIResponse<PerformancePrediction> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to predict performance with Copilot');
  }
  return res.data;
}

export async function listTrendsCopilotApi(): Promise<TrendReport[]> {
  const response = await fetch(`${API_BASE}/copilot/trends`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<TrendReport[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list trending topics');
  }
  return res.data;
}

export async function listWorkflowsCopilotApi(): Promise<WorkflowAutomationItem[]> {
  const response = await fetch(`${API_BASE}/copilot/workflows`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<WorkflowAutomationItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list workflows');
  }
  return res.data;
}

export async function createWorkflowCopilotApi(name: string, triggerEvent: string, actions: string[]): Promise<WorkflowAutomationItem> {
  const response = await fetch(`${API_BASE}/copilot/workflows`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name, trigger_event: triggerEvent, actions }),
  });
  const res: APIResponse<WorkflowAutomationItem> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to create workflow');
  }
  return res.data;
}

export async function listTemplatesCopilotApi(): Promise<ContentTemplateItem[]> {
  const response = await fetch(`${API_BASE}/copilot/templates`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<ContentTemplateItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list templates');
  }
  return res.data;
}

export async function listModelsCopilotApi(): Promise<AIModelConfigItem[]> {
  const response = await fetch(`${API_BASE}/copilot/models`, {
    headers: getAuthHeaders(),
  });
  const res: APIResponse<AIModelConfigItem[]> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to list AI models');
  }
  return res.data;
}

export async function optimizePromptCopilotApi(rawPrompt: string): Promise<{ original_prompt: string; optimized_prompt: string; quality_score: number; improvements: string[] }> {
  const response = await fetch(`${API_BASE}/copilot/optimize-prompt`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ raw_prompt: rawPrompt }),
  });
  const res: APIResponse<{ original_prompt: string; optimized_prompt: string; quality_score: number; improvements: string[] }> = await response.json();
  if (!response.ok || !res.success || !res.data) {
    throw new Error(res.error?.message || 'Failed to optimize prompt');
  }
  return res.data;
}

// Backward Compatibility Aliases
export const createProject = createProjectApi;
export const getProject = getProjectApi;
export async function listProjects(): Promise<Project[]> {
  const paginated = await listProjectsApi();
  return paginated.items;
}
