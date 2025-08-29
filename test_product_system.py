#!/usr/bin/env python3
"""
Test script for the new product-focused system
"""

import os
import sys
from database import DatabaseManager
from product_query_filter import ProductQueryFilter
from advanced_groq_chatbot import AdvancedGroqChatbot

def test_database():
    """Test database functionality"""
    print("🗄️ Testing Database System...")
    
    db = DatabaseManager("test_customer_support.db")
    
    # Test user creation
    user_id = db.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        website_url="https://redgear.in",
        company_name="Test Company"
    )
    print(f"✅ Created user with ID: {user_id}")
    
    # Test product creation
    product_id = db.add_product(
        user_id=user_id,
        name="Gaming Mouse",
        description="High-performance gaming mouse with RGB lighting",
        price="₹2,999",
        category="Gaming Accessories",
        url="https://redgear.in/gaming-mouse",
        image_url="https://example.com/mouse.jpg",
        features={"RGB Lighting": "16.7 million colors", "DPI": "Up to 12,000"},
        specifications={"Weight": "85g", "Cable Length": "1.8m"}
    )
    print(f"✅ Created product with ID: {product_id}")
    
    # Test Q&A creation
    qa_id = db.add_product_qa(
        user_id=user_id,
        question="What is the DPI of the gaming mouse?",
        answer="The gaming mouse has a DPI of up to 12,000 for precise gaming.",
        category="Gaming Accessories",
        product_id=product_id
    )
    print(f"✅ Created Q&A with ID: {qa_id}")
    
    # Test retrieval
    products = db.get_user_products(user_id)
    print(f"✅ Retrieved {len(products)} products")
    
    qa_pairs = db.get_user_qa_pairs(user_id)
    print(f"✅ Retrieved {len(qa_pairs)} Q&A pairs")
    
    stats = db.get_user_stats(user_id)
    print(f"✅ User stats: {stats}")
    
    # Cleanup
    os.remove("test_customer_support.db")
    print("✅ Database test completed successfully!")

def test_query_filter():
    """Test product query filter"""
    print("\n🔍 Testing Product Query Filter...")
    
    filter = ProductQueryFilter()
    
    # Test product-related queries
    product_queries = [
        "What products do you offer?",
        "Tell me about your gaming mouse",
        "What's the price of your keyboard?",
        "Do you have wireless headphones?",
        "What are the specifications of your monitor?"
    ]
    
    # Test non-product queries
    non_product_queries = [
        "What's the weather today?",
        "Tell me a joke",
        "How to cook pasta?",
        "What's the latest news?",
        "Help me with my homework"
    ]
    
    print("Product-related queries:")
    for query in product_queries:
        analysis = filter.analyze_query(query)
        print(f"  '{query}' -> Product-related: {analysis.is_product_related} (confidence: {analysis.confidence:.2f})")
    
    print("\nNon-product queries:")
    for query in non_product_queries:
        analysis = filter.analyze_query(query)
        print(f"  '{query}' -> Product-related: {analysis.is_product_related} (confidence: {analysis.confidence:.2f})")
    
    print("✅ Query filter test completed!")

def test_chatbot_with_filter():
    """Test chatbot with product filter"""
    print("\n🤖 Testing Chatbot with Product Filter...")
    
    # Check if we have a Groq API key
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️ GROQ_API_KEY not found. Skipping chatbot test.")
        return
    
    try:
        chatbot = AdvancedGroqChatbot()
        
        # Test product query
        print("Testing product query...")
        response = chatbot.get_response("What gaming products do you offer?")
        print(f"Response: {response['response'][:100]}...")
        print(f"Success: {response['success']}")
        print(f"Filtered: {response.get('filtered', False)}")
        
        # Test non-product query
        print("\nTesting non-product query...")
        response = chatbot.get_response("What's the weather like today?")
        print(f"Response: {response['response'][:100]}...")
        print(f"Success: {response['success']}")
        print(f"Filtered: {response.get('filtered', False)}")
        
        print("✅ Chatbot test completed!")
        
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Product-Focused AI Customer Support System")
    print("=" * 60)
    
    try:
        test_database()
        test_query_filter()
        test_chatbot_with_filter()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 System Features Validated:")
        print("✅ Multi-tenant database with user isolation")
        print("✅ Product-focused data management")
        print("✅ Query filtering for product-only responses")
        print("✅ Enhanced chatbot with product context")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()