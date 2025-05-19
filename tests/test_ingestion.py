import sys
import os
import json
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.document_store import DocumentStore
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables")
    sys.exit(1)

def test_document_ingestion():
    """Test document ingestion functionality."""
    print("Testing document ingestion...")
    
    document_store = DocumentStore(openai_api_key=openai_api_key)
    
    test_dir = "tests/test_data"
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = {
        "sample_kb.txt": "This is a sample knowledge base article about Access Workspace.",
        "sample_kb.html": "<html><body><h1>Access Financials</h1><p>This is a sample HTML article.</p></body></html>",
    }
    
    file_paths = []
    for filename, content in test_files.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        file_paths.append(file_path)
    
    salesforce_data = [
        {
            "CaseNumber": "00001",
            "Subject": "Password Reset Issue",
            "Description": "User cannot reset their password.",
            "Status": "Closed",
            "Comments": [
                {"CommentBody": "User was provided with password reset instructions."}
            ]
        }
    ]
    
    print("Ingesting test files...")
    document_ids = []
    for file_path in file_paths:
        document_id = document_store.ingest_file(file_path, {"test": True})
        document_ids.append(document_id)
        print(f"Ingested {file_path} with document ID: {document_id}")
    
    print("\nIngesting Salesforce data...")
    salesforce_document_ids = document_store.ingest_salesforce_data(salesforce_data)
    print(f"Ingested {len(salesforce_document_ids)} Salesforce cases")
    
    print("\nTesting similarity search...")
    query = "How do I reset my password?"
    results = document_store.similarity_search(query, k=2)
    
    print(f"Query: {query}")
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Content: {result['content'][:100]}...")
        print(f"Source: {result['metadata'].get('source', 'N/A')}")
        print(f"Score: {result['score']}")
    
    print("\nDocument ingestion test completed successfully!")
    return True

if __name__ == "__main__":
    test_document_ingestion()
