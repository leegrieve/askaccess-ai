from fastapi import APIRouter, HTTPException, Query as QueryParam
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import json
import os

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .query_processor import QueryProcessor
from .document_store import DocumentStore

router = APIRouter(prefix="/query", tags=["query"])

query_processor = None

class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str
    max_results: int = 4
    include_sources: bool = True
    log_query: bool = True

class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    query: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    processing_time: float
    timestamp: str

def initialize_query_processor(document_store_instance, openai_api_key: str):
    """Initialize the query processor with document store and LLM."""
    global query_processor
    query_processor = QueryProcessor(document_store_instance, openai_api_key)
    return query_processor

os.makedirs("data/query_logs", exist_ok=True)

def log_query(query: str, answer: str, sources: List[Dict[str, Any]], processing_time: float):
    """Log query and response to file."""
    log_entry = {
        "query": query,
        "answer": answer,
        "sources": sources,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }
    
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"data/query_logs/queries_{timestamp}.jsonl"
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process a natural language query and return a response.
    
    Args:
        request: Query request with query string and options
    
    Returns:
        Query response with answer and sources
    """
    if query_processor is None:
        raise HTTPException(status_code=500, detail="Query processor not initialized")
    
    try:
        result = query_processor.process_query(
            query=request.query,
            max_results=request.max_results,
            include_sources=request.include_sources
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            sources=result["sources"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/logs")
async def get_query_logs(limit: int = QueryParam(10, ge=1, le=100)):
    """
    Get recent query logs.
    
    Args:
        limit: Maximum number of logs to return
    
    Returns:
        List of recent query logs
    """
    if query_processor is None:
        raise HTTPException(status_code=500, detail="Query processor not initialized")
    
    try:
        logs = query_processor.get_query_logs(limit=limit)
        return {"logs": logs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving query logs: {str(e)}")
