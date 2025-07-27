#!/usr/bin/env python3
"""
Advanced Streamlit Web Application for Ask ET
Based on Phase 4 requirements from task_list_next.md
"""

import sys
import os
from pathlib import Path
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.rag_chain_improved import create_improved_rag_chain
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Setup Streamlit page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Ask ET Enterprise - AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise-grade CSS styling following Red Hat brand standards
st.markdown("""
<style>
/* Red Hat Brand Colors */
:root {
    --redhat-red: #EE0000;
    --redhat-dark-red: #CC0000;
    --redhat-black: #151515;
    --redhat-dark-gray: #333333;
    --redhat-gray: #666666;
    --redhat-light-gray: #F5F5F5;
    --redhat-white: #FFFFFF;
    --redhat-blue: #0066CC;
    --redhat-light-blue: #E6F3FF;
    --redhat-green: #3F9C35;
    --redhat-yellow: #F0AB00;
    --redhat-orange: #EC7A08;
}

/* Global Styles */
* {
    font-family: 'Red Hat Display', 'Overpass', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Main Container */
.main .block-container {
    max-width: 1200px;
    padding: 0;
    margin: 0 auto;
}

/* Header Section */
.enterprise-header {
    background: linear-gradient(135deg, var(--redhat-black) 0%, var(--redhat-dark-gray) 100%);
    padding: 2rem 0;
    margin: -1rem -1rem 2rem -1rem;
    border-bottom: 4px solid var(--redhat-red);
    position: relative;
}

.enterprise-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}

.header-content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: var(--redhat-white);
}

.header-content h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: var(--redhat-white);
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header-content .subtitle {
    font-size: 1.2rem;
    font-weight: 400;
    color: rgba(255,255,255,0.9);
    margin-bottom: 1rem;
}

.header-content .tagline {
    font-size: 1rem;
    color: rgba(255,255,255,0.7);
    font-weight: 300;
}

/* Chat Interface */
.chat-interface {
    background: var(--redhat-white);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin: 2rem 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 500px;
}

.chat-messages {
    padding: 2rem;
    flex: 1;
    overflow-y: auto;
    background: #FAFAFA;
    min-height: 300px;
}

/* Standalone Chat Input */
.chat-input-standalone {
    background: var(--redhat-white);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin: 2rem 0;
    padding: 2rem;
    text-align: center;
}

.chat-input-standalone .stTextInput {
    max-width: 600px;
    margin: 0 auto;
}



.message {
    margin-bottom: 1.5rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
}

.message.user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
}

.message-avatar.user {
    background: var(--redhat-blue);
}

.message-avatar.assistant {
    background: var(--redhat-red);
}

.message-content {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    max-width: 80%;
    border-left: 4px solid var(--redhat-blue);
}

.message.user .message-content {
    background: var(--redhat-light-blue);
    border-left: 4px solid var(--redhat-blue);
}

.message.assistant .message-content {
    background: white;
    border-left: 4px solid var(--redhat-red);
}

/* Quick Actions */
.quick-actions {
    background: var(--redhat-light-gray);
    padding: 1.5rem;
    border-bottom: 1px solid #E0E0E0;
}

.quick-actions h3 {
    color: var(--redhat-dark-gray);
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.quick-button {
    background: white;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    margin: 0.25rem;
    color: var(--redhat-dark-gray);
    font-weight: 500;
    transition: all 0.2s ease;
    cursor: pointer;
    display: inline-block;
    text-decoration: none;
}

.quick-button:hover {
    border-color: var(--redhat-red);
    color: var(--redhat-red);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(238,0,0,0.15);
}

/* Input Area */
.chat-input-area {
    padding: 1.5rem;
    background: white;
    border-top: 1px solid #E0E0E0;
    margin-top: 2rem;
}

.chat-input {
    width: 100%;
    padding: 1rem 1.5rem;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s ease;
    background: white;
}

.chat-input:focus {
    outline: none;
    border-color: var(--redhat-red);
    box-shadow: 0 0 0 3px rgba(238,0,0,0.1);
}

/* Sidebar Styling */
.sidebar .sidebar-content {
    background: var(--redhat-light-gray);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.sidebar h3 {
    color: var(--redhat-dark-gray);
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    border-bottom: 2px solid var(--redhat-red);
    padding-bottom: 0.5rem;
}

/* Status Indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.9rem;
}

.status-indicator.success {
    background: rgba(63, 156, 53, 0.1);
    color: var(--redhat-green);
    border: 1px solid rgba(63, 156, 53, 0.3);
}

.status-indicator.error {
    background: rgba(238, 0, 0, 0.1);
    color: var(--redhat-red);
    border: 1px solid rgba(238, 0, 0, 0.3);
}

.status-indicator.warning {
    background: rgba(240, 171, 0, 0.1);
    color: var(--redhat-yellow);
    border: 1px solid rgba(240, 171, 0, 0.3);
}

/* Source Links */
.source-link {
    color: var(--redhat-blue);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.source-link:hover {
    color: var(--redhat-dark-red);
    text-decoration: underline;
}

/* Analytics Cards */
.analytics-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin-bottom: 1rem;
}

.analytics-card h4 {
    color: var(--redhat-dark-gray);
    font-weight: 600;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content h1 {
        font-size: 2rem;
    }
    
    .message-content {
        max-width: 90%;
    }
    
    .quick-button {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
}

/* Loading Animation */
.loading-dots {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 20px;
}

.loading-dots div {
    position: absolute;
    top: 8px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--redhat-red);
    animation: loading-dots 1.2s linear infinite;
}

.loading-dots div:nth-child(1) {
    left: 8px;
    animation-delay: 0s;
}

.loading-dots div:nth-child(2) {
    left: 32px;
    animation-delay: 0.2s;
}

.loading-dots div:nth-child(3) {
    left: 56px;
    animation-delay: 0.4s;
}

@keyframes loading-dots {
    0%, 80%, 100% {
        transform: scale(0);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Enterprise Footer */
.enterprise-footer {
    background: var(--redhat-black);
    color: var(--redhat-white);
    padding: 2rem 0;
    margin: 2rem -1rem -1rem -1rem;
    text-align: center;
    font-size: 0.9rem;
    position: relative;
    z-index: 10;
}

.enterprise-footer a {
    color: var(--redhat-red);
    text-decoration: none;
}

.enterprise-footer a:hover {
    text-decoration: underline;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #ec4899 100%);
    padding: 4rem 2rem;
    margin: 0 -1rem 3rem -1rem;
    text-align: center;
    color: white;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 20px 20px;
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
    max-width: 600px;
    margin: 0 auto;
}

.hero h1 {
    font-size: 3.5rem;
    font-weight: 900;
    margin-bottom: 1rem;
    line-height: 1.1;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    letter-spacing: 2px;
}

.hero .subtitle {
    font-size: 1.2rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
    opacity: 0.95;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.hero .tagline {
    font-size: 1rem;
    font-weight: 300;
    opacity: 0.8;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

</style>
""", unsafe_allow_html=True)

