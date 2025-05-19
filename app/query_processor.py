from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import json
import os

from .response_generator import ResponseGenerator

class QueryProcessor:
    """
    Processes natural language queries and retrieves relevant information.
    """
    
    def __init__(self, document_store, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the query processor with document store and LLM.
        
        Args:
            document_store: Document store for retrieval
            openai_api_key: API key for OpenAI
            model_name: Model name for OpenAI
        """
        self.document_store = document_store
        
        # Initialize response generator
        self.response_generator = ResponseGenerator(
            document_store=document_store,
            openai_api_key=openai_api_key,
            model_name=model_name
        )
        
        os.makedirs("data/query_logs", exist_ok=True)
    
    def process_query(self, query: str, max_results: int = 4, include_sources: bool = True) -> Dict[str, Any]:
        """
        Process a natural language query and return a response.
        
        Args:
            query: Query string
            max_results: Maximum number of results to return
            include_sources: Whether to include sources in the response
        
        Returns:
            Dictionary with query response and metadata
        """
        start_time = time.time()
        
        try:
            results = self.document_store.similarity_search(query, k=max_results)
            
            if not results:
                return {
                    "query": query,
                    "answer": "I don't have enough information to answer this question based on the available knowledge base.",
                    "sources": [],
                    "processing_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate response using the response generator
            response = self.response_generator.generate_response(query, results)
            
            if "error" in response:
                return {
                    "query": query,
                    "error": response["error"],
                    "processing_time": response["processing_time"] + (time.time() - start_time),
                    "timestamp": datetime.now().isoformat()
                }
            
            answer = response["answer"]
            sources = response["sources"] if include_sources else None
            
            processing_time = response["processing_time"] + (time.time() - start_time)
            
            self.log_query(query, answer, sources if sources else [], processing_time)
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Error processing query: {str(e)}"
            
            self.log_query(query, error_message, [], processing_time, is_error=True)
            
            return {
                "query": query,
                "error": error_message,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def log_query(self, query: str, answer: str, sources: List[Dict[str, Any]], processing_time: float, is_error: bool = False, feedback: Optional[str] = None):
        """
        Log query and response to file for future analysis.
        
        Args:
            query: Query string
            answer: Answer string
            sources: List of sources
            processing_time: Processing time in seconds
            is_error: Whether the query resulted in an error
            feedback: Optional user feedback (thumbs up/down)
        """
        log_entry = {
            "query": query,
            "answer": answer,
            "sources": sources,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "is_error": is_error,
            "feedback": feedback,
            "latency_within_target": processing_time < 3.0  # Target: <3 seconds
        }
        
        os.makedirs("data/query_logs", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"data/query_logs/queries_{timestamp}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_query_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent query logs.
        
        Args:
            limit: Maximum number of logs to return
        
        Returns:
            List of recent query logs
        """
        logs = []
        log_files = sorted([f for f in os.listdir("data/query_logs") if f.startswith("queries_")], reverse=True)
        
        for log_file in log_files:
            if len(logs) >= limit:
                break
            
            with open(f"data/query_logs/{log_file}", "r") as f:
                for line in f:
                    if len(logs) >= limit:
                        break
                    
                    logs.append(json.loads(line))
        
        return logs
