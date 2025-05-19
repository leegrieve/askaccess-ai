"""
Mock implementation of OpenAI API for testing purposes.
"""
import random
from typing import List, Dict, Any

class MockEmbeddings:
    """Mock implementation of OpenAI embeddings."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock embeddings."""
        pass
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return mock embeddings for the given texts."""
        return [[random.random() for _ in range(1536)] for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Return mock embeddings for the given query."""
        return [random.random() for _ in range(1536)]
    
    def __call__(self, text: str) -> List[float]:
        """Make the class callable to support legacy interface."""
        return self.embed_query(text)

class MockOpenAI:
    """Mock implementation of OpenAI API."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock OpenAI API."""
        pass
    
    def create(self, *args, **kwargs) -> Dict[str, Any]:
        """Return mock response for the given query."""
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a mock response from the OpenAI API."
                    }
                }
            ]
        }
        
    def invoke(self, *args, **kwargs) -> Dict[str, Any]:
        """Return mock response for the given query."""
        return {
            "content": "This is a mock response from the OpenAI API."
        }

def patch_langchain_openai():
    """Patch langchain_openai to use mock implementations."""
    import sys
    from unittest.mock import MagicMock
    
    mock_openai = MagicMock()
    mock_openai.OpenAIEmbeddings = MockEmbeddings
    mock_openai.ChatOpenAI = MockOpenAI
    
    sys.modules['langchain_openai'] = mock_openai
    sys.modules['langchain_openai.embeddings'] = MagicMock()
    sys.modules['langchain_openai.embeddings.base'] = MagicMock()
    sys.modules['openai'] = MagicMock()
