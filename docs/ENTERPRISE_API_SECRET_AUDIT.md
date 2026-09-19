# Enterprise API, Secrets & Infrastructure Audit

**Platform**: KidsAI Studio v2.0  
**Date**: 2026-07-30  
**Scope**: Whole Repository (`apps/`, `packages/`, `docker/`, `docs/`, `config/`, `.env.example`)  
**Target Architecture**: Scalable, Multi-Tenant Cloud & Edge Hybrid Infrastructure for High-Throughput Video Generation

---

## 1. Executive Summary

This document provides a complete, evidence-based audit of every API key, environment variable, cloud service, credential, OAuth application, and third-party integration required to operate KidsAI Studio v2.0 at enterprise production scale.

The platform employs a **Provider Abstraction Layer** across all AI sub-systems (LLM, Image, Animation, TTS, Music). This design allows the application to run:
1. **Fully Offline in Development/Testing Mode**: Zero cloud API keys required (uses mock providers returning valid structured JSON, vector visemes, and static media buffers).
2. **Hybrid Cloud Mode**: Selectively replacing individual providers with live cloud APIs via environment variables.
3. **Enterprise Production Scale Mode**: Fully wired to high-concurrency external AI inference APIs, object storage, managed database backends, OAuth authentication, and payment gateways.

---

## 2. Complete Environment Variable Inventory

Below is the definitive matrix of every environment variable scanned across `apps/backend/app/core/`, `apps/frontend/src/`, `docker-compose.yml`, and `.env.example`.

| Variable Name | Category | Used In (File & Function) | Mandatory (Prod) | Mandatory (Dev) | Default Value / Fallback | Purpose & Functionality |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `SECRET_KEY` | Security | `apps/backend/app/core/security.py:create_access_token` | ✅ **Yes** | ❌ No | `"your_secure_jwt_secret_key_here"` | Secret key used to sign and verify HMAC-SHA256 JWT tokens. |
| `API_V1_STR` | Routing | `apps/backend/app/core/config.py` & `main.py` | ✅ **Yes** | ✅ **Yes** | `"/api/v1"` | Global REST API route prefix. |
| `PROJECT_NAME` | Metadata | `apps/backend/app/core/config.py:Settings` | ❌ Optional | ❌ Optional | `"KidsAI Studio API"` | System identifier string returned in health & metrics checks. |
| `ENV` / `NODE_ENV` | Environment | `apps/backend/app/core/config.py` | ❌ Optional | ❌ Optional | `"development"` | Controls logging verbosity and error trace rendering. |
| `NEXT_PUBLIC_API_URL` | Frontend | `apps/frontend/src/lib/api.ts:API_BASE` | ✅ **Yes** | ✅ **Yes** | `"http://localhost:8000/api/v1"` | Public backend REST API base URL consumed by Next.js client. |
| `SUPABASE_URL` | Auth & DB | `apps/backend/app/core/config.py` & `security.py` | ✅ **Yes** | ❌ No | `""` | Supabase Cloud project HTTPS endpoint. |
| `SUPABASE_ANON_KEY` | Frontend Auth | `apps/frontend/.env.local` | ✅ **Yes** | ❌ No | `""` | Supabase anonymous public client key for browser auth state. |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin Auth | `apps/backend/app/core/security.py` | ✅ **Yes** | ❌ No | `""` | Supabase service-role admin key for server-side token validation. |
| `KIMI_API_KEY` | AI LLM | `apps/backend/app/core/llm.py:KimiLLMProvider` | ⚡ Conditional | ❌ No | `""` | API key for Moonshot Kimi LLM (`https://api.moonshot.cn/v1/chat/completions`). |
| `OPENAI_API_KEY` | AI LLM | `apps/backend/app/core/adapters/llm_adapter.py` | ⚡ Conditional | ❌ No | `""` | API key for OpenAI GPT-4o / GPT-4o-mini completion endpoints. |
| `REPLICATE_API_KEY` | AI Media | `apps/backend/app/core/image_provider.py` & `animation_provider.py` | ⚡ Conditional | ❌ No | `""` | API token for Replicate FLUX-schnell & Wan 2.1 Video generation APIs. |
| `FLUX_API_KEY` | AI Image | `apps/backend/app/core/config.py:IMAGE_API_KEY` | ⚡ Conditional | ❌ No | `""` | Alias/Direct API token for dedicated FLUX image inference endpoints. |
| `WAN_API_KEY` | AI Video | `apps/backend/app/core/config.py` | ⚡ Conditional | ❌ No | `""` | Direct API key for Wan 2.1 video generation API. |
| `ELEVENLABS_API_KEY` | AI Voice | `apps/backend/app/core/voice_provider.py:KokoroTTSProvider` | ⚡ Conditional | ❌ No | `""` | API key for ElevenLabs Text-to-Speech API (`api.elevenlabs.io`). |
| `KOKORO_API_KEY` / `TTS_API_KEY` | AI Voice | `apps/backend/app/core/config.py:TTS_API_KEY` | ⚡ Conditional | ❌ No | `""` | Direct key for dedicated Kokoro-82M TTS endpoints. |
| `STABLE_AUDIO_API_KEY` | AI Music | `apps/backend/app/core/music_provider.py:StableAudioProvider` | ⚡ Conditional | ❌ No | `""` | API key for Stability AI Stable Audio API (`api.stability.ai`). |
| `DATABASE_URL` | Database | `apps/backend/app/core/db.py` | ✅ **Yes** | ❌ No | `""` (Uses in-memory `_db`) | PostgreSQL connection string (`postgresql://user:pass@host:5432/db`). |
| `R2_BUCKET` | Storage | `.env.example` | ⚡ Conditional | ❌ No | `""` | Cloudflare R2 bucket name for rendered media assets. |
| `R2_ACCESS_KEY_ID` | Storage | `.env.example` | ⚡ Conditional | ❌ No | `""` | Cloudflare R2 S3-compatible Access Key ID. |
| `R2_SECRET_ACCESS_KEY` | Storage | `.env.example` | ⚡ Conditional | ❌ No | `""` | Cloudflare R2 S3-compatible Secret Access Key. |
| `R2_ENDPOINT_URL` | Storage | `.env.example` | ⚡ Conditional | ❌ No | `""` | Cloudflare R2 S3 S3 endpoint URL (`https://<account_id>.r2.cloudflarestorage.com`). |
| `STRIPE_SECRET_KEY` | Billing | `apps/backend/app/services/billing_service.py` | ⚡ Conditional | ❌ No | `""` | Stripe API Secret Key (`sk_live_...`) for payment processing & subscriptions. |
| `STRIPE_WEBHOOK_SECRET` | Billing | `apps/backend/app/services/billing_service.py` | ⚡ Conditional | ❌ No | `""` | Stripe Webhook Signing Secret (`whsec_...`) for async payment notifications. |
| `REDIS_URL` | Queue & Cache | `.env.example` | ⚡ Conditional | ❌ No | `"redis://localhost:6379/0"` | Redis broker connection URI for Celery background tasks & rate limiting. |

