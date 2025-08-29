#!/usr/bin/env python3
"""
Test the products route to see if it returns the correct data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from flask import session

def test_products_route():
    """Test the products route"""
    print("🧪 Testing Products Route...")
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Set user_id in session
        
        # Test the products route
        response = client.get('/products')
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Products route accessible")
            
            # Check if the response contains product data
            response_text = response.get_data(as_text=True)
            
            if "No Products Found" in response_text:
                print("❌ Products page shows 'No Products Found'")
                print("🔍 This indicates the frontend is not receiving the product data")
            else:
                print("✅ Products page shows product data")
            
            # Check for specific product names from our database
            test_products = ["Swarm Sasuke Edition", "GoRec Professional Wireless Mic", "Hawk Naruto Black Orange"]
            found_products = 0
            
            for product in test_products:
                if product in response_text:
                    print(f"✅ Found product: {product}")
                    found_products += 1
                else:
                    print(f"❌ Missing product: {product}")
            
            print(f"📊 Found {found_products}/{len(test_products)} test products in HTML")
            
        else:
            print(f"❌ Products route failed with status {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")

def test_database_direct():
    """Test database directly"""
    print("\n🗄️ Testing Database Direct Access...")
    
    products = db.get_products_by_user(1)
    print(f"📦 Database returns {len(products)} products for user 1")
    
    if products:
        print("✅ Database has products")
        for i, product in enumerate(products[:3]):
            print(f"  {i+1}. {product.name}")
    else:
        print("❌ Database has no products")

if __name__ == "__main__":
    test_database_direct()
    test_products_route()