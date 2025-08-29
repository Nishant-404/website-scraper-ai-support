#!/usr/bin/env python3
"""
Direct test of the scraping functionality
"""

import sys
import logging
from user_scraper import UserScraper
from database import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_direct_scraping():
    """Test scraping directly"""
    
    print("🧪 Testing Direct Scraping")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseManager()
    user_scraper = UserScraper()
    
    # Create a test user
    try:
        user_id = db.create_user(
            username='testuser_scraping',
            email='test_scraping@example.com',
            password='testpass123',
            website_url='https://redragon.in/collections/keyboard',
            company_name='Test Scraping Company'
        )
        print(f"✅ Created test user with ID: {user_id}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False
    
    # Test scraping
    website_url = 'https://redragon.in/collections/keyboard'
    print(f"\n🔍 Testing scraping of: {website_url}")
    
    try:
        result = user_scraper.scrape_user_website(user_id, website_url)
        
        print(f"\n📊 Scraping Result:")
        print(f"Success: {result.get('success')}")
        print(f"Products Count: {result.get('products_count', 0)}")
        print(f"QA Pairs Count: {result.get('qa_pairs_count', 0)}")
        print(f"Error: {result.get('error', 'None')}")
        
        if result.get('success'):
            # Check database
            products = db.get_user_products(user_id)
            print(f"\n📦 Products in Database: {len(products)}")
            
            for i, product in enumerate(products[:3]):  # Show first 3
                print(f"  {i+1}. {product.name} - {product.price}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_scraping()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)