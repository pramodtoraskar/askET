#!/usr/bin/env python3
"""
Test script to verify the built FAISS index
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import pickle
import json
import numpy as np
import faiss
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import GOOGLE_API_KEY, VECTOR_STORE_PATH
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def test_index_loading():
    """Test loading the built index"""
    print("🧪 Testing index loading...")
    
    try:
        # Load index
        index_path = Path(VECTOR_STORE_PATH)
        index = faiss.read_index(str(index_path))
        
        print(f"   ✅ Index loaded successfully")
        print(f"   📊 Index contains {index.ntotal} vectors")
        print(f"   📏 Vector dimension: {index.d}")
        
        return index
        
    except Exception as e:
        print(f"   ❌ Error loading index: {e}")
        return None

def test_metadata_loading():
    """Test loading index metadata"""
    print("\n🧪 Testing metadata loading...")
    
    try:
        # Load metadata
        metadata_path = Path(VECTOR_STORE_PATH).parent / f"{Path(VECTOR_STORE_PATH).stem}_metadata.pkl"
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        print(f"   ✅ Metadata loaded successfully")
        print(f"   📄 Metadata contains {len(metadata)} entries")
        
        # Show sample metadata
        print(f"   📝 Sample metadata:")
        for i, meta in enumerate(metadata[:3]):
            print(f"      Entry {i+1}: {meta['title'][:50]}... ({meta['type']})")
        
        return metadata
        
    except Exception as e:
        print(f"   ❌ Error loading metadata: {e}")
        return None

def test_info_loading():
    """Test loading index info"""
    print("\n🧪 Testing info loading...")
    
    try:
        # Load info
        info_path = Path(VECTOR_STORE_PATH).parent / f"{Path(VECTOR_STORE_PATH).stem}_info.json"
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        print(f"   ✅ Info loaded successfully")
        print(f"   📊 Index info:")
        for key, value in info.items():
            print(f"      {key}: {value}")
        
        return info
        
    except Exception as e:
        print(f"   ❌ Error loading info: {e}")
        return None

def test_similarity_search(index, metadata):
    """Test similarity search functionality"""
    print("\n🧪 Testing similarity search...")
    
    try:
        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Test query
        test_query = "OpenShift AI machine learning"
        print(f"   🔍 Query: '{test_query}'")
        
        # Generate query embedding
        query_embedding = embeddings.embed_query(test_query)
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search
        k = 3  # Top 3 results
        distances, indices = index.search(query_vector, k)
        
        print(f"   ✅ Found {len(indices[0])} similar documents")
        print(f"   📈 Similarity scores:")
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(metadata):
                doc = metadata[idx]
                similarity = 1 - distance  # Convert distance to similarity
                print(f"      {i+1}. {doc['title'][:60]}... (similarity: {similarity:.3f})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error in similarity search: {e}")
        logger.error(f"Error in similarity search: {e}")
        return False

def main():
    """Run all index tests"""
    print("🚀 Starting index verification tests...\n")
    
    success = True
    
    # Test index loading
    index = test_index_loading()
    if index is None:
        success = False
    
    # Test metadata loading
    metadata = test_metadata_loading()
    if metadata is None:
        success = False
    
    # Test info loading
    info = test_info_loading()
    if info is None:
        success = False
    
    # Test similarity search
    if index is not None and metadata is not None:
        if not test_similarity_search(index, metadata):
            success = False
    
    if success:
        print("\n✅ All index tests passed!")
        print("🎉 The FAISS index is working correctly!")
        print("\n📝 Next steps:")
        print("   1. Move to Phase 2: LangChain Integration")
        print("   2. Create the conversational interface")
        print("   3. Build the CLI chatbot")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 