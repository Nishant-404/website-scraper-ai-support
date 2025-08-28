import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from typing import Set, List, Dict
import logging
from .models import ScrapedPage
from .storage import DataStorage
    
class WebCrawler:
    def __init__(self, base_url: str, max_pages: int = 100, delay: float = 1.0):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        self.scraped_pages: List[ScrapedPage] = []
        self.storage = DataStorage()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Headers to appear more like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        parsed = urlparse(url)
        
        # Only crawl same domain
        if parsed.netloc != self.domain:
            return False
            
        # Skip common non-content files
        skip_extensions = {'.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.zip'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        return True
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.main-content', '.post-content', '.entry-content'
        ]
        
        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(strip=True, separator=' ')
                break
        
        # Fallback to body if no main content found
        if not content:
            content = soup.body.get_text(strip=True, separator=' ') if soup.body else ""
        
        return content
    
    def scrape_page(self, url: str) -> ScrapedPage:
        """Scrape a single page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page data
            title = soup.title.string.strip() if soup.title else ""
            content = self.extract_content(soup)
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                    links.append(absolute_url)
            
            return ScrapedPage(
                url=url,
                title=title,
                content=content,
                links=links,
                meta_description=meta_desc
            )
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return ScrapedPage(url=url, title="", content="", links=[])
    
    def crawl(self) -> List[ScrapedPage]:
        """Main crawling method"""
        self.logger.info(f"Starting crawl of {self.base_url}")
        
        while self.to_visit and len(self.scraped_pages) < self.max_pages:
            url = self.to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.logger.info(f"Scraping: {url}")
            self.visited_urls.add(url)
            
            page = self.scrape_page(url)
            if page.content:  # Only add pages with content
                self.scraped_pages.append(page)
                
                # Add new links to visit
                for link in page.links:
                    if link not in self.visited_urls and link not in self.to_visit:
                        self.to_visit.append(link)
            
            # Be respectful - add delay
            time.sleep(self.delay)
        
        self.logger.info(f"Crawl complete. Scraped {len(self.scraped_pages)} pages")
        return self.scraped_pages
    
    def save_to_json(self, filename: str = None):
        """Save scraped data to JSON file (legacy method)"""
        if filename:
            # Legacy single file save
            data = []
            for page in self.scraped_pages:
                data.append({
                    'url': page.url,
                    'title': page.title,
                    'content': page.content,
                    'meta_description': page.meta_description,
                    'links': page.links
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data saved to {filename}")
        else:
            # New organized storage
            company_folder = self.storage.save_scraped_data(self.scraped_pages, self.base_url)
            self.logger.info(f"Data saved to organized folder: {company_folder}")
            return company_folder

if __name__ == "__main__":
    # Example usage
    crawler = WebCrawler("https://example.com", max_pages=50, delay=1.0)
    pages = crawler.crawl()
    # Save to organized folder structure
    company_folder = crawler.save_to_json()
    print(f"Data saved to: {company_folder}")