#!/usr/bin/env python3
"""
Comprehensive scraper for getting ALL pages from a website
Usage: python comprehensive_scraper.py <website_url>
"""

import sys
from scraper.crawler import WebCrawler

def main():
    if len(sys.argv) != 2:
        print("Usage: python comprehensive_scraper.py <website_url>")
        print("Example: python comprehensive_scraper.py https://kreo-tech.com")
        return
    
    website_url = sys.argv[1]
    
    print(f"🚀 Starting COMPREHENSIVE scrape of: {website_url}")
    print("This will get ALL pages, not just a sample!")
    print("=" * 60)
    
    # Create crawler with settings to get ALL content
    crawler = WebCrawler(
        base_url=website_url,
        max_pages=500,  # Much higher limit
        delay=1.5       # Still respectful but thorough
    )
    
    try:
        # Start crawling
        pages = crawler.crawl()
        
        print(f"\n✅ Successfully scraped {len(pages)} pages")
        print("=" * 60)
        
        # Show summary by page type
        product_pages = [p for p in pages if '/products/' in p.url]
        collection_pages = [p for p in pages if '/collections/' in p.url]
        policy_pages = [p for p in pages if '/policies/' in p.url]
        other_pages = [p for p in pages if p not in product_pages + collection_pages + policy_pages]
        
        print(f"📦 Product pages: {len(product_pages)}")
        print(f"📂 Collection pages: {len(collection_pages)}")
        print(f"📋 Policy pages: {len(policy_pages)}")
        print(f"🔗 Other pages: {len(other_pages)}")
        print()
        
        # Show some product examples
        if product_pages:
            print("🛍️ Sample products found:")
            for i, page in enumerate(product_pages[:10], 1):
                print(f"{i}. {page.title}")
                print(f"   URL: {page.url}")
                print(f"   Content: {len(page.content)} chars")
                print()
        
        if len(product_pages) > 10:
            print(f"... and {len(product_pages) - 10} more products!")
        
        # Save to organized folder
        company_folder = crawler.save_to_json()
        print(f"💾 All data saved to: {company_folder}")
        
        # Show final stats
        total_content = sum(len(page.content) for page in pages)
        total_words = sum(len(page.content.split()) for page in pages)
        print(f"\n📊 Final Stats:")
        print(f"Total pages: {len(pages)}")
        print(f"Total content: {total_content:,} characters")
        print(f"Total words: {total_words:,} words")
        print(f"Average per page: {total_content // len(pages):,} characters")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        if crawler.scraped_pages:
            company_folder = crawler.save_to_json()
            print(f"💾 Partial data saved to: {company_folder}")
    except Exception as e:
        print(f"❌ Error during scraping: {e}")

if __name__ == "__main__":
    main()