# Authentication & User Management — KidsAI Studio (Phase 4)

## 1. Authentication Architecture Overview

KidsAI Studio uses a hybrid Supabase Auth + FastAPI JWT token verification architecture.

```
┌─────────────────────────────────────────────────────────────┐
│                 Next.js Frontend Client                      │
│            (AuthProvider + AuthContext + Middleware)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Bearer JWT Token
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Security Middleware                  │
│       (get_current_user + require_role Security Scheme)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Supabase Auth Service                      │
│            (User Management & PostgreSQL RLS)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication Flow Diagram

```
[ Visitor ] ──► [ /login or /register ]
                      │
                      ▼
            [ Supabase Auth Provider ]
                      │
                      ├─► Google OAuth / Email Auth
                      ▼
            [ Generates Bearer Token ]
                      │
                      ▼
         [ AuthProvider Context & LocalStorage ]
                      │
                      ▼
       [ Route Protection Middleware Checks ]
                      │
                      ├─► Guest Trying Protected Route ──► Redirect /login
                      └─► Authenticated ──► Access Granted (/dashboard)
```

---

## 3. Folder Structure

```
apps/backend/
├── app/
│   ├── api/v1/
│   │   ├── auth.py         # Register, Login, Forgot/Reset Password, Me, Logout
│   │   └── users.py        # Profile GET/PUT & Password Change endpoints
│   ├── core/
│   │   └── security.py     # HTTPBearer JWT decoding & require_role dependency
│   └── schemas/
│       └── auth.py         # Pydantic schemas (RegisterRequest, LoginRequest, UserProfile, UserRole)
└── tests/
    └── test_auth.py        # Pytest auth verification suite

apps/frontend/
├── src/
│   ├── app/
│   │   ├── login/          # Login Page
│   │   ├── register/       # Registration Page
│   │   ├── forgot-password/# Password Reset Request Page
│   │   ├── reset-password/ # Password Reset Confirm Page
│   │   ├── profile/        # User Profile Management Page
│   │   └── unauthorized/   # 403 Forbidden Access Page
│   ├── lib/
│   │   ├── api.ts          # Auth API Client helper methods
│   │   └── auth-context.tsx# AuthProvider Context & useAuth Hook
│   └── middleware.ts       # Next.js Route Protection Middleware
```

---

## 4. Required Environment Variables

```env
# Root / Backend Environment Variables
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
JWT_SECRET=your_jwt_secret_key

# Frontend Environment Variables (apps/frontend/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## 5. Security & Role Management

- **User Roles**: `USER`, `ADMIN`, `MODERATOR`.
- **JWT Verification**: Backend verifies Bearer JWT tokens on every protected endpoint via FastAPI dependency injection `Depends(get_current_user)`.
- **Role Control**: Endpoint role authorization via `Depends(require_role([UserRole.ADMIN]))`.
- **Input Sanitization & Validation**: Client and server side Zod and Pydantic validation on all input fields.

---

## 6. Testing Checklist & Results

- [x] **Registration**: Validated full name, email, password match, and terms check.
- [x] **Login**: Email/Password authentication & token generation verified.
- [x] **Session Persistence**: LocalStorage and AuthProvider session recovery on page refresh verified.
- [x] **Logout**: Clears token and user context cleanly.
- [x] **Route Protection**: Middleware redirects unauthenticated requests away from `/dashboard`, `/projects`, `/profile`, `/settings`.
- [x] **Backend Test Suite**: `4 passed in 3.31s` (Pytest).
- [x] **Frontend Build**: Compiled successfully in Next.js App Router (0 errors).
