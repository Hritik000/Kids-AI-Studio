# Changelog

All notable changes to KidsAI Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-07-25 (Initial Release & First Commit)

### Added
- **Phase 1: Product Design & UI/UX Planning**: Architecture blueprints & design token specification (`docs/UI_UX_BLUEPRINT.md`).
- **Phase 2: Project Foundation & Monorepo Setup**: Next.js 16 + FastAPI 0.115 + Turbo monorepo workspace.
- **Phase 3: Design System & Tokens**: Reusable Tailwind/CSS component tokens and sleek dark theme.
- **Phase 4: Authentication & User Management**: Supabase Auth integration with Bearer JWT tokens, role management, and protected routes.
- **Phase 5: Dashboard & Project Management**: Project CRUD, search, status filtering, auto-save, duplicate, archive, and favorite capabilities.
- **Phase 6: Director Agent & Story Pipeline**: AI Director Agent orchestrator generating structured Production Plan JSON & Story Script JSON.
- **Phase 7: Storyboard Agent & Scene Planning**: Shot-by-shot visual, camera, motion, and continuity planner.
- **Phase 8: Character Memory Engine & Image Generation Pipeline**: Permanent character roster with visual memory & FLUX 3D Pixar adapter.
- **Phase 9: Animation Engine & Motion Generation Pipeline**: Motion Planner & Wan 2.2 14B Video Adapter for 3D clip rendering.
- **Phase 10: Voice Generation, Dialogue, Lip Sync & Audio Pipeline**: Dialogue Planner, Kokoro 82M TTS adapter, and lip-sync viseme generation.
- **Phase 11: Music Generation, Sound Effects & Audio Mixing Pipeline**: Stable Audio adapter, background music ducking, and -14.0 LUFS audio mastering.
- **Phase 12: Video Composition, Rendering & Export Engine**: Timeline Builder & FFmpeg H.264 MP4 rendering engine.
- **Phase 13: Thumbnail Generation, SEO Optimization & Publishing Assets Engine**: Version A/B/C/D thumbnail generator & YouTube Kids COPPA SEO package.
- **Phase 14: Multi-Platform Publishing, Scheduling & Distribution Engine**: Platform Adapters for YouTube, Shorts, TikTok, Reels, and publishing queue manager.
- **Phase 15: SaaS Platform, Billing, Workspaces, API Keys & Production Readiness**: Subscription billing, credit pool, team workspaces, developer API key management, analytics dashboard, and Docker Compose orchestration.
- **Phase 16: AI Creator Copilot, Trend Intelligence & Autonomous Optimization**: Optimization Score (0-100), CTR predictor, trend engine, workflow automations, and model manager.

### Security
- Verified zero committed secrets, keys, or passwords across repository code.
- Added strict `.env.example` templates and comprehensive `.gitignore`.
