import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.security import limiter, auth_limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.logging import setup_logging
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
from app.core.db import renders_db

# Setup logging
setup_logging()
logger = logging.getLogger("kidsai.main")

START_TIME = time.time()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add rate limiting
app.state.limiter = limiter

# Add exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Rate limiting exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"IP: {client_host}"
    )
    return response

# Enable CORS for Next.js frontend
# In production, replace ["*"] with specific domains
origins = [
    "http://localhost:3000",  # Development
    "http://localhost:3001",  # Alternative dev port
] if settings.ENVIRONMENT == "development" else [
    # Add your production domains here
    # "https://yourdomain.com",
    # "https://app.yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with rate limiting
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

@app.get("/metrics")
def metrics():
    uptime = round(time.time() - START_TIME, 2)
    return {
        "system_status": "HEALTHY",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": uptime,
        "total_projects": 0,  # Will be updated when we connect to real DB
        "total_renders": 0
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to KidsAI Studio API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }
