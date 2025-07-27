#!/usr/bin/env python3
"""
Content Scraping Script
Scrapes content from existing blog URLs without POC dependencies
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import shutil

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class ContentScraper:
    """Scrapes content from blog URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        self.delay = 1
        
    def load_existing_metadata(self) -> Dict[str, Any]:
        """Load existing blog metadata"""
        metadata_file = Path("data/blog_metadata.json")
        if not metadata_file.exists():
            logger.error("blog_metadata.json not found")
            return {}
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded existing metadata with {len(data.get('blogs', []))} blogs")
            return data
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def scrape_blog_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single blog URL"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            # Extract author
            author_elem = soup.find('span', class_='author') or soup.find('a', class_='author')
            author = author_elem.get_text().strip() if author_elem else "Unknown Author"
            
            # Extract main content
            content_elem = soup.find('article') or soup.find('div', class_='entry-content') or soup.find('div', class_='post-content')
            if not content_elem:
                content_elem = soup.find('body')
            
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # Extract text content
                text_content = content_elem.get_text(separator='\n', strip=True)
                text_content = self.clean_content(text_content)
                
                # Extract HTML content
                html_content = str(content_elem)
                
                # Extract headings
                headings = []
                for heading in content_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    headings.append({
                        'level': heading.name,
                        'text': heading.get_text().strip()
                    })
                
                # Extract links
                links = []
                for link in content_elem.find_all('a', href=True):
                    links.append({
                        'text': link.get_text().strip(),
                        'url': link['href']
                    })
                
                # Extract images
                images = []
                for img in content_elem.find_all('img', src=True):
                    images.append({
                        'alt': img.get('alt', ''),
                        'src': img['src']
                    })
                
                # Extract code blocks
                code_blocks = []
                for code in content_elem.find_all(['pre', 'code']):
                    if code.name == 'pre':
                        code_elem = code.find('code')
                        if code_elem:
                            language = code_elem.get('class', [''])[0] if code_elem.get('class') else ''
                            code_blocks.append({
                                'language': language,
                                'content': code_elem.get_text(),
                                'type': 'block'
                            })
                    elif code.name == 'code' and not code.find_parent('pre'):
                        code_blocks.append({
                            'language': '',
                            'content': code.get_text(),
                            'type': 'inline'
                        })
                
                return {
                    'metadata': {
                        'url': url,
                        'title': title,
                        'author': author,
                        'date': '',
                        'categories': [],
                        'tags': [],
                        'excerpt': text_content[:200] + '...' if len(text_content) > 200 else text_content,
                        'read_time': '',
                        'featured_image': '',
                        'word_count': len(text_content.split())
                    },
                    'content': {
                        'html_content': html_content,
                        'text_content': text_content,
                        'headings': headings,
                        'links': links,
                        'images': images,
                        'code_blocks': code_blocks
                    },
                    'scraped_at': datetime.now().isoformat()
                }
            
            else:
                logger.warning(f"No content found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted patterns
        content = re.sub(r'Share this page|Follow us|Subscribe|Newsletter', '', content, flags=re.IGNORECASE)
        
        # Clean up line breaks
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def scrape_all_blogs(self) -> List[Dict[str, Any]]:
        """Scrape content from all blog URLs"""
        # Load existing metadata
        existing_data = self.load_existing_metadata()
        if not existing_data:
            return []
        
        # Get URLs to scrape
        urls_to_scrape = existing_data.get('metadata', {}).get('scraped_urls', [])
        if not urls_to_scrape:
            logger.warning("No URLs found to scrape")
            return []
        
        logger.info(f"Found {len(urls_to_scrape)} URLs to scrape")
        
        # Scrape each URL
        scraped_content = []
        for i, url in enumerate(urls_to_scrape, 1):
            logger.info(f"Scraping {i}/{len(urls_to_scrape)}: {url}")
            
            content = self.scrape_blog_content(url)
            if content:
                scraped_content.append(content)
                logger.info(f"Successfully scraped: {content['metadata']['title']}")
            else:
                logger.warning(f"Failed to scrape: {url}")
            
            # Add delay to be respectful
            if i < len(urls_to_scrape):
                time.sleep(self.delay)
        
        logger.info(f"Successfully scraped {len(scraped_content)} out of {len(urls_to_scrape)} blogs")
        return scraped_content
    
    def update_metadata_with_content(self, scraped_content: List[Dict[str, Any]]) -> None:
        """Update the metadata file with scraped content"""
        # Load existing metadata
        existing_data = self.load_existing_metadata()
        if not existing_data:
            logger.error("No existing metadata to update")
            return
        
        # Create a mapping of URLs to scraped content
        content_map = {item['metadata']['url']: item for item in scraped_content}
        
        # Update existing blogs with content
        updated_blogs = []
        for blog in existing_data.get('blogs', []):
            url = blog.get('metadata', {}).get('url', '')
            if url in content_map:
                # Update with scraped content
                updated_blog = content_map[url]
                updated_blogs.append(updated_blog)
                logger.info(f"Updated content for: {updated_blog['metadata']['title']}")
            else:
                # Keep existing blog entry
                updated_blogs.append(blog)
        
        # Update the data structure
        existing_data['blogs'] = updated_blogs
        existing_data['metadata']['last_updated'] = datetime.now().isoformat()
        existing_data['metadata']['content_scraped'] = len(scraped_content)
        
        # Backup original file
        backup_file = Path("data/blog_metadata_backup.json")
        if Path("data/blog_metadata.json").exists():
            shutil.copy("data/blog_metadata.json", backup_file)
            logger.info(f"Backed up original metadata to {backup_file}")
        
        # Save updated metadata
        with open("data/blog_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated metadata with content for {len(scraped_content)} blogs")

def main():
    """Main function"""
    logger.info("Starting content scraping...")
    
    scraper = ContentScraper()
    
    # Scrape all blogs
    scraped_content = scraper.scrape_all_blogs()
    
    if scraped_content:
        # Update metadata with scraped content
        scraper.update_metadata_with_content(scraped_content)
        logger.info("Content scraping completed successfully!")
    else:
        logger.warning("No content was scraped")

if __name__ == "__main__":
    main() 