---

## 3. External AI Provider & SDK Specifications

Below is the complete analysis of external AI model provider integrations implemented in code:

### 1. Large Language Models (LLM)
- **Primary Integration**: Moonshot AI (Kimi LLM)
  - **Endpoint**: `https://api.moonshot.cn/v1/chat/completions`
  - **Model**: `moonshot-v1-8k`
  - **Auth Header**: `Authorization: Bearer <KIMI_API_KEY>`
  - **Code File**: `apps/backend/app/core/llm.py` (L386-L418)
- **Secondary Integration**: OpenAI API
  - **Endpoint**: `https://api.openai.com/v1/chat/completions`
  - **Model**: `gpt-4o-mini` / `gpt-4o`
  - **Auth Header**: `Authorization: Bearer <OPENAI_API_KEY>`
  - **Code File**: `apps/backend/app/core/adapters/llm_adapter.py` (L45-L84)
- **Fallback**: `MockLLMProvider` returning pre-parsed kid-friendly JSON structures.

### 2. 3D Scene Image Generation
- **Primary Integration**: Black Forest Labs FLUX-schnell via Replicate API
  - **Endpoint**: `https://api.replicate.com/v1/predictions`
  - **Model Version**: `black-forest-labs/flux-schnell`
  - **Auth Header**: `Authorization: Token <REPLICATE_API_KEY>`
  - **Code File**: `apps/backend/app/core/image_provider.py` (L42-L87)
- **Fallback**: `MockImageProvider` returning high-resolution placeholder images (`placehold.co`).

### 3. Video Animation Clips
- **Primary Integration**: Wan Video (Wan 2.1 1.3B) via Replicate API
  - **Endpoint**: `https://api.replicate.com/v1/predictions`
  - **Model Version**: `wan-video/wan-2.1-1.3b`
  - **Auth Header**: `Authorization: Token <REPLICATE_API_KEY>`
  - **Code File**: `apps/backend/app/core/animation_provider.py` (L45-L92)
- **Fallback**: `MockAnimationProvider` returning Google Cloud high-resolution sample MP4 streams.

### 4. Voice Narration & Speech Synthesis
- **Primary Integration**: ElevenLabs Multilingual TTS API
  - **Endpoint**: `https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM`
  - **Model**: `eleven_multilingual_v2`
  - **Auth Header**: `xi-api-key: <ELEVENLABS_API_KEY>`
  - **Code File**: `apps/backend/app/core/voice_provider.py` (L36-L73)
