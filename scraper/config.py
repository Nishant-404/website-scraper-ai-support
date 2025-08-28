"""Configuration settings for the web scraper"""

# Default scraping settings
DEFAULT_CONFIG = {
    "max_pages": 100,
    "delay_between_requests": 1.0,
    "request_timeout": 10,
    "max_retries": 3,
    "respect_robots_txt": True,
}

# Content extraction settings
CONTENT_SELECTORS = [
    'main',
    'article', 
    '.content',
    '#content',
    '.main-content',
    '.post-content',
    '.entry-content',
    '.page-content'
]

# Elements to remove during content extraction
REMOVE_ELEMENTS = [
    'script',
    'style',
    'nav',
    'footer', 
    'header',
    '.advertisement',
    '.ads',
    '.sidebar',
    '.menu'
]

# File extensions to skip
SKIP_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
    '.mp3', '.wav', '.ogg', '.flac',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.css', '.js', '.json', '.xml', '.rss'
}

# Common paths to skip
SKIP_PATHS = {
    '/admin', '/login', '/register', '/cart', '/checkout',
    '/search', '/tag/', '/category/', '/author/',
    '/wp-admin', '/wp-content', '/wp-includes'
}

# Headers for requests
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}