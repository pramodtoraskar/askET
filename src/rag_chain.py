#!/usr/bin/env python3
"""
LangChain RAG Chain for Ask ET chatbot
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import pickle
import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from config import (
    VECTOR_STORE_PATH, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    TOP_K_RESULTS,
    MAX_TOKENS,
    TEMPERATURE
)
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class AskETRAGChain:
    """RAG Chain for Ask ET chatbot"""
    
    def __init__(self):
        self.vector_store_path = Path(VECTOR_STORE_PATH)
        self.embeddings = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self.memory = None
        self.metadata = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        logger.info("Initializing RAG components...")
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Load FAISS index and metadata
        self._load_index_and_metadata()
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_TOKENS
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create custom prompt template
        self._create_prompt_template()
        
        # Initialize RAG chain
        self._create_rag_chain()
        
        logger.info("RAG components initialized successfully")
    
    def _load_index_and_metadata(self):
        """Load FAISS index and metadata"""
        try:
            # Load index
            self.index = faiss.read_index(str(self.vector_store_path))
            
            # Load metadata
            metadata_path = self.vector_store_path.parent / f"{self.vector_store_path.stem}_metadata.pkl"
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Loaded index with {self.index.ntotal} vectors and {len(self.metadata)} metadata entries")
            
        except Exception as e:
            logger.error(f"Error loading index and metadata: {e}")
            raise
    
    def _create_prompt_template(self):
        """Create custom prompt template for the chatbot"""
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""You are Ask ET, an AI assistant specialized in Red Hat Emerging Technologies content. 
You help users learn about Red Hat's latest technologies, projects, and blog posts.

Use the following context to answer the user's question. If you don't know the answer, say so. 
Always provide specific references to the source documents when possible.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""
        )
    
    def _create_rag_chain(self):
        """Create the conversational retrieval chain"""
        # Simplified approach - we'll handle retrieval manually
        pass
    
    def _get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant documents for a query"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_vector, TOP_K_RESULTS)
            
            # Get relevant documents
            relevant_docs = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata):
                    doc = self.metadata[idx].copy()
                    doc['similarity_score'] = 1 - distance  # Convert distance to similarity
                    relevant_docs.append(doc)
            
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents into context string"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            if doc['type'] == 'blog':
                # Handle missing fields safely
                title = doc.get('title', 'Unknown Title')
                author = doc.get('author', 'Unknown Author')
                date = doc.get('date', 'Unknown Date')
                category = doc.get('category', 'Unknown Category')
                content = doc.get('content', 'No content available')
                url = doc.get('url', 'No URL available')
                similarity = doc.get('similarity_score', 0.0)
                
                context_parts.append(f"""
Document {i} (Blog):
Title: {title}
Author: {author}
Date: {date}
Category: {category}
Content: {content[:500]}...
URL: {url}
Similarity: {similarity:.3f}
""")
            elif doc['type'] == 'project':
                # Handle missing fields safely
                title = doc.get('title', 'Unknown Project')
                category = doc.get('category', 'Unknown Category')
                description = doc.get('description', 'No description available')
                github_links = doc.get('github_links', [])
                similarity = doc.get('similarity_score', 0.0)
                
                context_parts.append(f"""
Document {i} (Project):
Name: {title}
Category: {category}
Description: {description}
GitHub Links: {', '.join(github_links) if github_links else 'No GitHub links available'}
Similarity: {similarity:.3f}
""")
        
        return "\n".join(context_parts)
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> str:
        """Format source references"""
        if not documents:
            return ""
        
        sources = []
        for i, doc in enumerate(documents, 1):
            if doc['type'] == 'blog':
                title = doc.get('title', 'Unknown Title')
                url = doc.get('url', 'No URL available')
                sources.append(f"{i}. **{title}** - {url}")
            elif doc['type'] == 'project':
                title = doc.get('title', 'Unknown Project')
                github_links = doc.get('github_links', [])
                if github_links:
                    github_links_str = ', '.join(github_links)
                    sources.append(f"{i}. **{title}** - GitHub: {github_links_str}")
                else:
                    sources.append(f"{i}. **{title}** - No GitHub links available")
        
        return "\n".join(sources)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG chain"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Get relevant documents
            relevant_docs = self._get_relevant_documents(question)
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find any relevant information in the Red Hat Emerging Technologies content for your question. Please try rephrasing your query or ask about a different topic.",
                    "sources": [],
                    "context": "No relevant documents found."
                }
            
            # Format context
            context = self._format_context(relevant_docs)
            
            # Create a simplified chain call
            # Note: We're using a simplified approach since the full ConversationalRetrievalChain
            # might have issues with our custom document format
            prompt = self.prompt_template.format(
                context=context,
                question=question,
                chat_history=""
            )
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            # Debug response
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response attributes: {dir(response)}")
            
            # Handle different response formats
            if hasattr(response, 'content'):
                answer = response.content
            elif hasattr(response, 'text'):
                answer = response.text
            elif hasattr(response, 'message'):
                answer = response.message.content if hasattr(response.message, 'content') else str(response.message)
            else:
                answer = str(response)
            
            # Format sources
            sources = self._format_sources(relevant_docs)
            
            return {
                "answer": answer,
                "sources": sources,
                "context": context,
                "relevant_docs": relevant_docs
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}. Please try again.",
                "sources": [],
                "context": "",
                "error": str(e)
            }
    
    def get_chat_history(self) -> List[str]:
        """Get current chat history"""
        return self.memory.chat_memory.messages if self.memory else []
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
            logger.info("Conversation memory cleared")

def create_rag_chain() -> AskETRAGChain:
    """Factory function to create RAG chain"""
    return AskETRAGChain()

if __name__ == "__main__":
    # Test the RAG chain
    print("Testing RAG Chain...")
    
    try:
        rag_chain = create_rag_chain()
        
        # Test query
        test_question = "What does Red Hat say about OpenShift AI?"
        print(f"Query: {test_question}")
        
        result = rag_chain.query(test_question)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources:\n{result['sources']}")
        
    except Exception as e:
        print(f"Error testing RAG chain: {e}")
        logger.error(f"Error testing RAG chain: {e}") 