- **Fallback**: `MockVoiceProvider` returning pre-synthesized audio streams.

### 5. Background Music & Soundscapes
- **Primary Integration**: Stability AI (Stable Audio Open API)
  - **Endpoint**: `https://api.stability.ai/v2beta/stable-image/generate/core`
  - **Auth Header**: `Authorization: Bearer <STABLE_AUDIO_API_KEY>`
  - **Code File**: `apps/backend/app/core/music_provider.py` (L32-L68)
- **Fallback**: `MockMusicProvider` returning audio samples.

---

## 4. OAuth Application Requirements (Multi-Platform Publishing)

To operate the Multi-Platform Distribution Engine (`apps/backend/app/api/v1/distribution.py` and `app/core/platform_adapters.py`) in live production mode, the following social media developer accounts and OAuth 2.0 applications must be registered:

1. **Google Cloud Platform (YouTube Data API v3)**:
   - **Scopes Required**: `https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube.readonly`
   - **Redirect URI**: `https://api.kidsaistudio.com/api/v1/distribution/oauth/youtube/callback`
   - **Credentials Needed**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

2. **TikTok Developer Portal (TikTok Content Posting API)**:
   - **Scopes Required**: `video.upload`, `user.info.basic`
   - **Redirect URI**: `https://api.kidsaistudio.com/api/v1/distribution/oauth/tiktok/callback`
   - **Credentials Needed**: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`

3. **Meta for Developers (Instagram Graph API & Facebook Content API)**:
   - **Scopes Required**: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
   - **Redirect URI**: `https://api.kidsaistudio.com/api/v1/distribution/oauth/meta/callback`
   - **Credentials Needed**: `META_APP_ID`, `META_APP_SECRET`

---

## 5. Local Execution Capabilities vs. Cloud API Modules

The table below outlines which system modules can be executed **100% locally on self-hosted infrastructure** vs. modules that require external cloud APIs:

| Module | Local Self-Hosted Support | Required Local Tooling / Models | Cloud API Alternative |
| :--- | :---: | :--- | :--- |
| **Director & Story Generation** | ✅ Supported | Local Ollama / vLLM (Llama 3 / Qwen 2.5) | Moonshot Kimi API / OpenAI GPT-4o |
| **Viseme Lip-Sync Generation** | ✅ Native | Built-in Python Algorithmic Engine (`app/services/lip_sync.py`) | None needed (Runs 100% locally) |
| **Audio Mixing & Mastering** | ✅ Native | Built-in Python DSP Engine (`app/services/music_service.py`) | None needed (Runs 100% locally) |
| **Thumbnail & SEO Generator** | ✅ Native | Built-in Python Engine (`app/services/seo_agent.py`) | None needed (Runs 100% locally) |
| **Video Compilation (FFmpeg)** | ✅ Native | Local `ffmpeg` CLI binary (`app/services/ffmpeg_service.py`) | Cloud video rendering services |
| **3D Scene Image Rendering** | ⚡ Optional | Local ComfyUI / Stable Diffusion / FLUX-schnell weights | Replicate FLUX API |
| **Motion Video Generation** | ⚡ Optional | Local ComfyUI Wan 2.1 / Hunyuan Video checkpoints | Replicate Wan 2.1 Video API |
| **Voice Narration (TTS)** | ⚡ Optional | Local Kokoro-82M ONNX model / Piper TTS | ElevenLabs TTS API |
| **Background Music** | ⚡ Optional | Local MusicGen PyTorch weights | Stability AI Stable Audio API |

---

## 6. Recommended Production Infrastructure Setup

For an enterprise deployment serving thousands of creators, the following infrastructure stack is recommended:

```
[ Cloudflare DNS & DDoS Protection / CDN ]
                   │
                   ▼
[ Next.js Frontend (Vercel / AWS Amplify / Kubernetes Node) ]
                   │
                   ▼
[ FastAPI Backend Instances (AWS ECS / GCP Cloud Run / K8s) ]
       │            │            │            │
       ▼            ▼            ▼            ▼
[ Managed Postgres ] [ Managed Redis ] [ S3 / R2 Media Storage ] [ External AI APIs ]
 (Supabase / RDS)     (ElastiCache)     (Cloudflare R2)           (Replicate / Kimi)
```

1. **Database**: Managed PostgreSQL (Supabase / AWS RDS PostgreSQL) with `DATABASE_URL`.
2. **Cache & Broker**: Managed Redis (AWS ElastiCache / Redis Enterprise) with `REDIS_URL`.
3. **Media Storage**: Cloudflare R2 / AWS S3 for zero-egress cost hosting of generated 1080p MP4 videos, scene images, and audio files.
4. **Secrets Management**: AWS Secrets Manager / HashiCorp Vault / Infisical to securely inject API keys at runtime without committing credentials to source control.
