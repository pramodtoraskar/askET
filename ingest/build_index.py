#!/usr/bin/env python3
"""
Core ingestion pipeline for Ask ET chatbot
Builds FAISS index from blog and project metadata
"""

import sys
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
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
from src.data_loader import DataLoader
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class IndexBuilder:
    """Builds and manages FAISS index for Ask ET chatbot"""
    
    def __init__(self):
        self.vector_store_path = Path(VECTOR_STORE_PATH)
        self.vector_store_path.parent.mkdir(exist_ok=True)
        
        # Initialize components
        self.data_loader = DataLoader()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
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
        
    def prepare_text_for_chunking(self, data: List[Dict[str, Any]]) -> List[str]:
        """Prepare text data for chunking"""
        texts = []
        
        for item in data:
            if item['type'] == 'blog':
                # For blogs, combine title, content, and metadata
                text_parts = [
                    f"Title: {item['title']}",
                    f"Author: {item['author']}",
                    f"Date: {item['date']}",
                    f"Category: {item['category']}",
                    f"Content: {item['content']}"
                ]
                text = "\n\n".join(filter(None, text_parts))
                
            elif item['type'] == 'project':
                # For projects, combine name, description, and metadata
                text_parts = [
                    f"Project: {item['title']}",
                    f"Category: {item['category']}",
                    f"Description: {item['description']}",
                    f"GitHub Links: {', '.join(item['github_links'])}"
                ]
                text = "\n\n".join(filter(None, text_parts))
            
            texts.append(text)
        
        return texts
    
    def create_chunks(self, data: List[Dict[str, Any]]) -> None:
        """Create text chunks from data"""
        logger.info("Creating text chunks...")
        
        texts = self.prepare_text_for_chunking(data)
        
        for i, text in enumerate(tqdm(texts, desc="Chunking texts")):
            try:
                # Split text into chunks
                text_chunks = self.text_splitter.split_text(text)
                
                # Store chunks with metadata
                for j, chunk in enumerate(text_chunks):
                    self.chunks.append(chunk)
                    
                    # Preserve metadata for each chunk
                    chunk_meta = {
                        'original_index': i,
                        'chunk_index': j,
                        'type': data[i]['type'],
                        'title': data[i]['title'],
                        'url': data[i].get('url', ''),
                        'project_url': data[i].get('project_url', ''),
                        'github_links': data[i].get('github_links', []),
                        'category': data[i].get('category', ''),
                        'author': data[i].get('author', ''),
                        'date': data[i].get('date', ''),
                        'chunk_size': len(chunk)
                    }
                    self.chunk_metadata.append(chunk_meta)
                    
            except Exception as e:
                logger.error(f"Error chunking text {i}: {e}")
                continue
        
        logger.info(f"Created {len(self.chunks)} chunks from {len(data)} documents")
    
    def generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all chunks"""
        logger.info("Generating embeddings...")
        
        if not self.chunks:
            raise ValueError("No chunks available. Run create_chunks() first.")
        
        # Generate embeddings in batches
        batch_size = 100
        all_embeddings = []
        
        for i in tqdm(range(0, len(self.chunks), batch_size), desc="Generating embeddings"):
            batch = self.chunks[i:i + batch_size]
            try:
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size}: {e}")
                # Add zero vectors for failed chunks
                all_embeddings.extend([[0.0] * 1536] * len(batch))
        
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        logger.info(f"Generated embeddings shape: {embeddings_array.shape}")
        
        return embeddings_array
    
    def build_faiss_index(self, embeddings: np.ndarray) -> None:
        """Build FAISS index from embeddings"""
        logger.info("Building FAISS index...")
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        self.index.add(embeddings)
        
        logger.info(f"FAISS index built with {self.index.ntotal} vectors")
    
    def save_index(self) -> None:
        """Save FAISS index and metadata"""
        logger.info("Saving index and metadata...")
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.vector_store_path))
        
        # Save metadata
        metadata_path = self.vector_store_path.parent / f"{self.vector_store_path.stem}_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.chunk_metadata, f)
        
        # Save index info
        info_path = self.vector_store_path.parent / f"{self.vector_store_path.stem}_info.json"
        info = {
            'created_at': datetime.now().isoformat(),
            'total_chunks': len(self.chunks),
            'total_documents': len(set(m['original_index'] for m in self.chunk_metadata)),
            'chunk_size': CHUNK_SIZE,
            'chunk_overlap': CHUNK_OVERLAP,
            'embedding_model': 'models/embedding-001',
            'index_type': 'IndexFlatIP',
            'dimension': self.index.d if self.index else None
        }
        
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Index saved to {self.vector_store_path}")
        logger.info(f"Metadata saved to {metadata_path}")
        logger.info(f"Info saved to {info_path}")
    
    def build_index(self) -> None:
        """Complete index building pipeline"""
        logger.info("Starting index building pipeline...")
        
        # Load and validate data
        data = self.data_loader.merge_data()
        if not data:
            raise ValueError("No data loaded. Check your metadata files.")
        
        logger.info(f"Loaded {len(data)} documents for indexing")
        
        # Create chunks
        self.create_chunks(data)
        
        # Generate embeddings
        embeddings = self.generate_embeddings()
        
        # Build FAISS index
        self.build_faiss_index(embeddings)
        
        # Save everything
        self.save_index()
        
        logger.info("Index building pipeline completed successfully!")

def main():
    """Main function to build the index"""
    try:
        builder = IndexBuilder()
        builder.build_index()
        print("✅ Index built successfully!")
        
    except Exception as e:
        logger.error(f"Error building index: {e}")
        print(f"❌ Error building index: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 