"""Data storage utilities for organizing scraped content by company"""

import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict
from .models import ScrapedPage

class DataStorage:
    def __init__(self, base_data_dir: str = "scraped_data"):
        self.base_data_dir = base_data_dir
        
    def get_company_name(self, url: str) -> str:
        """Extract company name from URL"""
        domain = urlparse(url).netloc
        
        # Remove www. and common prefixes
        domain = re.sub(r'^www\.', '', domain)
        
        # Remove TLD (.com, .org, etc.)
        company_name = domain.split('.')[0]
        
        # Clean up the name for folder usage
        company_name = re.sub(r'[^\w\-_]', '_', company_name)
        company_name = company_name.lower()
        
        return company_name
    
    def create_company_folder(self, company_name: str) -> str:
        """Create folder structure for a company"""
        company_folder = os.path.join(self.base_data_dir, company_name)
        
        # Create subfolders
        subfolders = [
            'raw_data',      # Original scraped content
            'processed',     # Cleaned and processed content
            'embeddings',    # Vector embeddings
            'qa_pairs',      # Generated Q&A pairs
            'metadata'       # Company info, scraping logs
        ]
        
        for subfolder in subfolders:
            folder_path = os.path.join(company_folder, subfolder)
            os.makedirs(folder_path, exist_ok=True)
        
        return company_folder
    
    def save_scraped_data(self, pages: List[ScrapedPage], base_url: str) -> str:
        """Save scraped pages with proper organization"""
        company_name = self.get_company_name(base_url)
        company_folder = self.create_company_folder(company_name)
        
        # Generate timestamp for this scraping session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw scraped data
        raw_data_file = os.path.join(company_folder, 'raw_data', f'scraped_{timestamp}.json')
        
        data = {
            'scraping_info': {
                'base_url': base_url,
                'company_name': company_name,
                'timestamp': timestamp,
                'total_pages': len(pages),
                'scraping_date': datetime.now().isoformat()
            },
            'pages': []
        }
        
        for page in pages:
            data['pages'].append({
                'url': page.url,
                'title': page.title,
                'content': page.content,
                'meta_description': page.meta_description,
                'links': page.links,
                'content_length': len(page.content),
                'word_count': len(page.content.split()) if page.content else 0
            })
        
        with open(raw_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata_file = os.path.join(company_folder, 'metadata', f'scraping_log_{timestamp}.json')
        metadata = {
            'company_name': company_name,
            'base_url': base_url,
            'scraping_date': datetime.now().isoformat(),
            'pages_scraped': len(pages),
            'total_content_length': sum(len(page.content) for page in pages),
            'unique_urls': list(set(page.url for page in pages)),
            'data_files': {
                'raw_data': raw_data_file,
                'metadata': metadata_file
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return company_folder
    
    def get_company_data(self, company_name: str) -> Dict:
        """Load existing data for a company"""
        company_folder = os.path.join(self.base_data_dir, company_name)
        
        if not os.path.exists(company_folder):
            return {}
        
        # Get latest raw data file
        raw_data_dir = os.path.join(company_folder, 'raw_data')
        if not os.path.exists(raw_data_dir):
            return {}
        
        raw_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
        if not raw_files:
            return {}
        
        # Get the most recent file
        latest_file = sorted(raw_files)[-1]
        file_path = os.path.join(raw_data_dir, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_companies(self) -> List[str]:
        """List all companies we have data for"""
        if not os.path.exists(self.base_data_dir):
            return []
        
        companies = []
        for item in os.listdir(self.base_data_dir):
            item_path = os.path.join(self.base_data_dir, item)
            if os.path.isdir(item_path):
                companies.append(item)
        
        return sorted(companies)
    
    def get_company_stats(self, company_name: str) -> Dict:
        """Get statistics for a company's scraped data"""
        data = self.get_company_data(company_name)
        
        if not data:
            return {}
        
        pages = data.get('pages', [])
        
        return {
            'company_name': company_name,
            'total_pages': len(pages),
            'total_content_length': sum(page.get('content_length', 0) for page in pages),
            'total_word_count': sum(page.get('word_count', 0) for page in pages),
            'average_page_length': sum(page.get('content_length', 0) for page in pages) / len(pages) if pages else 0,
            'last_scraped': data.get('scraping_info', {}).get('scraping_date', 'Unknown'),
            'base_url': data.get('scraping_info', {}).get('base_url', 'Unknown')
        }