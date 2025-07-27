#!/usr/bin/env python3
"""
Streamlit Web Application for Ask ET
Based on Phase 4 requirements from task_list_next.md
"""

import sys
import os
from pathlib import Path
import streamlit as st
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.rag_chain_improved import create_improved_rag_chain
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Setup Streamlit page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Ask ET - Emerging Technologies Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AskETWebApp:
    """Streamlit web application for Ask ET"""
    
    def __init__(self):
        self.rag_chain = None
        self.initialize_rag_chain()
    
    def initialize_rag_chain(self):
        """Initialize the RAG chain"""
        try:
            with st.spinner("Initializing Ask ET..."):
                self.rag_chain = create_improved_rag_chain()
            st.success("Ask ET is ready!")
            return True
        except Exception as e:
            st.error(f"Error initializing: {e}")
            logger.error(f"Error initializing RAG chain: {e}")
            return False
    
    def setup_sidebar(self):
        """Setup sidebar with controls and information"""
        with st.sidebar:
            st.title("Ask ET")
            st.markdown("AI-powered learning assistant for Emerging Technologies")
            
            # Session controls
            st.subheader("Session Controls")
            if st.button("Clear Chat History"):
                if self.rag_chain:
                    self.rag_chain.clear_memory()
                    st.session_state.messages = []
                    st.success("Chat history cleared!")
            
            # Settings
            st.subheader("Settings")
            st.session_state.max_results = st.slider(
                "Max Results", 
                min_value=1, 
                max_value=10, 
                value=5,
                help="Number of documents to retrieve"
            )
            
            st.session_state.temperature = st.slider(
                "Response Creativity", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.7,
                help="Higher values = more creative responses"
            )
            
            # System info
            st.subheader("System Info")
            st.info(f"Knowledge Base: 114+ blogs, 33+ projects")
            st.info(f"Model: Google Gemini 1.5 Flash")
            st.info(f"Vector DB: FAISS")
            
            # Quick actions
            st.subheader("Quick Actions")
            if st.button("Show About"):
                self.show_about()
    
    def show_about(self):
        """Display about information"""
        st.info("""
        **Ask ET** is an AI-powered learning assistant for Emerging Technologies content.
        
        **Features:**
        - Semantic search across Red Hat content
        - Conversational AI with context awareness
        - Source attribution and reference links
        - Real-time information retrieval
        
        **Technology Stack:**
        - AI Model: Google Gemini 1.5 Flash
        - Vector Database: FAISS
        - Framework: LangChain RAG
        - Embeddings: Google Gemini Embeddings
        """)
    
    def setup_main_interface(self):
        """Setup the main chat interface"""
        st.title("Ask ET - Emerging Technologies Assistant")
        st.markdown("Ask questions about Emerging Technologies, OpenShift, AI/ML, and more!")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message:
                    self.display_sources(message["sources"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about Emerging Technologies..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.process_query(prompt)
                    if response:
                        st.markdown(response["answer"])
                        if "sources" in response:
                            self.display_sources(response["sources"])
                        if "relevant_docs" in response:
                            self.display_relevant_docs(response["relevant_docs"])
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response["answer"],
                            "sources": response.get("sources", "")
                        })
                    else:
                        st.error("Sorry, I couldn't process your question. Please try again.")
    
    def process_query(self, query: str):
        """Process a user query"""
        if not self.rag_chain:
            st.error("RAG chain not initialized")
            return None
        
        try:
            result = self.rag_chain.query(query)
            return result
        except Exception as e:
            st.error(f"Error processing query: {e}")
            logger.error(f"Error processing query: {e}")
            return None
    
    def display_sources(self, sources: str):
        """Display source links"""
        if sources:
            st.markdown("**Sources:**")
            st.markdown(sources)
    
    def display_relevant_docs(self, docs: list):
        """Display relevant documents in an expander"""
        if docs:
            with st.expander("View Retrieved Documents"):
                for i, doc in enumerate(docs[:3], 1):
                    st.markdown(f"**{i}. {doc.get('title', 'Unknown Title')}**")
                    st.markdown(f"Type: {doc.get('type', 'Unknown')}")
                    st.markdown(f"Similarity: {doc.get('similarity_score', 0):.3f}")
                    if doc.get('url'):
                        st.markdown(f"URL: {doc['url']}")
                    st.markdown("---")
    
    def setup_suggested_queries(self):
        """Setup suggested queries panel"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("Suggested Queries")
        
        suggested_queries = [
            "What is OpenShift AI?",
            "Show me projects about edge computing",
            "What are Red Hat's latest AI initiatives?",
            "How do I deploy AI models on OpenShift?",
            "Tell me about Kubernetes and OpenShift differences",
            "What is confidential computing?",
            "Show me blogs about machine learning",
            "What are the latest emerging technologies?"
        ]
        
        for query in suggested_queries:
            if st.sidebar.button(query, key=f"suggest_{query}"):
                st.session_state.suggested_query = query
                st.rerun()
    
    def setup_export_features(self):
        """Setup export functionality"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("Export Options")
        
        if st.sidebar.button("Export Chat History"):
            if st.session_state.messages:
                chat_text = self.format_chat_for_export()
                st.sidebar.download_button(
                    label="Download Chat",
                    data=chat_text,
                    file_name=f"ask_et_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    def format_chat_for_export(self):
        """Format chat history for export"""
        chat_text = "Ask ET Chat History\n"
        chat_text += "=" * 50 + "\n\n"
        
        for message in st.session_state.messages:
            role = message["role"].title()
            content = message["content"]
            chat_text += f"{role}: {content}\n\n"
            
            if "sources" in message and message["sources"]:
                chat_text += f"Sources: {message['sources']}\n\n"
            
            chat_text += "-" * 30 + "\n\n"
        
        return chat_text
    
    def run(self):
        """Run the Streamlit application"""
        self.setup_sidebar()
        self.setup_suggested_queries()
        self.setup_export_features()
        self.setup_main_interface()

def main():
    """Main entry point for the Streamlit app"""
    app = AskETWebApp()
    app.run()

if __name__ == "__main__":
    main() 