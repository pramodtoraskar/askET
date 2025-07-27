#!/usr/bin/env python3
"""
Enhanced Vector Store Creation Script
Creates comprehensive FAISS index with enhanced content processing
"""

import sys
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import faiss
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import (
    VECTOR_STORE_PATH, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    GOOGLE_API_KEY,
    GEMINI_MODEL
)
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class EnhancedVectorStoreCreator:
    """Creates enhanced FAISS vector store with comprehensive content processing"""
    
    def __init__(self):
        self.vector_store_path = Path(VECTOR_STORE_PATH)
        self.vector_store_path.parent.mkdir(exist_ok=True)
        
        # Initialize text splitter with optimized settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize embeddings
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Storage for chunks and metadata
        self.chunks = []
        self.chunk_metadata = []
        self.index = None
        
    def load_data(self) -> Dict[str, Any]:
        """Load blog and project data"""
        logger.info("Loading data files...")
        
        data = {
            'blogs': [],
            'projects': []
        }
        
        # Load blog data - try enhanced format first, then fallback
        blog_file = Path("data/blog_metadata.json")
        if blog_file.exists():
            try:
                with open(blog_file, 'r', encoding='utf-8') as f:
                    blog_data = json.load(f)
                
                # Check if this is enhanced format
                blogs = blog_data.get('blogs', [])
                if blogs and 'raw_data' in blogs[0]:
                    # Enhanced format - use as is
                    data['blogs'] = blogs
                    logger.info(f"Loaded {len(data['blogs'])} enhanced blogs")
                else:
                    # Standard format - convert to enhanced format
                    enhanced_blogs = []
                    for blog in blogs:
                        enhanced_blog = {
                            'raw_data': blog,
                            'knowledge_base': {},
                            'training_text': ''
                        }
                        enhanced_blogs.append(enhanced_blog)
                    data['blogs'] = enhanced_blogs
                    logger.info(f"Converted {len(data['blogs'])} blogs to enhanced format")
                    
            except Exception as e:
                logger.error(f"Error loading blog data: {e}")
        else:
            logger.warning("blog_metadata.json not found")
        
        # Load project data
        project_file = Path("data/project_metadata.json")
        if project_file.exists():
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                data['projects'] = project_data.get('projects', [])
                logger.info(f"Loaded {len(data['projects'])} projects")
            except Exception as e:
                logger.error(f"Error loading project data: {e}")
        else:
            logger.warning("project_metadata.json not found")
        
        return data
    
    def process_blog_content(self, blog: Dict[str, Any]) -> List[str]:
        """Process blog content into structured text chunks"""
        texts = []
        
        # Check if this is enhanced blog data
        if 'raw_data' in blog:
            # Enhanced blog data format
            raw_data = blog['raw_data']
            knowledge_base = blog.get('knowledge_base', {})
            training_text = blog.get('training_text', '')
            
            # Use training text if available (most comprehensive)
            if training_text:
                return [training_text]
            
            # Fallback to knowledge base
            if knowledge_base:
                kb_content = knowledge_base.get('content', {})
                
                # Basic metadata
                metadata_parts = [
                    f"Title: {knowledge_base.get('title', 'Unknown Title')}",
                    f"Author: {knowledge_base.get('author', 'Unknown Author')}",
                    f"Date: {knowledge_base.get('date', 'Unknown Date')}",
                    f"Category: {knowledge_base.get('category', 'General')}",
                    f"URL: {knowledge_base.get('url', '')}"
                ]
                
                # Add series information if available
                if knowledge_base.get('series_info'):
                    metadata_parts.append(f"Series: {knowledge_base['series_info']}")
                
                # Add summary
                if kb_content.get('summary'):
                    metadata_parts.append(f"Summary: {kb_content['summary']}")
                
                # Add key concepts
                if kb_content.get('key_concepts'):
                    concepts_text = "Key Concepts:\n" + "\n".join([f"• {concept}" for concept in kb_content['key_concepts']])
                    metadata_parts.append(concepts_text)
                
                # Add technical details
                if kb_content.get('technical_details'):
                    for detail in kb_content['technical_details']:
                        detail_text = f"{detail['topic']}:\n{detail['details']}"
                        metadata_parts.append(detail_text)
                
                # Add code examples
                if kb_content.get('code_examples'):
                    for example in kb_content['code_examples']:
                        code_text = f"Code Example ({example['language']}):\n```{example['language']}\n{example['code']}\n```"
                        metadata_parts.append(code_text)
                
                # Add best practices
                if kb_content.get('best_practices'):
                    for practice in kb_content['best_practices']:
                        practice_text = f"Best Practice - {practice['topic']}:\n{practice['practices']}"
                        metadata_parts.append(practice_text)
                
                combined_text = "\n\n".join(metadata_parts)
                return [combined_text]
            
            # Fallback to raw data
            blog = raw_data
        
        # Original blog processing (for backward compatibility)
        # Basic metadata
        metadata_parts = [
            f"Title: {blog.get('title', 'Unknown Title')}",
            f"Author: {blog.get('author', 'Unknown Author')}",
            f"Date: {blog.get('date', 'Unknown Date')}",
            f"Category: {blog.get('category', 'General')}",
            f"URL: {blog.get('url', '')}"
        ]
        
        # Add series information if available
        if blog.get('series_info'):
            metadata_parts.append(f"Series: {blog['series_info']}")
        
        # Process content structure
        content = blog.get('content', {})
        
        # Introduction
        if content.get('introduction'):
            intro_text = f"Introduction:\n{content['introduction']}"
            texts.append(intro_text)
        
        # Process sections
        sections = content.get('sections', [])
        for section in sections:
            heading = section.get('heading', '')
            section_content = section.get('content', '')
            
            if heading and section_content:
                section_text = f"{heading}:\n{section_content}"
                texts.append(section_text)
        
        # Process code blocks
        code_blocks = content.get('code_blocks', [])
        for code_block in code_blocks:
            language = code_block.get('language', '')
            code_content = code_block.get('content', '')
            code_type = code_block.get('type', 'block')
            
            if code_content:
                code_text = f"Code Example ({language}):\n```{language}\n{code_content}\n```"
                texts.append(code_text)
        
        # Process tables
        tables = content.get('tables', [])
        for table in tables:
            if table:
                table_text = "Table:\n"
                for row in table:
                    table_text += " | ".join(row) + "\n"
                texts.append(table_text)
        
        # Combine all parts
        if texts:
            combined_text = "\n\n".join(metadata_parts + texts)
            return [combined_text]
        
        # Fallback to basic content if no structured content
        if blog.get('content', {}).get('text_content'):
            fallback_text = "\n\n".join(metadata_parts + [blog['content']['text_content']])
            return [fallback_text]
        
        return []
    
    def process_project_content(self, project: Dict[str, Any]) -> List[str]:
        """Process project content into structured text chunks"""
        texts = []
        
        # Project metadata
        metadata_parts = [
            f"Project: {project.get('name', 'Unknown Project')}",
            f"Category: {project.get('category', 'General')}",
            f"Description: {project.get('description', 'No description available')}",
            f"Project URL: {project.get('project_url', '')}"
        ]
        
        # Add GitHub links
        github_links = project.get('github_links', [])
        if github_links:
            metadata_parts.append(f"GitHub Links: {', '.join(github_links)}")
        
        # Combine metadata
        project_text = "\n\n".join(metadata_parts)
        texts.append(project_text)
        
        return texts
    
    def create_enhanced_chunks(self, data: Dict[str, Any]) -> None:
        """Create enhanced text chunks from data"""
        logger.info("Creating enhanced text chunks...")
        
        # Process blogs
        for blog in tqdm(data['blogs'], desc="Processing blogs"):
            blog_texts = self.process_blog_content(blog)
            
            for text in blog_texts:
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                for chunk in chunks:
                    self.chunks.append(chunk)
                    self.chunk_metadata.append({
                        'type': 'blog',
                        'title': blog.get('title', 'Unknown Title'),
                        'author': blog.get('author', 'Unknown Author'),
                        'url': blog.get('url', ''),
                        'category': blog.get('category', 'General'),
                        'chunk_index': len(self.chunks) - 1
                    })
        
        # Process projects
        for project in tqdm(data['projects'], desc="Processing projects"):
            project_texts = self.process_project_content(project)
            
            for text in project_texts:
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                for chunk in chunks:
                    self.chunks.append(chunk)
                    self.chunk_metadata.append({
                        'type': 'project',
                        'name': project.get('name', 'Unknown Project'),
                        'category': project.get('category', 'General'),
                        'project_url': project.get('project_url', ''),
                        'github_links': project.get('github_links', []),
                        'chunk_index': len(self.chunks) - 1
                    })
        
        logger.info(f"Created {len(self.chunks)} chunks from {len(data['blogs'])} blogs and {len(data['projects'])} projects")
    
    def generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all chunks"""
        logger.info("Generating embeddings...")
        
        if not self.chunks:
            raise ValueError("No chunks available for embedding generation")
        
        # Generate embeddings in batches
        batch_size = 10
        all_embeddings = []
        
        for i in tqdm(range(0, len(self.chunks), batch_size), desc="Generating embeddings"):
            batch = self.chunks[i:i + batch_size]
            try:
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size}: {e}")
                # Add zero embeddings for failed chunks
                for _ in batch:
                    all_embeddings.append([0.0] * 768)  # Default embedding dimension
        
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        logger.info(f"Generated embeddings with shape: {embeddings_array.shape}")
        
        return embeddings_array
    
    def build_faiss_index(self, embeddings: np.ndarray) -> None:
        """Build FAISS index from embeddings"""
        logger.info("Building FAISS index...")
        
        # Get embedding dimension
        dimension = embeddings.shape[1]
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        self.index.add(embeddings)
        
        logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def save_vector_store(self) -> None:
        """Save vector store and metadata"""
        logger.info("Saving vector store...")
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.vector_store_path))
        
        # Save metadata
        metadata = {
            'chunk_metadata': self.chunk_metadata,
            'total_chunks': len(self.chunks),
            'embedding_dimension': self.index.d,
            'index_type': 'IndexFlatIP',
            'created_at': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        metadata_path = self.vector_store_path.parent / 'faiss_index_metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Save index info
        info_path = self.vector_store_path.parent / 'faiss_index_info.json'
        info = {
            'total_vectors': int(self.index.ntotal),
            'dimension': int(self.index.d),
            'index_type': 'IndexFlatIP',
            'created_at': metadata['created_at'],
            'version': metadata['version']
        }
        
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Vector store saved to {self.vector_store_path}")
        logger.info(f"Metadata saved to {metadata_path}")
        logger.info(f"Index info saved to {info_path}")
    
    def create_vector_store(self) -> None:
        """Main method to create the vector store"""
        logger.info("Starting enhanced vector store creation...")
        
        # Load data
        data = self.load_data()
        
        if not data['blogs'] and not data['projects']:
            logger.error("No data available for vector store creation")
            return
        
        # Create chunks
        self.create_enhanced_chunks(data)
        
        # Generate embeddings
        embeddings = self.generate_embeddings()
        
        # Build FAISS index
        self.build_faiss_index(embeddings)
        
        # Save vector store
        self.save_vector_store()
        
        logger.info("Enhanced vector store creation completed successfully!")

def main():
    """Main function"""
    logger.info("Starting enhanced vector store creation...")
    
    creator = EnhancedVectorStoreCreator()
    creator.create_vector_store()

if __name__ == "__main__":
    main() 