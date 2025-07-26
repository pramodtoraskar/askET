#!/usr/bin/env python3
"""
Simple test for data loading and chunking
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
    
    texts = []
    
    for item in data[:5]:  # Test with first 5 items
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
    
    for i, text in enumerate(texts):
        print(f"   📄 Text {i+1} length: {len(text)} characters")
        print(f"   📄 Text {i+1} preview: {text[:100]}...")
        print()
    
    return texts

def test_chunking_logic():
    """Test chunking logic with a simple example"""
    print("🧪 Testing chunking logic...")
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Test with sample text
    test_text = "This is a test blog content. " * 50  # Create longer text
    
    # Split text into chunks
    chunks = text_splitter.split_text(test_text)
    
    print(f"   ✂️  Created {len(chunks)} chunks")
    print(f"   📊 Average chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} characters")
    
    # Show sample chunks
    for i, chunk in enumerate(chunks[:3]):
        print(f"   📄 Chunk {i+1}: {chunk[:100]}...")
    
    return chunks

def main():
    """Run all tests"""
    print("🚀 Starting simple tests...\n")
    
    try:
        # Test data loading
        data = test_data_loading()
        
        # Test text preparation
        texts = test_text_preparation(data)
        
        # Test chunking
        chunks = test_chunking_logic()
        
        print("\n✅ All tests passed!")
        print(f"📊 Summary:")
        print(f"   - Data entries: {len(data)}")
        print(f"   - Sample texts: {len(texts)}")
        print(f"   - Generated chunks: {len(chunks)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 