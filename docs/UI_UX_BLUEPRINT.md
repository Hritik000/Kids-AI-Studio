# KidsAI Studio — Phase 1: Product Design & UI/UX Master Blueprint
**Version**: 2.0  
**Authors**: Senior Product Designer, Lead UX Researcher, Product Manager, UI Architect  
**Design Philosophy**: Apple-inspired, Linear/Vercel precision, dark-mode first, minimal, responsive, accessible, high-performance SaaS.

---

# SECTION 1: DETAILED SCREEN DESIGN SPECIFICATIONS

---

## 1. Landing Page

### 1. Purpose of the Screen
Introduce KidsAI Studio to prospective creators, educators, and studio owners, positioning it as the premier autonomous AI platform for generating original, monetizable, YouTube Kids compliant videos. Convert anonymous traffic into registered free-tier/trial users.

### 2. User Goal
Understand what KidsAI Studio does within 5 seconds of landing, witness proof of video output quality, see pricing/tiers, and sign up.

### 3. Main Components
- **Global Header**: Logo, Nav links (Features, How it Works, Showcase, Pricing, FAQ), Sign In button, "Start Creating Free" CTA button.
- **Hero Banner**: High-impact value proposition title, dynamic subhead, primary CTA button, "No credit card required" pill, backdrop animated video teaser frame.
- **Interactive Product Demo Preview**: Embedded video player previewing sample videos (e.g., "Dinosaurs Learn Colors"), scene breakdown toggle, prompt playground preview.
- **Value Proposition Grid (6 Key Features)**: 100% Original Content, Copyright-Safe Guarantee, Character Memory, Multi-Voice Narration, Automated SEO & Thumbnail, 4K MP4 Export.
- **4-Step Visual Workflow**: 1. Prompt → 2. Storyboard → 3. AI Generation → 4. YouTube Ready.
- **Social Proof & Testimonial Carousel**: Creator metrics ($/month earned, subscribers gained, hours saved), video reviews, trust badges.
- **Tiered Pricing Cards**: Free Tier, Creator Tier, Studio Tier (Monthly/Annual toggle).
- **Interactive FAQ Accordion**: Common questions on copyright, monetization, generation time, Youtube Kids safety filters.
- **Footer**: Brand mark, Navigation column matrix (Product, Resources, Legal, Social), System Status indicator, Copyright notice.

### 4. Layout Description
- **Structure**: Single-column vertical scroll with fixed glassmorphic top navigation bar (`backdrop-blur-md bg-black/40 border-b border-white/10`).
- **Hero Layout**: Centered alignment with 120px top padding. Ambient background radial gradients (deep violet `#7C3AED` to cyan `#06B6D4` muted glow).
- **Grid Layout**: 3-column responsive grid (`grid-cols-1 md:grid-cols-3 gap-8`) for Features and Pricing.
- **Footer**: 4-column layout (`grid-cols-2 md:grid-cols-5`) at the bottom.

### 5. User Actions
- Click "Start Creating Free" or "Get Started" to navigate to Register Page.
- Click "Sign In" to navigate to Login Page.
- Play sample interactive video demo preview.
- Toggle monthly vs. annual pricing option.
- Expand/collapse FAQ accordion panels.

### 6. Navigation Flow
- Primary CTA → `/register`
- Secondary CTA / Sign In → `/login`
- Navigation Links → Smooth anchor scroll (`#features`, `#how-it-works`, `#pricing`, `#faq`).

### 7. Empty States
N/A (Public marketing page).

### 8. Loading States
- Video preview frame renders a muted pastel shimmer skeleton during stream initialization.
- CTA buttons render a subtle inline pulse loader if clicked.

### 9. Error States
- If media preview fails to load: Displays fallback high-resolution 3D thumbnail card with "Click to retry video play".

### 10. Success States
N/A (Public marketing page).

### 11. Mobile Responsiveness
- Nav bar collapses into a full-screen glassmorphic hamburger drawer.
- Hero text scales down from `text-6xl` to `text-3xl`.
- Feature grids stack vertically into single-column layout with 16px lateral padding.

### 12. Accessibility Considerations
- WCAG AAA color contrast ratios on text over dark backdrops (minimum contrast 7:1).
- Accessible ARIA labels on video player controls and FAQ expandables.
- Full keyboard tab navigation support across header, CTA buttons, and pricing toggles.

### 13. Future Scalability
- Capability to embed real-time platform statistics counter (e.g., "1,240,000+ Videos Generated").
- Dynamic geo-targeted localized currency switching on pricing cards.

---

## 2. Login Page

### 1. Purpose of the Screen
Authenticate returning creators securely and efficiently while maintaining a frictionless sign-in experience.

### 2. User Goal
Gain access to the studio dashboard with minimal clicks and immediate authentication feedback.

### 3. Main Components
- **Brand Identity Header**: Minimal KidsAI Studio emblem and title.
- **OAuth Social Auth Button**: "Continue with Google" button with official icon.
- **Divider**: "or continue with email" visual rule.
- **Credentials Form**:
  - Email Address Input
  - Password Input (with show/hide eye toggle)
  - "Remember me" checkbox
  - "Forgot password?" hyperlink
- **Submit Button**: "Sign In to Studio" (gradient styling).
- **Navigation Footer**: "Don't have an account? Sign up".

### 4. Layout Description
- Centered split layout. Left side: Abstract 3D animated artwork representing AI video creation. Right side: Minimal card container (440px fixed width) floating over dark canvas (`#090A0F`).

### 5. User Actions
- Click "Continue with Google" for OAuth redirect.
- Enter email/password and click "Sign In".
- Click "Forgot password?" to open recovery overlay.
- Click "Sign up" to navigate to `/register`.

### 6. Navigation Flow
- Successful Auth → Redirect to `/dashboard`.
- "Sign up" click → Navigate to `/register`.
- "Forgot password?" → Open modal or navigate to `/forgot-password`.

### 7. Empty States
Form fields initialized empty with subtle floating label placeholders.

