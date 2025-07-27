#!/usr/bin/env python3
"""
Improved Index Rebuilding Script for Ask ET
Enhanced with content validation and better error handling
"""

import sys
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import time
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ingest.build_index import IndexBuilder
from src.data_loader import DataLoader
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def validate_url_accessibility(url: str, timeout: int = 10) -> dict:
    """Validate if a URL is accessible and returns content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            # Check if content is meaningful
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            word_count = len(text.split())
            
            return {
                "accessible": True,
                "status_code": response.status_code,
                "word_count": word_count,
                "content_length": len(response.content),
                "has_content": word_count > 50  # Minimum content threshold
            }
        else:
            return {
                "accessible": False,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "accessible": False,
            "error": "Timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "accessible": False,
            "error": "Connection Error"
        }
    except Exception as e:
        return {
            "accessible": False,
            "error": str(e)
        }

def validate_blog_urls(blog_metadata_path: str) -> dict:
    """Validate all blog URLs and return accessibility report"""
    logger.info("Validating blog URLs...")
    
    with open(blog_metadata_path, 'r') as f:
        blog_data = json.load(f)
    
    validation_results = {
        "total_urls": len(blog_data.get("scraped_urls", [])),
        "accessible": [],
        "inaccessible": [],
        "errors": []
    }
    
    for i, url in enumerate(blog_data.get("scraped_urls", []), 1):
        logger.info(f"Validating URL {i}/{len(blog_data['scraped_urls'])}: {url}")
        
        result = validate_url_accessibility(url)
        
        if result["accessible"] and result.get("has_content", False):
            validation_results["accessible"].append({
                "url": url,
                "word_count": result.get("word_count", 0),
                "content_length": result.get("content_length", 0)
            })
        else:
            validation_results["inaccessible"].append({
                "url": url,
                "error": result.get("error", "Unknown error")
            })
        
        # Be respectful with requests
        time.sleep(1)
    
    logger.info(f"Validation complete: {len(validation_results['accessible'])} accessible, {len(validation_results['inaccessible'])} inaccessible")
    return validation_results

def filter_accessible_urls(blog_metadata_path: str, validation_results: dict) -> list:
    """Filter out inaccessible URLs from the metadata"""
    accessible_urls = {item["url"] for item in validation_results["accessible"]}
    
    with open(blog_metadata_path, 'r') as f:
        blog_data = json.load(f)
    
    # Filter scraped URLs
    original_urls = blog_data.get("scraped_urls", [])
    filtered_urls = [url for url in original_urls if url in accessible_urls]
    
    logger.info(f"Filtered URLs: {len(filtered_urls)} accessible out of {len(original_urls)} total")
    
    return filtered_urls

def create_improved_blog_metadata(accessible_urls: list) -> dict:
    """Create improved blog metadata with only accessible URLs"""
    return {
        "metadata": {
            "generated_on": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "https://next.redhat.com/blog/",
            "total_blogs": len(accessible_urls),
            "scraped_urls": accessible_urls,
            "validation": "Content validated and filtered for accessibility"
        }
    }

def rebuild_index_with_validation():
    """Rebuild the index with content validation"""
    logger.info("Starting improved index rebuild with content validation...")
    
    # Paths
    blog_metadata_path = Path("data/blog_metadata.json")
    project_metadata_path = Path("data/project_metadata.json")
    vector_store_path = Path("vector_store/faiss_index")
    
    try:
        # Step 1: Validate blog URLs
        logger.info("Step 1: Validating blog URLs...")
        validation_results = validate_blog_urls(str(blog_metadata_path))
        
        # Save validation report
        validation_report_path = Path("logs/url_validation_report.json")
        validation_report_path.parent.mkdir(exist_ok=True)
        
        with open(validation_report_path, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"Validation report saved to {validation_report_path}")
        
        # Step 2: Filter accessible URLs
        logger.info("Step 2: Filtering accessible URLs...")
        accessible_urls = filter_accessible_urls(str(blog_metadata_path), validation_results)
        
        # Step 3: Create improved metadata
        logger.info("Step 3: Creating improved metadata...")
        improved_blog_metadata = create_improved_blog_metadata(accessible_urls)
        
        # Save improved metadata
        improved_blog_metadata_path = Path("data/blog_metadata_improved.json")
        with open(improved_blog_metadata_path, 'w') as f:
            json.dump(improved_blog_metadata, f, indent=2)
        
        logger.info(f"Improved blog metadata saved to {improved_blog_metadata_path}")
        
        # Step 4: Use existing IndexBuilder to rebuild index
        logger.info("Step 4: Rebuilding index with validated content...")
        
        # Create a temporary metadata file with only accessible URLs
        temp_metadata_path = Path("data/temp_blog_metadata.json")
        with open(temp_metadata_path, 'w') as f:
            json.dump(improved_blog_metadata, f, indent=2)
        
        # Temporarily replace the original metadata
        original_metadata_backup = Path("data/blog_metadata_backup.json")
        if blog_metadata_path.exists():
            import shutil
            shutil.copy2(blog_metadata_path, original_metadata_backup)
            shutil.copy2(temp_metadata_path, blog_metadata_path)
        
        try:
            # Use the existing IndexBuilder
            builder = IndexBuilder()
            builder.build_index()
            
            logger.info("Index rebuilt successfully with validated content")
            
        finally:
            # Restore original metadata
            if original_metadata_backup.exists():
                shutil.copy2(original_metadata_backup, blog_metadata_path)
                original_metadata_backup.unlink()
            
            # Clean up temporary files
            if temp_metadata_path.exists():
                temp_metadata_path.unlink()
        
        # Step 5: Create summary report
        logger.info("Step 5: Creating summary report...")
        
        # Get final stats from the rebuilt index
        data_loader = DataLoader()
        final_data = data_loader.merge_data()
        
        summary_report = {
            "rebuild_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "validation_results": validation_results,
            "index_stats": {
                "total_documents": len(final_data) if final_data else 0,
                "accessible_urls": len(accessible_urls),
                "inaccessible_urls": len(validation_results["inaccessible"])
            },
            "files_created": [
                str(improved_blog_metadata_path),
                str(validation_report_path),
                str(vector_store_path),
                str(vector_store_path.parent / f"{vector_store_path.stem}_metadata.pkl")
            ]
        }
        
        summary_report_path = Path("logs/rebuild_summary.json")
        with open(summary_report_path, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        logger.info(f"Summary report saved to {summary_report_path}")
        logger.info("Improved index rebuild completed successfully!")
        
        return summary_report
        
    except Exception as e:
        logger.error(f"Error in improved index rebuild: {e}")
        raise

def main():
    """Main function"""
    print("Starting improved index rebuild with content validation...")
    
    try:
        summary = rebuild_index_with_validation()
        
        print("\n" + "="*60)
        print("IMPROVED INDEX REBUILD COMPLETED")
        print("="*60)
        print(f"Total documents indexed: {summary['index_stats']['total_documents']}")
        print(f"Accessible URLs: {summary['index_stats']['accessible_urls']}")
        print(f"Inaccessible URLs: {summary['index_stats']['inaccessible_urls']}")
        print("\nFiles created:")
        for file_path in summary['files_created']:
            print(f"  • {file_path}")
        print("\nValidation report: logs/url_validation_report.json")
        print("Summary report: logs/rebuild_summary.json")
        
    except Exception as e:
        print(f"Error during improved index rebuild: {e}")
        logger.error(f"Error during improved index rebuild: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 