class AskETAdvancedWebApp:
    """Advanced Streamlit web application for Ask ET"""
    
    def __init__(self):
        self.rag_chain = None
        self.initialize_rag_chain()
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = {
                "response_style": "detailed",
                "show_sources": True,
                "show_similarity": False,
                "auto_suggest": True
            }
        if "chat_stats" not in st.session_state:
            st.session_state.chat_stats = {
                "total_queries": 0,
                "session_start": datetime.now(),
                "topics": []
            }
    
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
    
    def setup_sidebar(self):
        """Setup advanced sidebar with controls and information"""
        with st.sidebar:
            # Navigation
            st.subheader("Navigation")
            page = st.selectbox(
                "Choose a page",
                ["Chat", "Analytics", "Settings", "About"]
            )
            
            if page == "Chat":
                self.show_chat_sidebar()
            elif page == "Analytics":
                self.show_analytics_sidebar()
            elif page == "Settings":
                self.show_settings_sidebar()
            elif page == "About":
                self.show_about_sidebar()
    
    def show_chat_sidebar(self):
        """Show chat-specific sidebar controls"""
        # Session controls
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🔄 Session Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                if self.rag_chain:
                    self.rag_chain.clear_memory()
                    st.session_state.messages = []
                    st.success("Chat cleared!")
        
        with col2:
            if st.button("Export Chat", use_container_width=True):
                self.export_chat_history()
        
        # Quick filters
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🔍 Content Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        content_type = st.multiselect(
            "Content Type",
            ["Blog Posts", "GitHub Projects", "Documentation"],
            default=["Blog Posts", "GitHub Projects"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=365), datetime.now()),
            help="Filter content by date range"
        )
        
        # Chat Statistics
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>📊 Chat Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        total_queries = st.session_state.chat_stats["total_queries"]
        avg_response_time = st.session_state.chat_stats.get("avg_response_time", 0)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Queries", total_queries)
        with col2:
            st.metric("Avg Response", f"{avg_response_time:.2f}s")
        
        # Suggested queries
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>⚡ Quick Queries</h3>
        </div>
        """, unsafe_allow_html=True)
        self.setup_quick_queries()
    
    def show_analytics_sidebar(self):
        """Show analytics sidebar"""
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>📈 Analytics Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Time period
        period = st.selectbox(
            "Time Period",
            ["This Session", "Last 7 Days", "Last 30 Days", "All Time"]
        )
        
        # Chart type
        chart_type = st.selectbox(
            "Chart Type",
            ["Topic Distribution", "Query Frequency", "Response Time", "User Engagement"]
        )
        
        if st.button("Generate Analytics", use_container_width=True):
            self.generate_analytics(period, chart_type)
    
    def show_settings_sidebar(self):
        """Show settings sidebar"""
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>⚙️ User Preferences</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Response style
        st.session_state.user_preferences["response_style"] = st.selectbox(
            "Response Style",
            ["detailed", "concise", "technical", "beginner-friendly"],
            help="Choose how detailed responses should be"
        )
        
        # Display options
        st.session_state.user_preferences["show_sources"] = st.checkbox(
            "Show Sources", 
            value=st.session_state.user_preferences["show_sources"]
        )
        
        st.session_state.user_preferences["show_similarity"] = st.checkbox(
            "Show Similarity Scores", 
            value=st.session_state.user_preferences["show_similarity"]
        )
        
        st.session_state.user_preferences["auto_suggest"] = st.checkbox(
            "Auto-suggest Follow-up Questions", 
            value=st.session_state.user_preferences["auto_suggest"]
        )
        
        # Model settings
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🤖 Model Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        temperature = st.slider(
            "Creativity", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.7,
            help="Higher values = more creative responses"
        )
        
        max_results = st.slider(
            "Max Results", 
            min_value=1, 
            max_value=10, 
            value=5,
            help="Number of documents to retrieve"
        )
    
    def show_about_sidebar(self):
        """Show about information"""
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>ℹ️ About Ask ET</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.info("""
        **Ask ET Enterprise** is an AI-powered learning assistant for Emerging Technologies content.
        
        **Current Features:**
        - Semantic search across 114+ blogs and 33+ projects
        - Conversational AI with context awareness
        - Source attribution and reference links
        - Real-time information retrieval
        - Advanced analytics and insights
        
        **Technology Stack:**
        - AI Model: Google Gemini 1.5 Flash
        - Vector Database: FAISS
        - Framework: LangChain RAG
        - Web Interface: Streamlit
        """)
        
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🔧 System Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if self.rag_chain:
            st.sidebar.markdown("""
            <div class="status-indicator success">
                ✅ RAG Chain: Active
            </div>
            """, unsafe_allow_html=True)
            st.sidebar.markdown("""
            <div class="status-indicator success">
                ✅ Vector DB: Connected
            </div>
            """, unsafe_allow_html=True)
            st.sidebar.markdown("""
            <div class="status-indicator success">
                ✅ AI Model: Ready
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""
            <div class="status-indicator error">
                ❌ System: Not Initialized
            </div>
            """, unsafe_allow_html=True)
    
    def setup_quick_queries(self):
        """Setup quick query buttons"""
        quick_queries = {
            "OpenShift AI": "What is OpenShift AI?",
            "Edge Computing": "Show me projects about edge computing",
            "AI Initiatives": "What are the latest AI initiatives?",
            "ML Deployment": "How do I deploy AI models on OpenShift?",
            "K8s vs OpenShift": "What's the difference between Kubernetes and OpenShift?",
            "Confidential Computing": "What is confidential computing?",
            "Machine Learning": "Show me blogs about machine learning",
            "Emerging Tech": "What are the latest emerging technologies?"
        }
        
        for label, query in quick_queries.items():
            if st.button(label, key=f"quick_{label}"):
                st.session_state.quick_query = query
    
    def setup_main_interface(self):
        """Setup the main chat interface"""
        st.markdown("""
        <div class="hero">
            <div class="hero-content">
                <h1>ASK ET</h1>
                <div class="subtitle">AI-Powered Knowledge Assistant</div>
                <div class="tagline">Red Hat Emerging Technologies</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Quick Actions Section
        # st.markdown("""
        # <div class="quick-actions">
        #     <h3>Quick Actions</h3>
        # </div>
        # """, unsafe_allow_html=True)
        #
        # # Setup quick query buttons
        # col1, col2, col3, col4 = st.columns(4)
        # quick_queries = {
        #     "OpenShift AI": "What is OpenShift AI?",
        #     "Edge Computing": "Show me projects about edge computing",
        #     "AI Initiatives": "What are the latest AI initiatives?",
        #     "ML Deployment": "How do I deploy AI models on OpenShift?",
        #     "K8s vs OpenShift": "What's the difference between Kubernetes and OpenShift?",
        #     "Confidential Computing": "What is confidential computing?",
        #     "Machine Learning": "Show me blogs about machine learning",
        #     "Emerging Tech": "What are the latest emerging technologies?"
        # }
        #
        # with col1:
        #     if st.button("OpenShift AI", key="quick_1"):
        #         st.session_state.quick_query = quick_queries["OpenShift AI"]
        #         st.rerun()
        #     if st.button("Edge Computing", key="quick_2"):
        #         st.session_state.quick_query = quick_queries["Edge Computing"]
        #         st.rerun()
        #
        # with col2:
        #     if st.button("AI Initiatives", key="quick_3"):
        #         st.session_state.quick_query = quick_queries["AI Initiatives"]
        #         st.rerun()
        #     if st.button("ML Deployment", key="quick_4"):
        #         st.session_state.quick_query = quick_queries["ML Deployment"]
        #         st.rerun()
        #
        # with col3:
        #     if st.button("K8s vs OpenShift", key="quick_5"):
        #         st.session_state.quick_query = quick_queries["K8s vs OpenShift"]
        #         st.rerun()
        #     if st.button("Confidential Computing", key="quick_6"):
        #         st.session_state.quick_query = quick_queries["Confidential Computing"]
        #         st.rerun()
        #
        # with col4:
        #     if st.button("Machine Learning", key="quick_7"):
        #         st.session_state.quick_query = quick_queries["Machine Learning"]
        #         st.rerun()
        #     if st.button("Emerging Tech", key="quick_8"):
        #         st.session_state.quick_query = quick_queries["Emerging Tech"]
        #         st.rerun()
        
        # Chat Interface Container - Only show if there are messages
        if st.session_state.messages:
            st.markdown('<div class="chat-interface">', unsafe_allow_html=True)
            # Chat Messages Area
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            # Display chat messages with enterprise styling
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="message user">
                        <div class="message-avatar user">U</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message assistant">
                        <div class="message-avatar assistant">A</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Display enhanced response, sources and relevant docs if available
                    if "enhanced_response" in message:
                        self.display_enhanced_response(message["enhanced_response"])
                    if "sources" in message and st.session_state.user_preferences["show_sources"]:
                        self.display_sources_advanced(message["sources"])
                    if "relevant_docs" in message and st.session_state.user_preferences["show_similarity"]:
                        self.display_relevant_docs_advanced(message["relevant_docs"])
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Welcome message when no messages
            st.markdown("""
            <div class="chat-input-standalone">
                <h3 style="color: var(--redhat-dark-gray); margin-bottom: 1rem;">Welcome!</h3>
                <p style="color: var(--redhat-gray); margin-bottom: 2rem;">
                    I'm your assistant for Red Hat Emerging Technologies Blogs. </br>
                    Ask me anything about OpenShift, AI/ML, edge computing, security blogs, and more!
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat Input Area - Always show at the bottom, simple approach
        st.markdown("---")
        st.markdown("### Ask:")
        
        # The actual chat input - always present
        if prompt := st.chat_input("Ask a question about Emerging Technologies, OpenShift, AI/ML, and more..."):
            # Process the query and add to session state
            self.process_user_query(prompt)
            # Force a rerun to display the new message
            st.rerun()
        
        # Handle quick queries after chat interface
        if "quick_query" in st.session_state:
            query = st.session_state.quick_query
            del st.session_state.quick_query
            self.process_user_query(query)

        # # Enterprise Footer
        # st.markdown("""
        # <div class="enterprise-footer">
        #     <p>© 2025 Red Hat, Inc. | Enterprise-grade AI assistant for knowledge discovery and learning</p>
        # </div>
        # """, unsafe_allow_html=True)
    
    def process_and_display_immediately(self, prompt):
        """Process a user query and display results immediately without session state dependency"""
        # Update stats
        st.session_state.chat_stats["total_queries"] += 1
        
        # Process the query
        start_time = time.time()
        response = self.process_query(prompt)
        response_time = time.time() - start_time
        
        if response:
            # Generate better main response text based on enhanced response
            main_response_text = self.generate_main_response_text(response)
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.write(main_response_text)
                
                # Display enhanced response immediately
                enhanced_response = response.get("enhanced_response", {})
                if enhanced_response:
                    print(f"DEBUG: Displaying enhanced response with {len(enhanced_response.get('blogs', []))} blogs")
                    self.display_enhanced_response(enhanced_response)
                
                # Display sources if enabled
                if st.session_state.user_preferences["show_sources"] and "sources" in response:
                    self.display_sources_advanced(response["sources"])
                
                # Display relevant docs if enabled
                if st.session_state.user_preferences["show_similarity"] and "relevant_docs" in response:
                    self.display_relevant_docs_advanced(response["relevant_docs"])
            
            # Auto-suggest follow-up questions
            if st.session_state.user_preferences["auto_suggest"]:
                self.suggest_follow_up_questions(prompt, response)
        else:
            # Display error message
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                st.error("❌ Sorry, I couldn't process your question. Please try again.")
    
    def process_user_query(self, prompt):
        """Process a user query with enhanced features"""
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Update stats
        st.session_state.chat_stats["total_queries"] += 1
        
        # Process the query
        start_time = time.time()
        response = self.process_query(prompt)
        response_time = time.time() - start_time
        
        if response:
            # Generate better main response text based on enhanced response
            main_response_text = self.generate_main_response_text(response)
            
            # Add assistant response to chat history with enhanced response
            enhanced_response = response.get("enhanced_response", {})
            st.session_state.messages.append({
                "role": "assistant", 
                "content": main_response_text,
                "sources": response.get("sources", ""),
                "relevant_docs": response.get("relevant_docs", []),
                "enhanced_response": enhanced_response,
                "response_time": response_time
            })
            
            # Auto-suggest follow-up questions
            if st.session_state.user_preferences["auto_suggest"]:
                self.suggest_follow_up_questions(prompt, response)
        else:
            # Add error message to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "❌ Sorry, I couldn't process your question. Please try again.",
                "response_time": response_time
            })
    
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
    
    def generate_main_response_text(self, response: dict) -> str:
        """Generate appropriate main response text based on enhanced response content"""
        enhanced_response = response.get('enhanced_response', {})
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # If we found blogs, create a positive response
        if blogs:
            try:
                blog_titles = [blog.get('title', 'Unknown Title') for blog in blogs]
                blog_authors = [blog.get('author', 'Unknown Author') for blog in blogs]
                
                if len(blogs) == 1:
                    return f"I found information about '{blog_titles[0]}' by {blog_authors[0]}. Here are the details along with related projects that might be of interest."
                else:
                    return f"I found {len(blogs)} relevant blog posts: {', '.join(blog_titles)}. Here are the details along with related projects that might be of interest."
            except Exception as e:
                print(f"Error generating blog response text: {e}")
                return f"I found {len(blogs)} relevant blog posts. Here are the details along with related projects that might be of interest."
        
        # If we found projects but no blogs
        elif projects:
            try:
                project_names = [project.get('name', 'Unknown Project') for project in projects]
                if len(projects) == 1:
                    return f"I found the '{project_names[0]}' project that might be relevant to your query. Here are the details."
                else:
                    return f"I found {len(projects)} related projects: {', '.join(project_names)}. Here are the details."
            except Exception as e:
                print(f"Error generating project response text: {e}")
                return f"I found {len(projects)} related projects. Here are the details."
        
        # If no enhanced content found, use the original response
        else:
            return response.get('answer', 'I could not find specific information for your query.')
    
    def display_sources_advanced(self, sources: str):
        """Display source links with enhanced formatting"""
        if sources and sources.strip() and sources != "No sources available.":
            with st.expander("📚 Sources & References", expanded=False):
                st.markdown(f"""
                <div style="font-size: 0.9rem; color: var(--redhat-gray);">
                    {sources}
                </div>
                """, unsafe_allow_html=True)
    
    def display_relevant_docs_advanced(self, docs: list):
        """Display relevant documents with enhanced formatting"""
        if docs and any(doc.get('title') and doc.get('title') != 'Unknown Title' for doc in docs):
            with st.expander("🔍 Retrieved Documents", expanded=False):
                for i, doc in enumerate(docs[:3], 1):
                    # Only show documents with meaningful data
                    if doc.get('title') and doc.get('title') != 'Unknown Title':
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{i}. {doc.get('title', 'Unknown Title')}**")
                            if doc.get('type') and doc.get('type') != 'Unknown':
                                st.markdown(f"Type: {doc.get('type')}")
                            if doc.get('url'):
                                st.markdown(f"[View Source]({doc['url']})")
                        
                        with col2:
                            similarity = doc.get('similarity_score', 0)
                            if similarity > 0:
                                st.metric("Similarity", f"{similarity:.3f}")
                        
                        st.markdown("---")
    
    def display_enhanced_response(self, enhanced_response: dict):
        """Display enhanced response with blog summaries and GitHub projects"""
        if not enhanced_response:
            return
            
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # Display blog summaries
        if blogs:
            with st.expander("📝 Related Blog Posts", expanded=True):
                for i, blog in enumerate(blogs, 1):
                    # Blog title with link
                    if blog.get('url'):
                        st.markdown(f"### [{blog['title']}]({blog['url']})")
                    else:
                        st.markdown(f"### {blog['title']}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Handle author display - support multiple authors
                        author_display = blog['author']
                        author_url = blog.get('author_url', '')  # Check for separate author URL field
                        
                        # Handle multiple authors (separated by commas, 'and', '&', etc.)
                        if blog['author'] and blog['author'] != 'Unknown':
                            # Split authors by common separators
                            author_separators = [',', ' and ', ' & ', ';']
                            authors = [blog['author']]  # Default to single author
                            
                            for separator in author_separators:
                                if separator in blog['author']:
                                    authors = [author.strip() for author in blog['author'].split(separator)]
                                    break
                            
                            # Process each author individually
                            author_links = []
                            for author in authors:
                                if author.startswith('https://next.redhat.com/author/'):
                                    # Author field is a URL
                                    author_name = author.split('/author/')[-1].rstrip('/')
                                    author_name = author_name.replace('-', ' ').title()
                                    author_links.append(f"[@{author_name}]({author})")
                                else:
                                    # Plain author name - construct URL
                                    author_name = author.lower().replace(' ', '-')
                                    author_url = f"https://next.redhat.com/author/{author_name}/"
                                    author_links.append(f"[@{author}]({author_url})")
                            
                            # Join multiple authors with commas
                            author_display = ', '.join(author_links)
                        elif author_url and author_url.startswith('https://next.redhat.com/author/'):
                            # Single author URL
                            author_name = author_url.split('/author/')[-1].rstrip('/')
                            author_name = author_name.replace('-', ' ').title()
                            author_display = f"[@{author_name}]({author_url})"
                        
                        # Compact blog info layout
                        st.markdown(f"**Author:** {author_display} • **Date:** {blog.get('date', 'N/A')} • **Category:** {blog.get('category', 'General')}")
                        st.markdown(f"**Summary:** {blog.get('summary', 'No summary available')}")
                    
                    with col2:
                        # Relevance as percentage with colored bar
                        relevance_score = blog.get('relevance_score', 0)
                        percentage = relevance_score * 100
                        
                        # Color based on relevance
                        if percentage >= 80:
                            color = "green"
                        elif percentage >= 60:
                            color = "orange"
                        else:
                            color = "red"
                        
                        st.markdown(f"""
                        <div style="margin-bottom: 0.5rem;">
                            <div style="font-size: 0.8rem; color: var(--redhat-gray); margin-bottom: 0.25rem;">
                                Relevance
                            </div>
                            <div style="background: #f0f0f0; border-radius: 8px; height: 6px; margin-bottom: 0.25rem;">
                                <div style="background: {color}; height: 6px; border-radius: 8px; width: {percentage}%;"></div>
                            </div>
                            <div style="font-size: 0.7rem; color: var(--redhat-gray);">
                                {percentage:.0f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if i < len(blogs):  # Don't add separator after last item
                        st.markdown("---")
        
        # Display related GitHub projects
        if projects:
            with st.expander("🚀 Related GitHub Projects", expanded=True):
                for i, project in enumerate(projects, 1):
                    # Project title with link if available
                    if project.get('project_url'):
                        st.markdown(f"### [{project['name']}]({project['project_url']})")
                    else:
                        st.markdown(f"### {project['name']}")
                    
                    # Compact layout with less spacing
                    st.markdown(f"**Category:** {project.get('category', 'General')} • **Description:** {project.get('description', 'No description available')}")
                    
                    github_links = project.get('github_links', [])
                    if github_links:
                        st.markdown("**GitHub:** " + ", ".join([f"[{link}]({link})" for link in github_links]))
                    
                    if i < len(projects):  # Don't add separator after last item
                        st.markdown("---")
    
    def suggest_follow_up_questions(self, original_query: str, response: dict):
        """Suggest follow-up questions based on the response"""
        # Simple follow-up suggestions based on common patterns
        suggestions = []
        
        if "OpenShift" in original_query:
            suggestions.extend([
                "How do I get started with OpenShift?",
                "What are the benefits of OpenShift?",
                "How does OpenShift compare to other platforms?"
            ])
        
        if "AI" in original_query or "machine learning" in original_query.lower():
            suggestions.extend([
                "What are the latest AI trends?",
                "How do I deploy AI models?",
                "What tools are available for AI development?"
            ])
        
        if "edge" in original_query.lower():
            suggestions.extend([
                "What are edge computing use cases?",
                "How do I implement edge computing?",
                "What are the challenges of edge computing?"
            ])
        
        if suggestions:
            with st.expander("💡 Suggested Follow-up Questions", expanded=False):
                for suggestion in suggestions[:3]:
                    if st.button(suggestion, key=f"suggest_{suggestion}"):
                        st.session_state.quick_query = suggestion
    
    def generate_analytics(self, period: str, chart_type: str):
        """Generate analytics charts"""
        st.subheader(f"Analytics: {chart_type}")
        
        if chart_type == "Topic Distribution":
            self.show_topic_distribution()
        elif chart_type == "Query Frequency":
            self.show_query_frequency()
        elif chart_type == "Response Time":
            self.show_response_time_analysis()
        elif chart_type == "User Engagement":
            self.show_user_engagement()
    
    def show_topic_distribution(self):
        """Show topic distribution chart"""
        # Mock data for demonstration
        topics = ["OpenShift", "AI/ML", "Edge Computing", "Kubernetes", "Security"]
        counts = [25, 30, 15, 20, 10]
        
        fig = px.pie(
            values=counts, 
            names=topics, 
            title="Query Topic Distribution"
        )
        st.plotly_chart(fig)
    
    def show_query_frequency(self):
        """Show query frequency over time"""
        # Mock data for demonstration
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        queries = [10 + i % 20 for i in range(len(dates))]
        
        df = pd.DataFrame({'Date': dates, 'Queries': queries})
        fig = px.line(df, x='Date', y='Queries', title='Query Frequency Over Time')
        st.plotly_chart(fig)
    
    def show_response_time_analysis(self):
        """Show response time analysis"""
        # Mock data for demonstration
        response_times = [1.2, 1.5, 0.8, 2.1, 1.7, 1.3, 1.9, 1.1]
        
        fig = go.Figure()
        fig.add_trace(go.Box(y=response_times, name="Response Time (seconds)"))
        fig.update_layout(title="Response Time Distribution")
        st.plotly_chart(fig)
    
    def show_user_engagement(self):
        """Show user engagement metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", st.session_state.chat_stats["total_queries"])
        
        with col2:
            session_duration = datetime.now() - st.session_state.chat_stats["session_start"]
            st.metric("Session Duration", f"{session_duration.seconds//60}m {session_duration.seconds%60}s")
        
        with col3:
            avg_queries_per_minute = st.session_state.chat_stats["total_queries"] / max(1, session_duration.seconds / 60)
            st.metric("Queries/Min", f"{avg_queries_per_minute:.1f}")
        
        with col4:
            st.metric("Active Topics", len(set(st.session_state.chat_stats["topics"])))
    
    def export_chat_history(self):
        """Export chat history with enhanced formatting"""
        if st.session_state.messages:
            chat_text = self.format_chat_for_export_advanced()
            
            # Create download button
            st.download_button(
                label="📥 Download Chat History",
                data=chat_text,
                file_name=f"ask_et_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    def format_chat_for_export_advanced(self):
        """Format chat history for export with enhanced formatting"""
        chat_text = "Ask ET Advanced - Chat History\n"
        chat_text += "=" * 60 + "\n\n"
        chat_text += f"Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        chat_text += f"Total Queries: {st.session_state.chat_stats['total_queries']}\n"
        chat_text += "=" * 60 + "\n\n"
        
        for i, message in enumerate(st.session_state.messages, 1):
            role = message["role"].title()
            content = message["content"]
            chat_text += f"Message {i} - {role}:\n"
            chat_text += f"{content}\n\n"
            
            if "sources" in message and message["sources"]:
                chat_text += f"Sources: {message['sources']}\n\n"
            
            if "response_time" in message:
                chat_text += f"Response Time: {message['response_time']:.2f} seconds\n\n"
            
            chat_text += "-" * 40 + "\n\n"
        
        return chat_text
    
    def run(self):
        """Run the advanced Streamlit application"""
        # Initialize session state first
        self.setup_session_state()
        
        # Initialize RAG chain
        if not hasattr(self, 'rag_chain'):
            self.initialize_rag_chain()
        
        self.setup_sidebar()
        self.setup_main_interface()

def main():
    """Main entry point for the advanced Streamlit app"""
    app = AskETAdvancedWebApp()
    app.run()

if __name__ == "__main__":
    main() 