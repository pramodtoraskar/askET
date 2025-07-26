#!/usr/bin/env python3
"""
Test script for chunking logic without requiring OpenAI API
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import DataLoader
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def test_data_loading():
    """Test data loading functionality"""
    print("🧪 Testing data loading...")
    
    data_loader = DataLoader()
    
    # Test blog loading
    blogs = data_loader.load_blog_metadata()
    print(f"   📝 Loaded {len(blogs)} blogs")
    
    # Test project loading
    projects = data_loader.load_project_metadata()
    print(f"   🚀 Loaded {len(projects)} projects")
    
    # Test data merging
    merged_data = data_loader.merge_data()
    print(f"   🔄 Merged {len(merged_data)} total entries")
    
    # Show sample data
    if merged_data:
        sample = merged_data[0]
        print(f"   📋 Sample entry type: {sample['type']}")
        print(f"   📋 Sample title: {sample['title'][:50]}...")
    
    return merged_data

def test_text_preparation(data):
    """Test text preparation for chunking"""
    print("\n🧪 Testing text preparation...")
    
    # Import directly to avoid path issues
    import sys
    sys.path.append('.')
    from ingest.build_index import IndexBuilder
    
    # Create IndexBuilder without embeddings (for testing)
    builder = IndexBuilder()
    
    # Test text preparation
    texts = builder.prepare_text_for_chunking(data[:5])  # Test with first 5 items
    
    for i, text in enumerate(texts):
        print(f"   📄 Text {i+1} length: {len(text)} characters")
        print(f"   📄 Text {i+1} preview: {text[:100]}...")
        print()
    
    return texts

def test_chunking(texts):
    """Test chunking logic"""
    print("🧪 Testing chunking logic...")
    
    # Import directly to avoid path issues
    import sys
    sys.path.append('.')
    from ingest.build_index import IndexBuilder
    
    # Create IndexBuilder without embeddings (for testing)
    builder = IndexBuilder()
    
    # Test chunking with sample data
    test_data = [
        {
            'type': 'blog',
            'title': 'Test Blog',
            'author': 'Test Author',
            'date': '2025-01-01',
            'category': 'Test Category',
            'content': 'This is a test blog content. ' * 50,  # Create longer text
            'url': 'https://test.com'
        }
    ]
    
    # Create chunks
    builder.create_chunks(test_data)
    
    print(f"   ✂️  Created {len(builder.chunks)} chunks")
    print(f"   📊 Average chunk size: {sum(len(c) for c in builder.chunks) / len(builder.chunks):.0f} characters")
    
    # Show sample chunks
    for i, chunk in enumerate(builder.chunks[:3]):
        print(f"   📄 Chunk {i+1}: {chunk[:100]}...")
    
    return builder.chunks

def main():
    """Run all tests"""
    print("🚀 Starting chunking tests...\n")
    
    try:
        # Test data loading
        data = test_data_loading()
        
        # Test text preparation
        texts = test_text_preparation(data)
        
        # Test chunking
        chunks = test_chunking(texts)
        
        print("\n✅ All tests passed!")
        print(f"📊 Summary:")
        print(f"   - Data entries: {len(data)}")
        print(f"   - Sample texts: {len(texts)}")
        print(f"   - Generated chunks: {len(chunks)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 