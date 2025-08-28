"""Advanced content cleaning with better extraction and structuring"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

@dataclass
class EnhancedContent:
    title: str
    content: str
    category: str
    url: str
    keywords: List[str]
    content_type: str
    structured_data: Dict  # New: structured product/policy data
    quality_score: float   # New: content quality rating

class AdvancedContentCleaner:
    def __init__(self):
        # Enhanced patterns for better extraction
        self.product_patterns = {
            'price': r'₹\s*[\d,]+/-|price.*₹\s*[\d,]+|sale.*₹\s*[\d,]+',
            'specifications': r'(\d+(?:g|dpi|hz|ms|inch|mm|gb|tb))',
            'features': r'(wireless|wired|rgb|mechanical|ergonomic|gaming|professional|premium|ultra|pro)',
            'colors': r'(black|white|purple|orange|red|blue|green|pink|grey|silver)',
            'ratings': r'(\d+\.\d+)\s*(?:stars?|rating|reviews?)',
            'discount': r'save\s*(\d+)%|(\d+)%\s*off'
        }
        
        # Policy extraction patterns
        self.policy_patterns = {
            'shipping_time': r'(\d+[-–]\d+)\s*(?:working\s*)?days?|within\s*(\d+)\s*(?:working\s*)?days?',
            'processing_time': r'processed?\s*within\s*(\d+[-–]\d+)\s*(?:working\s*)?days?',
            'delivery_time': r'delivery?\s*(?:takes?\s*)?(\d+[-–]\d+)\s*(?:working\s*)?days?',
            'free_shipping': r'free\s*shipping|no\s*shipping\s*(?:cost|charge|fee)',
            'return_period': r'return\s*within\s*(\d+)\s*days?|(\d+)[-–]day\s*return'
        }
        
        # Content quality indicators
        self.quality_indicators = {
            'high_quality': ['specifications', 'features', 'warranty', 'support', 'professional'],
            'medium_quality': ['price', 'available', 'stock', 'color', 'size'],
            'low_quality': ['click', 'here', 'more', 'view', 'add', 'cart']
        }
    
    def extract_structured_product_data(self, content: str, title: str) -> Dict:
        """Extract structured data from product content"""
        structured = {
            'name': self.clean_product_name(title),
            'price': self.extract_price(content),
            'specifications': self.extract_specifications(content),
            'features': self.extract_features(content),
            'colors': self.extract_colors(content),
            'rating': self.extract_rating(content),
            'discount': self.extract_discount(content),
            'availability': self.extract_availability(content)
        }
        return structured
    
    def extract_structured_policy_data(self, content: str, title: str) -> Dict:
        """Extract structured data from policy content"""
        structured = {
            'policy_type': self.identify_policy_type(title, content),
            'shipping_time': self.extract_shipping_time(content),
            'processing_time': self.extract_processing_time(content),
            'delivery_time': self.extract_delivery_time(content),
            'free_shipping': self.check_free_shipping(content),
            'return_period': self.extract_return_period(content),
            'key_points': self.extract_key_policy_points(content)
        }
        return structured
    
    def clean_product_name(self, title: str) -> str:
        """Clean product name from title"""
        # Remove common suffixes and prefixes
        name = re.sub(r'\s*–\s*Kreo$', '', title)
        name = re.sub(r'^\s*Kreo\s*', '', name)
        name = re.sub(r'\s*\|\s*.*$', '', name)
        return name.strip()
    
    def extract_price(self, content: str) -> Optional[str]:
        """Extract price information"""
        price_match = re.search(self.product_patterns['price'], content, re.IGNORECASE)
        if price_match:
            return price_match.group(0)
        return None
    
    def extract_specifications(self, content: str) -> List[str]:
        """Extract technical specifications"""
        specs = re.findall(self.product_patterns['specifications'], content, re.IGNORECASE)
        return list(set(specs))
    
    def extract_features(self, content: str) -> List[str]:
        """Extract product features"""
        features = re.findall(self.product_patterns['features'], content, re.IGNORECASE)
        return list(set([f.lower() for f in features]))
    
    def extract_colors(self, content: str) -> List[str]:
        """Extract available colors"""
        colors = re.findall(self.product_patterns['colors'], content, re.IGNORECASE)
        return list(set([c.lower() for c in colors]))
    
    def extract_rating(self, content: str) -> Optional[float]:
        """Extract product rating"""
        rating_match = re.search(self.product_patterns['ratings'], content, re.IGNORECASE)
        if rating_match:
            try:
                return float(rating_match.group(1))
            except:
                pass
        return None
    
    def extract_discount(self, content: str) -> Optional[str]:
        """Extract discount information"""
        discount_match = re.search(self.product_patterns['discount'], content, re.IGNORECASE)
        if discount_match:
            return discount_match.group(0)
        return None
    
    def extract_availability(self, content: str) -> str:
        """Extract availability status"""
        if re.search(r'sold\s*out|out\s*of\s*stock', content, re.IGNORECASE):
            return 'out_of_stock'
        elif re.search(r'in\s*stock|available', content, re.IGNORECASE):
            return 'in_stock'
        return 'unknown'
    
    def extract_shipping_time(self, content: str) -> Optional[str]:
        """Extract shipping time from policy content"""
        match = re.search(self.policy_patterns['shipping_time'], content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None
    
    def extract_processing_time(self, content: str) -> Optional[str]:
        """Extract processing time"""
        match = re.search(self.policy_patterns['processing_time'], content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None
    
    def extract_delivery_time(self, content: str) -> Optional[str]:
        """Extract delivery time"""
        match = re.search(self.policy_patterns['delivery_time'], content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None
    
    def check_free_shipping(self, content: str) -> bool:
        """Check if free shipping is mentioned"""
        return bool(re.search(self.policy_patterns['free_shipping'], content, re.IGNORECASE))
    
    def extract_return_period(self, content: str) -> Optional[str]:
        """Extract return period"""
        match = re.search(self.policy_patterns['return_period'], content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None
    
    def identify_policy_type(self, title: str, content: str) -> str:
        """Identify the type of policy"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        if 'shipping' in title_lower or 'delivery' in title_lower:
            return 'shipping'
        elif 'return' in title_lower or 'refund' in title_lower:
            return 'return'
        elif 'privacy' in title_lower:
            return 'privacy'
        elif 'terms' in title_lower:
            return 'terms'
        else:
            return 'general'
    
    def extract_key_policy_points(self, content: str) -> List[str]:
        """Extract key points from policy content"""
        # Split content into sentences and find important ones
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        important_keywords = [
            'processing', 'delivery', 'shipping', 'return', 'refund',
            'working days', 'business days', 'within', 'policy'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in important_keywords):
                key_points.append(sentence)
        
        return key_points[:5]  # Return top 5 key points
    
    def calculate_content_quality(self, content: str, structured_data: Dict) -> float:
        """Calculate content quality score (0-1)"""
        score = 0.0
        
        # Length factor
        if len(content) > 100:
            score += 0.2
        if len(content) > 500:
            score += 0.1
        
        # Structured data completeness
        non_empty_fields = sum(1 for v in structured_data.values() if v)
        score += (non_empty_fields / len(structured_data)) * 0.3
        
        # Quality indicators
        content_lower = content.lower()
        high_quality_count = sum(1 for word in self.quality_indicators['high_quality'] if word in content_lower)
        medium_quality_count = sum(1 for word in self.quality_indicators['medium_quality'] if word in content_lower)
        low_quality_count = sum(1 for word in self.quality_indicators['low_quality'] if word in content_lower)
        
        score += (high_quality_count * 0.1) + (medium_quality_count * 0.05) - (low_quality_count * 0.02)
        
        return min(max(score, 0.0), 1.0)
    
    def clean_and_enhance_content(self, raw_content: str, title: str, url: str) -> EnhancedContent:
        """Main method to clean and enhance content"""
        # Basic cleaning
        content = self.basic_clean(raw_content)
        
        # Determine content type
        content_type = self.determine_content_type(url, title, content)
        
        # Extract structured data based on type
        if content_type == 'product':
            structured_data = self.extract_structured_product_data(content, title)
        elif content_type == 'policy':
            structured_data = self.extract_structured_policy_data(content, title)
        else:
            structured_data = {}
        
        # Calculate quality score
        quality_score = self.calculate_content_quality(content, structured_data)
        
        # Categorize content
        category = self.categorize_content(content, title, structured_data)
        
        # Extract keywords
        keywords = self.extract_enhanced_keywords(content, title, structured_data)
        
        return EnhancedContent(
            title=title,
            content=content,
            category=category,
            url=url,
            keywords=keywords,
            content_type=content_type,
            structured_data=structured_data,
            quality_score=quality_score
        )
    
    def basic_clean(self, content: str) -> str:
        """Basic content cleaning"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove navigation elements
        nav_patterns = [
            r'skip to content|main content|navigation|menu',
            r'home|cart|login|register|account',
            r'search|contact|about|privacy policy'
        ]
        
        for pattern in nav_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def determine_content_type(self, url: str, title: str, content: str) -> str:
        """Determine content type"""
        url_lower = url.lower()
        
        if '/products/' in url_lower:
            return 'product'
        elif '/policies/' in url_lower:
            return 'policy'
        elif '/collections/' in url_lower:
            return 'collection'
        else:
            return 'other'
    
    def categorize_content(self, content: str, title: str, structured_data: Dict) -> str:
        """Enhanced content categorization"""
        combined_text = f"{title} {content}".lower()
        
        # Use structured data for better categorization
        if structured_data.get('features'):
            features = ' '.join(structured_data['features']).lower()
            combined_text += ' ' + features
        
        category_keywords = {
            'gaming_mouse': ['mouse', 'gaming mouse', 'wireless mouse', 'dpi'],
            'gaming_keyboard': ['keyboard', 'gaming keyboard', 'mechanical', 'switches'],
            'gaming_chair': ['chair', 'gaming chair', 'ergonomic', 'seating'],
            'audio_equipment': ['microphone', 'headphone', 'mic', 'audio', 'sound'],
            'video_equipment': ['webcam', 'camera', 'streaming', 'video', '4k'],
            'lighting': ['ring light', 'lighting', 'led', 'halo', 'illumination'],
            'accessories': ['mousepad', 'keycaps', 'tripod', 'stand', 'cooler'],
            'controllers': ['controller', 'gamepad', 'gaming controller'],
            'special_edition': ['naruto', 'sasuke', 'anime', 'special edition']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(combined_text.count(keyword.lower()) for keyword in keywords)
            category_scores[category] = score
        
        # Return best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return 'other'
    
    def extract_enhanced_keywords(self, content: str, title: str, structured_data: Dict) -> List[str]:
        """Extract enhanced keywords using structured data"""
        keywords = set()
        
        # Add keywords from structured data
        if structured_data.get('features'):
            keywords.update(structured_data['features'])
        if structured_data.get('colors'):
            keywords.update(structured_data['colors'])
        if structured_data.get('specifications'):
            keywords.update(structured_data['specifications'])
        
        # Extract from text
        text_keywords = re.findall(r'\b[a-zA-Z]{3,}\b', f"{title} {content}".lower())
        
        # Filter and add relevant keywords
        relevant_keywords = [
            'wireless', 'wired', 'rgb', 'mechanical', 'ergonomic', 'gaming',
            'professional', 'premium', 'ultra', 'pro', 'black', 'white',
            'purple', 'orange', 'naruto', 'sasuke'
        ]
        
        for word in text_keywords:
            if word in relevant_keywords:
                keywords.add(word)
        
        return list(keywords)