### 8. Loading States
- Upon submit: Form inputs lock (disabled state), button text transitions to spinner animation with text "Authenticating...".

### 9. Error States
- Invalid email format: Inline error below field "Please enter a valid email address".
- Wrong password / Auth error: Alert box at top of form "Invalid credentials. Please verify your email and password."

### 10. Success States
- Form input highlights green border, auto-redirects seamlessly to `/dashboard`.

### 11. Mobile Responsiveness
- Left-side artwork hides automatically; auth card centers with 100% width and 20px padding.

### 12. Accessibility Considerations
- Form inputs linked to semantic HTML labels (`for="..."`).
- Password field exposes aria-invalid attribute during error states.

### 13. Future Scalability
- Support for Single Sign-On (SSO) for enterprise studio accounts and multi-factor authentication (MFA).

---

## 3. Register Page

### 1. Purpose of the Screen
Onboard new creators quickly with low friction while gathering baseline information and agreeing to YouTube Kids safety guidelines.

### 2. User Goal
Create a new KidsAI Studio account and launch their first video project immediately.

### 3. Main Components
- **Header**: "Create your free account".
- **Google One-Tap / OAuth Button**: "Sign up with Google".
- **Registration Form**:
  - Full Name Input
  - Email Address Input
  - Password Input with real-time Password Strength Meter (Length, Numbers, Special Characters).
  - Terms of Service & Child Safety Guidelines acceptance checkbox.
- **CTA Button**: "Create Account & Start Generating".
- **Sign In Link**: "Already have an account? Log in".

### 4. Layout Description
- Centered 460px glassmorphic card over dark ambient mesh canvas.

### 5. User Actions
- Complete input fields and check terms box.
- View real-time password strength validation bar.
- Click "Create Account".

### 6. Navigation Flow
- Success → Redirect directly into `/projects/new` (Create Project Wizard).

### 7. Empty States
Empty form fields with clear placeholder hints.

### 8. Loading States
- Submit button shows dynamic spinner with "Creating Your Workspace...".

### 9. Error States
- Email already in use: Inline error message "An account with this email already exists. Log in instead."
- Weak password: Block submit button until minimum complexity requirement is met.

### 10. Success States
- Animated green checkmark badge appears briefly before smooth page transition into onboarding.

### 11. Mobile Responsiveness
- Single column layout, full viewport height adaptation with touch-optimized target sizes (48px minimum).

### 12. Accessibility Considerations
- Focus states wrapped in visible high-contrast ring (`ring-2 ring-purple-500`).
- Screen reader announcements for password strength changes (`aria-live="polite"`).

### 13. Future Scalability
- Referral code input field toggle for affiliate partner tracking.

---

## 4. Dashboard

### 1. Purpose of the Screen
Serve as the central command center for the creator, providing instant access to active projects, AI credit balance, usage analytics, and quick creation triggers.

### 2. User Goal
Check status of video generations, manage past projects, monitor credit balance, and start a new video project.

### 3. Main Components
- **Collapsible Sidebar**: Logo, Navigation Items (Dashboard, My Projects, Asset Library, Characters, Settings, Help Center), User Profile card, Collapse Toggle.
- **Top Navigation Bar**: Global Search Bar (fuzzy search projects/assets), Quick Action "+ New Video", Notifications Bell with unread badge, Credits Counter Pill (e.g., "⚡ 450 Credits"), User Avatar Menu.
- **Hero Quick Prompt Banner**: Large visual card "What story will you create today?" with quick prompt input bar and "Generate" action.
- **Usage & Analytics Widgets Grid**:
  - Total Videos Rendered (e.g., 28)
  - Total Watch Time Generated (e.g., 4h 12m)
  - Credits Used This Month (Bar progress indicator)
  - Active Generation Queue Status
- **Recent Projects Grid**: Cards showing project thumbnail, title, status pill (`COMPLETED`, `RENDERING`, `DRAFT`), age group, aspect ratio, duration, and action context menu (Edit, Download, Duplicate, Delete).
- **Recent Renders Shelf**: Horizontal thumbnail carousel of finished videos ready for instant MP4 download.

### 4. Layout Description
- 2-Column Dashboard Layout: Left sidebar (260px fixed width, collapsible to 72px icon mode). Right main workspace (flex fill) with 32px padding, structured with modular card grids (`grid-cols-1 md:grid-cols-2 xl:grid-cols-3`).

### 5. User Actions
- Click "+ New Video" to launch the Create Project Wizard.
- Filter projects by status (All, Rendering, Completed, Drafts).
- Click project card to enter Project Details or Storyboard Editor.
- Search projects via global search.

### 6. Navigation Flow
- "+ New Video" → `/projects/new`
- Project Card → `/projects/{id}`
- Asset Library -> `/assets`
- Settings → `/settings`

### 7. Empty States
- When no projects exist: Displays a friendly illustration of a dinosaur animator holding a blank canvas with title "No videos created yet", subhead "Turn your first prompt into an animated YouTube Kids video in under 2 minutes", and a prominent "+ Create First Video" button.

### 8. Loading States
- Skeleton loader pulse blocks (`animate-pulse bg-white/5 rounded-2xl`) for project cards and statistic widgets during data fetching.

### 9. Error States
- If API backend fails to fetch projects: Displays error banner "Unable to sync workspace projects. [Retry Refresh]".

### 10. Success States
- Newly created project automatically slides into top-left slot of project grid with glowing border.

### 11. Mobile Responsiveness
- Sidebar collapses into bottom drawer tab bar or slide-out menu. Top navigation header condenses.

### 12. Accessibility Considerations
- Keyboard shortcuts implemented: `Cmd+K` for global search, `Cmd+N` for new video creation.
- ARIA landmarks: `<aside>` for sidebar, `<main>` for workspace, `<nav>` for top navigation.

### 13. Future Scalability
- Real-time WebSocket connection badge showing active render progress across background workers without manual page reload.

---

