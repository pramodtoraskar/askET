#!/usr/bin/env python3
"""
Improved LangChain RAG Chain for Ask ET chatbot
Enhanced with better error handling, content validation, and helpful responses
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import urllib.parse

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
from src.enhanced_response_formatter import create_enhanced_response_formatter

# Setup logging
setup_logging()
logger = get_logger(__name__)

class ImprovedAskETRAGChain:
    """Improved RAG Chain for Ask ET chatbot with better error handling and content validation"""
    
    def __init__(self):
        self.vector_store_path = Path(VECTOR_STORE_PATH)
        self.embeddings = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self.memory = None
        self.metadata = None
        self.available_content = set()
        self.response_formatter = create_enhanced_response_formatter()
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        logger.info("Initializing improved RAG components...")
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Load FAISS index and metadata
        self._load_index_and_metadata()
        
        # Build available content set
        self._build_available_content()
        
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
        
        # Create improved prompt template
        self._create_improved_prompt_template()
        
        # Initialize RAG chain
        self._create_rag_chain()
        
        logger.info("Improved RAG components initialized successfully")
    
    def _load_index_and_metadata(self):
        """Load FAISS index and metadata"""
        try:
            # Load index
            self.index = faiss.read_index(str(self.vector_store_path))
            
            # Load metadata
            metadata_path = self.vector_store_path.parent / f"{self.vector_store_path.stem}_metadata.pkl"
            with open(metadata_path, 'rb') as f:
                metadata_dict = pickle.load(f)
            
            # Handle both dictionary and list formats
            if isinstance(metadata_dict, dict):
                self.metadata = metadata_dict.get('chunk_metadata', [])
            else:
                # Direct list format
                self.metadata = metadata_dict
            
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            logger.info(f"Loaded metadata for {len(self.metadata)} documents")
            
        except Exception as e:
            logger.error(f"Error loading index and metadata: {e}")
            raise
    
    def _build_available_content(self):
        """Build a set of available content URLs and titles for validation"""
        try:
            self.available_content = set()
            
            # Add URLs from metadata
            for doc_metadata in self.metadata:
                if 'source' in doc_metadata:
                    self.available_content.add(doc_metadata['source'])
                if 'title' in doc_metadata:
                    self.available_content.add(doc_metadata['title'].lower())
            
            logger.info(f"Built available content set with {len(self.available_content)} items")
            
        except Exception as e:
            logger.error(f"Error building available content set: {e}")
            self.available_content = set()
    
    def _create_improved_prompt_template(self):
        """Create an improved prompt template with better instructions"""
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""You are Ask ET, an AI assistant for Red Hat Emerging Technologies. You help users learn about AI, cloud computing, security, edge computing, and other emerging technologies based on Red Hat's research and projects.

IMPORTANT INSTRUCTIONS:
1. Base your answers ONLY on the provided context from Red Hat Emerging Technologies blogs and projects
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Always provide helpful guidance even when specific content is missing
4. Suggest related topics or alternative questions when appropriate
5. Be accurate, helpful, and professional
6. Include source references when possible

Context from Red Hat Emerging Technologies content:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""
        )
    
    def _create_rag_chain(self):
        """Create the RAG chain"""
        try:
            # Create FAISS vector store
            self.vector_store = FAISS(
                embedding_function=self.embeddings,
                index=self.index,
                docstore=None,  # We'll handle documents manually
                index_to_docstore_id=None
            )
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": TOP_K_RESULTS}
            )
            
            logger.info("RAG chain created successfully")
            
        except Exception as e:
            logger.error(f"Error creating RAG chain: {e}")
            raise
    
    def _get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant documents with improved error handling"""
        try:
            # Get embeddings for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in FAISS index
            scores, indices = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                TOP_K_RESULTS
            )
            
            # Convert numpy arrays to lists to avoid type issues
            scores = scores.tolist()
            indices = indices.tolist()
            
            relevant_docs = []
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata):
                    doc_metadata = self.metadata[idx].copy()  # Make a copy to avoid modifying original
                    
                    # Add score and index to metadata
                    doc_metadata['score'] = float(score)
                    doc_metadata['index'] = int(idx)
                    
                    relevant_docs.append(doc_metadata)
            
            # Filter out low-quality matches
            relevant_docs = [doc for doc in relevant_docs if doc.get('score', 0) > 0.3]
            
            # Deduplicate by URL to ensure we get different blogs
            unique_docs = []
            seen_urls = set()
            seen_titles = set()
            
            for doc in relevant_docs:
                url = doc.get('url', '')
                title = doc.get('title', '')
                
                # If we have a URL and haven't seen it, add it
                if url and url not in seen_urls:
                    unique_docs.append(doc)
                    seen_urls.add(url)
                    if title:
                        seen_titles.add(title)
                # If no URL but we have a title and haven't seen it, add it
                elif title and title not in seen_titles:
                    unique_docs.append(doc)
                    seen_titles.add(title)
                # If neither URL nor title, add it anyway (might be different content)
                elif not url and not title:
                    unique_docs.append(doc)
            
            # If we still have no unique docs, return the original list (don't filter everything out)
            if not unique_docs and relevant_docs:
                logger.info(f"No unique blogs found, returning original {len(relevant_docs)} documents")
                return relevant_docs
            
            logger.info(f"Found {len(relevant_docs)} relevant documents, {len(unique_docs)} unique blogs")
            return unique_docs
            
        except Exception as e:
            logger.error(f"Error getting relevant documents: {e}")
            return []
    
    def _validate_content_availability(self, query: str) -> Dict[str, Any]:
        """Validate if content is available for the query"""
        query_lower = query.lower()
        
        # Check for specific blog post references
        blog_patterns = [
            r'blog post "([^"]+)"',
            r'article "([^"]+)"',
            r'post "([^"]+)"',
            r'content "([^"]+)"'
        ]
        
        for pattern in blog_patterns:
            match = re.search(pattern, query_lower)
            if match:
                title = match.group(1).lower()
                if title not in self.available_content:
                    return {
                        "available": False,
                        "missing_content": title,
                        "suggestion": f"The specific content '{title}' is not available in the current index. Try asking about the general topic instead."
                    }
        
        # Check for URL references
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, query)
        
        for url in urls:
            if url not in self.available_content:
                return {
                    "available": False,
                    "missing_content": url,
                    "suggestion": f"The URL '{url}' is not available in the current index. Try asking about the general topic instead."
                }
        
        return {"available": True}
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format context with improved structure"""
        if not documents:
            return "No relevant content found."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            title = doc.get('title', 'Unknown Title')
            content = doc.get('content', 'No content available')
            source = doc.get('source', 'Unknown source')
            score = doc.get('score', 0)
            
            # Truncate content if too long
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            context_part = f"""Document {i}:
Title: {title}
Source: {source}
Relevance Score: {score:.3f}
Content: {content}

