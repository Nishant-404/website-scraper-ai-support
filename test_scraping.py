#!/usr/bin/env python3
"""
Test scraping functionality
"""

from scraper.crawler import WebCrawler
from processor.advanced_cleaner import AdvancedContentCleaner
from processor.smart_qa_generator import SmartQAGenerator
import json

def test_scraping():
    """Test scraping a website"""
    website_url = "https://redgear.in"
    
    print(f"🕷️ Testing scraping: {website_url}")
    
    # Initialize crawler
    crawler = WebCrawler(
        base_url=website_url,
        max_pages=5,  # Just test with 5 pages
        delay=1
    )
    
    # Scrape website
    print("Scraping pages...")
    scraped_pages = crawler.crawl()
    
    print(f"✅ Scraped {len(scraped_pages)} pages")
    
    if scraped_pages:
        # Test first page
        first_page = scraped_pages[0]
        print(f"📄 First page: {first_page.title}")
        print(f"🔗 URL: {first_page.url}")
        print(f"📝 Content length: {len(first_page.content)} characters")
        print(f"🔗 Links found: {len(first_page.links)}")
        
        # Test content cleaning
        print("\n🧹 Testing content cleaning...")
        cleaner = AdvancedContentCleaner()
        cleaned_content = cleaner.clean_content(
            first_page.content,
            first_page.url,
            first_page.title
        )
        
        if cleaned_content:
            print(f"✅ Cleaned content: {len(cleaned_content.get('content', ''))} characters")
            
            # Test Q&A generation
            print("\n🤖 Testing Q&A generation...")
            qa_generator = SmartQAGenerator()
            qa_pairs = qa_generator.generate_qa_pairs(cleaned_content)
            
            print(f"✅ Generated {len(qa_pairs)} Q&A pairs")
            
            if qa_pairs:
                print("\n📋 Sample Q&A:")
                for i, qa in enumerate(qa_pairs[:3]):
                    print(f"{i+1}. Q: {qa.get('question', '')}")
                    print(f"   A: {qa.get('answer', '')[:100]}...")
                    print()
        
        return True
    else:
        print("❌ No pages scraped")
        return False

if __name__ == "__main__":
    test_scraping()