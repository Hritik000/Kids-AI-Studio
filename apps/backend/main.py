from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.projects import router as projects_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.ai import router as ai_router
from app.api.v1.storyboard import router as storyboard_router
from app.api.v1.characters import router as characters_router
from app.api.v1.images import router as images_router
from app.api.v1.animations import router as animations_router
from app.api.v1.audio import router as audio_router
from app.api.v1.music import router as music_router
from app.api.v1.rendering import router as rendering_router
from app.api.v1.publishing import router as publishing_router
from app.api.v1.distribution import router as distribution_router
from app.api.v1.saas import router as saas_router
from app.api.v1.copilot import router as copilot_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(projects_router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(ai_router, prefix=settings.API_V1_STR, tags=["ai-pipeline"])
app.include_router(storyboard_router, prefix=settings.API_V1_STR, tags=["storyboard"])
app.include_router(characters_router, prefix=settings.API_V1_STR, tags=["characters"])
app.include_router(images_router, prefix=settings.API_V1_STR, tags=["images"])
app.include_router(animations_router, prefix=settings.API_V1_STR, tags=["animations"])
app.include_router(audio_router, prefix=settings.API_V1_STR, tags=["audio"])
app.include_router(music_router, prefix=settings.API_V1_STR, tags=["music"])
app.include_router(rendering_router, prefix=settings.API_V1_STR, tags=["rendering"])
app.include_router(publishing_router, prefix=settings.API_V1_STR, tags=["publishing"])
app.include_router(distribution_router, prefix=settings.API_V1_STR, tags=["distribution"])
app.include_router(saas_router, prefix=settings.API_V1_STR, tags=["saas"])
app.include_router(copilot_router, prefix=settings.API_V1_STR, tags=["copilot"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}
