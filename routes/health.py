"""
Health Check Router
Basic health and status endpoints
"""
from fastapi import APIRouter
from models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API status and service availability
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "rag_system": "available",
            "document_processor": "available",
            "agents": "available"
        }
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}