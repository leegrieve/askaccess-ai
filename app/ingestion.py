from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
import shutil
from datetime import datetime
from .document_store import DocumentStore

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

document_store = None

def initialize_document_store(openai_api_key: str):
    """Initialize the document store with the OpenAI API key."""
    global document_store
    document_store = DocumentStore(openai_api_key=openai_api_key)
    return document_store

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    document_type: str = Form("knowledge_base"),
    metadata: Optional[str] = Form(None)
):
    """
    Upload and ingest a file into the document store.
    
    Args:
        file: The file to upload
        document_type: Type of document (knowledge_base, salesforce, etc.)
        metadata: JSON string with additional metadata
    
    Returns:
        Information about the ingested document
    """
    if document_store is None:
        raise HTTPException(status_code=500, detail="Document store not initialized")
    
    parsed_metadata = {}
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    
    parsed_metadata["document_type"] = document_type
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join("data/uploads", safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        document_id = document_store.ingest_file(file_path, parsed_metadata)
        
        return {
            "status": "success",
            "document_id": document_id,
            "filename": file.filename,
            "stored_path": file_path,
            "document_type": document_type,
            "metadata": parsed_metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@router.post("/salesforce")
async def ingest_salesforce_data(data: List[Dict[str, Any]]):
    """
    Ingest Salesforce case data into the document store.
    
    Args:
        data: List of Salesforce case dictionaries
    
    Returns:
        Information about the ingested cases
    """
    if document_store is None:
        raise HTTPException(status_code=500, detail="Document store not initialized")
    
    try:
        document_ids = document_store.ingest_salesforce_data(data)
        
        return {
            "status": "success",
            "document_count": len(document_ids),
            "document_ids": document_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting Salesforce data: {str(e)}")

@router.get("/status")
async def get_ingestion_status():
    """Get the status of the document store."""
    if document_store is None:
        raise HTTPException(status_code=500, detail="Document store not initialized")
    
    return {
        "document_count": document_store.get_document_count(),
        "status": "ready"
    }
