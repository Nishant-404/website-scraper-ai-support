#!/usr/bin/env python3
"""
User-specific website scraper
Handles scraping and data management for individual users
"""

import os
import json
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
from database import Database
from scraper.product_scraper import ProductScraper
from processor.smart_qa_generator import SmartQAGenerator
from advanced_groq_chatbot import AdvancedGroqChatbot

class UserScraper:
    def __init__(self):
        self.db = Database()
        self.logger = logging.getLogger(__name__)
    
    def scrape_website(self, user_id: int, website_url: str) -> Dict:
        """Alias for scrape_user_website for compatibility"""
        return self.scrape_user_website(user_id, website_url)
    
    def scrape_user_website(self, user_id: int, website_url: str) -> Dict:
        """Scrape website for a specific user and save to database"""
        try:
            self.logger.info(f"Starting product scraping for user {user_id}: {website_url}")
            
            # Get user info
            user = self.db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Clear existing products for this user
            self._clear_user_products(user_id)
            
            # Initialize product scraper
            scraper = ProductScraper(website_url, max_products=50)
            
            # Scrape products
            products = scraper.scrape_products()
            self.logger.info(f"Scraped {len(products)} products for user {user_id}")
            
            if not products:
                return {'success': False, 'error': 'No products found on website'}
            
            # Save products to database
            products_added = 0
            for product_info in products:
                try:
                    product_id = self.db.add_product(
                        user_id=user_id,
                        name=product_info.name,
                        description=product_info.description,
                        price=product_info.price,
                        category=product_info.category,
                        url=product_info.url,
                        image_url=product_info.image_url,
                        features=product_info.features,
                        specifications=product_info.specifications
                    )
                    products_added += 1
                    self.logger.info(f"Added product: {product_info.name}")
                except Exception as e:
                    self.logger.error(f"Error saving product {product_info.name}: {e}")
                    continue
            
            # Generate Q&A pairs for products
            qa_pairs_added = self._generate_qa_pairs(user_id, products)
            
            # Create user-specific Q&A file for chatbot
            qa_file_path = self._create_qa_file(user_id, website_url)
            
            result = {
                'success': True,
                'products_count': products_added,
                'qa_pairs_count': qa_pairs_added,
                'qa_file_path': qa_file_path
            }
            
            self.logger.info(f"Scraping completed for user {user_id}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping website for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _clear_user_products(self, user_id: int):
        """Clear existing products and Q&A for user"""
        try:
            # Get existing products
            products = self.db.get_products_by_user(user_id)
            
            # Delete products and their Q&A
            for product in products:
                self.db.delete_product(product.id, user_id)
            
            # Clear Q&A pairs
            qa_pairs = self.db.get_qa_pairs_by_user(user_id)
            for qa in qa_pairs:
                # Soft delete Q&A pairs
                pass  # TODO: Implement delete_qa_pair method
            
            self.logger.info(f"Cleared existing data for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error clearing user data: {e}")
    
    def _generate_qa_pairs(self, user_id: int, products: List) -> int:
        """Generate Q&A pairs for products"""
        try:
            qa_generator = SmartQAGenerator()
            qa_pairs_added = 0
            
            for product_info in products:
                try:
                    # Create product context for Q&A generation
                    product_context = {
                        'content': f"{product_info.name}. {product_info.description}",
                        'title': product_info.name,
                        'url': product_info.url,
                        'category': product_info.category,
                        'products': [product_info.name]
                    }
                    
                    # Generate Q&A pairs
                    pairs = qa_generator.generate_qa_pairs(product_context)
                    
                    # Save Q&A pairs to database
                    for qa in pairs:
                        self.db.add_qa_pair(
                            user_id=user_id,
                            question=qa.get('question', ''),
                            answer=qa.get('answer', ''),
                            category=product_info.category,
                            url=product_info.url
                        )
                        qa_pairs_added += 1
                        
                except Exception as e:
                    self.logger.error(f"Error generating Q&A for {product_info.name}: {e}")
                    continue
            
            return qa_pairs_added
            
        except Exception as e:
            self.logger.error(f"Error generating Q&A pairs: {e}")
            return 0
    
    def _create_qa_file(self, user_id: int, website_url: str) -> str:
        """Create Q&A file for chatbot compatibility"""
        try:
            # Get user's Q&A pairs from database
            qa_pairs = self.db.get_qa_pairs_by_user(user_id)
            
            # Convert to chatbot format
            qa_data = []
            for qa in qa_pairs:
                qa_data.append({
                    'question': qa.question,
                    'answer': qa.answer,
                    'category': qa.category,
                    'url': ''
                })
            
            # Create user-specific directory
            domain = urlparse(website_url).netloc.replace('www.', '').replace('.', '-')
            user_data_dir = f"scraped_data/user_{user_id}_{domain}"
            os.makedirs(f"{user_data_dir}/qa_pairs", exist_ok=True)
            
            qa_file_path = f"{user_data_dir}/qa_pairs/qa_pairs.json"
            
            # Save Q&A file
            with open(qa_file_path, 'w', encoding='utf-8') as f:
                json.dump(qa_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created Q&A file: {qa_file_path}")
            return qa_file_path
            
        except Exception as e:
            self.logger.error(f"Error creating Q&A file: {e}")
            return ""
    
    def get_user_chatbot(self, user_id: int, website_url: str) -> Optional[AdvancedGroqChatbot]:
        """Get chatbot instance for user"""
        try:
            # Get user info for company name
            user = self.db.get_user_by_id(user_id)
            company_name = user.company_name if user else "AI Assistant"
            
            # Create Q&A file path
            domain = urlparse(website_url).netloc.replace('www.', '').replace('.', '-')
            qa_file_path = f"scraped_data/user_{user_id}_{domain}/qa_pairs/qa_pairs.json"
            
            if os.path.exists(qa_file_path):
                chatbot = AdvancedGroqChatbot(qa_file=qa_file_path, user_id=user_id)
                chatbot.company_name = company_name
                return chatbot
            else:
                self.logger.warning(f"No Q&A file found for user {user_id}")
                chatbot = AdvancedGroqChatbot(user_id=user_id)
                chatbot.company_name = company_name
                return chatbot
                
        except Exception as e:
            self.logger.error(f"Error creating chatbot for user {user_id}: {e}")
            return None