"""
FastAPI Main Application
Entry point for the startup analyzer API
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("data", exist_ok=True)

from routes import (
    analysis_router,
    document_router,
    report_router,
    email_router,
    health_router
)
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting AI Startup Analyzer API...")
    yield
    print("👋 Shutting down API...")


# Initialize FastAPI app
app = FastAPI(
    title="AI Startup Analyzer API",
    description="REST API for AI-powered startup analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(report_router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(email_router, prefix="/api/v1/email", tags=["Email"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Startup Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


