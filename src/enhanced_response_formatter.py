#!/usr/bin/env python3
"""
Enhanced Response Formatter for Ask ET
Formats responses to include blog summaries, blog links, and associated GitHub project work
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class EnhancedResponseFormatter:
    """Enhanced response formatter for blog summaries, links, and GitHub projects"""
    
    def __init__(self):
        self.project_metadata = self._load_project_metadata()
        self.blog_metadata = self._load_blog_metadata()
        
    def _load_project_metadata(self) -> Dict[str, Any]:
        """Load project metadata from JSON file"""
        try:
            project_file = Path("data/project_metadata.json")
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Project metadata file not found")
                return {"projects": []}
        except Exception as e:
            logger.error(f"Error loading project metadata: {e}")
            return {"projects": []}
    
    def _load_blog_metadata(self) -> Dict[str, Any]:
        """Load blog metadata from JSON file"""
        try:
            blog_file = Path("data/blog_metadata.json")
            if blog_file.exists():
                with open(blog_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Blog metadata file not found")
                return {"blogs": []}
        except Exception as e:
            logger.error(f"Error loading blog metadata: {e}")
            return {"blogs": []}
    
    def extract_blog_info_from_documents(self, documents: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
        """Extract blog information from retrieved documents"""
        blog_info = []
        
        for doc in documents:
            source = doc.get('source', '')
            title = doc.get('title', '')
            content = doc.get('content', '')
            
            # Extract blog URL if present
            blog_url = self._extract_blog_url(source, content)
            
            # Find matching blog metadata
            blog_metadata = self._find_blog_metadata(blog_url, title)
            
                    # If we have empty content but good metadata, use metadata
        if not title and not content and blog_metadata:
            title = blog_metadata.get('title', '')
            # Try to get content from metadata
            if 'content' in blog_metadata and isinstance(blog_metadata['content'], dict):
                content = blog_metadata['content'].get('summary', '')
                if not content:
                    # Try to get from introduction
                    content = blog_metadata['content'].get('introduction', '')
            if not blog_url:
                blog_url = blog_metadata.get('url', '')
            
            # Let the system learn naturally from the knowledge base
            # No artificial filtering - let relevance scoring handle it
            
            # If still no content, try to find a relevant blog from metadata
            if not title and not content:
                # Find a relevant blog based on the query context
                relevant_blogs = self._find_relevant_blogs_from_metadata(doc.get('score', 0), query)
                if relevant_blogs:
                    sample_blog = relevant_blogs[0]
                    title = sample_blog.get('title', '')
                    blog_url = sample_blog.get('url', '')
                    # Try to get content from metadata
                    if 'content' in sample_blog and isinstance(sample_blog['content'], dict):
                        content = sample_blog['content'].get('summary', '')
                        if not content:
                            content = sample_blog['content'].get('introduction', '')
                    blog_metadata = sample_blog
                    
                    # For very specific queries, try exact title matching
                    if not title and query:
                        exact_match = self._find_exact_blog_match(query)
                        if exact_match:
                            title = exact_match.get('title', '')
                            blog_url = exact_match.get('url', '')
                            if 'content' in exact_match and isinstance(exact_match['content'], dict):
                                content = exact_match['content'].get('summary', '')
                                if not content:
                                    content = exact_match['content'].get('introduction', '')
                            blog_metadata = exact_match
            
            blog_info.append({
                'title': title,
                'url': blog_url,
                'summary': self._generate_blog_summary(content, title),
                'author': blog_metadata.get('author', 'Unknown'),
                'date': blog_metadata.get('date', ''),
                'category': blog_metadata.get('category', ''),
                'relevance_score': doc.get('score', 0),
                'content_preview': content[:300] + "..." if len(content) > 300 else content
            })
        
        return blog_info
    
    def _extract_blog_url(self, source: str, content: str) -> str:
        """Extract blog URL from source or content"""
        # Check if source is already a URL
        if source.startswith('http'):
            return source
        
        # Look for URLs in content
        url_pattern = r'https?://[^\s<>"]+'
        urls = re.findall(url_pattern, content)
        
        # Filter for Red Hat blog URLs
        redhat_urls = [url for url in urls if 'redhat.com' in url or 'next.redhat.com' in url]
        
        return redhat_urls[0] if redhat_urls else source
    
    def _find_blog_metadata(self, url: str, title: str) -> Dict[str, Any]:
        """Find matching blog metadata"""
        blogs = self.blog_metadata.get('blogs', [])
        
        for blog in blogs:
            blog_url = blog.get('url', '')
            blog_title = blog.get('title', '')
            
            # Match by URL or title
            if url and blog_url and url in blog_url:
                return blog
            elif title and blog_title and title.lower() in blog_title.lower():
                return blog
        
        return {}
    
    def _generate_blog_summary(self, content: str, title: str = "") -> str:
        """Generate a concise summary of blog content"""
        if not content or content == "No content available":
            # Generate a meaningful summary based on the title
            if title:
                return self._generate_summary_from_title(title)
            return "Blog post about Red Hat Emerging Technologies"
        
        # Clean content
        clean_content = re.sub(r'\s+', ' ', content.strip())
        
        # Take first 200 characters and add ellipsis if longer
        if len(clean_content) > 200:
            # Try to break at sentence boundary
            sentences = re.split(r'[.!?]', clean_content[:250])
            if len(sentences) > 1:
                summary = '. '.join(sentences[:-1]) + '.'
            else:
                summary = clean_content[:200] + "..."
        else:
            summary = clean_content
        
        return summary
    
    def _generate_summary_from_title(self, title: str) -> str:
        """Generate a meaningful summary based on the blog title"""
        title_lower = title.lower()
        
        # Define topic mappings
        topic_mappings = {
            'ai': 'This blog post explores artificial intelligence and machine learning technologies in the context of Red Hat\'s emerging technology initiatives.',
            'machine learning': 'This article discusses machine learning applications, tools, and best practices for enterprise environments.',
            'openshift': 'This blog covers OpenShift platform features, deployment strategies, and cloud-native application development.',
            'kubernetes': 'This post examines Kubernetes orchestration, container management, and microservices architecture.',
            'edge': 'This article explores edge computing technologies, use cases, and implementation strategies.',
            'cloud': 'This blog discusses cloud computing trends, hybrid cloud solutions, and cloud-native development.',
            'security': 'This post covers cybersecurity, confidential computing, and security best practices.',
            'blockchain': 'This article examines blockchain technology, distributed systems, and decentralized applications.',
            'quantum': 'This blog explores quantum computing concepts, applications, and future implications.',
            'iot': 'This post discusses Internet of Things (IoT) technologies, edge computing, and connected devices.'
        }
        
        # Find matching topics
        for keyword, summary in topic_mappings.items():
            if keyword in title_lower:
                return summary
        
        # Default summary
        return f"This blog post discusses {title} and its relevance to Red Hat's emerging technology landscape."
    
    def find_related_projects(self, query: str, blog_titles: List[str]) -> List[Dict[str, Any]]:
        """Find projects related to the query and blog content"""
        related_projects = []
        projects = self.project_metadata.get('projects', [])
        
        # Create search terms from query and blog titles
        search_terms = [query.lower()] + [title.lower() for title in blog_titles if title]
        
        # Use meaningful search terms from the query and blog content
        meaningful_terms = [term for term in search_terms if term and len(term) > 2]
        if meaningful_terms:
            search_terms = meaningful_terms
        else:
            # If no meaningful terms, let the system find relevant projects naturally
            # Don't force specific terms - let the knowledge base guide the search
            search_terms = [query.lower()] if query else []
            
        # Let the system learn naturally from the knowledge base
        # No artificial filtering - let relevance scoring handle it
        
        for project in projects:
            project_name = project.get('name', '').lower()
            project_description = project.get('description', '').lower()
            project_category = project.get('category', '').lower()
            
            # Check if any search term matches project
            for term in search_terms:
                # Extract keywords from the search term
                keywords = term.split()
                for keyword in keywords:
                    if (keyword in project_name or 
                        keyword in project_description or 
                        keyword in project_category):
                        related_projects.append(project)
                        break
                if project in related_projects:
                    break
        
        # Remove duplicates and limit results
        unique_projects = []
        seen_names = set()
        for project in related_projects:
            if project['name'] not in seen_names:
                unique_projects.append(project)
                seen_names.add(project['name'])
        
        return unique_projects[:5]  # Limit to 5 projects
    
    def _find_relevant_blogs_from_metadata(self, score: float, query: str = "") -> List[Dict[str, Any]]:
        """Find relevant blogs from metadata when vector store content is empty"""
        blogs = self.blog_metadata.get('blogs', [])
        
        # If we have a specific query, try to find more relevant blogs
        if query:
            query_lower = query.lower()
            query_keywords = query_lower.split()
            
            # Enhanced author query handling
            if any(word in query_lower for word in ['by', 'blogs by', 'articles']):
                author_blogs = self._find_blogs_by_author(query_lower)
                if author_blogs:
                    return author_blogs
            
            # Enhanced technology query handling
            if any(word in query_lower for word in ['gpu', 'triton', 'sustainability', 'automation', 'cybersecurity', 'energy', 'environmental']):
                tech_blogs = self._find_blogs_by_technology(query_lower)
                if tech_blogs:
                    return tech_blogs
            
            # First, try to find blogs that match the query keywords
            query_matched_blogs = []
            for blog in blogs:
                title = blog.get('title', '').lower()
                category = blog.get('category', '').lower()
                author = blog.get('author', '').lower()
                
                # Check if any keyword matches the title, category, or author
                for keyword in query_keywords:
                    if len(keyword) > 2 and (keyword in title or keyword in category or keyword in author):
                        query_matched_blogs.append(blog)
                        break
                
                # Also check if the query contains the blog title keywords
                title_words = title.split()
                for title_word in title_words:
                    if len(title_word) > 3 and title_word in query_lower:
                        if blog not in query_matched_blogs:
                            query_matched_blogs.append(blog)
                            break
            
            if query_matched_blogs:
                # Sort by relevance - prioritize blogs with more keyword matches
                def relevance_score(blog):
                    title = blog.get('title', '').lower()
                    category = blog.get('category', '').lower()
                    author = blog.get('author', '').lower()
                    score = 0
                    
                    # Count how many query keywords match
                    for keyword in query_keywords:
                        if len(keyword) > 2:
                            if keyword in title:
                                score += 3  # Highest weight for title matches
                            if keyword in category:
                                score += 2  # Medium weight for category matches
                            if keyword in author:
                                score += 2  # Medium weight for author matches
                    
                    return score
                
                # Sort by relevance score (highest first)
                query_matched_blogs.sort(key=relevance_score, reverse=True)
                return query_matched_blogs[:3]
        
        # Enhanced fallback with broader keyword matching
        relevant_keywords = [
            'ai', 'machine learning', 'openshift', 'kubernetes', 'cloud', 'edge',
            'triton', 'gpu', 'sustainability', 'automation', 'security', 'trust',
            'blockchain', 'container', 'microshift', 'enarx', 'keylime', 'kepler'
        ]
        relevant_blogs = []
        
        for blog in blogs:
            title = blog.get('title', '').lower()
            category = blog.get('category', '').lower()
            
            # Check if blog contains relevant keywords
            for keyword in relevant_keywords:
                if keyword in title or keyword in category:
                    relevant_blogs.append(blog)
                    break
        
        # Return top 3 most relevant blogs
        return relevant_blogs[:3]
    
    def _find_blogs_by_author(self, query: str) -> List[Dict[str, Any]]:
        """Find blogs by specific author"""
        blogs = self.blog_metadata.get('blogs', [])
        query_lower = query.lower()
        
        # Extract author name from query patterns
        author_patterns = [
            'blogs by ', 'articles by ', 'by ', 'what has ', ' written about'
        ]
        
        author_name = query_lower
        for pattern in author_patterns:
            if pattern in query_lower:
                author_name = query_lower.replace(pattern, '').strip()
                break
        
        # Find blogs by this author
        author_blogs = []
        for blog in blogs:
            blog_author = blog.get('author', '').lower()
            if author_name in blog_author or blog_author in author_name:
                author_blogs.append(blog)
        
        # Sort by date (newest first) and return top 3
        author_blogs.sort(key=lambda x: x.get('date', ''), reverse=True)
        return author_blogs[:3]
    
    def _find_blogs_by_technology(self, query: str) -> List[Dict[str, Any]]:
        """Find blogs by specific technology"""
        blogs = self.blog_metadata.get('blogs', [])
        query_lower = query.lower()
        
        # Technology mapping for better matching
        tech_mapping = {
            'gpu': ['gpu', 'triton', 'accelerator', 'kernel'],
            'triton': ['triton', 'gpu', 'kernel', 'accelerator'],
            'sustainability': ['sustainability', 'kepler', 'green', 'energy', 'efficient'],
            'automation': ['automation', 'ansible', 'workflow', 'orchestration'],
            'cybersecurity': ['security', 'cybersecurity', 'trust', 'enarx', 'keylime'],
            'energy': ['energy', 'efficiency', 'power', 'sustainability', 'kepler'],
            'environmental': ['environmental', 'sustainability', 'green', 'kepler']
        }
        
        # Find matching technology
        matching_tech = None
        for tech, keywords in tech_mapping.items():
            if tech in query_lower:
                matching_tech = keywords
                break
        
        if matching_tech:
            tech_blogs = []
            for blog in blogs:
                title = blog.get('title', '').lower()
                category = blog.get('category', '').lower()
                
                # Check if blog contains any of the technology keywords
                for keyword in matching_tech:
                    if keyword in title or keyword in category:
                        tech_blogs.append(blog)
                        break
            
            # Sort by relevance and return top 3
            tech_blogs.sort(key=lambda x: x.get('date', ''), reverse=True)
            return tech_blogs[:3]
        
        return []
    
    def _find_exact_blog_match(self, query: str) -> Dict[str, Any]:
        """Find exact blog match by title"""
        blogs = self.blog_metadata.get('blogs', [])
        
        query_lower = query.lower().strip()
        
        for blog in blogs:
            blog_title = blog.get('title', '').lower().strip()
            
            # Check for exact title match (highest priority)
            if blog_title == query_lower:
                return blog
            
            # Check if query is contained in title (high priority)
            if query_lower in blog_title:
                return blog
            
            # Check if title is contained in query (high priority)
            if blog_title in query_lower:
                return blog
        
        # If no exact match found, try to find the most relevant blog
        # by counting how many significant words match
        best_match = {}
        best_score = 0
        
        for blog in blogs:
            blog_title = blog.get('title', '').lower().strip()
            
            # Split into words and filter out common words
            query_words = set([word for word in query_lower.split() if len(word) > 3])
            title_words = set([word for word in blog_title.split() if len(word) > 3])
            
            # Calculate match score
            if query_words and title_words:
                # Count how many query words are in title
                matches = sum(1 for word in query_words if word in title_words)
                score = matches / len(query_words) if query_words else 0
                
                # Prefer longer matches and exact word matches
                if score > best_score:
                    best_score = score
                    best_match = blog
        
        # Only return if we have a good match (at least 50% of words match)
        return best_match if best_score >= 0.5 else {}
    
    def format_enhanced_response(self, query: str, documents: List[Dict[str, Any]], 
                                original_answer: str) -> Dict[str, Any]:
        """Format response with blog summaries, links, and GitHub projects"""
        
        # Extract blog information
        blog_info = self.extract_blog_info_from_documents(documents, query)
        
        # Enhanced fallback logic for failed scenarios
        if not blog_info and query:
            # Try exact matching first
            exact_match = self._find_exact_blog_match(query)
            if exact_match:
                blog_info = [{
                    'title': exact_match.get('title', ''),
                    'url': exact_match.get('url', ''),
                    'summary': self._generate_blog_summary('', exact_match.get('title', '')),
                    'author': exact_match.get('author', 'Unknown'),
                    'date': exact_match.get('date', ''),
                    'category': exact_match.get('category', ''),
                    'relevance_score': 1.0,  # High relevance for exact match
                    'content_preview': ''
                }]
            else:
                # Try enhanced metadata search for failed scenarios
                enhanced_blogs = self._find_relevant_blogs_from_metadata(0.8, query)
                if enhanced_blogs:
                    blog_info = []
                    for blog in enhanced_blogs:
                        blog_info.append({
                            'title': blog.get('title', ''),
                            'url': blog.get('url', ''),
                            'summary': self._generate_blog_summary('', blog.get('title', '')),
                            'author': blog.get('author', 'Unknown'),
                            'date': blog.get('date', ''),
                            'category': blog.get('category', ''),
                            'relevance_score': 0.8,  # Good relevance for enhanced match
                            'content_preview': ''
                        })
        
        # Remove duplicate blogs based on URL or title
        unique_blogs = []
        seen_urls = set()
        seen_titles = set()
        for blog in blog_info:
            # Check if we've already seen this URL or title
            blog_url = blog.get('url', '')
            blog_title = blog.get('title', '')
            
            # If we have a URL and haven't seen it, add it
            if blog_url and blog_url not in seen_urls:
                unique_blogs.append(blog)
                seen_urls.add(blog_url)
                if blog_title:
                    seen_titles.add(blog_title)
            # If no URL but we have a title and haven't seen it, add it
            elif blog_title and blog_title not in seen_titles:
                unique_blogs.append(blog)
                seen_titles.add(blog_title)
        
        # Limit to top 3 unique blogs
        blog_info = unique_blogs[:3]
        
        # Find related projects
        blog_titles = [blog['title'] for blog in blog_info if blog['title']]
        # Remove duplicates from blog titles
        unique_blog_titles = list(set(blog_titles))
        related_projects = self.find_related_projects(query, unique_blog_titles)
        
        # Format the response
        formatted_response = {
            'query': query,
            'answer': original_answer,
            'blogs': blog_info,
            'related_projects': related_projects,
            'formatted_output': self._create_formatted_output(
                original_answer, blog_info, related_projects
            )
        }
        
        return formatted_response
    
    def _create_formatted_output(self, answer: str, blogs: List[Dict[str, Any]], 
                                projects: List[Dict[str, Any]]) -> str:
        """Create a compact formatted output string"""
        
        output_parts = []
        
        # Add the main answer (compact)
        output_parts.append(answer)
        output_parts.append("")
        
        # Add blog summaries and links (compact format)
        if blogs:
            output_parts.append("**📝 Related Blogs:**")
            for i, blog in enumerate(blogs, 1):
                # Compact single line format
                author = blog.get('author', 'Unknown')
                date = blog.get('date', '')
                category = blog.get('category', '')
                
                # Create compact metadata line
                metadata_parts = []
                if author and author != 'Unknown':
                    metadata_parts.append(f"@{author}")
                if date:
                    metadata_parts.append(date)
                if category:
                    metadata_parts.append(category)
                
                metadata = " • ".join(metadata_parts) if metadata_parts else ""
                
                # Compact blog entry
                if metadata:
                    output_parts.append(f"{i}. **{blog['title']}** - {metadata}")
                else:
                    output_parts.append(f"{i}. **{blog['title']}**")
                
                # Short summary (truncated if too long)
                summary = blog.get('summary', '')
                if summary and len(summary) > 100:
                    summary = summary[:97] + "..."
                if summary:
                    output_parts.append(f"   {summary}")
                output_parts.append("")
        
        # Add related GitHub projects (compact format)
        if projects:
            output_parts.append("**🔗 Related Projects:**")
            for i, project in enumerate(projects, 1):
                # Compact project entry
                output_parts.append(f"{i}. **{project['name']}** - {project.get('category', 'General')}")
                
                # Short description
                description = project.get('description', '')
                if description and len(description) > 80:
                    description = description[:77] + "..."
                if description:
                    output_parts.append(f"   {description}")
                
                # GitHub links (compact)
                github_links = project.get('github_links', [])
                if github_links:
                    output_parts.append(f"   GitHub: {', '.join(github_links)}")
                
                output_parts.append("")
        
        return "\n".join(output_parts)
    
    def format_for_web_display(self, enhanced_response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for web display with HTML/markdown"""
        
        blogs = enhanced_response.get('blogs', [])
        projects = enhanced_response.get('related_projects', [])
        
        # Create web-friendly format
        web_format = {
            'answer': enhanced_response['answer'],
            'blogs_section': {
                'title': 'Related Blog Posts',
                'items': []
            },
            'projects_section': {
                'title': 'Related GitHub Projects',
                'items': []
            }
        }
        
        # Format blogs for web
        for blog in blogs:
            web_format['blogs_section']['items'].append({
                'title': blog['title'],
                'url': blog['url'],
                'summary': blog['summary'],
                'author': blog['author'],
                'date': blog['date'],
                'category': blog['category'],
                'relevance_score': blog['relevance_score']
            })
        
        # Format projects for web
        for project in projects:
            web_format['projects_section']['items'].append({
                'name': project['name'],
                'description': project['description'],
                'category': project['category'],
                'github_links': project.get('github_links', []),
                'project_url': project.get('project_url', '')
            })
        
        return web_format

def create_enhanced_response_formatter() -> EnhancedResponseFormatter:
    """Factory function to create enhanced response formatter"""
    return EnhancedResponseFormatter() 