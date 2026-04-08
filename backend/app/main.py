import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .models.database import init_db
from .api.v1 import router as api_v1_router
from .monitoring.realtime import RealtimeMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create required directories at module load time
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# Global monitor instance
realtime_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global realtime_monitor
    
    # Startup
    logger.info("Starting AI Security Intelligence Platform...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start realtime monitor
    realtime_monitor = RealtimeMonitor()
    await realtime_monitor.start()
    logger.info("Realtime monitor started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if realtime_monitor:
        await realtime_monitor.stop()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Increase request body size limit (500MB)
@app.middleware("http")
async def increase_body_limit(request, call_next):
    request.scope["max_body_size"] = 500 * 1024 * 1024  # 500MB
    response = await call_next(request)
    return response

# Trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


# WebSocket endpoint for real-time updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time security updates."""
    await websocket.accept()
    
    if realtime_monitor:
        await realtime_monitor.add_client(client_id, websocket)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        if realtime_monitor:
            await realtime_monitor.remove_client(client_id)


# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("frontend/index.html")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# API info
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }
