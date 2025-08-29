#!/usr/bin/env python3
"""
Debug database to check if products are actually being saved
"""

import sqlite3
from database import Database

def debug_database():
    """Debug database contents"""
    print("🔍 Debugging Database Contents...")
    
    # Connect directly to database
    db = Database()
    
    # Check if tables exist
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📋 Tables in database: {[table[0] for table in tables]}")
    
    # Check users table
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"👥 Total users: {user_count}")
    
    if user_count > 0:
        cursor.execute("SELECT id, username, company_name FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"  User {user[0]}: {user[1]} ({user[2]})")
    
    # Check products table
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"📦 Total products: {product_count}")
    
    if product_count > 0:
        cursor.execute("SELECT user_id, COUNT(*) FROM products GROUP BY user_id")
        products_by_user = cursor.fetchall()
        for user_id, count in products_by_user:
            print(f"  User {user_id}: {count} products")
        
        # Show first few products
        cursor.execute("SELECT id, user_id, name, is_active FROM products LIMIT 10")
        products = cursor.fetchall()
        print(f"📋 First 10 products:")
        for product in products:
            print(f"  ID: {product[0]}, User: {product[1]}, Name: {product[2]}, Active: {product[3]}")
    
    # Check qa_pairs table
    cursor.execute("SELECT COUNT(*) FROM qa_pairs")
    qa_count = cursor.fetchone()[0]
    print(f"❓ Total Q&A pairs: {qa_count}")
    
    # Test the Database class methods
    print("\n🧪 Testing Database Class Methods...")
    
    # Test get_products_by_user for user 1
    products = db.get_products_by_user(1)
    print(f"📦 Products for user 1 via get_products_by_user(): {len(products)}")
    
    if products:
        print("  First 3 products:")
        for i, product in enumerate(products[:3]):
            print(f"    {i+1}. {product.name} (ID: {product.id})")
    
    # Test get_user_stats for user 1
    stats = db.get_user_stats(1)
    print(f"📊 Stats for user 1: {stats}")
    
    db.close()

if __name__ == "__main__":
    debug_database()