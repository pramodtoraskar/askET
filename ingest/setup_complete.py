#!/usr/bin/env python3
"""
Complete Setup Script for Ask ET
Orchestrates the entire data preparation and vector store creation process
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class CompleteSetup:
    """Complete setup orchestrator for Ask ET"""
    
    def __init__(self):
        self.steps = []
        self.results = {}
        
    def run_step(self, step_name: str, step_function, *args, **kwargs) -> bool:
        """Run a setup step and track results"""
        logger.info(f"Running step: {step_name}")
        self.steps.append(step_name)
        
        start_time = time.time()
        try:
            result = step_function(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            self.results[step_name] = {
                'success': True,
                'duration': duration,
                'result': result
            }
            
            logger.info(f"Step completed: {step_name} (took {duration:.2f}s)")
            return True
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            self.results[step_name] = {
                'success': False,
                'duration': duration,
                'error': str(e)
            }
            
            logger.error(f"❌ Step failed: {step_name} (took {duration:.2f}s) - {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ is required")
            return False
        
        # Check required files
        required_files = [
            "config.py",
            "requirements.txt",
            "src/cli.py",
            "src/rag_chain_improved.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        # Check environment variables
        try:
            from config import GOOGLE_API_KEY
            if not GOOGLE_API_KEY:
                logger.error("GOOGLE_API_KEY not set in config.py")
                return False
        except ImportError:
            logger.error("Could not import config.py")
            return False
        
        logger.info("All prerequisites met")
        return True
    
    def prepare_data(self) -> bool:
        """Prepare comprehensive data"""
        try:
            from ingest.enhanced_blog_processor import EnhancedBlogProcessor
            
            processor = EnhancedBlogProcessor()
            processed_blogs = processor.process_all_blogs()
            processor.save_enhanced_data(processed_blogs)
            
            return True
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            return False
    
    def scrape_content(self) -> bool:
        """Scrape content from existing URLs"""
        try:
            from ingest.scrape_content import ContentScraper
            
            scraper = ContentScraper()
            scraped_content = scraper.scrape_all_blogs()
            
            if scraped_content:
                scraper.update_metadata_with_content(scraped_content)
                return True
            else:
                logger.warning("No content was scraped")
                return False
                
        except Exception as e:
            logger.error(f"Content scraping failed: {e}")
            return False
    
    def create_vector_store(self) -> bool:
        """Create enhanced vector store"""
        try:
            from ingest.create_vector_store import EnhancedVectorStoreCreator
            
            creator = EnhancedVectorStoreCreator()
            creator.create_vector_store()
            
            return True
        except Exception as e:
            logger.error(f"Vector store creation failed: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """Validate the complete setup"""
        logger.info("Validating setup...")
        
        # Check if data files exist
        data_files = [
            "data/blog_metadata.json",
            "data/project_metadata.json"
        ]
        
        missing_files = []
        for file_path in data_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing data files: {missing_files}")
            return False
        
        # Check if vector store exists
        vector_store_files = [
            "vector_store/faiss_index",
            "vector_store/faiss_index_metadata.pkl",
            "vector_store/faiss_index_info.json"
        ]
        
        missing_files = []
        for file_path in vector_store_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing vector store files: {missing_files}")
            return False
        
        # Test imports
        try:
            from src.rag_chain_improved import create_improved_rag_chain
            from src.cli import AskETCLI
            
            logger.info("All imports successful")
            return True
            
        except Exception as e:
            logger.error(f"Import test failed: {e}")
            return False
    
    def print_summary(self) -> None:
        """Print setup summary"""
        logger.info("\n" + "="*60)
        logger.info("SETUP SUMMARY")
        logger.info("="*60)
        
        total_steps = len(self.steps)
        successful_steps = sum(1 for result in self.results.values() if result['success'])
        
        logger.info(f"Total steps: {total_steps}")
        logger.info(f"Successful: {successful_steps}")
        logger.info(f"Failed: {total_steps - successful_steps}")
        
        total_duration = sum(result['duration'] for result in self.results.values())
        logger.info(f"Total duration: {total_duration:.2f}s")
        
        logger.info("\nStep Details:")
        for step_name in self.steps:
            result = self.results[step_name]
            status = "PASS" if result['success'] else "FAIL"
            duration = result['duration']
            
            if result['success']:
                logger.info(f"  {status} {step_name} ({duration:.2f}s)")
            else:
                error = result.get('error', 'Unknown error')
                logger.info(f"  {status} {step_name} ({duration:.2f}s) - {error}")
        
        if successful_steps == total_steps:
            logger.info("\nSetup completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Test CLI: python src/cli.py")
            logger.info("2. Test web interface: python run_web.py --app basic")
            logger.info("3. Start using Ask ET!")
        else:
            logger.info("\nSetup completed with errors")
            logger.info("Please check the logs above and fix any issues")

def main():
    """Main setup function"""
    logger.info("Starting Complete Ask ET Setup")
    logger.info("="*60)
    
    setup = CompleteSetup()
    
    # Run setup steps
    steps = [
        ("Prerequisites Check", setup.check_prerequisites),
        ("Data Preparation", setup.prepare_data),
        ("Content Scraping", setup.scrape_content),
        ("Vector Store Creation", setup.create_vector_store),
        ("Setup Validation", setup.validate_setup)
    ]
    
    for step_name, step_function in steps:
        success = setup.run_step(step_name, step_function)
        if not success and step_name == "Prerequisites Check":
            logger.error("❌ Prerequisites check failed. Cannot continue.")
            break
    
    # Print summary
    setup.print_summary()

if __name__ == "__main__":
    main() 