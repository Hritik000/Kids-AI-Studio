# KidsAI Studio — Design System & Component Library Master Specification (v2.0)

**Design Philosophy**: Apple-inspired elegance, Linear/Vercel precision, dark-mode first, minimal, responsive, accessible, high-performance SaaS.

---

# 1. CENTRALIZED DESIGN TOKENS

## 1.1 Color Palette (Dark-Mode First & Light Fallback)

### Dark Mode Tokens (Primary Theme)
- `color-canvas-base`: `#090A0F` (Deep spatial black canvas)
- `color-surface-card`: `rgba(255, 255, 255, 0.04)` (Glassmorphic card container)
- `color-surface-card-hover`: `rgba(255, 255, 255, 0.07)`
- `color-surface-elevated`: `rgba(18, 20, 29, 0.85)` (Modals, Dropdowns, Command Palette)
- `color-border-subtle`: `rgba(255, 255, 255, 0.08)`
- `color-border-focus`: `rgba(139, 92, 246, 0.6)` (Purple focus ring)

### Brand Accent Tokens
- `color-primary-600`: `#7C3AED` (Violet primary)
- `color-primary-500`: `#8B5CF6`
- `color-accent-pink`: `#EC4899` (Secondary accent)
- `color-accent-cyan`: `#06B6D4` (Highlight accent)
- `gradient-primary`: `linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)`
- `gradient-glow`: `radial-gradient(circle at 50% 0%, rgba(124, 58, 237, 0.25) 0%, transparent 70%)`

### Semantic Feedback Status Colors
- `color-status-success`: `#10B981` (Emerald-500)
- `color-status-warning`: `#F59E0B` (Amber-500)
- `color-status-error`: `#F43F5E` (Rose-500)
- `color-status-info`: `#3B82F6` (Blue-500)

---

## 1.2 Typography System

