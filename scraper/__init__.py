"""Web scraper module for extracting content from websites"""

from .models import ScrapedPage
from .crawler import WebCrawler
from .config import DEFAULT_CONFIG, CONTENT_SELECTORS, SKIP_EXTENSIONS
from .utils import clean_text, is_same_domain, check_robots_txt

__all__ = [
    'WebCrawler',
    'ScrapedPage', 
    'DEFAULT_CONFIG',
    'CONTENT_SELECTORS',
    'SKIP_EXTENSIONS',
    'clean_text',
    'is_same_domain',
    'check_robots_txt'
]