## 5. Create Project Wizard

### 1. Purpose of the Screen
Guide the user through a frictionless 10-step configuration sequence to define all parameters for their AI-generated video before triggering the Director Agent pipeline.

### 2. User Goal
Define video topic, target audience, style, length, voice, and settings effortlessly through an intuitive multi-step form.

### 3. Main Components & Step Breakdown

#### Step 1: Project Name
- Input field for project title.
- Auto-generate suggestion button (e.g., "Dinosaurs Learn Colors #1").

#### Step 2: Video Topic & Prompt
- Large rich text prompt textarea.
- Inspiration tags & prompt expander assistant button.

#### Step 3: Target Age Group
- Selectable visual cards:
  - Toddlers (Ages 2-4) — Simple words, gentle colors.
  - Preschool (Ages 3-5) — Vibrant, playful, educational.
  - Early Elementary (Ages 6-8) — Story-driven, adventurous.

#### Step 4: Video Length
- Selectable duration chips:
  - Short (30-60 sec / Shorts format)
  - Standard (2-3 min / YouTube Kids)
  - Extended (5 min / Storybook compilation)

#### Step 5: Video Style
- Visual style cards with preview thumbnails:
  - 3D Pixar/Disney Digital Render
  - 2D Pastel Storybook Illustration
  - Claymation / Stop-Motion
  - Anime / Cartoon Style

#### Step 6: Language
- Dropdown selector supporting 20+ languages (English US/UK, Spanish, French, German, Japanese, Hindi, etc.).

#### Step 7: Voice Narration
- Voice selection cards with audio sample preview play buttons:
  - "Storyteller Emma" (Warm, gentle female)
  - "Uncle Bob" (Fun, energetic male)
  - "Little Timmy" (Child narrator voice)

#### Step 8: Aspect Ratio
- Visual toggle chips:
  - `16:9` YouTube Standard Landscape
  - `9:16` YouTube Shorts / TikTok Portrait
  - `1:1` Square Social

#### Step 9: Advanced Settings
- Accordion options:
  - Background Music Mood (Upbeat, Lullaby, Adventure, None)
  - Subtitle Style (Yellow Bubble, Clean Minimal, Karaoke Bounce)
  - Safety & Educational Focus (Colors, Counting, Morals, Vocabulary)

#### Step 10: Generate & Review Summary
- Final summary card listing all selected parameters, estimated AI credit cost (e.g., "15 Credits"), total estimated rendering time (~60 seconds), and high-impact "🚀 Launch Director Pipeline" button.

### 4. Layout Description
- Focused full-screen modal workspace (`max-w-3xl mx-auto`). Top persistent step indicator bar (1 to 10 step dots with progress line). Bottom fixed navigation bar with "Back" and "Next / Continue" buttons.

### 5. User Actions
- Select chips/cards and fill text inputs for each step.
- Listen to audio voice sample previews.
- Click "Next Step" or press `Enter` to advance.
- Click "Launch Director Pipeline" on Step 10.

### 6. Navigation Flow
- Step 1 -> Step 2 -> ... -> Step 10 -> Launch → Redirect to `/projects/{id}/progress` (Video Generation Progress Page).

### 7. Empty States
Default pre-selected intelligent defaults on every step (e.g., Preschool 3-5, 3D Pixar Style, 16:9) so a user can click "Next" rapidly.

### 8. Loading States
- Step transitions execute smooth 200ms slide-left animations.
- Step 10 Launch button displays loading state while registering project payload with backend API.

### 9. Error States
- If prompt is less than 5 characters on Step 2: Show inline alert "Please enter a descriptive prompt for your video story."

### 10. Success States
- Triggers celebratory particle animation upon clicking "Launch" before transitioning to the Progress Page.

### 11. Mobile Responsiveness
- Step cards stack vertically; step indicator transforms into a simple text tracker ("Step 4 of 10").

### 12. Accessibility Considerations
- Arrow key navigation between options within selection grids.
- `aria-valuemin="1" aria-valuemax="10" aria-valuenow="{step}"` on progress bar.

### 13. Future Scalability
- Ability to save custom user presets (e.g., "My Channel Style Preset").

---

## 6. Video Generation Progress Page

### 1. Purpose of the Screen
Provide real-time visibility into the multi-agent AI generation pipeline, building excitement while keeping the user informed of background processing status.

### 2. User Goal
Monitor progress as individual AI agents generate script, scenes, images, voice narration, and final video render.

### 3. Main Components
- **Header Status Banner**: Project title, prompt, and overall percentage progress ring (e.g., `65% Complete`).
- **Live State Machine Stepper**: Visual timeline showing active, pending, and completed pipeline stages:
  1. Planning (Director Agent)
  2. Story Script (Story Agent)
  3. Storyboard (Storyboard Agent)
  4. Visual Assets (Visual Artist Agent)
  5. Motion Paths (Animation Agent)
  6. Voiceover (Voice Agent)
  7. Background Music (Music Agent)
  8. Video Render (FFmpeg Engine)
  9. Quality Check (Verification Agent)
- **Active Agent Spotlight Card**: Shows current working agent, live log feed (e.g., *"Generating 3D scene asset 3 of 4..."*), and estimated remaining time indicator (e.g., *"~22 seconds remaining"*).
- **Live Preview Window**: Dynamic image asset slider showing generated scene images as they stream in from the Visual Artist Agent.
- **Action Controls**: "Cancel Pipeline" button, "Background Process" (allows navigating away safely), and "Retry Phase" button (visible on error).

### 4. Layout Description
- Split layout: Left column (40% width) for pipeline stepper and agent log stream. Right column (60% width) for live preview stage and progress metrics.

### 5. User Actions
- Watch live agent logs.
- Click "Process in Background" to return to Dashboard.
- Click "Cancel Pipeline" to terminate execution.

### 6. Navigation Flow
- Completion → Auto-redirect to `/projects/{id}` (Project Details Page).
- Cancel → Return to `/dashboard`.

