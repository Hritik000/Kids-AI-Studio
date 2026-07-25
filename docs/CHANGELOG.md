# Changelog — KidsAI Studio

All notable changes to KidsAI Studio are documented in this file.

## [2.0.0] - 2026-07-25

### Added
- **Monorepo Foundation**: Created `/packages/prompts`, `/packages/types`, `/packages/shared`, `/packages/ui`, `/packages/sdk`, `/infrastructure`, `/docs`, `/scripts`.
- **Director Agent Pipeline**: Implemented 12-stage state machine from `DRAFT` to `COMPLETED`.
- **Swappable AI Adapters**: Introduced `LLMAdapter`, `ImageAdapter`, and `TTSAdapter`.
- **Quality Checker Service**: Automated verification step before video project completion.
- **Apple-Inspired Dark UI**: Updated Next.js 15 dashboard with live pipeline state badges, scene cards, audio track indicators, and MP4 video download.
- **Comprehensive Documentation**: Added complete architectural blueprints, database schema, API specs, prompt libraries, and coding standards in `/docs`.
