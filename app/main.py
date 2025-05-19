from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("WARNING: OPENAI_API_KEY not found in environment variables")

app = FastAPI(title="AskAccess", description="AI assistant for answering internal employee questions and customer queries")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from app.ingestion import router as ingestion_router, initialize_document_store
from app.query import router as query_router, initialize_query_processor

document_store = None
if openai_api_key:
    document_store = initialize_document_store(openai_api_key)
    
    if document_store:
        initialize_query_processor(document_store, openai_api_key)

app.include_router(ingestion_router)
app.include_router(query_router)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "openai_api_key_configured": bool(openai_api_key),
        "document_store_initialized": document_store is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to AskAccess API",
        "description": "AI assistant for answering internal employee questions and customer queries",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