### 7. Empty States
Initial state displays "Waking up AI Agents..." loader indicator.

### 8. Loading States
- Pulse indicators and progress line fills with animated shimmer gradient (`bg-gradient-to-r from-purple-500 to-pink-500`).

### 9. Error States
- If an agent fails (e.g., Image API timeout): Pipeline pauses, step indicator turns red with message *"Visual Agent encountered an issue"*, exposing a prominent "Retry Stage" button.

### 10. Success States
- All 9 step badges illuminate green checkmarks, triggering an instant transition to the completed video project page.

### 11. Mobile Responsiveness
- Single column layout: Preview stage on top, timeline stepper below.

### 12. Accessibility Considerations
- Live region updates (`aria-live="polite"`) announcing stage changes for screen readers.

### 13. Future Scalability
- Real-time WebSocket connection with automatic HTTP long-polling fallback.

---

## 7. Project Details Page

### 1. Purpose of the Screen
Serve as the comprehensive hub for a completed or draft project, giving the user access to all generated assets, metadata, video player, and export tools.

### 2. User Goal
Review finished video, inspect generated scenes, download MP4, copy SEO tags, or open advanced editors.

### 3. Main Components
- **Top Header**: Project title, status pill (`COMPLETED`), target age group badge, duration pill, and primary actions ("Download MP4", "Share", "Delete").
- **Featured Video Player**: 16:9 / 9:16 responsive HTML5 video player with custom glass controls, speed control, and full-screen toggle.
- **Tab Navigation Bar**:
  - Overview
  - Storyboard & Script
  - Characters
  - SEO & Metadata
  - Analytics (Post-MVP)
- **Overview Tab Content**:
  - Video Description summary
  - Scene Carousel preview cards
  - Generation Metrics Box (Render time, AI model used, tokens, estimated cost)
- **SEO Package Card**: Generated YouTube Title options, description text with auto-hashtags, and 1-click "Copy SEO Package" button.
- **Thumbnail Selector Grid**: 3 AI-generated thumbnail variations with "Set as Primary" button.

### 4. Layout Description
- Top section: Large video player (left 65%) + Project Metadata & Actions panel (right 35%). Bottom section: Full-width tabbed detail panels.

### 5. User Actions
- Play video and inspect quality.
- Click "Download MP4" to trigger direct browser file download.
- Click "Edit in Storyboard" to open Storyboard Editor.
- Copy SEO metadata to clipboard.

### 6. Navigation Flow
- "Edit Storyboard" → `/projects/{id}/storyboard`
- "Preview Video" → `/projects/{id}/preview`
- "Back to Dashboard" → `/dashboard`

### 7. Empty States
If optional sections (e.g., custom music) were skipped: Show "Add background music track" prompt chip.

### 8. Loading States
- Media player displays custom dark spinner while fetching MP4 stream from Cloudflare R2 bucket.

### 9. Error States
- If video URL expires: Exposes "Refresh Download Link" action.

### 10. Success States
- Toast notification "Copied SEO Package to clipboard!" upon clicking copy button.

### 11. Mobile Responsiveness
- Player scales to 100% viewport width; tabs transform into a horizontally scrollable pill list.

### 12. Accessibility Considerations
- Video player includes closed-caption (`<track>`) support.
- Keyboard spacebar toggles video play/pause.

### 13. Future Scalability
- One-click "Publish directly to YouTube Kids Channel" button integration via n8n workflow.

---

## 8. Storyboard Editor

### 1. Purpose of the Screen
Provide fine-grained editing control over individual scenes, narration text, visual prompts, images, and audio sync.

### 2. User Goal
Customize script lines, swap generated scene images, reorder scenes, or fine-tune prompt details before final render re-stitch.

### 3. Main Components
- **Top Toolbar**: Back link, Project title, "Undo/Redo" buttons, "Add New Scene" button, and "Re-Render Video" primary button.
- **Left Panel (Scene Sequence Drag & Drop)**: Vertical list of scene cards with thumbnail, duration, drag handle (`grip-vertical`), and scene number index.
- **Center Canvas (Active Scene Editor)**:
  - Large Scene Image Preview with "Regenerate Image" and "Replace Asset" buttons.
  - Visual Prompt Input Box (editable prompt text sent to image model).
  - Narration Text Input Box (editable script line read by voice agent).
  - Audio Waveform Bar with playback speed and voice model selection.
- **Right Panel (Scene Settings & AI Assistant)**: Style adjustments, transition effect selector (Fade, Zoom In, Slide), and prompt enhancement suggestions.

### 4. Layout Description
- 3-Column Studio Layout: Left scene list (280px), Center workspace (flex grow), Right panel (320px).

### 5. User Actions
- Drag and drop scene cards to reorder sequence.
- Edit narration text or visual prompt.
- Click "Regenerate Image" to request a new visual variation for the active scene.
- Click "Re-Render Video" to compile changes into a new MP4.

### 6. Navigation Flow
- "Re-Render Video" → Triggers background render task and returns to Project Details Page.

### 7. Empty States
N/A (Always populates with project scenes).

### 8. Loading States
- When regenerating a single scene image: Active scene image frame shows an inline shimmer loader while maintaining the rest of the workspace interactive.

### 9. Error States
- If narration text is deleted completely: Highlight field in red "Scene requires narration text".

### 10. Success States
- Immediate visual feedback on scene reordering with smooth list layout animation.

### 11. Mobile Responsiveness
- Desktop 3-column layout collapses into a single-column tabbed view (Scenes | Canvas | Properties).

### 12. Accessibility Considerations
- Keyboard drag-and-drop support (`Space` to lift scene, `Arrow Up/Down` to move, `Space` to drop).

### 13. Future Scalability
- In-browser timeline audio trimming controls.

---

## 9. Character Manager

### 1. Purpose of the Screen
Manage consistent AI character memory profiles, ensuring the same recurring characters (e.g., "Sammy the Red Dinosaur") retain visual appearance across multiple video projects.

