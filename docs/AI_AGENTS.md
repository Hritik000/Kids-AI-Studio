# AI Agents Architecture & Specification — KidsAI Studio v2.0

## Agent Roster & Responsibilities

| Agent Name | Primary Responsibility | Input Artifact | Output Artifact |
| :--- | :--- | :--- | :--- |
| **Director Agent** | Orchestrates all sub-agents & generates Production Plan JSON | User Prompt & Parameters | Production Plan JSON |
| **Story Agent** | Generates original, educational kids script & scene breakdown | Production Plan JSON | Story Script JSON |
| **Storyboard Agent**| Converts story script into shot-by-shot visual, camera & continuity plan | Story Script JSON | Storyboard JSON |
| **Character Consistency Agent** | Builds permanent character profiles & visual anchor prompts | Story / Storyboard JSON | Character Profiles Roster |
| **Visual Artist Agent**| Renders 3D Pixar/Disney style scene images | Composed Prompts | Generated Scene Images |
| **Animation Agent** | Generates 3D animated video clips with camera & character motion | Scene Images & Motion Plan | Animated Video Clips |
| **Voice Agent** | Synthesizes child-friendly narration speech & lip sync visemes | Story Narration Text | Voice Audio & Viseme Timelines |
| **Music & Audio Enhancement Agent**| Composes background music, sound effects, ambience & masters audio mix | Storyboard & Voice Narration | Mastered Multi-Track Audio Mix |
| **Render Agent** | Stitches animations, audio tracks, and transitions into final MP4 | Approved Assets Bundle | Final Video MP4 & Export Package |
| **SEO & Publishing Agent**| Generates thumbnail variants (A/B/C/D), scored titles, descriptions & COPPA metadata | Approved Render & Storyboard | Publishing Assets & SEO Package |
| **Distribution Agent**| Dispatches videos to YouTube, Shorts, TikTok & Reels using modular platform adapters | Approved Video & Publishing Bundle | Live Post URLs & Queue Logs |
| **AI Creator Copilot Agent**| Evaluates project quality, predicts CTR/retention, discovers trends & optimizes prompts | Project State & Market Trends | Optimization Report & Predictions |
| **Quality Checker Agent** | Verifies all assets pass safety & completeness checks | Final Project Bundle | Pass/Fail Audit |

## Inter-Agent Communication Rule
No agent communicates directly with another agent unless coordinated by the **Director Agent**.

## AI Creator Copilot & Autonomous Optimization Sequence Diagram

```
[ Active Project & User Inputs ]
               │
               │ POST /copilot/analyze-project/{id}
               ▼
[ Creator Copilot Service ]
               │
               ├─► Audit Narrative Flow & Pacing (4.5s threshold)
               ├─► Evaluate Visual Contrast & Character Consistency
               │
               ▼
[ Prediction Service ]
               │
               ├─► Predict CTR (e.g. 13.8%)
               ├─► Forecast Retention (e.g. 82.4%) & Watch Time
               │
               ▼
[ Trend Intelligence Service ] ──► Inject High-Opportunity Keywords & Topics
               │
               ▼
[ Optimization Report & Performance Forecast ]
```
