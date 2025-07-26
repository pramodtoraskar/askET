#!/usr/bin/env python3
"""
Test script for Gemini integration
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from src.data_loader import DataLoader
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def test_gemini_embeddings():
    """Test Gemini embeddings generation"""
    print("🧪 Testing Gemini embeddings...")
    
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from config import GOOGLE_API_KEY
        
        if not GOOGLE_API_KEY:
            print("   ⚠️  GOOGLE_API_KEY not set. Please set it in your .env file.")
            print("   📝 You can get a free API key from: https://makersuite.google.com/app/apikey")
            return False
        
        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Test with a simple text
        test_texts = [
            "Red Hat Emerging Technologies",
            "OpenShift AI and machine learning",
            "Kubernetes container orchestration"
        ]
        
        print("   🔄 Generating embeddings...")
        test_embeddings = embeddings.embed_documents(test_texts)
        
        print(f"   ✅ Generated {len(test_embeddings)} embeddings")
        print(f"   📊 Embedding dimension: {len(test_embeddings[0])}")
        
        # Test similarity
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        embeddings_array = np.array(test_embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        print("   📈 Similarity matrix:")
        for i, text in enumerate(test_texts):
            for j, other_text in enumerate(test_texts):
                if i != j:
                    similarity = similarity_matrix[i][j]
                    print(f"      '{text[:30]}...' vs '{other_text[:30]}...': {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing Gemini embeddings: {e}")
        logger.error(f"Error testing Gemini embeddings: {e}")
        return False

def test_data_preparation():
    """Test data preparation for embeddings"""
    print("\n🧪 Testing data preparation...")
    
    data_loader = DataLoader()
    data = data_loader.merge_data()
    
    if not data:
        print("   ❌ No data loaded")
        return False
    
    print(f"   ✅ Loaded {len(data)} documents")
    
    # Test text preparation
    from ingest.build_index import IndexBuilder
    
    builder = IndexBuilder()
    texts = builder.prepare_text_for_chunking(data[:3])  # Test with first 3 items
    
    print(f"   📄 Prepared {len(texts)} texts for embedding")
    for i, text in enumerate(texts):
        print(f"      Text {i+1}: {len(text)} characters")
    
    return True

def main():
    """Run Gemini integration tests"""
    print("🚀 Starting Gemini integration tests...\n")
    
    success = True
    
    # Test data preparation
    if not test_data_preparation():
        success = False
    
    # Test Gemini embeddings
    if not test_gemini_embeddings():
        success = False
    
    if success:
        print("\n✅ All Gemini integration tests passed!")
        print("🎉 Ready to build the index with Gemini embeddings!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 