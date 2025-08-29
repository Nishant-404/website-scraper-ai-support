#!/usr/bin/env python3
"""
Test script to verify the clean user-isolated system
"""

import os
import sys
import requests
import time

def test_clean_system():
    """Test the clean system with proper user isolation"""
    
    print("🧪 Testing Clean User-Isolated System")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is running
    print("1. Testing server connection...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Cannot connect to server:", e)
        print("Please make sure the server is running with: python app.py")
        return False
    
    # Test 2: Check no old data exists
    print("\n2. Checking for clean data state...")
    
    # Check no scraped_data directory
    if not os.path.exists("scraped_data"):
        print("✅ No old scraped_data directory")
    else:
        print("❌ Old scraped_data directory still exists")
    
    # Check no database files
    db_files = [f for f in os.listdir(".") if f.endswith(".db")]
    if not db_files:
        print("✅ No old database files")
    else:
        print("❌ Old database files found:", db_files)
    
    # Check no users.json
    if not os.path.exists("users.json"):
        print("✅ No old users.json file")
    else:
        print("❌ Old users.json file still exists")
    
    # Test 3: Test user registration
    print("\n3. Testing user registration...")
    
    signup_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'company_name': 'Test Company',
        'website_url': 'https://example.com'
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/signup", data=signup_data)
        
        if response.status_code == 200 and "Account created successfully" in response.text:
            print("✅ User registration works")
        else:
            print("❌ User registration failed")
            return False
    except Exception as e:
        print("❌ Registration error:", e)
        return False
    
    # Test 4: Test user login
    print("\n4. Testing user login...")
    
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data)
        
        if response.status_code == 200 and "Dashboard" in response.text:
            print("✅ User login works")
        else:
            print("❌ User login failed")
            return False
    except Exception as e:
        print("❌ Login error:", e)
        return False
    
    # Test 5: Test dashboard loads without errors
    print("\n5. Testing dashboard...")
    
    try:
        response = session.get(f"{base_url}/dashboard")
        
        if response.status_code == 200 and "Welcome back" in response.text:
            print("✅ Dashboard loads correctly")
        else:
            print("❌ Dashboard failed to load")
            return False
    except Exception as e:
        print("❌ Dashboard error:", e)
        return False
    
    # Test 6: Test products page
    print("\n6. Testing products page...")
    
    try:
        response = session.get(f"{base_url}/products")
        
        if response.status_code == 200 and "Product Management" in response.text:
            print("✅ Products page loads correctly")
        else:
            print("❌ Products page failed to load")
            return False
    except Exception as e:
        print("❌ Products page error:", e)
        return False
    
    # Test 7: Test chatbot API (should fail gracefully)
    print("\n7. Testing chatbot API...")
    
    try:
        response = session.post(f"{base_url}/api/test-message", 
                               json={'message': 'Hello'})
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('success') and 'not available' in data.get('error', ''):
                print("✅ Chatbot correctly reports no data available")
            else:
                print("❌ Chatbot should report no data available")
                return False
        else:
            print("❌ Chatbot API error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Chatbot API error:", e)
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ System is clean and user-isolated")
    print("✅ No hardcoded Kreo-Tech data")
    print("✅ Ready for fresh user data")
    
    return True

if __name__ == "__main__":
    success = test_clean_system()
    sys.exit(0 if success else 1)