### 2. User Goal
Create, inspect, customize, and lock visual consistency profiles for original characters.

### 3. Main Components
- **Top Action Bar**: Title "Character Memory Library", Search bar, "+ Create New Character" button.
- **Character Grid**: Cards featuring:
  - Character Avatar / 3D Turnaround render.
  - Character Name & Tag (e.g., "Sammy / Protagonist").
  - Personality traits & Age group compatibility.
  - Color Palette swatches (e.g., Primary Red `#EF4444`, Accent Yellow `#F59E0B`).
  - Linked Projects Count (e.g., "Used in 6 Videos").
  - Actions: Edit, Regenerate Reference Sheets, Delete.
- **Character Detail Modal / Drawer**:
  - Multi-angle reference sheet images (Front view, Side view, Happy expression, Surprised expression).
  - Base Visual Prompt Anchor (e.g., *"Cute baby red Tyrannosaurus Rex with big cheerful dark eyes, soft rounded scales"*).
  - Preferred Voice Model selector.

### 4. Layout Description
- Responsive 4-column card grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6`) inside dashboard main container.

### 5. User Actions
- Click "+ Create Character" to define a new character prompt.
- Click character card to inspect reference sheet images and expressions.
- Click "Regenerate Sheet" to refine visual style.

### 6. Navigation Flow
- Character selection integrates directly into the Create Project Wizard (Step 2/Step 5).

### 7. Empty States
- "No custom characters created yet. Create a consistent character profile to reuse across your video series." with "+ Create Character" button.

### 8. Loading States
- Grid renders 4 skeleton cards while loading character memory data from API.

### 9. Error States
- Display notification if image reference generation fails.

### 10. Success States
- Newly created character badge appears with a "Memory Saved" green indicator.

### 11. Mobile Responsiveness
- Grid condenses to 1-column layout; detail drawer opens full-screen.

### 12. Accessibility Considerations
- Character color swatches expose tooltip hex codes and color name labels for screen readers.

### 13. Future Scalability
- Upload custom reference sketch images to seed AI character generation.

---

## 10. Video Preview Page

### 1. Purpose of the Screen
Provide a full-screen, cinema-style playback environment for final video QA, caption sync check, and presentation.

### 2. User Goal
Review the final MP4 video in high resolution with full player controls before publishing or downloading.

### 3. Main Components
- **Large Cinema Video Player**: Centered 16:9 / 9:16 video stage with ambient background blur glow.
- **Custom Player Controls**: Play/Pause, Timeline Scrubber bar with scene marker ticks, Current time / Total duration, Volume slider, Subtitle toggle (`CC`), Resolution selector (`720p`, `1080p`, `4K`), Fullscreen toggle.
- **Scene Marker Navigation Track**: Clicking a scene marker jumps playback directly to that scene.
- **Subtitle Preview Overlay**: Live preview of rendered captions with custom typography styling.
- **Export & Action Bar**: "Download MP4 Video", "Export Subtitles (.srt)", "Copy Share Link".

### 4. Layout Description
- Darkened cinema layout (`bg-[#050508]`). Player occupies 80% screen height with floating action bar at bottom.

### 5. User Actions
- Scrub timeline to test scene transitions.
- Toggle CC subtitles on/off.
- Click scene markers to jump playback.
- Click "Download MP4".

### 6. Navigation Flow
- "Back to Project" → `/projects/{id}`

### 7. Empty States
N/A (Invoked for valid video projects).

### 8. Loading States
- Video buffer spinner centered over video canvas during initial load.

### 9. Error States
- If media fails to stream: Show message "Video stream unavailable. [Download Direct File]".

### 10. Success States
- Smooth 60fps playback with responsive audio waveform visualization.

### 11. Mobile Responsiveness
- Video expands to native full-screen view on mobile devices.

### 12. Accessibility Considerations
- Fully controllable via keyboard (`Space` = Play/Pause, `F` = Fullscreen, `M` = Mute, `Left/Right Arrows` = Seek 5s).

### 13. Future Scalability
- Real-time side-by-side comparison mode for video revisions.

---

## 11. AI Asset Library

### 1. Purpose of the Screen
Serve as a centralized media repository storing all raw and generated AI assets (images, audio files, background music, video clips, thumbnails).

### 2. User Goal
Browse, search, filter, download, and reuse media assets across multiple video projects.

### 3. Main Components
- **Top Filter & Search Bar**: Search input, Category Tabs (All, Images, Voiceovers, Music, Thumbnails), Sorting dropdown (Newest, Oldest, File Size).
- **Media Asset Grid**: Cards displaying:
  - Visual preview thumbnail / Audio waveform card.
  - Asset Name & Type badge (e.g., `PNG Image`, `WAV Audio`).
  - Source Project reference link.
  - File details (Resolution, Size, Created date).
  - Hover Action Buttons: Quick View, Download, Copy URL, Delete.
- **Asset Detail Modal**: Large image/audio inspection window with full prompt metadata and "Reuse in New Project" action.

### 4. Layout Description
- Responsive masonry grid layout (`grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4`) under dashboard header.

### 5. User Actions
- Filter assets by type (Images, Audio, Video).
- Download individual raw assets.
- Click "Reuse Asset" to pre-fill prompt in new project.

### 6. Navigation Flow
- "Reuse in New Project" → `/projects/new` with asset pre-linked.

### 7. Empty States
- "No assets found in library. Generated images and audio from your projects will automatically appear here."

### 8. Loading States
- Masonry grid displays 10 shimmer skeleton boxes during initial fetch.

### 9. Error States
- Failure to fetch asset payload displays retry alert.

### 10. Success States
- Download triggers browser file save immediately.

### 11. Mobile Responsiveness
- Grid adapts to 2 columns on mobile screens with touch context menu.

### 12. Accessibility Considerations
- Every image card contains descriptive `alt` text populated from its visual prompt.

### 13. Future Scalability
- Cloudflare R2 bucket batch ZIP export for full channel asset backups.

---

## 12. Settings

### 1. Purpose of the Screen
Allow users to manage profile settings, account security, interface preferences, storage usage, and system parameters.

### 2. User Goal
Update account preferences, change password, manage storage, and configure defaults.

### 3. Main Components
- **Vertical Navigation Tabs**:
  - Profile & Account
  - Security & Password
  - Preferences (Theme, Language, Notifications)
  - Storage & Usage
  - API Keys (Future / Advanced)
  - Danger Zone
- **Profile Panel**: Avatar upload, Full Name, Email, Workspace Name.
- **Preferences Panel**: Dark Mode toggle, Default Target Age Group selector, Default Aspect Ratio selector.
- **Storage Panel**: Storage space used meter (e.g., `4.2 GB of 10 GB used`), "Clear Temporary Caches" button.
- **Danger Zone Panel**: Red bordered card with "Delete Account & Data" action requiring password confirmation.

### 4. Layout Description
- 2-Column Settings Layout: Left tab navigation bar (220px), Right content form panel (max 640px).

### 5. User Actions
- Update profile details and click "Save Changes".
- Change password.
- Toggle preferences.

### 6. Navigation Flow
- Settings persistent under sidebar item `/settings`.

### 7. Empty States
N/A.

### 8. Loading States
- Save button displays inline spinner "Saving preferences...".

### 9. Error States
- Password mismatch displays inline error "New passwords do not match".

### 10. Success States
- Top floating toast banner "Settings saved successfully".

### 11. Mobile Responsiveness
- Left tabs convert into a horizontal scrolling tab selector on top of content form.

### 12. Accessibility Considerations
- Clear form field error announcements and accessible switch controls (`role="switch"`).

### 13. Future Scalability
- Custom API key entry for bring-your-own (BYO) OpenAI or ElevenLabs accounts.

---

## 13. Billing (Placeholder)

### 1. Purpose of the Screen
Provide transparent view of credit balance, current plan subscription, invoice history, and tier upgrade options.

### 2. User Goal
Monitor credit consumption, view subscription tier, and upgrade plan for higher generation limits.

### 3. Main Components
- **Current Plan Card**: Active Plan name (e.g., "Creator Tier"), Renewal Date, Monthly Credit Balance (e.g., `450 / 500 Credits remaining`).
- **Credit Consumption Meter**: Visual progress bar breaking down credit usage (Story Generation, Image Assets, Voice Synthesis, Video Rendering).
- **Upgrade Tiers Grid**:
  - **Free Starter**: 50 Credits/mo, 720p Export, Watermarked.
  - **Creator ($29/mo)**: 500 Credits/mo, 1080p HD, No Watermark, Commercial License.
  - **Studio ($79/mo)**: 2,000 Credits/mo, 4K Export, Priority Rendering, Character Memory.
- **Invoice History Table**: Date, Description, Amount, PDF Download link.

### 4. Layout Description
- Stacked card layout with 3-column pricing grid underneath current plan overview.

### 5. User Actions
- Click "Upgrade Plan" to initiate Stripe Checkout modal.
- Click "Download Invoice PDF".

### 6. Navigation Flow
- Upgrade Click → Stripe Checkout redirect / modal.

### 7. Empty States
- Invoice history displays "No past invoices available" for free tier users.

### 8. Loading States
- Plan cards show shimmer loaders while syncing billing status.

### 9. Error States
- Payment decline notification modal with update payment method CTA.

### 10. Success States
- Instant credit balance update badge upon plan upgrade.

### 11. Mobile Responsiveness
- Pricing cards stack into a single column.

### 12. Accessibility Considerations
- Table headers contain appropriate `scope="col"` attributes.

### 13. Future Scalability
- Pay-as-you-go credit top-up pack purchases.

---

## 14. Help Center

### 1. Purpose of the Screen
Empower users to solve questions independently through structured guides, tutorials, and direct support channels.

### 2. User Goal
Find quick answers on YouTube Kids guidelines, prompt tips, and technical support.

### 3. Main Components
- **Search Header**: Large search bar "How can we help you today?".
- **Quick Topic Grid**:
  - Getting Started (First video creation guide)
  - Prompt Engineering for Kids Content
  - YouTube Monetization & Copyright Safety
  - Troubleshooting & Video Quality
- **Video Tutorial Library**: Embedded short video walkthroughs.
- **FAQ Accordion**: Searchable common questions.
- **Contact Support Card**: "Still need help? Open a ticket or join our Discord community."

### 4. Layout Description
- Clean centered layout with search hero banner on top and 4-column topic category grid below.

### 5. User Actions
- Search help documentation.
- Click topic card to view full article.
- Click "Open Support Ticket".

### 6. Navigation Flow
- Help Center accessible via sidebar `/help`.

### 7. Empty States
- Search query with no matches: "No articles found matching '[query]'. [Contact Support]".

### 8. Loading States
- Search bar displays inline spinner while querying articles.

### 9. Error States
- Network error banner if help articles fail to load.

### 10. Success States
- Article opens with helpfulness feedback prompt ("Was this article helpful? Yes / No").

### 11. Mobile Responsiveness
- Responsive grid adapts to mobile view.

### 12. Accessibility Considerations
- Full keyboard accessible search and expandable accordions.

### 13. Future Scalability
- Integrated AI Support Chatbot assistant widget.

---

## 15. Admin Panel (Future / Internal)

### 1. Purpose of the Screen
Provide platform administrators and system operators with real-time oversight of users, system health, API provider costs, background queue health, and model telemetry.

### 2. User Goal
Monitor system stability, manage user accounts, inspect model API costs, and debug failed background pipeline jobs.

### 3. Main Components
- **Top System Health Metrics Grid**:
  - Total Active Users
  - Total Videos Rendered Today
  - API Health Status (OpenAI, Replicate, EdgeTTS, Cloudflare R2)
  - Active Celery Queue Worker Jobs
  - Estimated API Costs (Daily / Monthly breakdown)
- **User Management Table**: User ID, Name, Email, Subscription Plan, Credits Left, Status (Active/Suspended), Actions.
- **Generation Jobs Log Monitor**: Real-time streaming log table of project pipeline executions with filter by status (`COMPLETED`, `FAILED`, `RENDERING`).
- **Model Cost & Latency Chart**: Graph showing cost per video and latency per AI provider.

### 4. Layout Description
- High-density telemetry dashboard layout with dark grid tables and real-time chart cards.

### 5. User Actions
- Filter system logs.
- Suspend/unsuspend user accounts.
- Inspect detailed error tracebacks for failed pipeline jobs.

### 6. Navigation Flow
- Admin Panel accessible at `/admin` (restricted to Super Admin role).

### 7. Empty States
N/A.

### 8. Loading States
- Real-time chart displays skeleton line graph while establishing telemetry stream.

### 9. Error States
- System health badge turns red if an underlying AI provider API degrades.

### 10. Success States
- Real-time status indicators update dynamically via WebSocket.

### 11. Mobile Responsiveness
- Restricted to desktop viewports with horizontal scroll wrappers for telemetry tables.

### 12. Accessibility Considerations
- High-contrast data tables with explicit column headers and status badges.

### 13. Future Scalability
- One-click manual model fallback switcher (e.g., force switch LLM provider from OpenAI to Gemini).

---

# SECTION 2: SYSTEM SPECIFICATIONS & DESIGN SYSTEM

---

## 1. Complete Navigation Map

```
Public Routes:
/ (Landing Page)
├── /login (Login Page)
├── /register (Register Page)
└── /forgot-password (Password Recovery)

Authenticated App Routes:
/dashboard (Main App Dashboard)
├── /projects/new (10-Step Create Project Wizard)
├── /projects/[id]/progress (Real-Time Generation Progress)
├── /projects/[id] (Project Details & Overview)
├── /projects/[id]/storyboard (Storyboard & Scene Editor)
├── /projects/[id]/preview (Full-Screen Video Preview)
├── /assets (AI Asset Library)
├── /characters (Character Memory Manager)
├── /settings (Account & App Preferences)
├── /billing (Plan & Credits Management)
└── /help (Help Center & Documentation)

Administrative Routes (Internal):
└── /admin (System Health & Telemetry Panel)
```

---

## 2. User Journey

```
[ Visitor Lands on / ] 
         │
         ▼
[ Clicks "Start Creating Free" ] ──► [ Registers on /register ] 
                                                │
                                                ▼
                                   [ Lands on /dashboard ] 
                                                │
                                                ▼
                                   [ Clicks "+ New Video" ] 
                                                │
                                                ▼
                                 [ Completes 10-Step Wizard ] 
                                                │
                                                ▼
                                 [ Launches Director Agent ] 
                                                │
                                                ▼
                              [ Monitors Live Progress Page ] 
                                                │
                                                ▼
                              [ Lands on Completed Details ] 
                                        │               │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
             [ Fine-Tunes Storyboard ]      [ Downloads Final MP4 ]
```

---

## 3. Information Architecture

```
KidsAI Studio Workspace
│
├── Project Lifecycle Core
│   ├── Prompt & Parameters Configuration
│   ├── Multi-Agent Execution Telemetry
│   ├── Asset Assembly (Script, Images, Audio, Video)
│   └── Export & Distribution (MP4, Subtitles, SEO)
│
├── Creative Asset Management
│   ├── Character Memory Profiles (Visual Anchors, Traits)
│   ├── Generated Image Vault
│   ├── Speech Narration Audio Repository
│   └── Background Music Library
│
└── Account & Infrastructure
    ├── Credit Balance & Billing Tier
    ├── Storage & System Preferences
    └── User Authentication & Workspace Security
```

---

## 4. Component Hierarchy

```
App Layout Shell
├── Top Navbar (Glassmorphic)
│   ├── Brand Identity
│   ├── Global Search Bar
│   ├── Credits Counter Pill
│   ├── Notifications Menu
│   └── User Avatar Dropdown
│
├── Collapsible Sidebar
│   ├── Primary Navigation Links
│   ├── Quick Action Button (+ New Video)
│   └── Workspace Status Badge
│
└── Main Workspace Canvas
    ├── Page Header & Context Toolbar
    ├── Content View Area
    │   ├── Card Grids / Telemetry Tables
    │   ├── Multi-Step Wizard Cards
    │   └── Media Player Stages
    └── Toast Notification Container
```

---

## 5. Design System Tokens

- **Theme Mode**: Dark Mode First (`#090A0F` Canvas Base).
- **Surface Elevation**:
  - `Base`: `#090A0F`
  - `Card / Glass Surface`: `rgba(255, 255, 255, 0.04)` with `backdrop-filter: blur(16px)`
  - `Elevated Modal / Dropdown`: `rgba(18, 20, 29, 0.85)` with `backdrop-filter: blur(24px)`
- **Borders & Dividers**:
  - Subtle Border: `rgba(255, 255, 255, 0.08)`
  - Focus Ring: `rgba(139, 92, 246, 0.5)`
- **Glassmorphism Spec**: `backdrop-blur-xl bg-white/[0.03] border border-white/[0.08] shadow-[0_8px_32px_0_rgba(0,0,0,0.36)]`

---

## 6. Typography Recommendations

- **Primary Font Family**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif` (Clean, hyper-legible UI text).
- **Display Accent Font**: `Outfit` or `Plus Jakarta Sans` (Modern geometric display headings).
- **Scale Matrix**:
  - `Display / Hero`: 56px / Line Height 1.1 / Font Weight 800
  - `H1`: 36px / Line Height 1.2 / Font Weight 700
  - `H2`: 24px / Line Height 1.3 / Font Weight 700
  - `H3`: 18px / Line Height 1.4 / Font Weight 600
  - `Body Large`: 16px / Line Height 1.5 / Font Weight 400
  - `Body Standard`: 14px / Line Height 1.5 / Font Weight 400
  - `Caption / Badge`: 12px / Line Height 1.4 / Font Weight 600 Upper

---

## 7. Color Palette

```
Surface Colors:
- Canvas Background: #090A0F
- Surface Card: #11131A
- Surface Elevated: #1A1D27

Brand & Accent Gradients:
- Primary Violet: #7C3AED (Tailwind violet-600)
- Primary Pink Accent: #EC4899 (Tailwind pink-500)
- Cyan Highlight: #06B6D4 (Tailwind cyan-500)
- Gradient Primary: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)

