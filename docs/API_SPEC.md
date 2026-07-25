# API Specification — KidsAI Studio v2.0

Base URL: `/api/v1`

## Endpoints Summary

### Authentication (`/auth`)
- `POST /auth/register` — User registration
- `POST /auth/login` — Email/password login
- `POST /auth/forgot-password` — Password reset request
- `GET /auth/me` — Current user profile

### User Management (`/users`)
- `PUT /users/profile` — Update user profile

### Project Management (`/projects`)
- `POST /projects` — Create project draft
- `GET /projects` — List, search (`q`), filter (`status`, `is_favorite`, `is_archived`), sort (`newest`, `title`), paginate
- `GET /projects/{id}` — Fetch single project
- `PUT /projects/{id}` — Update project / Auto-save
- `DELETE /projects/{id}` — Delete project
- `POST /projects/{id}/duplicate` — Duplicate project
- `POST /projects/{id}/archive` — Archive project
- `POST /projects/{id}/restore` — Restore archived project
- `POST /projects/{id}/favorite` — Toggle favorite status

### Phase 6 AI Director & Story Pipeline
- `POST /projects/{id}/generate-plan` — Director Agent creates Production Plan JSON (State: `PLANNING`)
- `POST /projects/{id}/generate-story` — Story Agent creates Story Script JSON (State: `STORY_READY`)
- `GET /projects/{id}/plan` — Retrieve stored Production Plan JSON
- `GET /projects/{id}/story` — Retrieve stored Story Script JSON
- `POST /projects/{id}/regenerate-story` — Regenerate Story Script
- `GET /projects/{id}/pipeline-status` — Retrieve AI pipeline execution stage & status

### Phase 7 Storyboard Agent Pipeline
- `POST /projects/{id}/generate-storyboard` — Storyboard Agent generates shot-by-shot visual & camera plan (State: `STORYBOARD_READY`)
- `GET /projects/{id}/storyboard` — Retrieve stored Storyboard JSON
- `POST /projects/{id}/storyboard/regenerate-scene/{scene_number}` — Regenerate single scene in Storyboard
- `PUT /projects/{id}/storyboard/scenes/{scene_number}` — Manually update scene storyboard metadata
- `POST /projects/{id}/storyboard/approve` — Approve Storyboard & lock version
- `GET /projects/{id}/storyboard/status` — Get Storyboard completion and approval status

### Phase 8 Character Memory Engine & Image Generation Pipeline
- `POST /projects/{id}/characters/generate` — Generate permanent character memory profiles & anchor prompts
- `GET /projects/{id}/characters` — Retrieve character memory roster
- `PUT /projects/{id}/characters/{char_id}` — Update character profile details
- `POST /projects/{id}/images/generate` — Render scene images using prompt composer & FLUX adapter (State: `IMAGES_READY`)
- `POST /projects/{id}/images/regenerate-scene/{scene_number}` — Regenerate single scene image
- `POST /projects/{id}/images/approve/{image_id}` — Approve scene image
- `POST /projects/{id}/images/reject/{image_id}` — Reject scene image
- `GET /projects/{id}/images` — List project scene images
- `GET /projects/{id}/images/status` — Get image generation pipeline status

### Phase 9 Animation Engine & Motion Generation Pipeline
- `POST /projects/{id}/animations/generate` — Motion Planner & Wan 2.2 Adapter render 3D video clips (State: `ANIMATION_READY`)
- `POST /projects/{id}/animations/regenerate-scene/{scene_number}` — Regenerate single scene animation clip
- `POST /projects/{id}/animations/approve/{animation_id}` — Approve animation clip
- `POST /projects/{id}/animations/reject/{animation_id}` — Reject animation clip
- `GET /projects/{id}/animations` — List project animated video clips
- `GET /projects/{id}/animations/status` — Get animation pipeline status

### Phase 10 Voice Generation, Dialogue, Lip Sync & Audio Pipeline
- `POST /projects/{id}/audio/generate-voices` — Dialogue Planner & Kokoro TTS render narration audio clips & Lip Sync visemes (State: `VOICE_READY`)
- `POST /projects/{id}/audio/regenerate-scene/{scene_number}` — Regenerate single scene audio clip
- `POST /projects/{id}/audio/approve/{audio_id}` — Approve narration audio clip
- `POST /projects/{id}/audio/reject/{audio_id}` — Reject narration audio clip
- `GET /projects/{id}/audio` — List project audio narration clips
- `GET /projects/{id}/audio/status` — Get voice pipeline status