**Primary Font Family**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`  
**Display Font Family**: `Outfit`, `Plus Jakarta Sans`, `sans-serif`  
**Monospace Font Family**: `JetBrains Mono`, `Fira Code`, `monospace`

| Style Token | Size | Line Height | Weight | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- |
| **Display XL** | 64px | 1.1 | 800 (ExtraBold) | `-0.02em` |
| **Display Large** | 48px | 1.15 | 800 (ExtraBold) | `-0.02em` |
| **Display Medium**| 36px | 1.2 | 700 (Bold) | `-0.01em` |
| **Heading 1 (H1)**| 30px | 1.25 | 700 (Bold) | `-0.01em` |
| **Heading 2 (H2)**| 24px | 1.3 | 700 (Bold) | `0em` |
| **Heading 3 (H3)**| 20px | 1.35 | 600 (SemiBold) | `0em` |
| **Heading 4 (H4)**| 16px | 1.4 | 600 (SemiBold) | `0em` |
| **Body Large** | 16px | 1.5 | 400 (Regular) | `0em` |
| **Body Medium** | 14px | 1.5 | 400 (Regular) | `0em` |
| **Body Small** | 12px | 1.4 | 400 (Regular) | `0.01em` |
| **Caption** | 11px | 1.3 | 500 (Medium) | `0.02em` |
| **Label** | 12px | 1.2 | 600 (SemiBold) | `0.05em UPPER` |
| **Button Text** | 14px | 1.0 | 600 (SemiBold) | `0.01em` |
| **Code Block** | 13px | 1.6 | 400 (Regular) | `0em` |

---

## 1.3 Spacing Scale & Layout Grid (8pt System)

- `space-1`: `4px` (xs / micro gap)
- `space-2`: `8px` (sm / component padding)
- `space-3`: `12px` (md-sm / form field padding)
- `space-4`: `16px` (md / standard padding)
- `space-6`: `24px` (lg / card container padding)
- `space-8`: `32px` (xl / grid gutters)
- `space-12`: `48px` (2xl / section margins)
- `space-16`: `64px` (3xl / hero padding)

### Breakpoints & Container Widths
- `sm`: `640px` (Mobile landscape)
- `md`: `768px` (Tablet)
- `lg`: `1024px` (Laptop / Small desktop)
- `xl`: `1280px` (Desktop)
- `2xl`: `1536px` (Ultra-wide display)
- `max-width-content`: `1280px`
- `max-width-wizard`: `768px`

---

## 1.4 Elevation, Shadows, Radii & Z-Index

### Border Radius Tokens
- `radius-sm`: `6px` (Buttons, Badges)
- `radius-md`: `12px` (Inputs, Small cards)
- `radius-lg`: `16px` (Cards, Panels)
- `radius-xl`: `24px` (Wizard containers, Modals)
- `radius-full`: `9999px` (Pills, Avatars)

### Glassmorphism & Shadow Tokens
- `shadow-glass`: `0 8px 32px 0 rgba(0, 0, 0, 0.36)`
- `shadow-glow-purple`: `0 0 30px rgba(124, 58, 237, 0.3)`
- `shadow-glow-pink`: `0 0 30px rgba(236, 72, 153, 0.3)`
- `glass-border`: `1px solid rgba(255, 255, 255, 0.08)`
- `glass-backdrop`: `blur(16px)`

### Z-Index Scale
- `z-base`: `0`
- `z-dropdown`: `10`
- `z-sticky`: `20`
- `z-header`: `30`
- `z-drawer`: `40`
- `z-modal`: `50`
- `z-toast`: `60`
- `z-tooltip`: `70`

---

# 2. ICON SYSTEM SPECIFICATION

**Icon Library**: `lucide-react` (1.5px stroke weight, clean geometric curves).

### Icon Taxonomy
- **Navigation**: `LayoutDashboard`, `FolderKanban`, `Film`, `Sparkles`, `UserCheck`, `Library`, `Settings`, `HelpCircle`, `LogOut`, `ChevronRight`
- **Action**: `Plus`, `Edit3`, `Trash2`, `Download`, `Share2`, `Copy`, `RotateCcw`, `Play`, `Pause`, `Search`, `Check`, `X`
- **Status**: `CheckCircle2`, `AlertCircle`, `Clock`, `Zap`, `Lock`, `ShieldCheck`
- **Media**: `Volume2`, `VolumeX`, `Music`, `Image`, `Video`, `Subtitles`, `Layers`, `Sliders`

---

# 3. COMPONENT LIBRARY SPECIFICATIONS

## 3.1 Buttons
- **Variants**: `Primary` (Gradient background), `Secondary` (Glass fill), `Ghost` (Transparent), `Outline` (Bordered), `Danger` (Rose fill), `Success` (Emerald fill), `Loading` (Spinner state), `IconButton` (Square icon container), `FAB` (Floating action pill).
- **States**: Default, Hover (`translateY(-1px)`), Active (`scale(0.98)`), Focused (`ring-2 ring-purple-500`), Disabled (`opacity-50 pointer-events-none`).

## 3.2 Inputs & Forms
- **Components**: `TextInput`, `PasswordInput` (Eye toggle), `SearchInput` (Kbd shortcut chip), `EmailInput`, `NumberInput`, `Textarea` (Auto-expand), `SelectDropdown` (Custom glass menu), `Autocomplete`, `DatePicker`, `Checkbox` (Custom check mark), `Radio`, `Toggle` (`role="switch"`), `Slider` (Custom thumb range), `FileUpload` (Drag and drop zone).
- **Architecture**: Integrated with `react-hook-form` and `zod` schema resolvers. Exposes error messages, helper text, and validation states.

## 3.3 Cards & Containers
- **Components**: `ProjectCard` (Thumbnail preview, status badge, action menu), `StatisticCard` (Metric value, trend percentage, icon), `FeatureCard` (Icon pill, title, description), `VideoCard` (Player preview, duration), `CharacterCard` (Avatar turnarounds, traits, swatches), `SceneCard` (Narration line, visual prompt, audio indicator).

## 3.4 Dialogs & Overlays
- **Components**: `Modal` (Glass container, header, body, footer), `ConfirmationDialog` (Action prompt, proceed button), `DeleteDialog` (Danger state, double confirm), `Drawer` (Slide-in from right), `BottomSheet` (Mobile slide-up modal).

## 3.5 Navigation Elements
- **Components**: `Navbar` (Glass bar, search, credits pill, profile dropdown), `Sidebar` (Collapsible 260px/72px, item badges), `Breadcrumb` (Step trail), `Tabs` (Pill & Underline styles), `Pagination` (Page numbers & arrows), `CommandPalette` (`Cmd+K` quick search modal), `AvatarMenu` (User dropdown menu).

## 3.6 Media Components
- **Components**: `VideoPlayer` (HTML5 custom player, progress bar, CC toggle, quality selector), `AudioPlayer` (Waveform visualization, play button), `ImageViewer` (Light-box modal), `Timeline` (Scene track sequence scrubber).

## 3.7 Feedback & Notifications
- **Components**: `Toast` (Floating notification popups), `Snackbar` (Bottom status pill), `AlertBanner` (Inline error/warning alert), `ProgressBar` (Linear progress), `CircularProgress` (Ring spinner), `SkeletonLoader` (Shimmer pulse block), `Stepper` (10-step progress dots).

---

# 4. COMPONENT ARCHITECTURE & FOLDER STRUCTURE (`packages/ui`)

```
packages/ui/
├── tokens/
│   ├── colors.ts
│   ├── typography.ts
│   ├── spacing.ts
│   ├── shadows.ts
│   └── animations.ts
├── theme/
│   ├── tailwind-plugin.ts
│   └── globals.css
├── button/
│   ├── Button.tsx
│   ├── IconButton.tsx
│   └── FAB.tsx
├── input/
│   ├── TextInput.tsx
│   ├── PasswordInput.tsx
│   ├── SelectDropdown.tsx
│   ├── Checkbox.tsx
│   └── Toggle.tsx
├── card/
│   ├── GlassCard.tsx
│   ├── ProjectCard.tsx
│   └── SceneCard.tsx
├── modal/
│   ├── Modal.tsx
│   ├── Drawer.tsx
│   └── ConfirmDialog.tsx
├── navigation/
│   ├── Navbar.tsx
│   ├── Sidebar.tsx
│   └── Tabs.tsx
├── feedback/
│   ├── Toast.tsx
│   ├── Skeleton.tsx
│   └── ProgressBar.tsx
├── media/
│   ├── VideoPlayer.tsx
│   └── AudioWaveform.tsx
├── forms/
│   ├── FormField.tsx
│   └── FormErrorMessage.tsx
├── hooks/
│   ├── useTheme.ts
│   ├── useDisclosure.ts
│   └── useMediaQuery.ts
└── index.ts
```

---

# 5. UI DEVELOPMENT PRIORITY ORDER

```
Priority 1: Design System Core & Base Primitives (Week 1)
├── Design Token Constants & Tailwind Plugin
├── Button (Primary, Secondary, Ghost, Outline, Loading)
├── GlassCard & Surface Containers
└── Typography & Badge Primitives

Priority 2: Form & Input System (Week 2)
├── TextInput, PasswordInput, SelectDropdown
├── Checkbox, Toggle, Textarea, Slider
└── FormField & Zod Integration Wrappers

Priority 3: Navigation & Shell (Week 3)
├── Top Navbar & Collapsible Sidebar
├── Tabs, Breadcrumbs, Avatar Menu
└── Command Palette (Cmd+K)

Priority 4: Feedback & Modals (Week 4)
├── Modal, Drawer, DeleteDialog
├── Toast, AlertBanner, ProgressBar
└── Skeleton Loaders & Shimmer States

Priority 5: Media & Complex Components (Week 5)
├── VideoPlayer & Subtitle Overlay
├── AudioWaveform Bar
├── Scene Timeline Sequence Track
└── Asset Grid & Masonry Layouts
```
