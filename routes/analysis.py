"""
Analysis Router
Handles startup analysis operations
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import json

from models import (
    StartAnalysisRequest,
    AnalysisStatusResponse,
    AnalysisResults,
    AnalysisStatus
)
from backend.services.rag_system import RAGSystem
from backend.agents.agent_orchestrator import AgentOrchestrator


router = APIRouter()

# Initialize services
rag_system = RAGSystem()
orchestrator = AgentOrchestrator(rag_system)

# In-memory storage for analysis status and results
# In production, use Redis or a database
analysis_storage: Dict[str, Dict] = {}


def run_analysis_background(startup_id: str):
    """Background task to run analysis"""
    try:
        # Update status to processing
        analysis_storage[startup_id] = {
            "status": AnalysisStatus.PROCESSING,
            "progress": 10,
            "message": "Starting analysis..."
        }
        
        # Run agent orchestrator
        results = orchestrator.analyze_startup(startup_id)
        
        # Update status to completed
        analysis_storage[startup_id] = {
            "status": AnalysisStatus.COMPLETED,
            "progress": 100,
            "message": "Analysis completed successfully",
            "results": results
        }
        
    except Exception as e:
        # Update status to failed
        analysis_storage[startup_id] = {
            "status": AnalysisStatus.FAILED,
            "progress": 0,
            "message": f"Analysis failed: {str(e)}",
            "error": str(e)
        }


@router.post("/start", response_model=AnalysisStatusResponse)
async def start_analysis(
    request: StartAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start analysis for a startup
    
    This endpoint initiates the 6-agent analysis pipeline in the background
    Use /status endpoint to check progress
    """
    startup_id = request.startup_id
    
    # Check if already analyzing
    if startup_id in analysis_storage:
        current_status = analysis_storage[startup_id].get("status")
        if current_status == AnalysisStatus.PROCESSING:
            raise HTTPException(
                status_code=409,
                detail="Analysis already in progress for this startup"
            )
    
    # Initialize status
    analysis_storage[startup_id] = {
        "status": AnalysisStatus.PENDING,
        "progress": 0,
        "message": "Analysis queued"
    }
    
    # Add background task
    background_tasks.add_task(run_analysis_background, startup_id)
    
    return {
        "startup_id": startup_id,
        "status": AnalysisStatus.PENDING,
        "progress": 0,
        "message": "Analysis started"
    }


@router.get("/status/{startup_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(startup_id: str):
    """
    Get analysis status for a startup
    
    Returns current progress and status
    """
    if startup_id not in analysis_storage:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this startup"
        )
    
    data = analysis_storage[startup_id]
    
    return {
        "startup_id": startup_id,
        "status": data.get("status"),
        "progress": data.get("progress"),
        "message": data.get("message")
    }


@router.get("/results/{startup_id}")
async def get_analysis_results(startup_id: str):
    """
    Get complete analysis results for a startup
    
    Returns full analysis data including:
    - Extracted data
    - Benchmark data
    - Risk analysis
    - Market research
    - Growth assessment
    - Investment recommendation
    """
    if startup_id not in analysis_storage:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this startup"
        )
    
    data = analysis_storage[startup_id]
    
    if data.get("status") != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Current status: {data.get('status')}"
        )
    
    return data.get("results")


@router.delete("/{startup_id}")
async def delete_analysis(startup_id: str):
    """
    Delete analysis results for a startup
    """
    if startup_id in analysis_storage:
        del analysis_storage[startup_id]
        return {"message": f"Analysis deleted for startup {startup_id}"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )


@router.get("/list")
async def list_analyses():
    """
    List all analyses with their status
    """
    analyses = []
    for startup_id, data in analysis_storage.items():
        analyses.append({
            "startup_id": startup_id,
            "status": data.get("status"),
            "progress": data.get("progress"),
            "message": data.get("message")
        })
    
    return {"analyses": analyses, "total": len(analyses)}