### Phase 11 Music Generation, Sound Effects & Audio Mixing Pipeline
- `POST /projects/{id}/music/generate` — Music Planner, SFX, Ambient & Audio Mixer master multi-track audio (State: `MUSIC_READY`)
- `POST /projects/{id}/music/regenerate-scene/{scene_number}` — Regenerate single scene audio mix
- `POST /projects/{id}/music/approve/{mix_id}` — Approve mixed audio track
- `POST /projects/{id}/music/reject/{mix_id}` — Reject mixed audio track
- `GET /projects/{id}/music` — List project mixed audio tracks
- `GET /projects/{id}/music/status` — Get music pipeline status

### Phase 12 Video Composition & Rendering Engine
- `POST /projects/{id}/timeline/build` — Timeline Builder compiles master video timeline JSON
- `GET /projects/{id}/timeline` — Retrieve stored video timeline
- `POST /projects/{id}/render/generate` — FFmpeg Render Service compiles MP4 video (State: `RENDERING` -> `COMPLETED`)
- `POST /projects/{id}/render/approve/{render_id}` — Approve render task
- `POST /projects/{id}/render/reject/{render_id}` — Reject render task
- `GET /projects/{id}/render` — List render tasks for project
- `GET /projects/{id}/render/export` — Download MP4 & export metadata package JSON
- `GET /projects/{id}/render/status` — Get render pipeline status

### Phase 13 Thumbnail Generation, SEO Optimization & Publishing Assets
- `POST /projects/{id}/publishing/generate` — Thumbnail Planner & SEO Agent generate 4 thumbnail variants A/B/C/D and YouTube Kids SEO package (State: `PUBLISHED`)
- `GET /projects/{id}/publishing` — Retrieve stored publishing asset bundle
- `POST /projects/{id}/publishing/select-thumbnail/{variant_id}` — Select preferred thumbnail variant
- `POST /projects/{id}/publishing/approve` — Approve publishing asset package
- `POST /projects/{id}/publishing/reject` — Reject publishing asset package
- `GET /projects/{id}/publishing/status` — Get publishing asset status

### Phase 14 Multi-Platform Distribution & Scheduling Engine
- `GET /distribution/accounts` — List connected social media channels (YouTube, TikTok, Reels)
- `POST /distribution/accounts/connect` — Connect new social media account
- `DELETE /distribution/accounts/{account_id}` — Disconnect social media account
- `POST /projects/{id}/distribution/publish-now` — Dispatch immediate multi-platform upload
- `POST /projects/{id}/distribution/schedule` — Schedule multi-platform video release
- `GET /projects/{id}/distribution/queue` — List publishing queue & status
- `GET /projects/{id}/distribution/history` — List distribution history
- `POST /projects/{id}/distribution/cancel/{queue_id}` — Cancel queue item
- `POST /projects/{id}/distribution/retry/{queue_id}` — Retry failed distribution task
- `GET /projects/{id}/distribution/status` — Get distribution pipeline status

### Phase 15 SaaS Platform, Billing, Workspaces, API Keys & Analytics
- `GET /saas/billing/plans` — List subscription plans
- `GET /saas/billing/subscription` — Get current user subscription
- `POST /saas/billing/subscribe` — Upgrade subscription plan
- `GET /saas/workspaces` — List team workspaces
- `POST /saas/workspaces` — Create new workspace
- `GET /saas/api-keys` — List developer API keys
- `POST /saas/api-keys` — Generate new API key
- `DELETE /saas/api-keys/{key_id}` — Revoke API key
- `GET /saas/notifications` — List user notifications
- `GET /saas/analytics/summary` — Fetch platform analytics summary

### Phase 16 AI Creator Copilot, Trend Intelligence & Performance Predictor
- `POST /copilot/analyze-project/{project_id}` — Perform complete copilot quality & pacing audit
- `POST /copilot/predict-performance/{project_id}` — Predict CTR, audience retention, and publishing risk
- `GET /copilot/trends` — Fetch trending educational topics and search volume scores
- `GET /copilot/workflows` & `POST /copilot/workflows` — Manage trigger-action workflow automations
- `GET /copilot/templates` & `POST /copilot/templates` — Template marketplace for reusable story & thumbnail presets
- `GET /copilot/models` & `PUT /copilot/models/{model_id}` — AI Model roster & provider status management
- `POST /copilot/optimize-prompt` — Enhance raw prompts with 3D Pixar render tokens
