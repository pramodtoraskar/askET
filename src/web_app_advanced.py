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
    page_title="Ask ET - Advanced",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}
.chat-container {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.source-link {
    color: #0066cc;
    text-decoration: none;
}
.source-link:hover {
    text-decoration: underline;
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
                "show_similarity": True,
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
            st.title("Ask ET Advanced")
            st.markdown("AI-powered learning assistant")
            
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
        st.subheader("Session Controls")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Chat"):
                if self.rag_chain:
                    self.rag_chain.clear_memory()
                    st.session_state.messages = []
                    st.success("Chat cleared!")
        
        with col2:
            if st.button("Export Chat"):
                self.export_chat_history()
        
        # Quick filters
        st.subheader("Content Filters")
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
        
        # Suggested queries
        st.subheader("Quick Queries")
        self.setup_quick_queries()
    
    def show_analytics_sidebar(self):
        """Show analytics sidebar"""
        st.subheader("Analytics Controls")
        
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
        
        if st.button("Generate Analytics"):
            self.generate_analytics(period, chart_type)
    
    def show_settings_sidebar(self):
        """Show settings sidebar"""
        st.subheader("User Preferences")
        
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
        st.subheader("Model Settings")
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
        st.subheader("About Ask ET")
        st.info("""
        **Ask ET** is an AI-powered learning assistant for Emerging Technologies content.
        
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
        
        st.subheader("System Status")
        if self.rag_chain:
                    st.success("RAG Chain: Active")
        st.success("Vector DB: Connected")
        st.success("AI Model: Ready")
        else:
            st.error("❌ System: Not Initialized")
    
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
                st.rerun()
    
    def setup_main_interface(self):
        """Setup the main chat interface"""
        st.markdown('<h1 class="main-header">Ask ET - Advanced</h1>', unsafe_allow_html=True)
        st.markdown("Ask questions about Emerging Technologies, OpenShift, AI/ML, and more!")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and st.session_state.user_preferences["show_sources"]:
                    self.display_sources_advanced(message["sources"])
                if "relevant_docs" in message and st.session_state.user_preferences["show_similarity"]:
                    self.display_relevant_docs_advanced(message["relevant_docs"])
        
        # Handle quick queries
        if "quick_query" in st.session_state:
            query = st.session_state.quick_query
            del st.session_state.quick_query
            self.process_user_query(query)
        
        # Chat input
        if prompt := st.chat_input("Ask a question about Emerging Technologies..."):
            self.process_user_query(prompt)
    
    def process_user_query(self, prompt):
        """Process a user query with enhanced features"""
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Update stats
        st.session_state.chat_stats["total_queries"] += 1
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                start_time = time.time()
                response = self.process_query(prompt)
                response_time = time.time() - start_time
                
                if response:
                    # Generate better main response text based on enhanced response
                    main_response_text = self.generate_main_response_text(response)
                    st.markdown(main_response_text)
                    
                    # Display enhanced response with blogs and GitHub projects
                    if "enhanced_response" in response:
                        self.display_enhanced_response(response["enhanced_response"])
                    
                    # Display sources if enabled
                    if st.session_state.user_preferences["show_sources"] and "sources" in response:
                        self.display_sources_advanced(response["sources"])
                    
                    # Display relevant docs if enabled
                    if st.session_state.user_preferences["show_similarity"] and "relevant_docs" in response:
                        self.display_relevant_docs_advanced(response["relevant_docs"])
                    
                    # Auto-suggest follow-up questions
                    if st.session_state.user_preferences["auto_suggest"]:
                        self.suggest_follow_up_questions(prompt, response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": main_response_text,
                        "sources": response.get("sources", ""),
                        "relevant_docs": response.get("relevant_docs", []),
                        "response_time": response_time
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
    
    def generate_main_response_text(self, response: dict) -> str:
        """Generate appropriate main response text based on enhanced response content"""
        enhanced_response = response.get('enhanced_response', {})
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # If we found blogs, create a positive response
        if blogs:
            blog_titles = [blog['title'] for blog in blogs]
            blog_authors = [blog['author'] for blog in blogs]
            
            if len(blogs) == 1:
                return f"I found information about '{blog_titles[0]}' by {blog_authors[0]}. Here are the details along with related projects that might be of interest."
            else:
                return f"I found {len(blogs)} relevant blog posts: {', '.join(blog_titles)}. Here are the details along with related projects that might be of interest."
        
        # If we found projects but no blogs
        elif projects:
            project_names = [project['name'] for project in projects]
            if len(projects) == 1:
                return f"I found the '{project_names[0]}' project that might be relevant to your query. Here are the details."
            else:
                return f"I found {len(projects)} related projects: {', '.join(project_names)}. Here are the details."
        
        # If no enhanced content found, use the original response
        else:
            return response.get('answer', 'I could not find specific information for your query.')
    
    def display_sources_advanced(self, sources: str):
        """Display source links with enhanced formatting"""
        if sources:
            with st.expander("Sources", expanded=False):
                st.markdown(sources)
    
    def display_relevant_docs_advanced(self, docs: list):
        """Display relevant documents with enhanced formatting"""
        if docs:
            with st.expander("Retrieved Documents", expanded=False):
                for i, doc in enumerate(docs[:3], 1):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{i}. {doc.get('title', 'Unknown Title')}**")
                        st.markdown(f"Type: {doc.get('type', 'Unknown')}")
                        if doc.get('url'):
                            st.markdown(f"[View Source]({doc['url']})")
                    
                    with col2:
                        similarity = doc.get('similarity_score', 0)
                        st.metric("Similarity", f"{similarity:.3f}")
                    
                    st.markdown("---")
    
    def display_enhanced_response(self, enhanced_response: dict):
        """Display enhanced response with blog summaries and GitHub projects"""
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # Display blog summaries
        if blogs:
            with st.expander("Related Blog Posts", expanded=True):
                for i, blog in enumerate(blogs, 1):
                    st.markdown(f"### {i}. {blog['title']}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Author:** {blog['author']}")
                        if blog['date']:
                            st.markdown(f"**Date:** {blog['date']}")
                        if blog['category']:
                            st.markdown(f"**Category:** {blog['category']}")
                        st.markdown(f"**Summary:** {blog['summary']}")
                    
                    with col2:
                        st.metric("Relevance", f"{blog['relevance_score']:.3f}")
                        if blog['url']:
                            st.markdown(f"[Read Full Blog]({blog['url']})")
                    
                    st.markdown("---")
        
        # Display related GitHub projects
        if projects:
            with st.expander("Related GitHub Projects", expanded=True):
                for i, project in enumerate(projects, 1):
                    st.markdown(f"### {i}. {project['name']}")
                    st.markdown(f"**Category:** {project['category']}")
                    st.markdown(f"**Description:** {project['description']}")
                    
                    github_links = project.get('github_links', [])
                    if github_links:
                        st.markdown("**GitHub Links:**")
                        for link in github_links:
                            st.markdown(f"[{link}]({link})")
                    
                    project_url = project.get('project_url', '')
                    if project_url:
                        st.markdown(f"[Project Page]({project_url})")
                    
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
                        st.rerun()
    
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
        self.setup_sidebar()
        self.setup_main_interface()

def main():
    """Main entry point for the advanced Streamlit app"""
    app = AskETAdvancedWebApp()
    app.run()

if __name__ == "__main__":
    main() 