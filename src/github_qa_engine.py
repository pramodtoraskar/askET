#!/usr/bin/env python3
"""
GitHub Repository Q&A Engine for AskET
Scrapes GitHub repos, extracts technical documentation, and provides Q&A capabilities
"""

import os
import re
import json
import requests
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import streamlit as st

# Optional imports with fallbacks
try:
    import markdown
except ImportError:
    markdown = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.logger import get_logger
    from src.rag_chain_improved import create_improved_rag_chain
except ImportError:
    # Fallback for direct execution
    try:
        from logger import get_logger
        from rag_chain_improved import create_improved_rag_chain
    except ImportError:
        # Simple fallback logger
        import logging
        def get_logger(name):
            logger = logging.getLogger(name)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            return logger
        
        def create_improved_rag_chain():
            return None

logger = get_logger(__name__)

class GitHubQAEngine:
    """GitHub Repository Q&A Engine"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.session_state_key = 'github_qa_session'
        self.setup_session_state()
        
    def setup_session_state(self):
        """Setup session state for GitHub Q&A"""
        if self.session_state_key not in st.session_state:
            st.session_state[self.session_state_key] = {
                'repo_content': {},
                'qa_history': [],
                'current_repo': None,
                'rag_chain': None
            }
    
    def extract_repo_info_from_url(self, repo_url: str) -> Dict[str, str]:
        """Extract repository information from GitHub URL"""
        try:
            # Parse GitHub URL
            parsed = urlparse(repo_url)
            if 'github.com' not in parsed.netloc:
                raise ValueError("Not a GitHub URL")
            
            # Extract owner and repo name
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repository URL")
            
            owner = path_parts[0]
            repo_name = path_parts[1]
            
            return {
                'owner': owner,
                'repo': repo_name,
                'full_name': f"{owner}/{repo_name}",
                'url': repo_url
            }
        except Exception as e:
            logger.error(f"Error extracting repo info: {e}")
            raise ValueError(f"Invalid GitHub URL: {e}")
    
    def get_github_api_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AskET-GitHub-QA'
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        return headers
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.get_github_api_headers())
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data['description'] or '',
                'language': repo_data['language'] or '',
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'topics': repo_data.get('topics', []),
                'default_branch': repo_data['default_branch'],
                'url': repo_data['html_url'],
                'api_url': repo_data['url']
            }
        except Exception as e:
            logger.error(f"Error getting repo info: {e}")
            raise
    
    def get_repo_contents(self, owner: str, repo: str, path: str = '', branch: str = 'main') -> List[Dict[str, Any]]:
        """Get repository contents from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            params = {'ref': branch}
            response = requests.get(url, headers=self.get_github_api_headers(), params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting repo contents: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, file_path: str, branch: str = 'main') -> str:
        """Get file content from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            params = {'ref': branch}
            response = requests.get(url, headers=self.get_github_api_headers(), params=params)
            response.raise_for_status()
            
            file_data = response.json()
            if file_data['type'] != 'file':
                return ''
            
            # Decode content
            content = file_data['content']
            encoding = file_data.get('encoding', 'base64')
            
            if encoding == 'base64':
                return base64.b64decode(content).decode('utf-8')
            else:
                return content
                
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return ''
    
    def is_technical_file(self, file_path: str) -> bool:
        """Check if a file contains technical documentation"""
        technical_extensions = {
            '.md', '.txt', '.rst', '.adoc', '.asciidoc',  # Documentation
            '.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h',  # Code
            '.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf',  # Config
            '.dockerfile', '.dockerignore', '.gitignore',  # Build/Deploy
            '.sh', '.bash', '.zsh', '.fish',  # Scripts
            '.sql', '.graphql', '.gql',  # Data
            '.proto', '.thrift', '.avdl'  # API definitions
        }
        
        technical_files = {
            'readme', 'readme.md', 'readme.txt', 'readme.rst',
            'license', 'license.txt', 'license.md',
            'changelog', 'changelog.md', 'changes.md',
            'contributing', 'contributing.md', 'contribute.md',
            'setup', 'setup.py', 'setup.cfg',
            'requirements', 'requirements.txt', 'requirements.in',
            'package.json', 'cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'makefile', 'cmakelists.txt', 'build.sh', 'install.sh',
            'api.md', 'api.rst', 'docs/api.md',
            'architecture.md', 'arch.md', 'design.md',
            'deployment.md', 'deploy.md', 'production.md'
        }
        
        file_lower = file_path.lower()
        file_name = Path(file_path).name.lower()
        file_stem = Path(file_path).stem.lower()
        
        # Check file extension
        if Path(file_path).suffix.lower() in technical_extensions:
            return True
        
        # Check specific file names
        if file_name in technical_files or file_stem in technical_files:
            return True
        
        # Check for documentation directories
        if any(part in file_lower for part in ['docs/', 'documentation/', 'examples/', 'samples/']):
            return True
        
        return False
    
    def extract_technical_content(self, owner: str, repo: str, branch: str = 'main') -> Dict[str, Any]:
        """Extract technical content from GitHub repository"""
        try:
            logger.info(f"Extracting technical content from {owner}/{repo}")
            
            # Get repository info
            repo_info = self.get_repo_info(owner, repo)
            
            # Get root contents
            contents = self.get_repo_contents(owner, repo, branch=branch)
            
            technical_files = {}
            processed_paths = set()
            
            def process_directory(path: str = ''):
                """Recursively process directory contents"""
                if path in processed_paths:
                    return
                processed_paths.add(path)
                
                try:
                    dir_contents = self.get_repo_contents(owner, repo, path, branch)
                    
                    for item in dir_contents:
                        item_path = item['path']
                        
                        if item['type'] == 'file' and self.is_technical_file(item_path):
                            try:
                                content = self.get_file_content(owner, repo, item_path, branch)
                                if content.strip():
                                    technical_files[item_path] = {
                                        'content': content,
                                        'size': item['size'],
                                        'type': item['type'],
                                        'url': item['html_url']
                                    }
                                    logger.info(f"Extracted: {item_path}")
                            except Exception as e:
                                logger.warning(f"Failed to extract {item_path}: {e}")
                        
                        elif item['type'] == 'dir':
                            # Skip certain directories to avoid infinite recursion
                            dir_name = item['name'].lower()
                            if dir_name not in ['.git', 'node_modules', 'vendor', '__pycache__', '.pytest_cache']:
                                process_directory(item_path)
                
                except Exception as e:
                    logger.warning(f"Failed to process directory {path}: {e}")
            
            # Start processing from root
            process_directory()
            
            return {
                'repo_info': repo_info,
                'technical_files': technical_files,
                'total_files': len(technical_files),
                'extraction_time': str(Path.cwd())
            }
            
        except Exception as e:
            logger.error(f"Error extracting technical content: {e}")
            raise
    
    def create_github_rag_chain(self, technical_content: Dict[str, Any]) -> Any:
        """Create RAG chain for GitHub repository content"""
        try:
            # Prepare documents for RAG
            documents = []
            
            for file_path, file_data in technical_content['technical_files'].items():
                content = file_data['content']
                
                # Split content into chunks (simple approach)
                chunks = self._split_content_into_chunks(content, file_path)
                
                for i, chunk in enumerate(chunks):
                    documents.append({
                        'content': chunk,
                        'source': file_path,
                        'title': f"{file_path} (chunk {i+1})",
                        'url': file_data['url'],
                        'type': 'github_file',
                        'score': 1.0
                    })
            
            # Create a simple in-memory RAG chain
            # For production, you'd want to use FAISS or another vector store
            return {
                'documents': documents,
                'repo_info': technical_content['repo_info'],
                'total_chunks': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error creating GitHub RAG chain: {e}")
            raise
    
    def _split_content_into_chunks(self, content: str, file_path: str, chunk_size: int = 1000) -> List[str]:
        """Split content into manageable chunks"""
        chunks = []
        
        # For markdown files, try to split by headers
        if file_path.lower().endswith('.md'):
            lines = content.split('\n')
            current_chunk = []
            
            for line in lines:
                current_chunk.append(line)
                
                # Split on headers or when chunk gets too large
                if (line.startswith('#') and len(current_chunk) > 10) or len('\n'.join(current_chunk)) > chunk_size:
                    chunk_text = '\n'.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append(chunk_text)
                    current_chunk = []
            
            # Add remaining content
            if current_chunk:
                chunk_text = '\n'.join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)
        else:
            # For other files, simple character-based splitting
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
        
        return chunks
    
    def ask_question(self, question: str, rag_chain: Dict[str, Any]) -> Dict[str, Any]:
        """Ask a question about the GitHub repository"""
        try:
            # Simple keyword-based search for now
            # In production, you'd use the actual RAG chain with embeddings
            relevant_docs = self._find_relevant_documents(question, rag_chain['documents'])
            
            # Generate answer using LLM (simplified for now)
            answer = self._generate_answer(question, relevant_docs, rag_chain['repo_info'])
            
            return {
                'question': question,
                'answer': answer,
                'sources': [doc['source'] for doc in relevant_docs],
                'relevant_docs': relevant_docs
            }
            
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return {
                'question': question,
                'answer': f"Sorry, I encountered an error while processing your question: {e}",
                'sources': [],
                'relevant_docs': []
            }
    
    def _find_relevant_documents(self, question: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find relevant documents using simple keyword matching"""
        question_lower = question.lower()
        keywords = question_lower.split()
        
        scored_docs = []
        
        for doc in documents:
            content_lower = doc['content'].lower()
            source_lower = doc['source'].lower()
            
            # Calculate relevance score
            score = 0
            
            # Exact keyword matches
            for keyword in keywords:
                if keyword in content_lower:
                    score += 2
                if keyword in source_lower:
                    score += 1
            
            # Bonus for README and documentation files
            if 'readme' in source_lower or 'docs/' in source_lower:
                score += 1
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
    
    def _generate_answer(self, question: str, relevant_docs: List[Dict[str, Any]], repo_info: Dict[str, Any]) -> str:
        """Generate answer using relevant documents"""
        try:
            # For now, create a simple answer
            # In production, you'd use Gemini or another LLM
            
            if not relevant_docs:
                return f"I couldn't find specific information about '{question}' in the {repo_info['full_name']} repository. Try asking about the project overview, setup instructions, or specific features."
            
            # Create context from relevant documents
            context_parts = []
            for doc in relevant_docs:
                content_preview = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
                context_parts.append(f"From {doc['source']}:\n{content_preview}")
            
            context = "\n\n".join(context_parts)
            
            # Simple answer generation
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['what', 'overview', 'about', 'purpose']):
                return f"Based on the repository content, {repo_info['full_name']} appears to be {repo_info['description']}. Here's what I found:\n\n{context}"
            
            elif any(word in question_lower for word in ['how', 'run', 'setup', 'install', 'demo']):
                return f"Here's how to set up and run {repo_info['full_name']}:\n\n{context}"
            
            elif any(word in question_lower for word in ['dependencies', 'requirements', 'packages']):
                return f"Here are the dependencies and requirements for {repo_info['full_name']}:\n\n{context}"
            
            elif any(word in question_lower for word in ['api', 'interface', 'usage']):
                return f"Here's information about the API and usage of {repo_info['full_name']}:\n\n{context}"
            
            else:
                return f"Here's what I found about '{question}' in the {repo_info['full_name']} repository:\n\n{context}"
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Sorry, I encountered an error while generating an answer: {e}"
    
    def export_qa_session(self) -> str:
        """Export the current Q&A session"""
        session = st.session_state.get(self.session_state_key, {})
        
        if not session.get('qa_history'):
            return "No Q&A history to export."
        
        export_data = {
            'repo_info': session.get('repo_info'),
            'qa_history': session['qa_history'],
            'export_time': str(Path.cwd())
        }
        
        return json.dumps(export_data, indent=2)

def create_github_qa_engine() -> GitHubQAEngine:
    """Create and return a GitHub Q&A engine instance"""
    return GitHubQAEngine() 