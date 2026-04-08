from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging
from contextlib import asynccontextmanager

from api.routes import scan, clean, boost
from services.analysis.threat_intelligence import threat_intel

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configure Global Rate Limiting
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the external Threat Database on server boot
    await threat_intel.initialize()
    logging.info("Enterprise Threat Intelligence SQL System Booted.")
    yield
    # Cleanup task (if necessary)

app = FastAPI(title="AppGuardAi Backend API", version="1.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Because Flutter web runs locally or emulator sends to host, CORS must be broad during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api/v1")
app.include_router(clean.router, prefix="/api/v1/clean", tags=["Clean"])
app.include_router(boost.router, prefix="/api/v1/boost", tags=["Boost"])

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return {"status": "online", "message": "AppGuardAi backend is protecting."}
