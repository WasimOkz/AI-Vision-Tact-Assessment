"""
AI Candidate Assessment Platform - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.routers import candidates, assessment, voice, hr
from app.websockets.chat_handler import router as ws_chat_router
from app.websockets.voice_handler import router as ws_voice_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered candidate assessment platform with multi-agent system",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(assessment.router, prefix="/api/assessment", tags=["Assessment"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(hr.router, prefix="/api/hr", tags=["HR Dashboard"])

# Register WebSocket routers
app.include_router(ws_chat_router, tags=["WebSocket - Chat"])
app.include_router(ws_voice_router, tags=["WebSocket - Voice"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "llm_configured": bool(settings.GROQ_API_KEY),
        "voice_configured": bool(settings.ELEVENLABS_API_KEY or settings.DEEPGRAM_API_KEY),
        "avatar_configured": bool(settings.DID_API_KEY)
    }
