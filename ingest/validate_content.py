#!/usr/bin/env python3
"""
Content Validation Script for Ask ET
Validates URL accessibility and generates reports without rebuilding the index
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
        "total_urls": len(blog_data.get("metadata", {}).get("scraped_urls", [])),
        "accessible": [],
        "inaccessible": [],
        "errors": []
    }
    
    for i, url in enumerate(blog_data.get("metadata", {}).get("scraped_urls", []), 1):
        logger.info(f"Validating URL {i}/{len(blog_data['metadata']['scraped_urls'])}: {url}")
        
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

def validate_project_urls(project_metadata_path: str) -> dict:
    """Validate all project URLs and return accessibility report"""
    logger.info("Validating project URLs...")
    
    with open(project_metadata_path, 'r') as f:
        project_data = json.load(f)
    
    validation_results = {
        "total_urls": 0,
        "accessible": [],
        "inaccessible": [],
        "errors": []
    }
    
    for project in project_data.get("projects", []):
        project_url = project.get("project_url")
        if project_url:
            validation_results["total_urls"] += 1
            logger.info(f"Validating project URL: {project_url}")
            
            result = validate_url_accessibility(project_url)
            
            if result["accessible"] and result.get("has_content", False):
                validation_results["accessible"].append({
                    "url": project_url,
                    "project_name": project.get("name", "Unknown"),
                    "word_count": result.get("word_count", 0),
                    "content_length": result.get("content_length", 0)
                })
            else:
                validation_results["inaccessible"].append({
                    "url": project_url,
                    "project_name": project.get("name", "Unknown"),
                    "error": result.get("error", "Unknown error")
                })
            
            # Be respectful with requests
            time.sleep(1)
    
    logger.info(f"Project validation complete: {len(validation_results['accessible'])} accessible, {len(validation_results['inaccessible'])} inaccessible")
    return validation_results

def generate_validation_report(blog_results: dict, project_results: dict) -> dict:
    """Generate a comprehensive validation report"""
    total_urls = blog_results["total_urls"] + project_results["total_urls"]
    total_accessible = len(blog_results["accessible"]) + len(project_results["accessible"])
    total_inaccessible = len(blog_results["inaccessible"]) + len(project_results["inaccessible"])
    
    accessibility_rate = (total_accessible / total_urls * 100) if total_urls > 0 else 0
    
    report = {
        "validation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total_urls": total_urls,
            "accessible_urls": total_accessible,
            "inaccessible_urls": total_inaccessible,
            "accessibility_rate": round(accessibility_rate, 2)
        },
        "blog_validation": blog_results,
        "project_validation": project_results,
        "recommendations": []
    }
    
    # Generate recommendations
    if accessibility_rate < 80:
        report["recommendations"].append("Consider rebuilding the index to remove inaccessible content")
    
    if len(blog_results["inaccessible"]) > 0:
        report["recommendations"].append(f"Found {len(blog_results['inaccessible'])} inaccessible blog URLs")
    
    if len(project_results["inaccessible"]) > 0:
        report["recommendations"].append(f"Found {len(project_results['inaccessible'])} inaccessible project URLs")
    
    if accessibility_rate >= 90:
        report["recommendations"].append("Content accessibility is excellent")
    
    return report

def main():
    """Main function"""
    print("Starting content validation...")
    
    try:
        # Paths
        blog_metadata_path = Path("data/blog_metadata.json")
        project_metadata_path = Path("data/project_metadata.json")
        
        if not blog_metadata_path.exists():
            print(f"Error: Blog metadata file not found at {blog_metadata_path}")
            return 1
        
        if not project_metadata_path.exists():
            print(f"Error: Project metadata file not found at {project_metadata_path}")
            return 1
        
        # Validate blog URLs
        print("Validating blog URLs...")
        blog_results = validate_blog_urls(str(blog_metadata_path))
        
        # Validate project URLs
        print("Validating project URLs...")
        project_results = validate_project_urls(str(project_metadata_path))
        
        # Generate comprehensive report
        print("Generating validation report...")
        report = generate_validation_report(blog_results, project_results)
        
        # Save reports
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Save detailed validation report
        validation_report_path = logs_dir / "content_validation_report.json"
        with open(validation_report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save summary report
        summary_report_path = logs_dir / "content_validation_summary.json"
        with open(summary_report_path, 'w') as f:
            json.dump({
                "timestamp": report["validation_timestamp"],
                "summary": report["summary"],
                "recommendations": report["recommendations"]
            }, f, indent=2)
        
        # Print results
        print("\n" + "="*60)
        print("CONTENT VALIDATION COMPLETED")
        print("="*60)
        print(f"Total URLs checked: {report['summary']['total_urls']}")
        print(f"Accessible URLs: {report['summary']['accessible_urls']}")
        print(f"Inaccessible URLs: {report['summary']['inaccessible_urls']}")
        print(f"Accessibility Rate: {report['summary']['accessibility_rate']}%")
        
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        
        print(f"\nDetailed report: {validation_report_path}")
        print(f"Summary report: {summary_report_path}")
        
        # Show some examples of inaccessible URLs
        if blog_results["inaccessible"]:
            print(f"\nExamples of inaccessible blog URLs:")
            for i, item in enumerate(blog_results["inaccessible"][:5], 1):
                print(f"  {i}. {item['url']} - {item['error']}")
        
        if project_results["inaccessible"]:
            print(f"\nExamples of inaccessible project URLs:")
            for i, item in enumerate(project_results["inaccessible"][:5], 1):
                print(f"  {i}. {item['project_name']} - {item['url']} - {item['error']}")
        
        return 0
        
    except Exception as e:
        print(f"Error during content validation: {e}")
        logger.error(f"Error during content validation: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 