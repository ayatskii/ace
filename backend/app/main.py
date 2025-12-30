from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from app.database import engine, get_db, init_db
from app.models import Base
from app.routers import api_router  # Changed from app.api.v1.router
import time

# Load environment variables
load_dotenv()

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready with retries"""
    from sqlalchemy import text
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection established!")
            return True
        except Exception as e:
            print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
    print("❌ Could not connect to database after maximum retries")
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    print("🚀 Starting up ACE Platform...")
    if wait_for_db():
        init_db()
    else:
        print("⚠️ Starting without database initialization")
    yield
    print("👋 Shutting down ACE Platform...")

# Create FastAPI application
app = FastAPI(
    title="ACE Platform API",
    description="API for the ACE Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check endpoints
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "ACE Platform API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

# Include API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True, log_level="info")
