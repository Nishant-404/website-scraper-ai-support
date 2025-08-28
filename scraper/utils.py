"""Utility functions for web scraping"""

import re
from urllib.parse import urlparse, urljoin
from typing import List, Set
import requests
from urllib.robotparser import RobotFileParser

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
    
    return text.strip()

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain"""
    domain1 = urlparse(url1).netloc.lower()
    domain2 = urlparse(url2).netloc.lower()
    return domain1 == domain2

def normalize_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute URL"""
    return urljoin(base_url, url)

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    return urlparse(url).netloc

def is_valid_url_format(url: str) -> bool:
    """Check if URL has valid format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_robots_txt(base_url: str, user_agent: str = '*') -> bool:
    """Check if crawling is allowed by robots.txt"""
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, base_url)
    except:
        # If robots.txt can't be read, assume crawling is allowed
        return True

def extract_links_from_text(text: str, base_url: str) -> List[str]:
    """Extract URLs from text content"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    
    # Convert to absolute URLs and filter
    absolute_urls = []
    for url in urls:
        if is_same_domain(url, base_url):
            absolute_urls.append(url)
    
    return absolute_urls

def get_page_language(soup) -> str:
    """Detect page language from HTML"""
    # Check html lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        return html_tag.get('lang')[:2]  # Get first 2 chars (e.g., 'en' from 'en-US')
    
    # Check meta tags
    meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
    if meta_lang and meta_lang.get('content'):
        return meta_lang.get('content')[:2]
    
    return 'en'  # Default to English

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes"""
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract potential keywords from text"""
    # Simple keyword extraction - can be improved with NLP
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'must'
    }
    
    # Count word frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]