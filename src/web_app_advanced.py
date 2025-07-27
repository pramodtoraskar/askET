#!/usr/bin/env python3
"""
Advanced Streamlit Web Application for Ask ET
Based on Phase 4 requirements from task_list_next.md
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup

try:
    from src.github_qa_engine import create_github_qa_engine
except ImportError:
    # Fallback for direct execution
    from github_qa_engine import create_github_qa_engine

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

/* Ultra Compact Global Spacing */
.stApp {
    padding: 0.25rem !important;
}

.stApp > div {
    padding: 0.1rem !important;
}

/* Reduce spacing in main content */
.main .block-container {
    padding-top: 0.25rem !important;
    padding-bottom: 0.25rem !important;
}

/* Compact sidebar */
.sidebar .sidebar-content {
    margin-bottom: 0.25rem !important;
}

/* Compact chat messages */
.stChatMessage {
    margin-bottom: 0.25rem !important;
}

.stChatMessage > div {
    padding: 0.1rem !important;
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
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: var(--redhat-white);
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header-content .subtitle {
    font-size: 1.3rem;
    font-weight: 400;
    color: rgba(255,255,255,0.9);
    margin-bottom: 0.75rem;
}

.header-content .tagline {
    font-size: 1rem;
    color: rgba(255,255,255,0.7);
    font-weight: 300;
}

/* Chat Interface */
.chat-interface {
    background: var(--redhat-white);
    border-radius: 6px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin: 0.5rem 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 300px;
}

.chat-messages {
    padding: 0.5rem;
    flex: 1;
    overflow-y: auto;
    background: #FAFAFA;
    min-height: 200px;
}

/* Standalone Chat Input */
.chat-input-standalone {
    background: var(--redhat-white);
    border-radius: 6px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin: 0.5rem 0;
    padding: 1rem;
    text-align: center;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.chat-input-standalone .stTextInput {
    max-width: 600px;
    margin: 0 auto;
}



.message {
    margin-bottom: 0.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.25rem;
}

.message.user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
    font-size: 0.9rem;
}

.message-avatar.user {
    background: var(--redhat-blue);
}

.message-avatar.assistant {
    background: var(--redhat-red);
}

.message-content {
    background: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    max-width: 80%;
    border-left: 2px solid var(--redhat-blue);
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
    padding: 0.5rem;
    border-bottom: 1px solid #E0E0E0;
}

.quick-actions h3 {
    color: var(--redhat-dark-gray);
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.quick-button {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 0.25rem 0.75rem;
    margin: 0.1rem;
    color: var(--redhat-dark-gray);
    font-weight: 500;
    transition: all 0.2s ease;
    cursor: pointer;
    display: inline-block;
    text-decoration: none;
    font-size: 0.75rem;
}

.quick-button:hover {
    border-color: var(--redhat-red);
    color: var(--redhat-red);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(238,0,0,0.15);
}

/* Input Area */
.chat-input-area {
    padding: 0.5rem;
    background: white;
    border-top: 1px solid #E0E0E0;
    margin-top: 0.25rem;
}

.chat-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    font-size: 0.85rem;
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
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.sidebar h3 {
    color: var(--redhat-dark-gray);
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--redhat-red);
    padding-bottom: 0.1rem;
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
    border-radius: 4px;
    padding: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #E0E0E0;
    margin-bottom: 0.5rem;
}

.analytics-card h4 {
    color: var(--redhat-dark-gray);
    font-weight: 600;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
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
    padding: 0.5rem 0;
    margin: 0.5rem -1rem -1rem -1rem;
    text-align: center;
    font-size: 0.75rem;
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
    padding: 3rem 2rem;
    margin: 0 -1rem 2rem -1rem;
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
    max-width: 1200px;
    margin: 0 auto;
}

.hero h1 {
    font-size: 4rem;
    font-weight: 900;
    margin-bottom: 1rem;
    line-height: 1.1;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    letter-spacing: 2px;
}

.hero .subtitle {
    font-size: 1.4rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
    opacity: 0.95;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.hero .tagline {
    font-size: 1.1rem;
    font-weight: 300;
    opacity: 0.8;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* Chat Input Container - matches hero banner width */
.chat-input-container {
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
    padding: 0.5rem 0;
}

/* Compact Chat Input */
.stChatInput {
    max-width: 600px !important;
    margin: 0 auto !important;
    padding: 0.5rem !important;
}

.stTextInput > div {
    max-width: 600px !important;
    margin: 0 auto !important;
}

div[data-testid="stChatInput"] {
    max-width: 600px !important;
    margin: 0 auto !important;
    padding: 0.25rem !important;
}

/* Ultra Compact Blog Display */
.stExpander {
    margin-bottom: 0.25rem !important;
}

.stExpander > div {
    padding: 0.25rem !important;
}

.stExpander h3 {
    margin-bottom: 0.1rem !important;
    font-size: 0.9rem !important;
}

.stExpander p {
    margin-bottom: 0.1rem !important;
    line-height: 1.2 !important;
}

.stExpander hr {
    margin: 0.25rem 0 !important;
}

/* Ultra Compact Column Layout */
.stColumns > div {
    padding: 0.1rem !important;
}

/* Ultra Compact Button Styling */
.stButton > div {
    margin: 0.05rem 0 !important;
}

.stButton > div > div {
    padding: 0.1rem 0.25rem !important;
    font-size: 0.7rem !important;
}

/* Ultra Compact Relevance Section */
.relevance-section {
    margin: 0.1rem 0 !important;
    padding: 0.1rem !important;
}

.chat-input-container h3 {
    color: var(--redhat-dark-gray);
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 1.2rem;
}

/* Style the Streamlit chat input to match the container */
.stChatInput {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

.stChatInput > div {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Style text inputs to match the container width */
.stTextInput > div {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Center the chat input container */
div[data-testid="stChatInput"] {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Style Q&A buttons */
button[data-testid*="qa_btn"] {
    background: linear-gradient(135deg, var(--redhat-blue) 0%, var(--redhat-dark-red) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    font-size: 0.8rem !important;
}

button[data-testid*="qa_btn"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

/* Style inline Q&A link buttons */
button[data-testid*="qa_link"] {
    background: transparent !important;
    color: var(--redhat-blue) !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0.25rem 0.5rem !important;
    font-weight: 400 !important;
    font-size: 0.9rem !important;
    text-decoration: underline !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

button[data-testid*="qa_link"]:hover {
    background: transparent !important;
    color: var(--redhat-dark-red) !important;
    text-decoration: underline !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Ensure right column content is aligned to the far right */
.stButton > div {
    display: flex !important;
    justify-content: flex-end !important;
}

/* Style the relevance section to align right */
.relevance-section {
    text-align: right !important;
    margin-left: auto !important;
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
        """Initialize session state variables with robust persistence"""
        # Core session state variables
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
        
        # Navigation state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Chat"
        
        # Q&A state persistence
        if "blog_url_input" not in st.session_state:
            st.session_state.blog_url_input = ""
        
        if "github_url_input" not in st.session_state:
            st.session_state.github_url_input = ""
        
        # Redirect flags
        if "redirect_to_blog_qa" not in st.session_state:
            st.session_state.redirect_to_blog_qa = False
        
        if "redirect_to_github_qa" not in st.session_state:
            st.session_state.redirect_to_github_qa = False
        
        # Rerun flags
        if "needs_rerun" not in st.session_state:
            st.session_state.needs_rerun = False
        
        # Quick query state
        if "quick_query" not in st.session_state:
            st.session_state.quick_query = None
        
        # Last query for persistence
        if "last_query" not in st.session_state:
            st.session_state.last_query = ""
        
        # Ensure messages is always a list
        if not isinstance(st.session_state.get('messages'), list):
            st.session_state.messages = []
    
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
            
            # Use buttons instead of selectbox to avoid session state conflicts
            if st.button("💬 Chat", use_container_width=True, key="nav_chat"):
                st.session_state.current_page = "Chat"
                # Preserve all session state during navigation
                st.rerun()
            
            if st.button("🔍 Blog Q&A", use_container_width=True, key="nav_blog_qa"):
                st.session_state.current_page = "Blog Q&A"
                # Preserve all session state during navigation
                st.rerun()
            
            if st.button("🐙 GitHub Q&A", use_container_width=True, key="nav_github_qa"):
                st.session_state.current_page = "GitHub Q&A"
                # Preserve all session state during navigation
                st.rerun()
            
            if st.button("📊 Analytics", use_container_width=True, key="nav_analytics"):
                st.session_state.current_page = "Analytics"
                # Preserve all session state during navigation
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
                st.session_state.current_page = "Settings"
                # Preserve all session state during navigation
                st.rerun()
            
            if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
                st.session_state.current_page = "About"
                # Preserve all session state during navigation
                st.rerun()
            
            # Get current page
            current_page = st.session_state.get('current_page', 'Chat')
            
            # Show page-specific sidebar content
            if current_page == "Chat":
                self.show_chat_sidebar()
            elif current_page == "Blog Q&A":
                self.show_blog_qa_sidebar()
            elif current_page == "GitHub Q&A":
                self.show_github_qa_sidebar()
            elif current_page == "Analytics":
                self.show_analytics_sidebar()
            elif current_page == "Settings":
                self.show_settings_sidebar()
            elif current_page == "About":
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
        - Blog Q&A with Gemini Pro
        
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
    
    def show_blog_qa_sidebar(self):
        """Show blog Q&A sidebar controls"""
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🔍 Blog Q&A Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Blog URL input
        st.sidebar.markdown("**📝 Enter Blog URL:**")
        
        # Clear blog content button
        if st.sidebar.button("🗑️ Clear Blog Content", use_container_width=True):
            if "blog_content" in st.session_state:
                del st.session_state.blog_content
            if "blog_qa_messages" in st.session_state:
                del st.session_state.blog_qa_messages
            st.success("Blog content cleared!")
            st.rerun()
        
        # Export Q&A session
        if st.sidebar.button("📥 Export Q&A Session", use_container_width=True):
            self.export_blog_qa_session()
        
        # Q&A Statistics
        if "blog_qa_messages" in st.session_state and st.session_state.blog_qa_messages:
            st.sidebar.markdown("""
            <div class="sidebar-content">
                <h3>📊 Q&A Statistics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            total_qa = len([msg for msg in st.session_state.blog_qa_messages if msg["role"] == "user"])
            st.sidebar.metric("Questions Asked", total_qa)
    
    def show_github_qa_sidebar(self):
        """Show GitHub Q&A sidebar controls"""
        st.sidebar.markdown("""
        <div class="sidebar-content">
            <h3>🐙 GitHub Q&A Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # GitHub repository URL input
        st.sidebar.markdown("**📝 Enter GitHub Repository URL:**")
        
        # Clear GitHub content button
        if st.sidebar.button("🗑️ Clear GitHub Content", use_container_width=True):
            if 'github_qa_session' in st.session_state:
                st.session_state.github_qa_session = {
                    'repo_content': {},
                    'qa_history': [],
                    'current_repo': None,
                    'rag_chain': None
                }
            st.success("GitHub content cleared!")
            st.rerun()
        
        # Export Q&A session
        if st.sidebar.button("📥 Export GitHub Q&A Session", use_container_width=True):
            self.export_github_qa_session()
        
        # Q&A Statistics
        if 'github_qa_session' in st.session_state and st.session_state.github_qa_session.get('qa_history'):
            st.sidebar.markdown("""
            <div class="sidebar-content">
                <h3>📊 GitHub Q&A Statistics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            total_qa = len(st.session_state.github_qa_session['qa_history'])
            st.sidebar.metric("Questions Asked", total_qa)
    
    def scrape_blog_content(self, url):
        """Scrape blog content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from paragraphs and other content
            content_elements = []
            
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post')
            
            if main_content:
                # Extract from main content area
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            else:
                # Fallback to all paragraphs
                paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            for element in paragraphs:
                text = element.get_text().strip()
                if text and len(text) > 10:  # Filter out very short text
                    content_elements.append(text)
            
            if content_elements:
                return "\n\n".join(content_elements)
            else:
                return "No readable content found on this page."
                
        except requests.RequestException as e:
            return f"Error loading blog: {str(e)}"
        except Exception as e:
            return f"Error processing blog content: {str(e)}"
    
    def ask_gemini_about_blog(self, question, blog_content):
        """Ask Gemini about the blog content"""
        try:
            # Use the existing RAG chain's LLM for consistency
            if self.rag_chain and hasattr(self.rag_chain, 'llm'):
                prompt = f"""Based on the following blog content, please answer the question below.

Blog Content:
{blog_content}

Question: {question}

Please provide a comprehensive and accurate answer based only on the information in the blog content. If the blog doesn't contain information to answer the question, please say so."""
                
                response = self.rag_chain.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                return "Error: AI model not available. Please ensure the RAG chain is properly initialized."
                
        except Exception as e:
            return f"Error getting AI response: {str(e)}"
    
    def export_blog_qa_session(self):
        """Export blog Q&A session"""
        if "blog_qa_messages" in st.session_state and st.session_state.blog_qa_messages:
            qa_text = "Blog Q&A Session\n"
            qa_text += "=" * 50 + "\n\n"
            
            if "blog_url" in st.session_state:
                qa_text += f"Blog URL: {st.session_state.blog_url}\n\n"
            
            for i, message in enumerate(st.session_state.blog_qa_messages, 1):
                role = message["role"].title()
                content = message["content"]
                qa_text += f"Message {i} - {role}:\n{content}\n\n"
                qa_text += "-" * 40 + "\n\n"
            
            st.download_button(
                label="📥 Download Q&A Session",
                data=qa_text,
                file_name=f"blog_qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("No Q&A session to export.")
    
    def setup_blog_qa_interface(self):
        """Setup the blog Q&A interface"""
        st.markdown("""
        <div class="hero">
            <div class="hero-content">
                <h1>🔍 Blog Q&A</h1>
                <div class="subtitle">Ask Gemini Anything About Any Blog</div>
                <div class="tagline">Powered by Google Gemini Pro</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize blog Q&A session state
        if "blog_qa_messages" not in st.session_state:
            st.session_state.blog_qa_messages = []
        
        # Blog URL input
        col1, col2 = st.columns([3, 1])
        with col1:
            blog_url = st.text_input(
                "Enter a blog URL",
                placeholder="https://next.redhat.com/blog/example",
                key="blog_url_input"
            )
        with col2:
            if st.button("📄 Load Blog", use_container_width=True):
                if blog_url:
                    with st.spinner("Loading blog content..."):
                        blog_content = self.scrape_blog_content(blog_url)
                        st.session_state.blog_content = blog_content
                        st.session_state.blog_url = blog_url
                        st.session_state.blog_qa_messages = []  # Clear previous Q&A
                    st.success("Blog loaded successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid blog URL.")
        
        # Auto-load blog if URL is set in session state (from Q&A button)
        if "blog_url_input" in st.session_state and st.session_state.blog_url_input and "blog_content" not in st.session_state:
            auto_blog_url = st.session_state.blog_url_input
            with st.spinner("Auto-loading blog content..."):
                blog_content = self.scrape_blog_content(auto_blog_url)
                st.session_state.blog_content = blog_content
                st.session_state.blog_url = auto_blog_url
                st.session_state.blog_qa_messages = []  # Clear previous Q&A
            st.success(f"Blog loaded automatically: {auto_blog_url}")
            # Clear the auto-load flag
            del st.session_state.blog_url_input
            st.rerun()
        
        # Display blog content
        if "blog_content" in st.session_state and st.session_state.blog_content:
            st.markdown("### 📄 Blog Content")
            
            # Show blog URL
            if "blog_url" in st.session_state:
                st.markdown(f"**Source:** [{st.session_state.blog_url}]({st.session_state.blog_url})")
            
            # Blog content in scrollable area
            st.text_area(
                "Loaded Blog Text",
                st.session_state.blog_content,
                height=300,
                key="blog_content_display",
                disabled=True
            )
            
            # Q&A Interface
            st.markdown("""
            <div class="chat-input-container">
                <h3>🤖 Ask Questions About This Blog</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display previous Q&A messages
            if st.session_state.blog_qa_messages:
                st.markdown("#### Previous Questions & Answers:")
                for message in st.session_state.blog_qa_messages:
                    if message["role"] == "user":
                        st.markdown(f"**❓ Question:** {message['content']}")
                    else:
                        st.markdown(f"**🤖 Answer:** {message['content']}")
                        st.markdown("---")
            
            # New question input
            question = st.text_input(
                "Ask a question about the blog",
                placeholder="What is the main topic of this blog?",
                key="blog_question_input"
            )
            
            if question:
                if st.button("🚀 Ask Gemini", use_container_width=True):
                    with st.spinner("Asking Gemini..."):
                        answer = self.ask_gemini_about_blog(question, st.session_state.blog_content)
                        
                        # Add to Q&A history
                        st.session_state.blog_qa_messages.append({"role": "user", "content": question})
                        st.session_state.blog_qa_messages.append({"role": "assistant", "content": answer})
                        
                        st.success("Answer received!")
                        st.rerun()
        else:
            # Welcome message
            st.markdown("""
            <div class="chat-input-standalone">
                <h3 style="color: var(--redhat-dark-gray); margin-bottom: 1rem;">Welcome to Blog Q&A!</h3>
                <p style="color: var(--redhat-gray); margin-bottom: 2rem;">
                    Enter a blog URL above to get started. I'll help you understand any blog content using Google Gemini Pro.
                </p>
                <div style="background: var(--redhat-light-gray); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h4>💡 How it works:</h4>
                    <ol style="text-align: left;">
                        <li>Enter any blog URL</li>
                        <li>I'll scrape and display the content</li>
                        <li>Ask questions about the blog</li>
                        <li>Get AI-powered answers from Gemini Pro</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def export_github_qa_session(self):
        """Export GitHub Q&A session"""
        if 'github_qa_session' in st.session_state and st.session_state.github_qa_session.get('qa_history'):
            qa_text = "GitHub Q&A Session\n"
            qa_text += "=" * 50 + "\n\n"
            
            repo_info = st.session_state.github_qa_session.get('repo_info')
            if repo_info:
                qa_text += f"Repository: {repo_info.get('full_name', 'Unknown')}\n"
                qa_text += f"Description: {repo_info.get('description', 'No description')}\n"
                qa_text += f"URL: {repo_info.get('url', 'No URL')}\n\n"
            
            for i, qa in enumerate(st.session_state.github_qa_session['qa_history'], 1):
                qa_text += f"Q&A {i}:\n"
                qa_text += f"Question: {qa['question']}\n"
                qa_text += f"Answer: {qa['answer']}\n"
                qa_text += f"Sources: {', '.join(qa.get('sources', []))}\n"
                qa_text += "-" * 40 + "\n\n"
            
            st.download_button(
                label="📥 Download GitHub Q&A Session",
                data=qa_text,
                file_name=f"github_qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("No GitHub Q&A session to export.")
    
    def setup_github_qa_interface(self):
        """Setup the GitHub Q&A interface"""
        st.markdown("""
        <div class="hero">
            <div class="hero-content">
                <h1>🐙 GitHub Q&A</h1>
                <div class="subtitle">Ask Questions About Any GitHub Repository</div>
                <div class="tagline">Powered by Technical Documentation Analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize GitHub Q&A engine
        if not hasattr(self, 'github_qa_engine'):
            self.github_qa_engine = create_github_qa_engine()
        
        # GitHub repository URL input
        col1, col2 = st.columns([3, 1])
        with col1:
            repo_url = st.text_input(
                "Enter a GitHub repository URL",
                placeholder="https://github.com/redhat-developer/example-repo",
                key="github_repo_url_input"
            )
        with col2:
            if st.button("🐙 Load Repository", use_container_width=True):
                if repo_url:
                    try:
                        with st.spinner("Loading repository content..."):
                            # Extract repo info
                            repo_info = self.github_qa_engine.extract_repo_info_from_url(repo_url)
                            
                            # Extract technical content
                            technical_content = self.github_qa_engine.extract_technical_content(
                                repo_info['owner'], 
                                repo_info['repo']
                            )
                            
                            # Create RAG chain
                            rag_chain = self.github_qa_engine.create_github_rag_chain(technical_content)
                            
                            # Store in session state
                            st.session_state.github_qa_session = {
                                'repo_content': technical_content,
                                'qa_history': [],
                                'current_repo': repo_info,
                                'rag_chain': rag_chain,
                                'repo_info': technical_content['repo_info']
                            }
                        
                        st.success(f"Repository loaded successfully! Found {technical_content['total_files']} technical files.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error loading repository: {str(e)}")
                else:
                    st.error("Please enter a valid GitHub repository URL.")
        
        # Display repository content
        if 'github_qa_session' in st.session_state and st.session_state.github_qa_session.get('repo_content'):
            session = st.session_state.github_qa_session
            repo_info = session['repo_info']
            
            st.markdown("### 📁 Repository Information")
            
            # Repository details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Repository", repo_info['full_name'])
            with col2:
                st.metric("Language", repo_info['language'] or "Unknown")
            with col3:
                st.metric("Files Extracted", session['repo_content']['total_files'])
            
            # Repository description
            if repo_info['description']:
                st.markdown(f"**Description:** {repo_info['description']}")
            
            # Repository URL
            st.markdown(f"**Source:** [{repo_info['url']}]({repo_info['url']})")
            
            # Technical files summary
            st.markdown("### 📄 Technical Files Extracted")
            technical_files = session['repo_content']['technical_files']
            
            # Group files by type
            file_types = {}
            for file_path in technical_files.keys():
                ext = Path(file_path).suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
                else:
                    file_types['No extension'] = file_types.get('No extension', 0) + 1
            
            # Display file type summary
            if file_types:
                file_summary = ", ".join([f"{ext}: {count}" for ext, count in file_types.items()])
                st.info(f"**File types found:** {file_summary}")
            
            # Show some example files
            st.markdown("**Sample files:**")
            sample_files = list(technical_files.keys())[:10]
            for file_path in sample_files:
                st.markdown(f"- `{file_path}`")
            
            if len(technical_files) > 10:
                st.markdown(f"... and {len(technical_files) - 10} more files")
            
            # Q&A Interface
            st.markdown("### 🤖 Ask Questions About This Repository")
            
            # Display previous Q&A messages
            if session.get('qa_history'):
                st.markdown("#### Previous Questions & Answers:")
                for qa in session['qa_history']:
                    st.markdown(f"**❓ Question:** {qa['question']}")
                    st.markdown(f"**🤖 Answer:** {qa['answer']}")
                    if qa.get('sources'):
                        st.markdown(f"**📄 Sources:** {', '.join(qa['sources'])}")
                    st.markdown("---")
            
            # New question input
            question = st.text_input(
                "Ask a question about the repository",
                placeholder="What is this repository for? How do I run it?",
                key="github_question_input"
            )
            
            if question:
                if st.button("🚀 Ask AI", use_container_width=True):
                    with st.spinner("Analyzing repository content..."):
                        # Ask question using GitHub Q&A engine
                        result = self.github_qa_engine.ask_question(question, session['rag_chain'])
                        
                        # Add to Q&A history
                        session['qa_history'].append(result)
                        
                        st.success("Answer received!")
                        st.rerun()
        else:
            # Welcome message
            st.markdown("""
            <div class="chat-input-standalone">
                <h3 style="color: var(--redhat-dark-gray); margin-bottom: 1rem;">Welcome to GitHub Q&A!</h3>
                <p style="color: var(--redhat-gray); margin-bottom: 2rem;">
                    Enter a GitHub repository URL above to get started. I'll analyze the technical documentation and help you understand the project.
                </p>
                <div style="background: var(--redhat-light-gray); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h4>💡 How it works:</h4>
                    <ol style="text-align: left;">
                        <li>Enter any GitHub repository URL</li>
                        <li>I'll extract technical documentation (README, docs, code comments, etc.)</li>
                        <li>Ask questions about the project</li>
                        <li>Get AI-powered answers based on the repository content</li>
                    </ol>
                </div>
                <div style="background: var(--redhat-light-gray); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h4>🔍 What I can analyze:</h4>
                    <ul style="text-align: left;">
                        <li>README.md files and project documentation</li>
                        <li>Setup and installation instructions</li>
                        <li>API documentation and usage examples</li>
                        <li>Dependencies and requirements</li>
                        <li>Code comments and architecture details</li>
                        <li>Deployment and configuration guides</li>
                    </ul>
                </div>
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
        messages = st.session_state.get('messages', [])
        if messages and len(messages) > 0:
            st.markdown('<div class="chat-interface">', unsafe_allow_html=True)
            # Chat Messages Area
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            # Display chat messages with enterprise styling
            for message in messages:
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
                        # Use message index as unique suffix to avoid duplicate widget keys
                        message_index = messages.index(message)
                        self.display_enhanced_response(message["enhanced_response"], f"_msg_{message_index}")
                    if "sources" in message and st.session_state.user_preferences["show_sources"]:
                        self.display_sources_advanced(message["sources"])
                    if "relevant_docs" in message and st.session_state.user_preferences["show_similarity"]:
                        self.display_relevant_docs_advanced(message["relevant_docs"])
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Welcome message when no messages
            st.markdown("""
            <div class="chat-input-standalone" style="border: 1px solid var(--redhat-blue); background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);">
                <h3 style="color: var(--redhat-dark-gray); margin-bottom: 0.25rem; font-size: 1rem; font-weight: 600;">Welcome!</h3>
                <p style="color: var(--redhat-gray); margin-bottom: 0.25rem; font-size: 0.9rem;">
                    I'm your AI assistant for Red Hat Emerging Technologies.
                </p>
                <p style="color: var(--redhat-gray); margin-bottom: 0.5rem;">
                    Ask me anything about OpenShift, AI/ML, edge computing, security blogs, and more!
                </p>
                <div style="background: var(--redhat-light-gray); padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0; border: 1px solid #E0E0E0;">
                    <h4 style="color: var(--redhat-dark-gray); margin-bottom: 0.1rem; font-size: 0.8rem;">💡 Try asking:</h4>
                    <ul style="text-align: left; color: var(--redhat-gray); margin: 0; padding-left: 0.75rem; font-size: 0.75rem;">
                        <li>"What is OpenShift AI?"</li>
                        <li>"Tell me about Triton development"</li>
                        <li>"Show me blogs about machine learning"</li>
                        <li>"What are the latest emerging technologies?"</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat Input Area - Always show at the bottom, matching hero banner width
        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
        
        # Create a container that matches the hero banner width and styling
        st.markdown("""
        <div class="chat-input-container">
            <h3 style="margin-bottom: 0.25rem; font-size: 1rem;">Ask:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # The actual chat input - always present
        if prompt := st.chat_input("Ask a question about Emerging Technologies, OpenShift, AI/ML, and more..."):
            # Process the query and display immediately
            self.process_and_display_immediately(prompt)
        
        # Handle quick queries after chat interface
        if "quick_query" in st.session_state and st.session_state.quick_query:
            query = st.session_state.quick_query
            del st.session_state.quick_query
            if query and isinstance(query, str):
                # Use the same method as typed queries for consistent display
                self.process_and_display_immediately(query)

        # # Enterprise Footer
        # st.markdown("""
        # <div class="enterprise-footer">
        #     <p>© 2025 Red Hat, Inc. | Enterprise-grade AI assistant for knowledge discovery and learning</p>
        # </div>
        # """, unsafe_allow_html=True)
    
    def process_and_display_immediately(self, prompt):
        """Process a user query and display results immediately without session state dependency"""
        # Handle None or empty prompt
        if not prompt or not isinstance(prompt, str):
            st.error("Invalid query. Please enter a valid question.")
            return
        
        # Update stats
        st.session_state.chat_stats["total_queries"] += 1
        
        # Process the query
        start_time = time.time()
        response = self.process_query(prompt)
        response_time = time.time() - start_time
        
        if response:
            # Generate better main response text based on enhanced response
            main_response_text = self.generate_main_response_text(response)
            
            # Store in session state for Q&A functionality
            enhanced_response = response.get("enhanced_response", {})
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt
            })
            st.session_state.messages.append({
                "role": "assistant", 
                "content": main_response_text,
                "sources": response.get("sources", ""),
                "relevant_docs": response.get("relevant_docs", []),
                "enhanced_response": enhanced_response,
                "response_time": response_time
            })
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.write(main_response_text)
                
                # Display enhanced response immediately
                if enhanced_response:
                    # Use timestamp as unique suffix for new displays
                    timestamp = int(time.time())
                    self.display_enhanced_response(enhanced_response, f"_new_{timestamp}")
                
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
        # Handle None or empty prompt
        if not prompt or not isinstance(prompt, str):
            st.error("Invalid query. Please enter a valid question.")
            return
        
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
        """Generate compact main response text based on enhanced response content"""
        enhanced_response = response.get('enhanced_response', {})
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # If we found blogs, create a compact response
        if blogs:
            try:
                blog_titles = [blog.get('title', 'Unknown Title') for blog in blogs]
                
                if len(blogs) == 1:
                    return f"📝 Found: {blog_titles[0]}"
                else:
                    # Truncate titles if too long
                    titles_text = ', '.join(blog_titles)
                    if len(titles_text) > 80:
                        titles_text = ', '.join(blog_titles[:2]) + f" and {len(blogs)-2} more"
                    return f"📝 Found {len(blogs)} blogs: {titles_text}"
            except Exception as e:
                print(f"Error generating blog response text: {e}")
                return f"📝 Found {len(blogs)} relevant blogs"
        
        # If we found projects but no blogs
        elif projects:
            try:
                project_names = [project.get('name', 'Unknown Project') for project in projects]
                if len(projects) == 1:
                    return f"🔗 Found: {project_names[0]}"
                else:
                    return f"🔗 Found {len(projects)} projects"
            except Exception as e:
                print(f"Error generating project response text: {e}")
                return f"🔗 Found {len(projects)} projects"
        
        # If no enhanced content found, use the original response
        else:
            return response.get('answer', 'No specific information found.')
    
    def display_sources_advanced(self, sources: str):
        """Display source links with compact formatting"""
        if sources and sources.strip() and sources != "No sources available.":
            with st.expander("📚 Sources", expanded=False):
                st.markdown(f"""
                <div style="font-size: 0.8rem; color: var(--redhat-gray); line-height: 1.2;">
                    {sources}
                </div>
                """, unsafe_allow_html=True)
    
    def display_relevant_docs_advanced(self, docs: list):
        """Display relevant documents with compact formatting"""
        if docs and any(doc.get('title') and doc.get('title') != 'Unknown Title' for doc in docs):
            with st.expander("🔍 Retrieved Documents", expanded=False):
                for i, doc in enumerate(docs[:3], 1):
                    # Only show documents with meaningful data
                    if doc.get('title') and doc.get('title') != 'Unknown Title':
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{i}. {doc.get('title', 'Unknown Title')}**")
                            if doc.get('type') and doc.get('type') != 'Unknown':
                                st.markdown(f"Type: {doc.get('type')}", help="Document type")
                            if doc.get('url'):
                                st.markdown(f"[View]({doc['url']})")
                        
                        with col2:
                            similarity = doc.get('similarity_score', 0)
                            if similarity > 0:
                                st.metric("Score", f"{similarity:.2f}")
                        
                        if i < min(3, len(docs)):
                            st.markdown("<hr style='margin: 0.25rem 0;'>", unsafe_allow_html=True)
    
    def display_enhanced_response(self, enhanced_response: dict, unique_suffix: str = ""):
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
                    if blog.get('url') and blog.get('url').strip():
                        st.markdown(f"### [{blog['title']}]({blog['url']})")
                    else:
                        st.markdown(f"### {blog['title']}")
                    
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
                    
                    # Main layout with Q&A and Relevance aligned to the far right
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Compact author info and summary in left column
                        metadata_parts = []
                        if author_display and author_display != 'Unknown':
                            metadata_parts.append(author_display)
                        if blog.get('date'):
                            metadata_parts.append(blog.get('date'))
                        if blog.get('category'):
                            metadata_parts.append(blog.get('category'))
                        
                        metadata = " • ".join(metadata_parts) if metadata_parts else ""
                        
                        if metadata:
                            st.markdown(f"**{metadata}**")
                        
                        # Truncate summary if too long
                        summary = blog.get('summary', 'No summary available')
                        if len(summary) > 150:
                            summary = summary[:147] + "..."
                        st.markdown(f"{summary}")
                    
                    with col2:
                        # Q&A button and Relevance in right column, aligned to far right
                        if blog.get('url'):
                            button_key = f"qa_link_{i}{unique_suffix}"
                            if st.button(f"Q&A", key=button_key, help=f"Ask questions about this blog: {blog['title']}", use_container_width=True):
                                # Set the blog URL in session state and redirect to Blog Q&A
                                st.session_state.blog_url_input = blog['url']
                                st.session_state.redirect_to_blog_qa = True
                                st.rerun()
                        
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
                        <div class="relevance-section" style="margin-bottom: 0.5rem;">
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
                        st.markdown("<hr style='margin: 0.25rem 0;'>", unsafe_allow_html=True)
        
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
        # Handle None or empty query
        if not original_query or not isinstance(original_query, str):
            return
        
        # Simple follow-up suggestions based on common patterns
        suggestions = []
        query_lower = original_query.lower()
        
        # Dynamic suggestions based on query content
        if "openshift" in query_lower:
            suggestions.extend([
                "How do I get started with OpenShift?",
                "What are the benefits of OpenShift?",
                "How does OpenShift compare to other platforms?"
            ])
        
        if "ai" in query_lower or "machine learning" in query_lower or "ml" in query_lower:
            suggestions.extend([
                "What are the latest AI trends?",
                "How do I deploy AI models?",
                "What tools are available for AI development?"
            ])
        
        if "edge" in query_lower or "edge computing" in query_lower:
            suggestions.extend([
                "What are edge computing use cases?",
                "How do I implement edge computing?",
                "What are the challenges of edge computing?"
            ])
        
        if "triton" in query_lower:
            suggestions.extend([
                "What is Triton used for?",
                "How do I get started with Triton?",
                "What are the benefits of Triton?"
            ])
        
        if "kubernetes" in query_lower or "k8s" in query_lower:
            suggestions.extend([
                "How do I deploy applications on Kubernetes?",
                "What are Kubernetes best practices?",
                "How does Kubernetes work with OpenShift?"
            ])
        
        if "security" in query_lower:
            suggestions.extend([
                "What are the latest security trends?",
                "How do I secure my applications?",
                "What security tools are available?"
            ])
        
        # Generic suggestions if no specific patterns found
        if not suggestions:
            suggestions.extend([
                "Tell me more about this topic",
                "What are the latest developments?",
                "How can I get started?"
            ])
        
        if suggestions:
            with st.expander("💡 Follow-up Questions", expanded=False):
                cols = st.columns(3)
                for i, suggestion in enumerate(suggestions[:3]):
                    with cols[i]:
                        if st.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
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
        """Run the advanced Streamlit application with robust session state management"""
        # Always setup session state first
        self.setup_session_state()
        
        # Initialize RAG chain if not already done
        if not hasattr(self, 'rag_chain'):
            self.initialize_rag_chain()
        
        # Handle rerun flag
        if st.session_state.get('needs_rerun', False):
            del st.session_state.needs_rerun
        
        # Check for redirect from Q&A buttons
        if st.session_state.get('redirect_to_blog_qa', False):
            # Set the current page to Blog Q&A
            st.session_state.current_page = "Blog Q&A"
            del st.session_state.redirect_to_blog_qa
            st.rerun()
        
        # Check for redirect from GitHub Q&A buttons
        if st.session_state.get('redirect_to_github_qa', False):
            # Set the current page to GitHub Q&A
            st.session_state.current_page = "GitHub Q&A"
            del st.session_state.redirect_to_github_qa
            st.rerun()
        
        # Setup sidebar (this handles navigation)
        self.setup_sidebar()
        
        # Get current page with fallback
        current_page = st.session_state.get('current_page', 'Chat')
        
        # Route to appropriate interface while preserving session state
        if current_page == 'Blog Q&A':
            self.setup_blog_qa_interface()
        elif current_page == 'GitHub Q&A':
            self.setup_github_qa_interface()
        elif current_page == 'Analytics':
            self.setup_analytics_interface()
        elif current_page == 'Settings':
            self.setup_settings_interface()
        elif current_page == 'About':
            self.setup_about_interface()
        else:
            # Default to Chat interface
            self.setup_main_interface()
    
    def setup_analytics_interface(self):
        """Setup analytics interface"""
        st.title("📊 Analytics Dashboard")
        st.write("Analytics interface - Coming soon!")
    
    def setup_settings_interface(self):
        """Setup settings interface"""
        st.title("⚙️ Settings")
        st.write("Settings interface - Coming soon!")
    
    def setup_about_interface(self):
        """Setup about interface"""
        st.title("ℹ️ About Ask ET")
        st.write("About interface - Coming soon!")

def main():
    """Main entry point for the advanced Streamlit app"""
    app = AskETAdvancedWebApp()
    app.run()

if __name__ == "__main__":
    main() 