#!/usr/bin/env python3
"""
Product-focused web scraper
Extracts only product information from e-commerce websites
"""

import re
import json
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

@dataclass
class ProductInfo:
    name: str
    description: str
    price: str
    category: str
    url: str
    image_url: str
    features: Dict
    specifications: Dict
    brand: str = ""
    sku: str = ""
    availability: str = ""

class ProductScraper:
    def __init__(self, base_url: str, max_products: int = 100):
        self.base_url = base_url
        self.max_products = max_products
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
        # Product URL patterns (common e-commerce patterns)
        self.product_patterns = [
            r'/product/',
            r'/item/',
            r'/p/',
            r'/products/',
            r'/shop/',
            r'/buy/',
            r'-p-\d+',
            r'/\d+\.html',
            r'/product-\d+',
            r'/item-\d+',
            r'/collections/',
            r'/collection/',
            r'keyboard',
            r'mouse',
            r'headset',
            r'gaming',
            r'reddragon',
            r'red-dragon'
        ]
        
        # Category patterns
        self.category_patterns = [
            r'/category/',
            r'/categories/',
            r'/c/',
            r'/cat/',
            r'/collection/',
            r'/collections/'
        ]
    
    def is_product_url(self, url: str) -> bool:
        """Check if URL is likely a product page"""
        url_lower = url.lower()
        
        # Check for product patterns
        for pattern in self.product_patterns:
            if re.search(pattern, url_lower):
                return True
        
        # Check for product-like keywords
        product_keywords = ['product', 'item', 'buy', 'shop', 'detail', 'keyboard', 'mouse', 'headset', 'gaming', 'collection']
        for keyword in product_keywords:
            if keyword in url_lower:
                return True
        
        return False
    
    def is_category_url(self, url: str) -> bool:
        """Check if URL is likely a category page"""
        url_lower = url.lower()
        
        for pattern in self.category_patterns:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    def extract_product_urls(self, start_url: str) -> List[str]:
        """Extract product URLs from website"""
        product_urls = set()
        visited_urls = set()
        urls_to_visit = [start_url]
        
        while urls_to_visit and len(product_urls) < self.max_products:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
            
            visited_urls.add(current_url)
            
            try:
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    # Skip external links
                    if urlparse(full_url).netloc != self.domain:
                        continue
                    
                    # Check if it's a product URL
                    if self.is_product_url(full_url):
                        product_urls.add(full_url)
                    
                    # Add category URLs to visit for more products
                    elif self.is_category_url(full_url) and full_url not in visited_urls:
                        urls_to_visit.append(full_url)
                
                self.logger.info(f"Found {len(product_urls)} products so far from {current_url}")
                
            except Exception as e:
                self.logger.error(f"Error scraping {current_url}: {e}")
                continue
        
        return list(product_urls)[:self.max_products]
    
    def extract_product_info(self, product_url: str) -> Optional[ProductInfo]:
        """Extract product information from a product page"""
        try:
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic product info
            product_info = self._extract_basic_info(soup, product_url)
            
            # Try to extract structured data (JSON-LD)
            structured_data = self._extract_structured_data(soup)
            if structured_data:
                product_info = self._merge_structured_data(product_info, structured_data)
            
            # Extract features and specifications
            product_info.features = self._extract_features(soup)
            product_info.specifications = self._extract_specifications(soup)
            
            return product_info
            
        except Exception as e:
            self.logger.error(f"Error extracting product info from {product_url}: {e}")
            return None
    
    def _extract_basic_info(self, soup: BeautifulSoup, url: str) -> ProductInfo:
        """Extract basic product information using common selectors"""
        
        # Product name
        name = ""
        name_selectors = [
            'h1[class*="product"]',
            'h1[class*="title"]',
            '.product-title',
            '.product-name',
            'h1',
            '[data-testid*="product-title"]',
            '[data-testid*="product-name"]'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                name = element.get_text(strip=True)
                break
        
        # Product description
        description = ""
        desc_selectors = [
            '.product-description',
            '.product-details',
            '[class*="description"]',
            '.product-summary',
            '[data-testid*="description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                break
        
        # Price
        price = ""
        price_selectors = [
            '.price',
            '.product-price',
            '[class*="price"]',
            '[data-testid*="price"]',
            '.cost',
            '.amount'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Extract price using regex
                price_match = re.search(r'[\$₹€£¥]\s*[\d,]+\.?\d*', price_text)
                if price_match:
                    price = price_match.group()
                    break
        
        # Category
        category = ""
        category_selectors = [
            '.breadcrumb',
            '.breadcrumbs',
            '.category',
            '.product-category',
            '[class*="breadcrumb"]'
        ]
        
        for selector in category_selectors:
            element = soup.select_one(selector)
            if element:
                category = element.get_text(strip=True)
                break
        
        # Image
        image_url = ""
        image_selectors = [
            '.product-image img',
            '.product-photo img',
            '[class*="product-image"] img',
            '.main-image img',
            '[data-testid*="product-image"] img'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element and element.get('src'):
                image_url = urljoin(url, element['src'])
                break
        
        return ProductInfo(
            name=name,
            description=description,
            price=price,
            category=category,
            url=url,
            image_url=image_url,
            features={},
            specifications={}
        )
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract structured data (JSON-LD) for products"""
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle single object or array
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Check if it's product data
                if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                    return data
                    
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return None
    
    def _merge_structured_data(self, product_info: ProductInfo, structured_data: Dict) -> ProductInfo:
        """Merge structured data with extracted product info"""
        
        # Update name if better one found
        if structured_data.get('name') and not product_info.name:
            product_info.name = structured_data['name']
        
        # Update description
        if structured_data.get('description') and not product_info.description:
            product_info.description = structured_data['description']
        
        # Update price
        if structured_data.get('offers'):
            offers = structured_data['offers']
            if isinstance(offers, list):
                offers = offers[0]
            
            if offers.get('price') and not product_info.price:
                currency = offers.get('priceCurrency', '')
                price = offers.get('price', '')
                product_info.price = f"{currency} {price}".strip()
        
        # Update brand
        if structured_data.get('brand'):
            brand = structured_data['brand']
            if isinstance(brand, dict):
                product_info.brand = brand.get('name', '')
            else:
                product_info.brand = str(brand)
        
        # Update SKU
        if structured_data.get('sku'):
            product_info.sku = structured_data['sku']
        
        # Update image
        if structured_data.get('image') and not product_info.image_url:
            image = structured_data['image']
            if isinstance(image, list):
                image = image[0]
            if isinstance(image, dict):
                product_info.image_url = image.get('url', '')
            else:
                product_info.image_url = str(image)
        
        return product_info
    
    def _extract_features(self, soup: BeautifulSoup) -> Dict:
        """Extract product features"""
        features = {}
        
        # Look for feature lists
        feature_selectors = [
            '.features',
            '.product-features',
            '.highlights',
            '.key-features',
            '[class*="feature"]'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(f"{selector} li, {selector} p")
            if elements:
                for i, element in enumerate(elements[:10]):  # Limit to 10 features
                    text = element.get_text(strip=True)
                    if text:
                        features[f"feature_{i+1}"] = text
                break
        
        return features
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict:
        """Extract product specifications"""
        specifications = {}
        
        # Look for specification tables
        spec_selectors = [
            '.specifications table',
            '.specs table',
            '.product-specs table',
            '[class*="specification"] table'
        ]
        
        for selector in spec_selectors:
            table = soup.select_one(selector)
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            specifications[key] = value
                break
        
        # Look for specification lists
        if not specifications:
            spec_list_selectors = [
                '.specifications dl',
                '.specs dl',
                '.product-specs dl'
            ]
            
            for selector in spec_list_selectors:
                dl = soup.select_one(selector)
                if dl:
                    dts = dl.find_all('dt')
                    dds = dl.find_all('dd')
                    
                    for dt, dd in zip(dts, dds):
                        key = dt.get_text(strip=True)
                        value = dd.get_text(strip=True)
                        if key and value:
                            specifications[key] = value
                    break
        
        return specifications
    
    def scrape_products(self) -> List[ProductInfo]:
        """Main method to scrape all products from website"""
        self.logger.info(f"Starting product scraping for {self.base_url}")
        
        # Step 1: Find all product URLs
        product_urls = self.extract_product_urls(self.base_url)
        self.logger.info(f"Found {len(product_urls)} product URLs")
        
        # Step 2: Extract product information
        products = []
        for i, url in enumerate(product_urls, 1):
            self.logger.info(f"Scraping product {i}/{len(product_urls)}: {url}")
            
            product_info = self.extract_product_info(url)
            if product_info and product_info.name:  # Only add if we got a name
                products.append(product_info)
            
            # Add delay to be respectful
            import time
            time.sleep(1)
        
        self.logger.info(f"Successfully scraped {len(products)} products")
        return products