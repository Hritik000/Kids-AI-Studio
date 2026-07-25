# Production Deployment Guide — KidsAI Studio v2.0

## 1. Overview
KidsAI Studio is configured for multi-container production deployment using Docker, Docker Compose, or Kubernetes.

## 2. Environment Variables

### Backend (`apps/backend/.env`)
```ini
PROJECT_NAME=KidsAI Studio Backend
VERSION=2.0.0
API_V1_STR=/api/v1
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-key
SECRET_KEY=your-jwt-secret-key
```

### Frontend (`apps/frontend/.env.local`)
```ini
NEXT_PUBLIC_API_URL=https://api.kidsaistudio.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 3. Launching with Docker Compose

```bash
# Build and launch services in background
docker-compose up -d --build

# View container logs
docker-compose logs -f
```

## 4. Health Checks
- Backend Health Endpoint: `GET /health` -> `{"status": "ok", "app": "KidsAI Studio Backend", "version": "2.0.0"}`
- Frontend Health Page: `GET /`
