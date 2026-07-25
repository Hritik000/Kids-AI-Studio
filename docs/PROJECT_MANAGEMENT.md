# Dashboard & Project Management Specification — KidsAI Studio (Phase 5)

## 1. System Architecture Overview

The Project Management System manages creator video project metadata, draft states, search indexing, auto-saving, and lifecycle operations (Create, Edit, Duplicate, Favorite, Archive, Restore, Delete).

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js Dashboard & Wizard                │
│       (Notion/Linear UX + Zustand State + useAutoSave Hook) │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API + Auth Token
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Project CRUD Router                 │
│         (List, Search, Filter, Sort, Paginate, CRUD)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Supabase PostgreSQL Storage                  │
│       (projects table + RLS policies + Indexes)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Project Data Model

```typescript
interface Project {
  id: string;                    // Unique UUID identifier
  title: string;                 // Project Name
  description?: string;          // Summary or notes
  prompt: string;                // Story topic prompt
  target_age_group: string;      // "2-4", "3-5", "6-8"
  language: string;              // "English (US)", "Spanish", etc.
  video_length: string;          // "Short (30-60s)", "Standard (2-3 min)", etc.
  aspect_ratio: string;          // "16:9", "9:16", "1:1"
  video_style: string;           // "3D Pixar Render", "2D Storybook", etc.
  voice: string;                 // "Storyteller Emma", "Uncle Bob", etc.
  status: ProjectStatus;         // DRAFT | PLANNING | READY | PROCESSING | COMPLETED | FAILED | ARCHIVED
  thumbnail_url?: string;        // Preview thumbnail URL
  favorite: boolean;             // Favorite toggle boolean
  archived: boolean;             // Soft-delete / Archive status
  owner_id: string;              // Linked creator user ID
  created_at: string;            // ISO UTC timestamp
  updated_at: string;            // ISO UTC timestamp
  last_opened_at?: string;       // Recently opened tracking timestamp
}
```

---

## 3. REST API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/v1/projects` | Create a new project draft |
| **GET** | `/api/v1/projects` | List projects with search (`q`), filter (`status`, `is_favorite`, `is_archived`), sort (`newest`, `oldest`, `title`, `recently_opened`), and pagination (`page`, `limit`) |
| **GET** | `/api/v1/projects/{id}` | Fetch project details & update `last_opened_at` |
| **PUT** | `/api/v1/projects/{id}` | Update project details / Auto-save |
| **DELETE** | `/api/v1/projects/{id}` | Delete project |
| **POST** | `/api/v1/projects/{id}/duplicate` | Duplicate project with copy title |
| **POST** | `/api/v1/projects/{id}/archive` | Archive project |
| **POST** | `/api/v1/projects/{id}/restore` | Restore archived project |
| **POST** | `/api/v1/projects/{id}/favorite` | Toggle favorite status |

---

## 4. Frontend Component Breakdown

- **`/dashboard`**: SaaS dashboard with status metric cards, quick project creation button, search bar, status filter tabs, sort dropdown, grid/list view toggle, and pagination.
- **`/projects/new`**: 10-step wizard (Name → Topic → Age Group → Language → Duration → Aspect Ratio → Voice → Art Style → Review → Save Draft).
- **`/projects/[id]`**: Project details & workspace page with auto-save hook (`useAutoSave`), tabbed views (Overview, Scenes, Characters, Assets, History), and actions (Duplicate, Archive, Restore, Delete, Favorite).
- **`/projects/archive`**: Archive vault page for restoring or purging archived projects.

---

## 5. Testing & Verification Results

- [x] **Project CRUD Operations**: Create, Read, Update (Auto-save), Delete verified.
- [x] **Lifecycle Actions**: Duplicate, Archive, Restore, and Favorite toggles verified.
- [x] **Search & Filters**: Fuzzy search by title/prompt, filter by status/favorite/archived, and sorting verified.
- [x] **Auto-Save**: Debounced auto-save hook verified with visual status badge indicator.
- [x] **Backend Test Suite**: `5 passed in 0.18s` (Pytest).
- [x] **Frontend Build**: Compiled successfully with Next.js App Router (0 errors).
