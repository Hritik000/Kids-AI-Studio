# Architecture Documentation — KidsAI Studio v2.0

## System Overview

KidsAI Studio is engineered as an autonomous, multi-agent AI video generator. The architecture is modular, decoupled via adapter layers, and orchestrated by a central Director Agent.

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js 15 Web Dashboard                  │
│                (Zustand State + TanStack Query)             │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend Orchestrator                │
│                     (Director Agent Core)                   │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ LLM Adapter  │        │ Image Adapter│        │ TTS Adapter  │
│ (OpenAI/     │        │ (Replicate/  │        │ (EdgeTTS/    │
│  Gemini)     │        │  Flux/Mock)  │        │  ElevenLabs) │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │   FFmpeg Composite Engine    │
                │     (MP4 Audio/Video Sync)   │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │  Automated Quality Checker   │
                │  (Sanity & Asset Verification│
                └──────────────────────────────┘
```

## Core Architectural Principles

1. **Provider Decoupling via Adapters**: Business logic never calls AI providers directly. All calls go through provider interfaces (`llm_adapter`, `image_adapter`, `tts_adapter`).
2. **Strict Project State Machine**: Projects transition immutably through 12 predefined states (`DRAFT` -> `PLANNING` -> ... -> `COMPLETED`).
3. **Externalized Prompt Library**: All prompt templates are stored in `/packages/prompts/*.md` rather than hardcoded in Python code.
4. **Standardized API Envelope**: All API endpoints return `{ success: bool, data: T, error: APIError }`.
