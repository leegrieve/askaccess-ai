from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredHTMLLoader,
    TextLoader,
    CSVLoader,
)
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

class DocumentStore:
    """
    Handles document ingestion, embedding, and retrieval using LangChain and FAISS.
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialize the document store with OpenAI embeddings and FAISS vector store.
        
        Args:
            openai_api_key: API key for OpenAI
        """
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        self.document_metadata = {}
        
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/uploads", exist_ok=True)
        
        if os.path.exists("data/vector_store"):
            try:
                self.vector_store = FAISS.load_local("data/vector_store", self.embeddings)
                print("Loaded existing vector store")
                
                if os.path.exists("data/document_metadata.json"):
                    with open("data/document_metadata.json", "r") as f:
                        self.document_metadata = json.load(f)
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vector_store = FAISS.from_texts(["AskAccess initialization"], self.embeddings)
        else:
            self.vector_store = FAISS.from_texts(["AskAccess initialization"], self.embeddings)
    
    def _get_loader_for_file(self, file_path: str):
        """
        Get the appropriate document loader based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            LangChain document loader
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == ".pdf":
            return PyPDFLoader(file_path)
        elif file_extension in [".html", ".htm"]:
            return UnstructuredHTMLLoader(file_path)
        elif file_extension == ".csv":
            return CSVLoader(file_path)
        else:
            return TextLoader(file_path)
    
    def ingest_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Ingest a file into the vector store.
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata for the document
            
        Returns:
            document_id: Unique ID for the ingested document
        """
        try:
            document_id = hashlib.md5(f"{file_path}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            loader = self._get_loader_for_file(file_path)
            documents = loader.load()
            
            base_metadata = {
                "source": file_path,
                "document_id": document_id,
                "ingestion_time": datetime.now().isoformat(),
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            for doc in documents:
                doc.metadata.update(base_metadata)
            
            splits = self.text_splitter.split_documents(documents)
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
            else:
                self.vector_store.add_documents(splits)
            
            self.document_metadata[document_id] = {
                "file_path": file_path,
                "metadata": base_metadata,
                "chunk_count": len(splits),
            }
            
            self._save_state()
            
            return document_id
        
        except Exception as e:
            print(f"Error ingesting document: {e}")
            raise
    
    def ingest_salesforce_data(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Ingest Salesforce case data into the vector store.
        
        Args:
            data: List of Salesforce case dictionaries
            
        Returns:
            List of document IDs
        """
        document_ids = []
        
        for case in data:
            case_id = case.get("CaseNumber", str(case.get("Id", "")))
            document_id = hashlib.md5(f"salesforce_case_{case_id}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            case_text = f"Case Number: {case.get('CaseNumber', 'N/A')}\n"
            case_text += f"Subject: {case.get('Subject', 'N/A')}\n"
            case_text += f"Description: {case.get('Description', 'N/A')}\n"
            case_text += f"Status: {case.get('Status', 'N/A')}\n"
            
            if "Comments" in case and isinstance(case["Comments"], list):
                case_text += "Comments:\n"
                for comment in case["Comments"]:
                    case_text += f"- {comment.get('CommentBody', '')}\n"
            
            metadata = {
                "source": "salesforce",
                "document_id": document_id,
                "case_id": case_id,
                "case_number": case.get("CaseNumber", ""),
                "subject": case.get("Subject", ""),
                "status": case.get("Status", ""),
                "ingestion_time": datetime.now().isoformat(),
            }
            
            texts = self.text_splitter.split_text(case_text)
            
            documents = [
                {"page_content": text, "metadata": metadata}
                for text in texts
            ]
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            self.document_metadata[document_id] = {
                "source": "salesforce",
                "metadata": metadata,
                "chunk_count": len(texts),
            }
            
            document_ids.append(document_id)
        
        self._save_state()
        
        return document_ids
    
    def _save_state(self):
        """Save the vector store and document metadata to disk."""
        if self.vector_store:
            self.vector_store.save_local("data/vector_store")
        
        with open("data/document_metadata.json", "w") as f:
            json.dump(self.document_metadata, f)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of documents with their content and metadata
        """
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for doc, score in results
        ]
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store."""
        return len(self.document_metadata)