---"""
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> str:
        """Format sources with improved presentation"""
        if not documents:
            return "No sources available."
        
        sources = []
        
        for doc in documents:
            # Try different possible field names for title
            title = (
                doc.get('title') or 
                doc.get('name') or 
                doc.get('author') or 
                'Unknown Title'
            )
            
            # Try different possible field names for source
            source = (
                doc.get('source') or 
                doc.get('url') or 
                doc.get('author') or 
                doc.get('category') or 
                'Unknown source'
            )
            
            # Get score with fallback
            score = doc.get('score', doc.get('similarity_score', 0))
            
            # Only add if we have meaningful data
            if title != 'Unknown Title' or source != 'Unknown source':
                source_info = f"• {title} ({source}) - Relevance: {score:.3f}"
                sources.append(source_info)
        
        # If no meaningful sources found, return empty
        if not sources:
            return ""
        
        return "\n".join(sources)
    
    def _generate_helpful_response(self, query: str, validation_result: Dict[str, Any]) -> str:
        """Generate a helpful response when content is missing"""
        missing_content = validation_result.get('missing_content', '')
        suggestion = validation_result.get('suggestion', '')
        
        # Extract topic from query
        query_lower = query.lower()
        
        # Common topics mapping
        topic_keywords = {
            'triton': 'GPU programming, AI accelerators, and machine learning optimization',
            'openshift': 'OpenShift platform, container orchestration, and cloud-native applications',
            'ai': 'artificial intelligence, machine learning, and AI applications',
            'ml': 'machine learning, model deployment, and MLOps',
            'kubernetes': 'Kubernetes, container orchestration, and cloud-native technologies',
            'security': 'cybersecurity, confidential computing, and zero trust',
            'edge': 'edge computing, IoT, and distributed systems',
            'cloud': 'cloud computing, hybrid cloud, and cloud-native development'
        }
        
        # Find relevant topic
        relevant_topic = "emerging technologies"
        for keyword, topic in topic_keywords.items():
            if keyword in query_lower:
                relevant_topic = topic
                break
        
        response = f"""I don't have access to the specific content you're asking about: "{missing_content}"

However, I can help you learn about {relevant_topic} based on the available Red Hat Emerging Technologies content.

{suggestion}

