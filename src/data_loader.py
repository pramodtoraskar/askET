#!/usr/bin/env python3
"""
Data loaders for Ask ET chatbot
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from config import BLOG_METADATA_PATH, PROJECT_METADATA_PATH
from src.logger import get_logger

logger = get_logger(__name__)

@dataclass
class BlogEntry:
    """Blog entry data structure"""
    title: str
    author: str
    date: str
    url: str
    category: str
    content: str
    metadata: Dict[str, Any]

@dataclass
class ProjectEntry:
    """Project entry data structure"""
    name: str
    category: str
    description: str
    github_links: List[str]
    project_url: str
    metadata: Dict[str, Any]

class DataLoader:
    """Data loader for blog and project metadata"""
    
    def __init__(self):
        self.blog_metadata_path = Path(BLOG_METADATA_PATH)
        self.project_metadata_path = Path(PROJECT_METADATA_PATH)
        
    def load_blog_metadata(self) -> List[BlogEntry]:
        """Load blog metadata from JSON file"""
        try:
            with open(self.blog_metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            blogs = []
            for blog in data.get('blogs', []):
                try:
                    blog_entry = BlogEntry(
                        title=blog.get('metadata', {}).get('title', ''),
                        author=blog.get('metadata', {}).get('author', ''),
                        date=blog.get('metadata', {}).get('date', ''),
                        url=blog.get('metadata', {}).get('url', ''),
                        category=blog.get('metadata', {}).get('category', ''),
                        content=blog.get('content', {}).get('introduction', ''),
                        metadata=blog
                    )
                    blogs.append(blog_entry)
                except Exception as e:
                    logger.warning(f"Error processing blog entry: {e}")
                    continue
            
            logger.info(f"Loaded {len(blogs)} blog entries")
            return blogs
            
        except Exception as e:
            logger.error(f"Error loading blog metadata: {e}")
            return []
    
    def load_project_metadata(self) -> List[ProjectEntry]:
        """Load project metadata from JSON file"""
        try:
            with open(self.project_metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            projects = []
            for project in data.get('projects', []):
                try:
                    project_entry = ProjectEntry(
                        name=project.get('name', ''),
                        category=project.get('category', ''),
                        description=project.get('description', ''),
                        github_links=project.get('github_links', []),
                        project_url=project.get('project_url', ''),
                        metadata=project
                    )
                    projects.append(project_entry)
                except Exception as e:
                    logger.warning(f"Error processing project entry: {e}")
                    continue
            
            logger.info(f"Loaded {len(projects)} project entries")
            return projects
            
        except Exception as e:
            logger.error(f"Error loading project metadata: {e}")
            return []
    
    def merge_data(self) -> List[Dict[str, Any]]:
        """Merge blog and project data into a unified format"""
        blogs = self.load_blog_metadata()
        projects = self.load_project_metadata()
        
        merged_data = []
        
        # Add blogs
        for blog in blogs:
            merged_data.append({
                'type': 'blog',
                'title': blog.title,
                'author': blog.author,
                'date': blog.date,
                'url': blog.url,
                'category': blog.category,
                'content': blog.content,
                'metadata': blog.metadata
            })
        
        # Add projects
        for project in projects:
            merged_data.append({
                'type': 'project',
                'title': project.name,
                'category': project.category,
                'description': project.description,
                'github_links': project.github_links,
                'project_url': project.project_url,
                'metadata': project.metadata
            })
        
        logger.info(f"Merged {len(merged_data)} total entries ({len(blogs)} blogs, {len(projects)} projects)")
        return merged_data
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate data integrity and return statistics"""
        blogs = self.load_blog_metadata()
        projects = self.load_project_metadata()
        
        stats = {
            'total_blogs': len(blogs),
            'total_projects': len(projects),
            'blogs_with_content': len([b for b in blogs if b.content]),
            'projects_with_github': len([p for p in projects if p.github_links]),
            'categories': {
                'blogs': list(set(b.category for b in blogs if b.category)),
                'projects': list(set(p.category for p in projects if p.category))
            }
        }
        
        logger.info(f"Data validation stats: {stats}")
        return stats 