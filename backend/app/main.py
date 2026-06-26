from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.products import router as products_router
from app.database.database import init_db
from app.database.seed import seed_database
from app.services.gemini_service import GeminiService
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PixaFlow ChatBot API",
    description="A simple market chatbot using FastAPI and Gemini AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api")
app.include_router(products_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """
    Initialize database and seed it with sample data on startup.
    """
    init_db()
    seed_database()


@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {
        "message": "PixaFlow ChatBot API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with component status.
    """
    from app.database.database import engine
    
    health_status = {
        "api": True,
        "database": False,
        "gemini": False
    }
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Gemini API
    try:
        gemini_service = GeminiService()
        # Simple test call
        test_response = gemini_service.model.generate_content("Test")
        health_status["gemini"] = True
    except Exception as e:
        logger.error(f"Gemini health check failed: {e}")
    
    overall_status = "ok" if all(health_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "version": "1.0.0",
        "components": health_status
    }
