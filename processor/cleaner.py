"""Content cleaning and preprocessing for scraped data"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CleanedContent:
    title: str
    content: str
    category: str
    url: str
    keywords: List[str]
    content_type: str  # 'product', 'policy', 'collection', 'other'
    
class ContentCleaner:
    def __init__(self):
        # Common noise patterns to remove
        self.noise_patterns = [
            r'\s+',  # Multiple whitespace
            r'[\r\n\t]+',  # Line breaks and tabs
            r'[^\w\s.,!?;:()\-\'"]+',  # Special characters (keep basic punctuation)
            r'\b(click here|read more|learn more|view all)\b',  # Generic link text
            r'\b(home|cart|login|register|account)\b',  # Navigation terms
        ]
        
        # Product-specific patterns
        self.product_indicators = [
            'price', 'buy', 'add to cart', 'specifications', 'features',
            'gaming', 'wireless', 'rgb', 'mechanical', 'mouse', 'keyboard',
            'chair', 'headphone', 'microphone', 'webcam', 'controller'
        ]
        
        # Category keywords
        self.category_keywords = {
            'gaming_mouse': ['mouse', 'gaming mouse', 'wireless mouse', 'rgb mouse'],
            'gaming_keyboard': ['keyboard', 'gaming keyboard', 'wireless keyboard', 'mechanical'],
            'gaming_chair': ['chair', 'gaming chair', 'ergonomic'],
            'audio_equipment': ['microphone', 'headphone', 'mic', 'audio', 'sound'],
            'video_equipment': ['webcam', 'camera', 'streaming', 'video'],
            'lighting': ['ring light', 'lighting', 'led', 'halo'],
            'accessories': ['mousepad', 'keycaps', 'tripod', 'stand'],
            'controllers': ['controller', 'gamepad', 'gaming controller'],
            'special_edition': ['naruto', 'sasuke', 'anime', 'special edition']
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Convert to lowercase for processing
        cleaned = text.lower()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove common noise
        cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
        
        # Remove navigation and UI elements
        ui_noise = [
            'skip to content', 'main content', 'navigation', 'menu',
            'search', 'cart', 'login', 'register', 'account',
            'home', 'contact', 'about', 'privacy policy'
        ]
        
        for noise in ui_noise:
            cleaned = re.sub(rf'\b{noise}\b', '', cleaned)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def extract_product_info(self, content: str, title: str) -> Dict:
        """Extract structured product information"""
        product_info = {
            'name': title,
            'features': [],
            'specifications': [],
            'price_mentioned': False,
            'category': 'unknown'
        }
        
        # Look for features (common product description patterns)
        feature_patterns = [
            r'(\d+g|\d+dpi|\d+hz|\d+ms)',  # Technical specs
            r'(wireless|wired|rgb|mechanical|ergonomic)',  # Key features
            r'(gaming|professional|premium|ultra)',  # Quality indicators
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            product_info['features'].extend(matches)
        
        # Check for price indicators
        if re.search(r'(price|cost|\$|\₹|buy|purchase)', content, re.IGNORECASE):
            product_info['price_mentioned'] = True
        
        # Determine category
        product_info['category'] = self.categorize_content(content, title)
        
        return product_info
    
    def categorize_content(self, content: str, title: str) -> str:
        """Categorize content based on keywords"""
        combined_text = f"{title} {content}".lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                score += combined_text.count(keyword.lower())
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        # Fallback categorization
        if 'product' in combined_text:
            return 'product'
        elif 'policy' in combined_text:
            return 'policy'
        elif 'collection' in combined_text:
            return 'collection'
        
        return 'other'
    
    def determine_content_type(self, url: str, title: str, content: str) -> str:
        """Determine the type of content"""
        url_lower = url.lower()
        
        if '/products/' in url_lower:
            return 'product'
        elif '/collections/' in url_lower:
            return 'collection'
        elif '/policies/' in url_lower:
            return 'policy'
        elif 'cart' in url_lower or 'login' in url_lower:
            return 'navigation'
        else:
            return 'other'
    
    def extract_keywords(self, content: str, title: str) -> List[str]:
        """Extract relevant keywords from content"""
        combined_text = f"{title} {content}".lower()
        
        # Product-related keywords
        keywords = []
        
        # Technical specifications
        tech_specs = re.findall(r'\b(\d+(?:g|dpi|hz|ms|inch|mm))\b', combined_text)
        keywords.extend(tech_specs)
        
        # Product features
        feature_words = [
            'wireless', 'wired', 'rgb', 'mechanical', 'ergonomic',
            'gaming', 'professional', 'premium', 'ultra', 'pro',
            'black', 'white', 'purple', 'orange', 'naruto', 'sasuke'
        ]
        
        for word in feature_words:
            if word in combined_text:
                keywords.append(word)
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def clean_page_data(self, page_data: Dict) -> Optional[CleanedContent]:
        """Clean a single page's data"""
        try:
            title = page_data.get('title', '').strip()
            content = page_data.get('content', '').strip()
            url = page_data.get('url', '')
            
            # Skip if no meaningful content
            if not title and not content:
                return None
            
            if len(content) < 50:  # Skip very short content
                return None
            
            # Clean the content
            cleaned_content = self.clean_text(content)
            
            # Determine content type and category
            content_type = self.determine_content_type(url, title, content)
            category = self.categorize_content(cleaned_content, title)
            
            # Extract keywords
            keywords = self.extract_keywords(cleaned_content, title)
            
            return CleanedContent(
                title=title,
                content=cleaned_content,
                category=category,
                url=url,
                keywords=keywords,
                content_type=content_type
            )
            
        except Exception as e:
            print(f"Error cleaning page data: {e}")
            return None
    
    def clean_company_data(self, raw_data_file: str) -> List[CleanedContent]:
        """Clean all data for a company"""
        try:
            with open(raw_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cleaned_pages = []
            pages = data.get('pages', [])
            
            print(f"Cleaning {len(pages)} pages...")
            
            for i, page in enumerate(pages):
                cleaned = self.clean_page_data(page)
                if cleaned:
                    cleaned_pages.append(cleaned)
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(pages)} pages...")
            
            print(f"Successfully cleaned {len(cleaned_pages)} pages")
            return cleaned_pages
            
        except Exception as e:
            print(f"Error cleaning company data: {e}")
            return []