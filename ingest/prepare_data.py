#!/usr/bin/env python3
"""
Comprehensive Data Preparation Script
Prepares all data for Ask ET chatbot including blogs, projects, and enhanced content
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

class DataPreparator:
    """Comprehensive data preparation for Ask ET chatbot"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
    
    def extract_enhanced_blog_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract enhanced blog content with structured sections"""
        try:
            logger.info(f"Extracting enhanced content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic metadata
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
            
            # Extract author, date, category using regex
            full_text = soup.get_text()
            author_match = re.search(r'by\s+([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|\n]+)', full_text)
            if author_match:
                blog_data['author'] = author_match.group(1).strip()
                blog_data['date'] = author_match.group(2).strip()
                blog_data['category'] = author_match.group(3).strip()
            
            # Extract series information
            series_pattern = r'This is article #\d+ in our series on [^.]+\.'
            series_match = re.search(series_pattern, full_text)
            if series_match:
                blog_data['series_info'] = series_match.group(0)
            
            # Find main content area
            main_content = None
            selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.blog-post-content'
            ]
            
            for selector in selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                title_elem = soup.find('h1')
                if title_elem:
                    main_content = title_elem.parent
            
            if main_content:
                # Extract structured content
                content_data = {
                    'introduction': '',
                    'sections': [],
                    'code_blocks': [],
                    'images': [],
                    'tables': [],
                    'conclusion': '',
                    'references': []
                }
                
                # Get full text and split into sections
                full_text = main_content.get_text(separator='\n', strip=True)
                
                # Extract headings and create sections
                headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                if headings:
                    # Split content by headings
                    current_section = {'heading': 'Introduction', 'content': ''}
                    sections = [current_section]
                    
                    for heading in headings:
                        heading_text = heading.get_text(strip=True)
                        
                        # Start new section
                        current_section = {
                            'heading': heading_text,
                            'content': ''
                        }
                        sections.append(current_section)
                    
                    # Extract code blocks
                    for code in main_content.find_all(['pre', 'code']):
                        if code.name == 'pre':
                            code_elem = code.find('code')
                            if code_elem:
                                language = code_elem.get('class', [''])[0] if code_elem.get('class') else ''
                                content_data['code_blocks'].append({
                                    'language': language,
                                    'content': code_elem.get_text(),
                                    'type': 'block'
                                })
                        elif code.name == 'code' and not code.find_parent('pre'):
                            content_data['code_blocks'].append({
                                'language': '',
                                'content': code.get_text(),
                                'type': 'inline'
                            })
                    
                    # Extract images
                    for img in main_content.find_all('img', src=True):
                        content_data['images'].append({
                            'alt': img.get('alt', ''),
                            'src': img['src']
                        })
                    
                    # Extract tables
                    for table in main_content.find_all('table'):
                        table_data = []
                        for row in table.find_all('tr'):
                            row_data = []
                            for cell in row.find_all(['td', 'th']):
                                row_data.append(cell.get_text(strip=True))
                            if row_data:
                                table_data.append(row_data)
                        if table_data:
                            content_data['tables'].append(table_data)
                    
                    content_data['sections'] = sections
                
                blog_data['content'] = content_data
                return blog_data
            
            else:
                logger.warning(f"No content found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting enhanced content from {url}: {e}")
            return None
    
    def get_redhat_projects(self) -> List[Dict[str, Any]]:
        """Get comprehensive list of Red Hat Emerging Technologies projects"""
        logger.info("Getting Red Hat projects...")
        
        projects = [
            # AI Projects
            {
                "name": "ROSA – Data Analysis Models",
                "category": "AI",
                "description": "Machine learning models for churn and revenue prediction",
                "github_links": ["https://github.com/hemajv"],
                "project_url": "https://next.redhat.com/project/rosa-data-analysis-models/"
            },
            {
                "name": "Aspen social graph analysis",
                "category": "AI",
                "description": "Understand changes in strategic open source ecosystems and identify new strategic ecosystems",
                "github_links": ["https://github.com/oindrillac"],
                "project_url": "https://next.redhat.com/project/aspen-social-graph-analysis/"
            },
            {
                "name": "Confidential Compute for ML Workloads in OpenShift",
                "category": "AI",
                "description": "The goal of this project is to understand the technical requirements and any gaps around being able to run ML workloads in confidential compute environments on OpenShift",
                "github_links": ["https://github.com/erikerlandson"],
                "project_url": "https://next.redhat.com/project/confidential-compute-for-ml-workloads-in-openshift/"
            },
            {
                "name": "Open ML-Ops Stacks – VectorDB",
                "category": "AI",
                "description": "Study some open vector-db approaches - these will include things like postgressql+vector plugin but also purpose built vector databases",
                "github_links": ["https://github.com/erikerlandson"],
                "project_url": "https://next.redhat.com/project/open-ml-ops-stacks-vectordb/"
            },
            {
                "name": "generative AI for CVE backports",
                "category": "AI",
                "description": "Use generative AI code generation to automatically port CVE patches across multiple versions of Red Hat Products",
                "github_links": ["https://github.com/redhat-et/cve-backport-ai", "https://github.com/oindrillac"],
                "project_url": "https://next.redhat.com/project/generative-ai-for-cve-backports/"
            },
            {
                "name": "Open MLOps Stacks – Data Labeling",
                "category": "AI",
                "description": "The team has started to work on the MLOps stack for Data Labeling. Both traditional machine learning training, and generative AI training",
                "github_links": ["https://github.com/aakankshaduggal"],
                "project_url": "https://next.redhat.com/project/open-mlops-stacks-data-labeling/"
            },
            {
                "name": "ShadowBot.AI",
                "category": "AI",
                "description": "Instant access to the company's internal data & documentation via a LLM-assisted chatbot that is integrated into Slack",
                "github_links": [],
                "project_url": "https://next.redhat.com/project/shadowbot-ai/"
            },
            {
                "name": "HCS – Red Hat Subscription Delivery",
                "category": "AI",
                "description": "Increase productivity of Global Business Delivery (GBD) and increase revenue from Red Hat product subscriptions",
                "github_links": ["https://github.com/aakankshaduggal"],
                "project_url": "https://next.redhat.com/project/hcs-red-hat-subscription-delivery/"
            },
            {
                "name": "Codeflare Stack Integration to ODH/RHODS",
                "category": "AI",
                "description": "Enable machine learning for AI Developers with faster time to value. This project carries into the completed Ray Operator work",
                "github_links": [],
                "project_url": "https://next.redhat.com/project/codeflare-stack-integration-to-odh-rhods/"
            },
            {
                "name": "ROSA – Foundation Models Generative AI for Doc Search",
                "category": "AI",
                "description": "A useful application of foundation models, or large language models (LLMs), is documentation search. LLMs can understand the context and intent of user queries",
                "github_links": ["https://github.com/redhat-et/foundation-models-for-documentation", "https://github.com/Shreyanand"],
                "project_url": "https://next.redhat.com/project/rosa-foundation-models-generative-ai-for-doc-search/"
            },
            
            # Developer Productivity Projects
            {
                "name": "bpfman",
                "category": "Developer Productivity",
                "description": "bpfman is a system daemon aimed at simplifying the deployment and management of eBPF programs. It's goal is to provide a cloud-native way of deploying and managing eBPF programs",
                "github_links": ["https://github.com/dave-tucker", "https://github.com/bpfman/bpfman"],
                "project_url": "https://next.redhat.com/project/bpfman/"
            },
            {
                "name": "Wasm and WASI on Openshift",
                "category": "Developer Productivity",
                "description": "Compiled Wasm code is packaged as a scratch OCI container image and deployed on OpenShift (MicroShift) or Podman",
                "github_links": ["https://github.com/font"],
                "project_url": "https://next.redhat.com/project/wasm-and-wasi-on-openshift/"
            },
            {
                "name": "MicroShift",
                "category": "Developer Productivity",
                "description": "MicroShift is a Kubernetes distribution designed for edge computing and resource-constrained environments",
                "github_links": ["https://github.com/redhat-et/microshift"],
                "project_url": "https://next.redhat.com/project/microshift/"
            },
            {
                "name": "Kubernetes Operators",
                "category": "Developer Productivity",
                "description": "Collection of Kubernetes operators for various Red Hat technologies and tools",
                "github_links": ["https://github.com/redhat-et/operators"],
                "project_url": "https://next.redhat.com/project/kubernetes-operators/"
            },
            
            # Security Projects
            {
                "name": "Enarx",
                "category": "Security",
                "description": "Enarx provides hardware independence for confidential computing, enabling applications to run in secure enclaves",
                "github_links": ["https://github.com/enarx/enarx"],
                "project_url": "https://next.redhat.com/project/enarx/"
            },
            {
                "name": "Keylime",
                "category": "Security",
                "description": "Keylime provides a scalable, distributed trust system for cloud and edge computing",
                "github_links": ["https://github.com/keylime/keylime"],
                "project_url": "https://next.redhat.com/project/keylime/"
            },
            {
                "name": "Sigstore",
                "category": "Security",
                "description": "Sigstore provides a way to sign, verify and protect software using digital signatures",
                "github_links": ["https://github.com/sigstore/sigstore"],
                "project_url": "https://next.redhat.com/project/sigstore/"
            },
            
            # Cloud & Edge Projects
            {
                "name": "Open Data Hub",
                "category": "Cloud & Edge",
                "description": "Open Data Hub is a reference architecture for building AI/ML platforms on OpenShift",
                "github_links": ["https://github.com/opendatahub-io/opendatahub-operator"],
                "project_url": "https://next.redhat.com/project/open-data-hub/"
            },
            {
                "name": "Kepler",
                "category": "Cloud & Edge",
                "description": "Kepler (Kubernetes-based Efficient Power Level Exporter) enables monitoring of power consumption in Kubernetes clusters",
                "github_links": ["https://github.com/sustainable-computing-io/kepler"],
                "project_url": "https://next.redhat.com/project/kepler/"
            },
            {
                "name": "VolSync",
                "category": "Cloud & Edge",
                "description": "VolSync provides data mobility for Kubernetes workloads across clusters and clouds",
                "github_links": ["https://github.com/backube/volsync"],
                "project_url": "https://next.redhat.com/project/volsync/"
            },
            {
                "name": "Rook",
                "category": "Cloud & Edge",
                "description": "Rook is a cloud-native storage orchestrator for Kubernetes",
                "github_links": ["https://github.com/rook/rook"],
                "project_url": "https://next.redhat.com/project/rook/"
            },
            {
                "name": "Ceph",
                "category": "Cloud & Edge",
                "description": "Ceph is a distributed storage system designed to provide excellent performance, reliability, and scalability",
                "github_links": ["https://github.com/ceph/ceph"],
                "project_url": "https://next.redhat.com/project/ceph/"
            }
        ]
        
        logger.info(f"Loaded {len(projects)} Red Hat projects")
        return projects
    
    def prepare_comprehensive_data(self) -> Dict[str, Any]:
        """Prepare comprehensive data including blogs and projects"""
        logger.info("Starting comprehensive data preparation...")
        
        # Crawl blog links
        blog_links = self.crawl_blog_links()
        
        # Extract enhanced blog content
        blog_data = []
        for i, url in enumerate(blog_links, 1):
            logger.info(f"Processing blog {i}/{len(blog_links)}: {url}")
            
            content = self.extract_enhanced_blog_content(url)
            if content:
                blog_data.append(content)
                logger.info(f"Successfully extracted: {content['title']}")
            else:
                logger.warning(f"Failed to extract content from: {url}")
            
            # Add delay to be respectful
            if i < len(blog_links):
                time.sleep(self.delay)
        
        # Get projects
        projects = self.get_redhat_projects()
        
        # Create comprehensive metadata
        comprehensive_data = {
            'metadata': {
                'generated_on': datetime.now().isoformat(),
                'source': 'https://next.redhat.com/blog/',
                'total_blogs': len(blog_data),
                'total_projects': len(projects),
                'scraped_urls': blog_links,
                'version': '2.0',
                'description': 'Comprehensive data for Ask ET chatbot including enhanced blog content and project information'
            },
            'blogs': blog_data,
            'projects': projects
        }
        
        return comprehensive_data
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save prepared data to files"""
        logger.info("Saving prepared data...")
        
        # Backup existing files
        if Path("data/blog_metadata.json").exists():
            shutil.copy("data/blog_metadata.json", "data/blog_metadata_backup.json")
            logger.info("Backed up existing blog metadata")
        
        if Path("data/project_metadata.json").exists():
            shutil.copy("data/project_metadata.json", "data/project_metadata_backup.json")
            logger.info("Backed up existing project metadata")
        
        # Save blog data
        blog_metadata = {
            'metadata': data['metadata'],
            'blogs': data['blogs']
        }
        with open("data/blog_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(blog_metadata, f, indent=2, ensure_ascii=False)
        
        # Save project data
        project_metadata = {
            'metadata': {
                'generated_on': data['metadata']['generated_on'],
                'total_projects': data['metadata']['total_projects'],
                'version': data['metadata']['version']
            },
            'projects': data['projects']
        }
        with open("data/project_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(project_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data['blogs'])} blogs and {len(data['projects'])} projects")

def main():
    """Main function"""
    logger.info("Starting comprehensive data preparation...")
    
    preparator = DataPreparator()
    
    # Prepare comprehensive data
    data = preparator.prepare_comprehensive_data()
    
    # Save data
    preparator.save_data(data)
    
    logger.info("Data preparation completed successfully!")
    logger.info(f"Prepared {len(data['blogs'])} blogs and {len(data['projects'])} projects")

if __name__ == "__main__":
    main() 