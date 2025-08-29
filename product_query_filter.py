#!/usr/bin/env python3
"""
Product Query Filter
Filters and validates queries to ensure they are product-related
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class QueryAnalysis:
    is_product_related: bool
    confidence: float
    category: str
    intent: str
    suggested_response: Optional[str] = None

class ProductQueryFilter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Product-related keywords
        self.product_keywords = {
            'general': [
                'product', 'item', 'buy', 'purchase', 'order', 'shop', 'shopping',
                'price', 'cost', 'expensive', 'cheap', 'affordable', 'budget',
                'quality', 'brand', 'model', 'version', 'type', 'kind',
                'available', 'stock', 'inventory', 'in stock', 'out of stock',
                'delivery', 'shipping', 'return', 'warranty', 'guarantee'
            ],
            'specifications': [
                'specs', 'specification', 'feature', 'features', 'detail', 'details',
                'size', 'weight', 'color', 'colour', 'material', 'made of',
                'dimension', 'capacity', 'power', 'battery', 'memory', 'storage',
                'compatibility', 'compatible', 'works with', 'support', 'supports'
            ],
            'comparison': [
                'compare', 'comparison', 'difference', 'better', 'best', 'worst',
                'vs', 'versus', 'alternative', 'similar', 'like', 'recommend',
                'suggestion', 'advice', 'choose', 'select', 'pick'
            ],
            'usage': [
                'how to use', 'how to', 'usage', 'instruction', 'guide', 'tutorial',
                'setup', 'install', 'configure', 'operate', 'work', 'function'
            ]
        }
        
        # Non-product keywords (things to avoid)
        self.non_product_keywords = [
            'weather', 'news', 'politics', 'sports', 'entertainment', 'celebrity',
            'recipe', 'cooking', 'health', 'medical', 'doctor', 'medicine',
            'travel', 'vacation', 'hotel', 'flight', 'restaurant',
            'job', 'career', 'salary', 'interview', 'resume',
            'relationship', 'dating', 'marriage', 'family', 'personal',
            'education', 'school', 'university', 'homework', 'study',
            'programming', 'code', 'software development', 'algorithm'
        ]
        
        # Intent patterns
        self.intent_patterns = {
            'product_inquiry': [
                r'what is.*product',
                r'tell me about.*product',
                r'do you have.*product',
                r'show me.*product',
                r'product.*available'
            ],
            'price_inquiry': [
                r'how much.*cost',
                r'what.*price',
                r'how expensive',
                r'price.*of',
                r'cost.*of'
            ],
            'specification_inquiry': [
                r'what.*specification',
                r'what.*feature',
                r'how.*work',
                r'what.*made of',
                r'what.*size'
            ],
            'comparison_inquiry': [
                r'compare.*with',
                r'difference.*between',
                r'which.*better',
                r'recommend.*product',
                r'best.*product'
            ],
            'availability_inquiry': [
                r'in stock',
                r'available.*now',
                r'when.*available',
                r'out of stock',
                r'delivery.*time'
            ]
        }
        
        # Standard responses for non-product queries
        self.standard_responses = {
            'non_product': "I'm here to help you with product-related questions. Please ask me about our products, their features, pricing, or availability.",
            'greeting': "Hello! I'm here to help you with questions about our products. What would you like to know?",
            'general_help': "I can help you with information about our products, including features, specifications, pricing, and availability. What specific product are you interested in?"
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze if query is product-related and determine intent"""
        query_lower = query.lower().strip()
        
        # Check for greetings
        if self._is_greeting(query_lower):
            return QueryAnalysis(
                is_product_related=True,
                confidence=1.0,
                category='greeting',
                intent='greeting',
                suggested_response=self.standard_responses['greeting']
            )
        
        # Check for general help requests
        if self._is_general_help(query_lower):
            return QueryAnalysis(
                is_product_related=True,
                confidence=1.0,
                category='help',
                intent='general_help',
                suggested_response=self.standard_responses['general_help']
            )
        
        # Calculate product relevance score
        product_score = self._calculate_product_score(query_lower)
        non_product_score = self._calculate_non_product_score(query_lower)
        
        # Determine if query is product-related
        is_product_related = product_score > non_product_score and product_score > 0.3
        confidence = max(product_score - non_product_score, 0)
        
        # Determine intent
        intent = self._determine_intent(query_lower)
        category = self._determine_category(query_lower)
        
        # If not product-related, suggest standard response
        suggested_response = None
        if not is_product_related:
            suggested_response = self.standard_responses['non_product']
        
        return QueryAnalysis(
            is_product_related=is_product_related,
            confidence=confidence,
            category=category,
            intent=intent,
            suggested_response=suggested_response
        )
    
    def _is_greeting(self, query: str) -> bool:
        """Check if query is a greeting"""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'greetings', 'howdy', 'what\'s up', 'how are you'
        ]
        
        return any(greeting in query for greeting in greetings)
    
    def _is_general_help(self, query: str) -> bool:
        """Check if query is asking for general help"""
        help_patterns = [
            'help', 'assist', 'support', 'what can you do', 'how can you help',
            'what do you do', 'what are you', 'who are you'
        ]
        
        return any(pattern in query for pattern in help_patterns)
    
    def _calculate_product_score(self, query: str) -> float:
        """Calculate how product-related the query is"""
        matched_keywords = 0
        total_possible = len(self.product_keywords['general']) + len(self.product_keywords['specifications']) + len(self.product_keywords['comparison']) + len(self.product_keywords['usage'])
        
        for category, keywords in self.product_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    matched_keywords += 1
                    # Give higher weight to more specific categories
                    if category in ['specifications', 'comparison']:
                        matched_keywords += 0.5
        
        # Also check for direct product-related words
        direct_product_words = ['product', 'item', 'buy', 'price', 'cost', 'offer', 'sell', 'available']
        for word in direct_product_words:
            if word in query:
                matched_keywords += 2  # Higher weight for direct product words
        
        return min(matched_keywords / 10, 1.0)  # Normalize to 0-1 range
    
    def _calculate_non_product_score(self, query: str) -> float:
        """Calculate how non-product-related the query is"""
        matched_keywords = 0
        
        for keyword in self.non_product_keywords:
            if keyword in query:
                matched_keywords += 1
        
        return matched_keywords / max(len(self.non_product_keywords), 1)
    
    def _determine_intent(self, query: str) -> str:
        """Determine the intent of the query"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent
        
        return 'general_inquiry'
    
    def _determine_category(self, query: str) -> str:
        """Determine the category of the query"""
        category_scores = {}
        
        for category, keywords in self.product_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'general'
    
    def filter_query(self, query: str) -> Tuple[bool, str]:
        """
        Filter query and return (should_process, response_or_query)
        
        Returns:
            - (True, original_query) if query should be processed
            - (False, standard_response) if query should be rejected with standard response
        """
        analysis = self.analyze_query(query)
        
        self.logger.info(f"Query analysis: {analysis}")
        
        if analysis.is_product_related:
            return True, query
        else:
            return False, analysis.suggested_response or self.standard_responses['non_product']
    
    def enhance_query_context(self, query: str, user_products: List[Dict]) -> str:
        """Enhance query with product context"""
        analysis = self.analyze_query(query)
        
        if not analysis.is_product_related:
            return query
        
        # Add context based on intent
        context_additions = []
        
        if analysis.intent == 'product_inquiry':
            context_additions.append("Focus on product information and features.")
        elif analysis.intent == 'price_inquiry':
            context_additions.append("Focus on pricing information.")
        elif analysis.intent == 'specification_inquiry':
            context_additions.append("Focus on technical specifications and features.")
        elif analysis.intent == 'comparison_inquiry':
            context_additions.append("Focus on comparing products and their differences.")
        elif analysis.intent == 'availability_inquiry':
            context_additions.append("Focus on product availability and delivery information.")
        
        # Add product categories context
        if user_products:
            categories = list(set(p.get('category', '') for p in user_products if p.get('category')))
            if categories:
                context_additions.append(f"Available product categories: {', '.join(categories)}")
        
        if context_additions:
            enhanced_query = f"{query}\n\nContext: {' '.join(context_additions)}"
            return enhanced_query
        
        return query
    
    def get_query_suggestions(self, query: str) -> List[str]:
        """Get suggestions for better product-related queries"""
        analysis = self.analyze_query(query)
        
        if analysis.is_product_related:
            return []
        
        suggestions = [
            "What products do you offer?",
            "Can you tell me about your product features?",
            "What are the prices of your products?",
            "Do you have any products in stock?",
            "Can you compare your products?",
            "What are the specifications of your products?"
        ]
        
        return suggestions[:3]  # Return top 3 suggestions