Feedback & Status Colors:
- Success Green: #10B981 (Emerald-500)
- Warning Amber: #F59E0B (Amber-500)
- Error Rose: #F43F5E (Rose-500)
- Info Blue: #3B82F6 (Blue-500)

Text Hierarchy:
- Primary Text: #F9FAFB (Gray-50)
- Secondary Text: #9CA3AF (Gray-400)
- Muted Text: #6B7280 (Gray-500)
```

---

## 8. Icon System

- **Icon Set**: Lucide Icons (Minimal, 1.5px stroke weight, consistent 24x24 / 20x20 sizing).
- **Key Icon Tokens**:
  - `Sparkles`: AI Generation & Magic actions.
  - `Film`: Scenes & Storyboard.
  - `Wand2`: Prompt Generator.
  - `Volume2`: Voice Narration.
  - `Music`: Background Soundtracks.
  - `PlayCircle`: Video Playback.
  - `CheckCircle2`: Pipeline Success / Quality Check.
  - `Clock`: Duration & Progress.
  - `Zap`: Credits & Speed.

---

## 9. Spacing System

Strict 8pt Spatial Grid:
- `4px` (xs / tight gap)
- `8px` (sm / element padding)
- `16px` (md / standard component padding)
- `24px` (lg / card internal padding)
- `32px` (xl / grid gap)
- `48px` (2xl / section vertical spacing)
- `64px` (3xl / hero section spacing)

---

## 10. Grid System

- **Desktop (1440px+)**: 12-column responsive fluid grid with 32px gutters and 48px margin bounds.
- **Tablet (768px - 1024px)**: 8-column grid with 24px gutters and 24px margin bounds.
- **Mobile (< 768px)**: 4-column grid with 16px gutters and 16px lateral padding.

---

## 11. Animation Guidelines

- **Duration Tokens**:
  - `Micro-Interactions (Hovers, Toggles)`: `150ms ease-out`
  - `Modal / Overlay Slide`: `250ms cubic-bezier(0.16, 1, 0.3, 1)`
  - `Page Transitions`: `300ms ease-in-out`
- **Transforms**:
  - Card Hover: `transform: translateY(-2px) scale(1.01)`
  - Button Active Press: `transform: scale(0.98)`
  - Shimmer Loader: Linear infinite gradient translation.

---

## 12. Responsive Breakpoints

- `sm`: `640px` (Mobile landscape / small tablets)
- `md`: `768px` (Tablets portrait)
- `lg`: `1024px` (Tablets landscape / small laptops)
- `xl`: `1280px` (Desktop)
- `2xl`: `1536px` (Large Desktop Displays)

---

## 13. Accessibility Checklist (WCAG 2.1 AA Compliant)

- [x] Minimum 4.5:1 contrast ratio for normal text and 3:1 for large display text.
- [x] Visible focus indicators on all interactive elements (`ring-2 ring-purple-500`).
- [x] Semantic HTML structural elements (`header`, `nav`, `main`, `aside`, `footer`, `article`).
- [x] Keyboard operable navigation (Tab, Shift+Tab, Enter, Space, Esc, Arrow keys).
- [x] All images contain explicit descriptive `alt` tags.
- [x] Dynamic updates wrapped in `aria-live="polite"` regions.
- [x] Form inputs linked to semantic `<label>` elements with `id` matching.

---

## 14. Reusable Component Library Specification

1. `Button`: Primary Gradient, Secondary Glass, Ghost, Danger, Icon-only variants with inline loading state support.
2. `Card / GlassPanel`: Base, Interactive Hover, Selected, and Bordered variants.
3. `InputText / Textarea`: Floating label, character count, error state text support.
4. `SelectDropdown`: Custom searchable glass dropdown menu.
5. `Badge / Pill`: Status indicator badges (`Success`, `Warning`, `Error`, `Neutral`, `Gradient`).
6. `Modal / Drawer`: Glassmorphic backdrop overlay container with keyboard `Esc` listener.
7. `ProgressBar`: Stepped indicator and fluid percentage bar.
8. `TabGroup`: Pill-style and Underline-style navigation tabs.
9. `Tooltip`: Hover delayed contextual micro-card (`delay-300`).
10. `SkeletonLoader`: Pulse animated placeholders for cards, text, and media frames.

---

## 15. UI Development Priority Order

```
Phase 1: Shared Core & Layout (Week 1)
├── 1. Design System Tokens & Tailwind CSS Base Config
├── 2. Global Layout Shell (Top Navbar, Collapsible Sidebar)
└── 3. Reusable UI Primitives (Button, GlassPanel, Input, Badge, Modal)

Phase 2: Authentication & Onboarding (Week 2)
├── 4. Login Page
├── 5. Register Page
└── 6. Landing Page Marketing Suite

Phase 3: Core SaaS Dashboard & Creation Engine (Week 3)
├── 7. Main Dashboard Space
├── 8. 10-Step Create Project Wizard
└── 9. Real-Time Video Generation Progress Page

Phase 4: Asset Management & Editing Studio (Week 4)
├── 10. Project Details Page
├── 11. Storyboard Editor
├── 12. Character Memory Manager
└── 13. Full-Screen Video Preview Page

Phase 5: Library, Settings & System Telemetry (Week 5)
├── 14. AI Asset Library
├── 15. Settings Suite
├── 16. Billing & Subscription Tiers
├── 17. Help Center
└── 18. Admin Telemetry Panel
```
