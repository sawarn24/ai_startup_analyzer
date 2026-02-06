"""
Document Upload Router
Handles document upload and processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
import uuid
import os
import shutil

from models import DocumentUploadResponse
from backend.services.document_processor import DocumentProcessor
from backend.services.rag_system import RAGSystem

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
rag_system = RAGSystem()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    pitch_deck: UploadFile = File(...),
    transcripts: Optional[List[UploadFile]] = File(None),
    emails: Optional[List[UploadFile]] = File(None),
    updates: Optional[List[UploadFile]] = File(None),
):
    """
    Upload and process startup documents

    - pitch_deck: Required pitch deck PDF
    - transcripts: Optional call transcripts
    - emails: Optional email documents
    - updates: Optional update documents
    """

    try:
        # Normalize optional inputs (handle None values)
        transcripts = transcripts or []
        emails = emails or []
        updates = updates or []

        # Generate unique startup ID
        startup_id = str(uuid.uuid4())

        # Create upload directory
        upload_dir = f"uploads/{startup_id}"
        os.makedirs(upload_dir, exist_ok=True)

        # Save pitch deck (required)
        pitch_deck_path = os.path.join(upload_dir, pitch_deck.filename)
        with open(pitch_deck_path, "wb") as buffer:
            shutil.copyfileobj(pitch_deck.file, buffer)

        uploaded_files = {
            "pitch_deck": pitch_deck_path,
            "transcripts": [],
            "emails": [],
            "updates": [],
        }

        # Save transcripts
        for transcript in transcripts:
            if not transcript or not transcript.filename:
                continue

            file_path = os.path.join(upload_dir, transcript.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(transcript.file, buffer)

            uploaded_files["transcripts"].append(file_path)

        # Save emails
        for email in emails:
            if not email or not email.filename:
                continue

            file_path = os.path.join(upload_dir, email.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(email.file, buffer)

            uploaded_files["emails"].append(file_path)

        # Save updates
        for update in updates:
            if not update or not update.filename:
                continue

            file_path = os.path.join(upload_dir, update.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(update.file, buffer)

            uploaded_files["updates"].append(file_path)

        # Process documents
        extracted_data = document_processor.process_uploaded_files(uploaded_files)

        # Add to RAG system
        chunks_added = rag_system.add_documents(extracted_data, startup_id)

        return {
            "startup_id": startup_id,
            "message": "Documents processed successfully",
            "files_processed": {
                "pitch_deck": 1,
                "transcripts": len(uploaded_files["transcripts"]),
                "emails": len(uploaded_files["emails"]),
                "updates": len(uploaded_files["updates"]),
            },
            "chunks_created": chunks_added,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}",
        )


@router.delete("/{startup_id}")
async def delete_documents(startup_id: str):
    """
    Delete uploaded documents for a startup
    """
    try:
        upload_dir = f"uploads/{startup_id}"
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            return {"message": f"Documents deleted for startup {startup_id}"}
        else:
            raise HTTPException(status_code=404, detail="Startup documents not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting documents: {str(e)}",
        )