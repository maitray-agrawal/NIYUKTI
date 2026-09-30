from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base, get_db
from app.routes import candidates, jobs, ranking, copilot, submission
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ASTRA / NIYUKTI: AI-Powered Talent Intelligence and Recruitment Platform Backend.",
    version="1.0.0"
)

import os
from fastapi.staticfiles import StaticFiles

# CORS configuration — supports configured FRONTEND_URL, live Vercel domain, and local dev
_origins_set = {
    settings.FRONTEND_URL.strip(),
    "https://astra-niyukti.vercel.app",
    "https://talentmindai-app.vercel.app",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
}
# Also parse comma-separated FRONTEND_URL if user provided multiple
if "," in settings.FRONTEND_URL:
    for o in settings.FRONTEND_URL.split(","):
        if o.strip():
            _origins_set.add(o.strip())

_allowed_origins = [o for o in _origins_set if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],  # Required so browser JS can read pagination count
)

# Create database tables on startup (not at import time)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(candidates.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(ranking.router, prefix=settings.API_V1_STR)
app.include_router(copilot.router, prefix=settings.API_V1_STR)
app.include_router(submission.router, prefix=settings.API_V1_STR)

@app.get("/api")
@app.get("/api/")
def api_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/health")
def health(db=Depends(get_db)):
    """Enhanced health check that verifies database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    groq_configured = bool(
        __import__("os").environ.get("GROQ_API_KEY")
    )
    
    is_healthy = db_status == "connected"
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "project": settings.PROJECT_NAME,
            "database": db_status,
            "groq_api_key_configured": groq_configured
        }
    )

@app.get("/api/health")
def api_health(db=Depends(get_db)):
    """Alias for /health under the /api prefix for proxy resilience."""
    return health(db)

# Mount frontend_screens static UI files at root if available
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend_screens"))
if not os.path.isdir(frontend_dir):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend_screens"))

if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
