from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional
import os
import time

class ResponseGenerator:
    """
    Generates responses to user queries using OpenAI's GPT model.
    """
    
    def __init__(self, document_store, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the response generator with document store and LLM.
        
        Args:
            document_store: Document store for retrieval
            openai_api_key: API key for OpenAI
            model_name: Model name for OpenAI
        """
        self.document_store = document_store
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,
            openai_api_key=openai_api_key
        )
        
        self.prompt_template = """
        You are AskAccess, an AI assistant for Access Group employees and customers.
        Answer the question based only on the following context:
        
        {context}
        
        Question: {question}
        
        Provide a concise and accurate answer. If the context doesn't contain the information needed to answer the question, say "I don't have enough information to answer this question based on the available knowledge base."
        """
        
        self.PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def generate_response(self, query: str, retrieved_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response to a query using the retrieved documents.
        
        Args:
            query: Query string
            retrieved_documents: List of retrieved documents
        
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            if not retrieved_documents:
                return {
                    "answer": "I don't have enough information to answer this question based on the available knowledge base.",
                    "sources": [],
                    "processing_time": time.time() - start_time
                }
            
            chain_type_kwargs = {"prompt": self.PROMPT}
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.document_store.vector_store.as_retriever(),
                chain_type_kwargs=chain_type_kwargs,
                return_source_documents=True
            )
            
            chain_response = qa_chain({"query": query})
            answer = chain_response["result"]
            
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in chain_response["source_documents"]
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": time.time() - start_time
            }
        
        except Exception as e:
            return {
                "error": f"Error generating response: {str(e)}",
                "processing_time": time.time() - start_time
            }