Here are some related topics you can ask about:
• General information about {relevant_topic}
• Best practices and implementation guides
• Case studies and real-world applications
• Latest developments and trends

Would you like to ask about any of these topics instead?"""
        
        return response
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the improved RAG chain with better error handling"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Validate content availability
            validation_result = self._validate_content_availability(question)
            
            if not validation_result["available"]:
                helpful_response = self._generate_helpful_response(question, validation_result)
                return {
                    "answer": helpful_response,
                    "sources": [],
                    "context": "Content validation failed",
                    "validation_result": validation_result
                }
            
            # Get relevant documents
            relevant_docs = self._get_relevant_documents(question)
            
            if not relevant_docs:
                return {
                    "answer": """I couldn't find specific information about your question in the available Red Hat Emerging Technologies content.

Here are some suggestions:
• Try rephrasing your question with different keywords
• Ask about broader topics like AI, cloud computing, security, or edge computing
• Request information about specific technologies like OpenShift, Kubernetes, or confidential computing
• Ask for best practices or implementation guides

What would you like to learn about?""",
                    "sources": [],
                    "context": "No relevant documents found."
                }
            
            # Format context
            context = self._format_context(relevant_docs)
            
            # Create enhanced response with blog summaries and GitHub projects
            enhanced_response = self.response_formatter.format_enhanced_response(
                question, relevant_docs, ""
            )
            
            # Create prompt
            prompt = self.prompt_template.format(
                context=context,
                question=question,
                chat_history=""
            )
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            # Handle different response formats
            if hasattr(response, 'content'):
                answer = response.content
            elif hasattr(response, 'text'):
                answer = response.text
            elif hasattr(response, 'message'):
                answer = response.message.content if hasattr(response.message, 'content') else str(response.message)
            else:
                answer = str(response)
            
            # Update enhanced response with the actual answer
            enhanced_response = self.response_formatter.format_enhanced_response(
                question, relevant_docs, answer
            )
            
            # Format sources
            sources = self._format_sources(relevant_docs)
            
            return {
                "answer": answer,
                "sources": sources,
                "context": context,
                "relevant_docs": relevant_docs,
                "validation_result": validation_result,
                "enhanced_response": enhanced_response
            }
            
        except Exception as e:
            logger.error(f"Error in improved RAG query: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "answer": f"""I encountered an error while processing your question. This might be due to:
• Network connectivity issues
• Service availability problems
• Content indexing issues

Please try:
1. Rephrasing your question
2. Asking about a different topic
3. Trying again in a few moments

Error details: {str(e)}""",
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
    
    def get_available_topics(self) -> List[str]:
        """Get list of available topics"""
        topics = set()
        
        for doc in self.metadata:
            if 'title' in doc:
                title = doc['title'].lower()
                # Extract key topics from titles
                if 'ai' in title or 'machine learning' in title:
                    topics.add('AI & Machine Learning')
                if 'openshift' in title or 'kubernetes' in title:
                    topics.add('Cloud & Containers')
                if 'security' in title or 'confidential' in title:
                    topics.add('Security & Trust')
                if 'edge' in title or 'iot' in title:
                    topics.add('Edge Computing')
                if 'quantum' in title:
                    topics.add('Quantum Computing')
                if 'blockchain' in title:
                    topics.add('Blockchain')
                if 'triton' in title:
                    topics.add('GPU Programming')
        
        return sorted(list(topics))

def create_improved_rag_chain() -> ImprovedAskETRAGChain:
    """Factory function to create improved RAG chain"""
    return ImprovedAskETRAGChain()

if __name__ == "__main__":
    # Test the improved RAG chain
    print("Testing Improved RAG Chain...")
    
    try:
        rag_chain = create_improved_rag_chain()
        
        # Test queries
        test_queries = [
            "What is OpenShift AI?",
            "Tell me about the blog post 'Understanding Triton Cache: Optimizing GPU Kernel Compilation'",
            "What are the latest AI initiatives?",
            "How do I deploy AI models on OpenShift?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            
            result = rag_chain.query(query)
            
            print(f"Answer: {result['answer']}")
            print(f"\nSources:\n{result['sources']}")
            
            if 'validation_result' in result:
                print(f"\nValidation: {result['validation_result']}")
        
        # Show available topics
        print(f"\n{'='*60}")
        print("Available Topics:")
        print(f"{'='*60}")
        topics = rag_chain.get_available_topics()
        for topic in topics:
            print(f"• {topic}")
        
    except Exception as e:
        print(f"Error testing improved RAG chain: {e}")
        logger.error(f"Error testing improved RAG chain: {e}") 