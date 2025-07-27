#!/usr/bin/env python3
"""
Minimal Streamlit Web Application for Ask ET
Inspired by Red Hat Emerging Technologies blog homepage design
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
    initial_sidebar_state="collapsed"
)

# Custom CSS for Red Hat Emerging Technologies inspired design
st.markdown("""
<style>
/* Global Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Reset and base styles */
.main .block-container {
    padding-top: 0;
    padding-bottom: 0;
    max-width: 100%;
}

/* Header Styles */
.header {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 1.5rem 0;
    margin: -1rem -1rem 0 -1rem;
    border-bottom: 4px solid #e31e24;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: white;
    font-weight: 700;
    font-size: 1.4rem;
    text-decoration: none;
}

.logo-icon {
    color: #e31e24;
    font-size: 1.8rem;
    background: white;
    border-radius: 50%;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(227, 30, 36, 0.3);
}

.nav-links {
    display: flex;
    gap: 2.5rem;
    color: white;
}

.nav-link {
    color: #e5e7eb;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem;
    border-radius: 4px;
}

.nav-link:hover {
    color: white;
    background: rgba(227, 30, 36, 0.1);
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #ec4899 100%);
    padding: 6rem 2rem;
    margin: 0 -1rem 4rem -1rem;
    text-align: center;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.4;
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 800px;
    margin: 0 auto;
}

