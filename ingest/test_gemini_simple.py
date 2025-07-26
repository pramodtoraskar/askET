#!/usr/bin/env python3
"""
Simple test for Gemini integration without API key
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

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("   ✅ langchain_google_genai imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import langchain_google_genai: {e}")
        return False
    
    try:
        import google.generativeai
        print("   ✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import google.generativeai: {e}")
        return False
    
    return True

def test_config():
    """Test configuration setup"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import GOOGLE_API_KEY, GEMINI_MODEL
        
        print(f"   📝 GEMINI_MODEL: {GEMINI_MODEL}")
        
        if GOOGLE_API_KEY:
            print("   ✅ GOOGLE_API_KEY is set")
        else:
            print("   ⚠️  GOOGLE_API_KEY not set (this is expected)")
            print("   📝 You can get a free API key from: https://makersuite.google.com/app/apikey")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing config: {e}")
        return False

def test_data_preparation():
    """Test data preparation without requiring API key"""
    print("\n🧪 Testing data preparation...")
    
    try:
        data_loader = DataLoader()
        data = data_loader.merge_data()
        
        if not data:
            print("   ❌ No data loaded")
            return False
        
        print(f"   ✅ Loaded {len(data)} documents")
        
        # Test text preparation manually
        texts = []
        for item in data[:3]:  # Test with first 3 items
            if item['type'] == 'blog':
                text_parts = [
                    f"Title: {item['title']}",
                    f"Author: {item['author']}",
                    f"Date: {item['date']}",
                    f"Category: {item['category']}",
                    f"Content: {item['content']}"
                ]
                text = "\n\n".join(filter(None, text_parts))
                
            elif item['type'] == 'project':
                text_parts = [
                    f"Project: {item['title']}",
                    f"Category: {item['category']}",
                    f"Description: {item['description']}",
                    f"GitHub Links: {', '.join(item['github_links'])}"
                ]
                text = "\n\n".join(filter(None, text_parts))
            
            texts.append(text)
        
        print(f"   📄 Prepared {len(texts)} texts for embedding")
        for i, text in enumerate(texts):
            print(f"      Text {i+1}: {len(text)} characters")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing data preparation: {e}")
        logger.error(f"Error testing data preparation: {e}")
        return False

def test_chunking():
    """Test chunking logic"""
    print("\n🧪 Testing chunking logic...")
    
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Test with sample text
        test_text = "This is a test blog content about Red Hat Emerging Technologies. " * 30
        
        # Split text into chunks
        chunks = text_splitter.split_text(test_text)
        
        print(f"   ✂️  Created {len(chunks)} chunks")
        print(f"   📊 Average chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} characters")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing chunking: {e}")
        logger.error(f"Error testing chunking: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Gemini integration tests...\n")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test configuration
    if not test_config():
        success = False
    
    # Test data preparation
    if not test_data_preparation():
        success = False
    
    # Test chunking
    if not test_chunking():
        success = False
    
    if success:
        print("\n✅ All Gemini integration tests passed!")
        print("🎉 Ready to build the index with Gemini embeddings!")
        print("\n📝 Next steps:")
        print("   1. Get a Google API key from: https://makersuite.google.com/app/apikey")
        print("   2. Add it to your .env file: GOOGLE_API_KEY=your_key_here")
        print("   3. Run: python ingest/build_index.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 