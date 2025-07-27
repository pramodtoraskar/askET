#!/usr/bin/env python3
"""
Enhanced Blog Processor for Ask ET
Incorporates sophisticated content extraction and LLM formatting from POC scripts
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

class EnhancedBlogProcessor:
    """Enhanced blog processor with sophisticated content extraction and LLM formatting"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.timeout = 30
        self.delay = 1
        
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
    
    def crawl_blog_links(self) -> List[str]:
        """Crawl all blog links from Red Hat Emerging Technologies"""
        logger.info("Crawling blog links...")
        
        base_url = "https://next.redhat.com"
        start_url = f"{base_url}/blog/"
        visited_pages = set()
        all_blog_links = []
        
        url = start_url
        page_count = 0
        
        while url and url not in visited_pages and page_count < 50:  # Safety limit
            logger.info(f"Fetching page {page_count + 1}: {url}")
            visited_pages.add(url)
            page_count += 1
            
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract blog links
                articles = soup.select("article h2 a")
                blog_links = [a['href'] for a in articles if a['href'].startswith("https://")]
                all_blog_links.extend(blog_links)
                logger.info(f"Found {len(blog_links)} blog links on this page")
                
                # Find next page
                nav = soup.find("div", class_="pagination")
                if nav:
                    next_link = nav.find("a", string="« Older Entries")
                    url = next_link['href'] if next_link else None
                else:
                    url = None
                
                time.sleep(self.delay)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                break
        
        # Remove duplicates and sort
        all_blog_links = sorted(list(set(all_blog_links)))
        logger.info(f"Total unique blog links found: {len(all_blog_links)}")
        
        return all_blog_links
    
    def extract_blog_content_for_llm(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract complete blog content from a Red Hat blog post for LLM knowledge building"""
        try:
            logger.info(f"Extracting enhanced content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract blog metadata
            blog_data = {
                'url': url,
                'title': '',
                'author': '',
                'date': '',
                'category': '',
                'series_info': '',
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_elem = soup.find('h1')
            if title_elem:
                blog_data['title'] = title_elem.get_text(strip=True)
            
            # Extract author and date - enhanced pattern matching
            author_date_elem = soup.find('div', class_='author-date') or soup.find('div', class_='meta')
            if author_date_elem:
                author_text = author_date_elem.get_text()
                # Look for author pattern
                author_match = re.search(r'by\s+([^|]+)', author_text)
                if author_match:
                    blog_data['author'] = author_match.group(1).strip()
                
                # Look for date pattern
                date_match = re.search(r'(\w+\s+\d+,\s+\d{4})', author_text)
                if date_match:
                    blog_data['date'] = date_match.group(1)
            
            # Fallback to regex pattern if not found
            if not blog_data['author'] or not blog_data['date']:
                full_text = soup.get_text()
                author_match = re.search(r'by\s+([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|\n]+)', full_text)
                if author_match:
                    blog_data['author'] = author_match.group(1).strip()
                    blog_data['date'] = author_match.group(2).strip()
                    blog_data['category'] = author_match.group(3).strip()
            
            # Extract category
            category_elem = soup.find('span', class_='category') or soup.find('a', class_='category')
            if category_elem:
                blog_data['category'] = category_elem.get_text(strip=True)
            
            # Extract series information
            series_elem = soup.find('div', class_='series-info') or soup.find('p', string=re.compile(r'article #\d+'))
            if series_elem:
                blog_data['series_info'] = series_elem.get_text(strip=True)
            else:
                # Fallback to regex
                series_pattern = r'This is article #\d+ in our series on [^.]+\.'
                series_match = re.search(series_pattern, full_text)
                if series_match:
                    blog_data['series_info'] = series_match.group(0)
            
            # Extract main content with enhanced structure
            content_data = {
                'introduction': '',
                'sections': [],
                'code_blocks': [],
                'images': [],
                'tables': [],
                'conclusion': '',
                'references': []
            }
            
            # Find the main content area
            main_content = soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post-content')
            
            if main_content:
                # Extract introduction (first paragraph or two)
                intro_elems = main_content.find_all('p')[:3]  # First 3 paragraphs
                content_data['introduction'] = '\n\n'.join([p.get_text(strip=True) for p in intro_elems if p.get_text(strip=True)])
                
                # Extract sections with headings - enhanced processing
                sections = []
                current_section = None
                
                for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote']):
                    if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        # Start new section
                        if current_section:
                            sections.append(current_section)
                        
                        current_section = {
                            'heading': elem.get_text(strip=True),
                            'content': '',
                            'subsections': []
                        }
                    elif current_section:
                        # Add content to current section
                        if elem.name == 'p':
                            current_section['content'] += elem.get_text(strip=True) + '\n\n'
                        elif elem.name in ['ul', 'ol']:
                            items = [li.get_text(strip=True) for li in elem.find_all('li')]
                            current_section['content'] += '\n'.join([f"• {item}" for item in items]) + '\n\n'
                        elif elem.name == 'blockquote':
                            current_section['content'] += f"Quote: {elem.get_text(strip=True)}\n\n"
                
                # Add the last section
                if current_section:
                    sections.append(current_section)
                
                content_data['sections'] = sections
                
                # Extract code blocks with enhanced processing
                code_blocks = main_content.find_all(['pre', 'code'])
                for code in code_blocks:
                    if code.name == 'pre':
                        code_content = code.get_text()
                        language = ''
                        if code.find('code'):
                            code_classes = code.find('code').get('class', [])
                            if code_classes:
                                language = code_classes[0]
                        
                        content_data['code_blocks'].append({
                            'language': language,
                            'content': code_content,
                            'type': 'block'
                        })
                    elif code.name == 'code' and not code.parent.name == 'pre':
                        content_data['code_blocks'].append({
                            'language': '',
                            'content': code.get_text(),
                            'type': 'inline'
                        })
                
                # Extract images with enhanced metadata
                images = main_content.find_all('img')
                for img in images:
                    content_data['images'].append({
                        'src': img.get('src', ''),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'caption': ''
                    })
                
                # Extract tables with enhanced structure
                tables = main_content.find_all('table')
                for table in tables:
                    table_data = []
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        table_data.append([cell.get_text(strip=True) for cell in cells])
                    content_data['tables'].append(table_data)
                
                # Extract conclusion (last few paragraphs)
                all_paragraphs = main_content.find_all('p')
                if len(all_paragraphs) > 3:
                    conclusion_elems = all_paragraphs[-3:]  # Last 3 paragraphs
                    content_data['conclusion'] = '\n\n'.join([p.get_text(strip=True) for p in conclusion_elems if p.get_text(strip=True)])
                
                # Extract references/links
                links = main_content.find_all('a', href=True)
                for link in links:
                    if link.get('href') and not link.get('href').startswith('#'):
                        content_data['references'].append({
                            'text': link.get_text(strip=True),
                            'url': link.get('href')
                        })
            
            # Combine all data
            blog_data['content'] = content_data
            
            return blog_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
    
    def format_for_llm_knowledge(self, blog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format blog data for LLM knowledge building"""
        
        if not blog_data:
            return None
        
        # Create a structured knowledge format
        knowledge_base = {
            "source": "Red Hat Emerging Technologies Blog",
            "url": blog_data['url'],
            "title": blog_data['title'],
            "author": blog_data['author'],
            "date": blog_data['date'],
            "category": blog_data['category'],
            "series_info": blog_data['series_info'],
            "extracted_at": blog_data['extracted_at'],
            "content": {
                "summary": "",
                "key_concepts": [],
                "technical_details": [],
                "code_examples": [],
                "best_practices": [],
                "references": []
            }
        }
        
        # Extract summary from introduction
        if blog_data['content']['introduction']:
            knowledge_base['content']['summary'] = blog_data['content']['introduction']
        
        # Extract key concepts from section headings
        for section in blog_data['content']['sections']:
            if section['heading']:
                knowledge_base['content']['key_concepts'].append(section['heading'])
        
        # Extract technical details from sections
        for section in blog_data['content']['sections']:
            if section['content']:
                knowledge_base['content']['technical_details'].append({
                    'topic': section['heading'],
                    'details': section['content']
                })
        
        # Extract code examples
        for code_block in blog_data['content']['code_blocks']:
            if code_block['type'] == 'block':
                knowledge_base['content']['code_examples'].append({
                    'language': code_block['language'],
                    'code': code_block['content'],
                    'description': ''
                })
        
        # Extract best practices (look for specific patterns)
        for section in blog_data['content']['sections']:
            if any(keyword in section['heading'].lower() for keyword in ['best practice', 'recommendation', 'tip', 'guideline']):
                knowledge_base['content']['best_practices'].append({
                    'topic': section['heading'],
                    'practices': section['content']
                })
        
        # Add references
        knowledge_base['content']['references'] = blog_data['content']['references']
        
        return knowledge_base
    
    def generate_llm_training_text(self, blog_data: Dict[str, Any]) -> str:
        """Generate training text for LLM from blog data"""
        
        if not blog_data:
            return ""
        
        training_text = f"""
# {blog_data['title']}

**Source:** Red Hat Emerging Technologies Blog  
**URL:** {blog_data['url']}  
**Author:** {blog_data['author']}  
**Date:** {blog_data['date']}  
**Category:** {blog_data['category']}  

## Introduction

{blog_data['content']['introduction']}

## Main Content

"""
        
        # Add sections
        for section in blog_data['content']['sections']:
            training_text += f"### {section['heading']}\n\n"
            training_text += f"{section['content']}\n\n"
        
        # Add code examples
        if blog_data['content']['code_blocks']:
            training_text += "## Code Examples\n\n"
            for i, code_block in enumerate(blog_data['content']['code_blocks'], 1):
                if code_block['type'] == 'block':
                    training_text += f"### Code Example {i}\n"
                    if code_block['language']:
                        training_text += f"**Language:** {code_block['language']}\n\n"
                    training_text += f"```{code_block['language']}\n{code_block['content']}\n```\n\n"
        
        # Add tables
        if blog_data['content']['tables']:
            training_text += "## Tables\n\n"
            for i, table in enumerate(blog_data['content']['tables'], 1):
                training_text += f"### Table {i}\n\n"
                for row in table:
                    training_text += "| " + " | ".join(row) + " |\n"
                training_text += "\n"
        
        # Add conclusion
        if blog_data['content']['conclusion']:
            training_text += f"## Conclusion\n\n{blog_data['content']['conclusion']}\n\n"
        
        # Add references
        if blog_data['content']['references']:
            training_text += "## References\n\n"
            for ref in blog_data['content']['references']:
                training_text += f"- [{ref['text']}]({ref['url']})\n"
        
        return training_text
    
    def process_all_blogs(self) -> List[Dict[str, Any]]:
        """Process all blogs with enhanced extraction and LLM formatting"""
        logger.info("Processing all blogs with enhanced extraction...")
        
        # Crawl blog links
        blog_links = self.crawl_blog_links()
        
        # Process each blog
        processed_blogs = []
        for i, url in enumerate(blog_links, 1):
            logger.info(f"Processing blog {i}/{len(blog_links)}: {url}")
            
            # Extract content
            blog_data = self.extract_blog_content_for_llm(url)
            if blog_data:
                # Format for LLM knowledge
                knowledge_base = self.format_for_llm_knowledge(blog_data)
                if knowledge_base:
                    # Generate training text
                    training_text = self.generate_llm_training_text(blog_data)
                    
                    # Add to processed blogs
                    processed_blog = {
                        'raw_data': blog_data,
                        'knowledge_base': knowledge_base,
                        'training_text': training_text
                    }
                    processed_blogs.append(processed_blog)
                    
                    logger.info(f"Successfully processed: {blog_data['title']}")
                else:
                    logger.warning(f"Failed to format knowledge base for: {url}")
            else:
                logger.warning(f"Failed to extract content from: {url}")
            
            # Add delay to be respectful
            if i < len(blog_links):
                time.sleep(self.delay)
        
        logger.info(f"Successfully processed {len(processed_blogs)} out of {len(blog_links)} blogs")
        return processed_blogs
    
    def save_enhanced_data(self, processed_blogs: List[Dict[str, Any]]) -> None:
        """Save enhanced blog data with multiple formats"""
        logger.info("Saving enhanced blog data...")
        
        # Backup existing files
        if Path("data/blog_metadata.json").exists():
            shutil.copy("data/blog_metadata.json", "data/blog_metadata_backup.json")
            logger.info("Backed up existing blog metadata")
        
        # Save raw data
        raw_blogs = [blog['raw_data'] for blog in processed_blogs]
        blog_metadata = {
            'metadata': {
                'generated_on': datetime.now().isoformat(),
                'source': 'https://next.redhat.com/blog/',
                'total_blogs': len(processed_blogs),
                'version': '3.0',
                'description': 'Enhanced blog data with LLM knowledge formatting'
            },
            'blogs': raw_blogs
        }
        
        with open("data/blog_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(blog_metadata, f, indent=2, ensure_ascii=False)
        
        # Save knowledge base data
        knowledge_bases = [blog['knowledge_base'] for blog in processed_blogs]
        knowledge_metadata = {
            'metadata': {
                'generated_on': datetime.now().isoformat(),
                'total_blogs': len(processed_blogs),
                'version': '3.0',
                'description': 'LLM knowledge base formatted data'
            },
            'knowledge_bases': knowledge_bases
        }
        
        with open("data/knowledge_base.json", 'w', encoding='utf-8') as f:
            json.dump(knowledge_metadata, f, indent=2, ensure_ascii=False)
        
        # Save training text
        training_texts = []
        for blog in processed_blogs:
            training_texts.append({
                'title': blog['raw_data']['title'],
                'url': blog['raw_data']['url'],
                'training_text': blog['training_text']
            })
        
        training_metadata = {
            'metadata': {
                'generated_on': datetime.now().isoformat(),
                'total_blogs': len(processed_blogs),
                'version': '3.0',
                'description': 'LLM training text data'
            },
            'training_texts': training_texts
        }
        
        with open("data/training_texts.json", 'w', encoding='utf-8') as f:
            json.dump(training_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved enhanced data for {len(processed_blogs)} blogs")
        logger.info("Files created:")
        logger.info("- data/blog_metadata.json (raw data)")
        logger.info("- data/knowledge_base.json (LLM knowledge base)")
        logger.info("- data/training_texts.json (training text)")

def main():
    """Main function"""
    logger.info("Starting enhanced blog processing...")
    
    processor = EnhancedBlogProcessor()
    
    # Process all blogs
    processed_blogs = processor.process_all_blogs()
    
    # Save enhanced data
    processor.save_enhanced_data(processed_blogs)
    
    logger.info("Enhanced blog processing completed successfully!")

if __name__ == "__main__":
    main() 