.hero h1 {
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    line-height: 1.1;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.hero p {
    font-size: 1.4rem;
    font-weight: 300;
    margin-bottom: 3rem;
    opacity: 0.95;
    line-height: 1.6;
}

/* Button Styles */
.btn {
    display: inline-block;
    padding: 1rem 2.5rem;
    background: white;
    color: #1a1a1a;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    border: 2px solid white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn:hover {
    background: transparent;
    color: white;
    border-color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

/* Content Sections */
.section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 4rem 2rem;
}

.section-title {
    font-size: 3rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 1rem;
    text-align: center;
    line-height: 1.2;
}

.section-subtitle {
    font-size: 1.2rem;
    color: #6b7280;
    text-align: center;
    margin-bottom: 4rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

/* Quick Actions */
.quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.quick-action-btn {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    font-size: 1rem;
    color: #374151;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.quick-action-btn:hover {
    border-color: #e31e24;
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(227, 30, 36, 0.15);
    color: #e31e24;
}

/* Chat Interface */
.chat-section {
    background: #f8fafc;
    border-radius: 16px;
    padding: 3rem;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.chat-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}

.chat-messages {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

.message {
    margin-bottom: 1.5rem;
    padding: 1.2rem;
    border-radius: 8px;
    line-height: 1.6;
}

.message.user {
    background: linear-gradient(135deg, #e31e24 0%, #dc2626 100%);
    color: white;
    margin-left: 3rem;
    box-shadow: 0 2px 8px rgba(227, 30, 36, 0.2);
}

.message.assistant {
    background: white;
    border: 1px solid #e5e7eb;
    margin-right: 3rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.message strong {
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: block;
}

/* Chat Input */
.chat-input-container {
    display: flex;
    gap: 1rem;
    align-items: center;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.chat-input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 1rem;
    padding: 0.75rem;
    background: transparent;
}

.chat-input:focus {
    outline: none;
}

.send-btn {
    background: #e31e24;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.send-btn:hover {
    background: #dc2626;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(227, 30, 36, 0.3);
}

/* Clear Chat Button */
.clear-chat-btn {
    background: #6b7280;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 1rem;
}

.clear-chat-btn:hover {
    background: #4b5563;
}

/* Footer */
.footer {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    padding: 3rem 2rem;
    margin: 4rem -1rem -1rem -1rem;
    text-align: center;
    border-top: 4px solid #e31e24;
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
}

.footer p {
    margin: 0.5rem 0;
    opacity: 0.9;
    font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero h1 {
        font-size: 2.5rem;
    }
    
    .hero p {
        font-size: 1.1rem;
    }
    
    .section-title {
        font-size: 2.2rem;
    }
    
    .nav-links {
        display: none;
    }
    
    .quick-actions-grid {
        grid-template-columns: 1fr;
    }
    
    .chat-input-container {
        flex-direction: column;
    }
    
    .message.user {
        margin-left: 1rem;
    }
    
    .message.assistant {
        margin-right: 1rem;
    }
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #e31e24;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #c41e3a;
}

/* Streamlit specific overrides */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input {
    border-radius: 8px;
    border: 2px solid #e5e7eb;
    padding: 0.75rem;
    font-size: 1rem;
}

.stTextInput > div > div > input:focus {
    border-color: #e31e24;
    box-shadow: 0 0 0 3px rgba(227, 30, 36, 0.1);
}
</style>
""", unsafe_allow_html=True)

class AskETMinimalWebApp:
    """Minimal Streamlit web application for Ask ET"""
    
    def __init__(self):
        self.rag_chain = None
        self.initialize_rag_chain()
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "show_about" not in st.session_state:
            st.session_state.show_about = False
    
    def initialize_rag_chain(self):
        """Initialize the RAG chain"""
        try:
            with st.spinner("Initializing Ask ET..."):
                self.rag_chain = create_improved_rag_chain()
            return True
        except Exception as e:
            st.error(f"Error initializing: {e}")
            logger.error(f"Error initializing RAG chain: {e}")
            return False
    
    def render_header(self):
        """Render the header section"""
        st.markdown("""
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon"></div>
                    Ask ET
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_hero(self):
        """Render the hero section"""
        st.markdown("""
        <div class="hero">
            <div class="hero-content">
                <h1>Ask ET</h1>
                <p>AI-powered learning assistant! Ask questions about Emerging Technologies, OpenShift, AI/ML, and more</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_quick_actions(self):
        """Render quick action buttons"""
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Quick Actions</h2>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Get started with these common questions</p>', unsafe_allow_html=True)
        
        # Create a custom grid layout for better visual appeal
        st.markdown('<div class="quick-actions-grid">', unsafe_allow_html=True)
        
        # First row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("What is OpenShift AI?", key="qa1", use_container_width=True):
                st.session_state.quick_query = "What is OpenShift AI?"
                st.rerun()
        
        with col2:
            if st.button("Edge Computing Projects", key="qa2", use_container_width=True):
                st.session_state.quick_query = "Show me projects about edge computing"
                st.rerun()
        
        with col3:
            if st.button("Latest AI Initiatives", key="qa3", use_container_width=True):
                st.session_state.quick_query = "What are the latest AI initiatives?"
                st.rerun()
        
        # Second row
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("ML Deployment", key="qa4", use_container_width=True):
                st.session_state.quick_query = "How do I deploy AI models on OpenShift?"
                st.rerun()
        
        with col5:
            if st.button("K8s vs OpenShift", key="qa5", use_container_width=True):
                st.session_state.quick_query = "What's the difference between Kubernetes and OpenShift?"
                st.rerun()
        
        with col6:
            if st.button("Confidential Computing", key="qa6", use_container_width=True):
                st.session_state.quick_query = "What is confidential computing?"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_chat_interface(self):
        """Render the chat interface"""
        # st.markdown('<div class="section">', unsafe_allow_html=True)
        # st.markdown('<h2 class="section-title">Chat with Ask ET</h2>', unsafe_allow_html=True)
        # st.markdown('<p class="section-subtitle">Ask questions about Emerging Technologies, OpenShift, AI/ML, and more</p>', unsafe_allow_html=True)

        # Handle quick queries
        if "quick_query" in st.session_state:
            query = st.session_state.quick_query
            del st.session_state.quick_query
            self.process_user_query(query)
        
        # Chat section with better styling
        st.markdown('<div class="chat-section">', unsafe_allow_html=True)
        
        # Display chat messages
        if st.session_state.messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="message user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="message assistant"><strong>Ask ET:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear chat button
            if st.button("Clear Chat", key="clear_chat"):
                st.session_state.messages = []
                if self.rag_chain:
                    self.rag_chain.clear_memory()
                st.rerun()
        
        # Chat input with better styling
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        
        # Use columns for better layout
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("", key="chat_input", placeholder="Type your question here...", label_visibility="collapsed")
        with col2:
            if st.button("Send", key="send_button", use_container_width=True):
                if user_input:
                    self.process_user_query(user_input)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def process_user_query(self, query):
        """Process a user query"""
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Get response
        if self.rag_chain:
            try:
                with st.spinner("Thinking..."):
                    response = self.rag_chain.query(query)
                    if response and "answer" in response:
                        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I couldn't process your question. Please try again."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "RAG chain not initialized. Please try again."})
    
    def render_footer(self):
        """Render the footer"""
        st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <p>Ask ET - AI-powered learning assistant for Emerging Technologies</p>
                <p>Built with Streamlit and Google Gemini</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the minimal Streamlit application"""
        self.render_header()
        self.render_hero()
        #self.render_quick_actions()
        self.render_chat_interface()
        self.render_footer()

def main():
    """Main entry point for the minimal Streamlit app"""
    app = AskETMinimalWebApp()
    app.run()

if __name__ == "__main__":
    main() 