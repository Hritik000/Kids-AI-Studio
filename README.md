# KidsAI Studio (v2.0)

> **Autonomous Multi-Agent AI Video Studio & Multi-Platform SaaS for Kids Educational Content**

KidsAI Studio is an end-to-end autonomous AI video production platform. From a single prompt, it plans, scripts, visualizes, animates, narrates, composes music, renders, optimizes SEO, and publishes 3D Pixar-style educational videos across YouTube, TikTok, and Instagram Reels.

---

## ✨ Features

- 🎯 **Director & Story Agent Pipeline**: Generates structured Production Plans & Educational Scripts.
- 🎨 **Storyboard & Character Memory Engine**: Shot-by-shot camera planning & visual character consistency across all scenes.
- 🖼️ **FLUX 3D Visual Artist**: Renders high-quality 3D Pixar/Disney style scene images.
- 🎬 **Wan 2.2 Animation Engine**: Generates smooth 3D animated video clips with custom motion paths.
- 🎙️ **Kokoro TTS & Lip-Sync Visemes**: Child-friendly voice narration synchronized with mouth viseme markers.
- 🎵 **Audio Mixing & Mastering**: Background music ducking (-12dB speech ducking, -14.0 LUFS mastering) & sound effects.
- 🎞️ **FFmpeg Video Render Engine**: Composes animations, multi-track audio, and cross-fade transitions into 1080p MP4.
- 🏷️ **SEO & Thumbnail Engine**: Generates Version A/B/C/D CTR-optimized thumbnail variants and COPPA-compliant SEO metadata.
- 🌐 **Multi-Platform Distribution**: Platform adapters for YouTube, YouTube Shorts, TikTok, and Instagram Reels with scheduling and upload queues.
- 💳 **SaaS Platform & Credit Billing**: Subscription plans (Free, Starter, Creator, Pro), credit tracking, team workspaces, and developer API key management.
- 🤖 **AI Creator Copilot & Performance Predictor**: Automated optimization score (0-100), CTR forecasting, trend intelligence, and workflow automations.

---

## 📁 Monorepo Structure

```
kidsAI/
├── apps/
│   ├── frontend/         # Next.js 16 App Router (TypeScript, Tailwind, Lucide React)
│   └── backend/          # FastAPI Backend (Python 3.14, Pydantic, Pytest, Uvicorn)
├── packages/             # Shared Monorepo Packages
│   ├── ui/               # Reusable UI Tokens & Theme
│   ├── shared/           # Shared Constants & Utilities
│   └── prompts/          # External Prompt Templates (thumbnail.md, seo.md, title.md, etc.)
├── docs/                 # Product Specifications & Phase Architecture Documentation
│   ├── UI_UX_BLUEPRINT.md
│   ├── ARCHITECTURE.md
│   ├── AI_AGENTS.md
│   ├── API_SPEC.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   └── ROADMAP.md
├── docker-compose.yml    # Production Multi-Container Orchestration
├── CHANGELOG.md          # Release Changelog
├── LICENSE               # MIT License
├── .env.example          # Environment Variables Template
└── README.md
```

---

## 🛠️ Tech Stack

### Frontend (`apps/frontend`)
- **Framework**: Next.js 16 (App Router), React 19, TypeScript
- **Styling**: Vanilla CSS / Tailwind Tokens, Lucide Icons
- **State & Data**: React Custom Hooks, LocalStorage Auth Context

### Backend (`apps/backend`)
- **Framework**: FastAPI 0.115+, Python 3.11+, Pydantic v2
- **Audio & Media**: FFmpeg, Pytest Test Suite
- **Auth & Database**: Supabase Auth, PostgreSQL / In-Memory Mock Store

---

## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/kidsai-studio.git
cd kidsai-studio

# Setup environment variables
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env.local
```

### 2. Development Setup

#### Backend (`http://localhost:8000`)
```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend (`http://localhost:3000`)
```bash
cd apps/frontend
npm install
npm run dev
```

### 3. Running with Docker Compose
```bash
docker-compose up --build
```

---

## 🧪 Verification & Testing

### Run Backend Unit & Integration Tests
```bash
cd apps/backend
source .venv/bin/activate
PYTHONPATH=. pytest
```

### Run Frontend Production Build
```bash
cd apps/frontend
npm run build
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
