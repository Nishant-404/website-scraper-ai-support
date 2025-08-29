#!/usr/bin/env python3
"""
Database models and management for AI Customer Support System
Multi-tenant product-focused system
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    website_url: str
    company_name: str
    created_at: str
    is_active: bool = True

@dataclass
class Product:
    id: int
    user_id: int
    name: str
    description: str
    price: str
    category: str
    url: str
    image_url: str
    features: str  # JSON string
    specifications: str  # JSON string
    scraped_at: str
    is_active: bool = True

@dataclass
class ProductQA:
    id: int
    product_id: int
    user_id: int
    question: str
    answer: str
    category: str
    is_active: bool = True

@dataclass
class QAPair:
    id: int
    user_id: int
    question: str
    answer: str
    category: str
    url: str
    created_at: str
    is_active: bool = True

@dataclass
class Conversation:
    id: int
    user_id: int
    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    total_messages: int = 0

@dataclass
class Message:
    id: int
    conversation_id: int
    user_id: int
    message: str
    response: str
    timestamp: str
    is_helpful: Optional[bool] = None

class Database:
    """Database manager for AI Customer Support System"""
    
    def __init__(self, db_path: str = "customer_support.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price TEXT,
                category TEXT,
                url TEXT,
                image_url TEXT,
                features TEXT,
                specifications TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # QA Pairs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_helpful BOOLEAN,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   company_name: str, website_url: str) -> Optional[int]:
        """Create a new user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, company_name, website_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, company_name, website_url))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
        row = cursor.fetchone()
        if row:
            return User(**dict(row))
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        row = cursor.fetchone()
        if row:
            return User(**dict(row))
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
        row = cursor.fetchone()
        if row:
            return User(**dict(row))
        return None
    
    def add_product(self, user_id: int, name: str, description: str, price: str,
                   category: str, url: str, image_url: str = "", features: str = "{}",
                   specifications: str = "{}") -> Optional[int]:
        """Add a product"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO products (user_id, name, description, price, category, url, 
                                    image_url, features, specifications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, description, price, category, url, image_url, features, specifications))
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            return None
    
    def get_products_by_user(self, user_id: int) -> List[Product]:
        """Get all products for a user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE user_id = ? AND is_active = 1', (user_id,))
        rows = cursor.fetchall()
        return [Product(**dict(row)) for row in rows]
    
    def get_product_by_id(self, product_id: int, user_id: int) -> Optional[Product]:
        """Get a specific product by ID for a user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ? AND user_id = ? AND is_active = 1', 
                      (product_id, user_id))
        row = cursor.fetchone()
        if row:
            return Product(**dict(row))
        return None
    
    def update_product(self, product_id: int, user_id: int, **kwargs) -> bool:
        """Update a product"""
        try:
            # Build dynamic update query
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['name', 'description', 'price', 'category', 'url', 'image_url', 'features', 'specifications']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.extend([product_id, user_id])
            cursor = self.conn.cursor()
            cursor.execute(f'''
                UPDATE products SET {', '.join(fields)}
                WHERE id = ? AND user_id = ? AND is_active = 1
            ''', values)
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def delete_product(self, product_id: int, user_id: int) -> bool:
        """Delete a product (soft delete)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE products SET is_active = 0 WHERE id = ? AND user_id = ?', 
                          (product_id, user_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def add_qa_pair(self, user_id: int, question: str, answer: str, 
                   category: str = "", url: str = "") -> Optional[int]:
        """Add a Q&A pair"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO qa_pairs (user_id, question, answer, category, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, question, answer, category, url))
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            return None
    
    def get_qa_pairs_by_user(self, user_id: int) -> List[QAPair]:
        """Get all Q&A pairs for a user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM qa_pairs WHERE user_id = ? AND is_active = 1', (user_id,))
        rows = cursor.fetchall()
        return [QAPair(**dict(row)) for row in rows]
    
    def create_conversation(self, user_id: int, session_id: str) -> Optional[int]:
        """Create a new conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_id, session_id)
                VALUES (?, ?)
            ''', (user_id, session_id))
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            return None
    
    def add_message(self, conversation_id: int, user_id: int, message: str, response: str) -> Optional[int]:
        """Add a message to a conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO messages (conversation_id, user_id, message, response)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, user_id, message, response))
            
            # Update conversation message count
            cursor.execute('''
                UPDATE conversations SET total_messages = total_messages + 1
                WHERE id = ?
            ''', (conversation_id,))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            return None
    
    def get_user_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Get user conversations"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE user_id = ? 
            ORDER BY started_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        return [Conversation(**dict(row)) for row in rows]
    
    def update_user_website(self, user_id: int, website_url: str) -> bool:
        """Update user's website URL"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users SET website_url = ? 
                WHERE id = ? AND is_active = 1
            ''', (website_url, user_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        cursor = self.conn.cursor()
        
        # Get product count
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (user_id,))
        total_products = cursor.fetchone()[0]
        
        # Get Q&A count
        cursor.execute('SELECT COUNT(*) FROM qa_pairs WHERE user_id = ? AND is_active = 1', (user_id,))
        total_qa_pairs = cursor.fetchone()[0]
        
        # Get conversation count
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ?', (user_id,))
        total_conversations = cursor.fetchone()[0]
        
        # Get message count
        cursor.execute('SELECT COUNT(*) FROM messages WHERE user_id = ?', (user_id,))
        total_messages = cursor.fetchone()[0]
        
        return {
            'total_products': total_products,
            'total_qa_pairs': total_qa_pairs,
            'total_conversations': total_conversations,
            'total_messages': total_messages
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class DatabaseManager:
    def __init__(self, db_path: str = "customer_support.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                website_url TEXT,
                company_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price TEXT,
                category TEXT,
                url TEXT,
                image_url TEXT,
                features TEXT,  -- JSON
                specifications TEXT,  -- JSON
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Product Q&A table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                customer_phone TEXT,
                customer_email TEXT,
                message TEXT NOT NULL,
                response TEXT,
                channel TEXT,  -- whatsapp, email, web
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User Management
    def create_user(self, username: str, email: str, password: str, 
                   website_url: str = "", company_name: str = "") -> int:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, website_url, company_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, website_url, company_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(**dict(row))
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(**dict(row))
        return None
    
    def update_user_website(self, user_id: int, website_url: str) -> bool:
        """Update user's website URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET website_url = ? WHERE id = ?
        ''', (website_url, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Product Management
    def add_product(self, user_id: int, name: str, description: str = "", 
                   price: str = "", category: str = "", url: str = "", 
                   image_url: str = "", features: Dict = None, 
                   specifications: Dict = None) -> int:
        """Add a new product"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        features_json = json.dumps(features or {})
        specs_json = json.dumps(specifications or {})
        
        cursor.execute('''
            INSERT INTO products (user_id, name, description, price, category, 
                                url, image_url, features, specifications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, description, price, category, url, image_url, 
              features_json, specs_json))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def get_user_products(self, user_id: int) -> List[Product]:
        """Get all products for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM products WHERE user_id = ? AND is_active = 1 
            ORDER BY scraped_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            product_data = dict(row)
            # Parse JSON fields
            product_data['features'] = json.loads(product_data['features'] or '{}')
            product_data['specifications'] = json.loads(product_data['specifications'] or '{}')
            products.append(Product(**product_data))
        
        return products
    
    def update_product(self, product_id: int, user_id: int, **kwargs) -> bool:
        """Update product information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['name', 'description', 'price', 'category', 'url', 'image_url']:
                fields.append(f"{field} = ?")
                values.append(value)
            elif field in ['features', 'specifications'] and isinstance(value, dict):
                fields.append(f"{field} = ?")
                values.append(json.dumps(value))
        
        if not fields:
            return False
        
        values.extend([product_id, user_id])
        query = f"UPDATE products SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        
        cursor.execute(query, values)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_product_by_id(self, product_id: int, user_id: int) -> Optional[Product]:
        """Get a specific product by ID for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM products WHERE id = ? AND user_id = ? AND is_active = 1
        ''', (product_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            product_data = dict(row)
            # Parse JSON fields
            product_data['features'] = json.loads(product_data['features'] or '{}')
            product_data['specifications'] = json.loads(product_data['specifications'] or '{}')
            return Product(**product_data)
        return None
    
    def delete_product(self, product_id: int, user_id: int) -> bool:
        """Soft delete a product"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE products SET is_active = 0 WHERE id = ? AND user_id = ?
        ''', (product_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Product Q&A Management
    def add_product_qa(self, user_id: int, question: str, answer: str, 
                      category: str = "", product_id: int = None) -> int:
        """Add product Q&A"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO product_qa (user_id, product_id, question, answer, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, product_id, question, answer, category))
        
        qa_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return qa_id
    
    def get_user_qa_pairs(self, user_id: int) -> List[ProductQA]:
        """Get all Q&A pairs for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM product_qa WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ProductQA(**dict(row)) for row in rows]
    
    def update_qa_pair(self, qa_id: int, user_id: int, question: str = None, 
                      answer: str = None, category: str = None) -> bool:
        """Update Q&A pair"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        
        if question:
            fields.append("question = ?")
            values.append(question)
        if answer:
            fields.append("answer = ?")
            values.append(answer)
        if category:
            fields.append("category = ?")
            values.append(category)
        
        if not fields:
            return False
        
        values.extend([qa_id, user_id])
        query = f"UPDATE product_qa SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        
        cursor.execute(query, values)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_qa_pair(self, qa_id: int, user_id: int) -> bool:
        """Soft delete Q&A pair"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE product_qa SET is_active = 0 WHERE id = ? AND user_id = ?
        ''', (qa_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Conversation Management
    def log_conversation(self, user_id: int, message: str, response: str = "", 
                        channel: str = "web", customer_phone: str = "", 
                        customer_email: str = "") -> int:
        """Log a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, message, response, channel, 
                                     customer_phone, customer_email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, message, response, channel, customer_phone, customer_email))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conversation_id
    
    def get_user_conversations(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user's conversations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Analytics
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Product count
        cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', (user_id,))
        product_count = cursor.fetchone()[0]
        
        # Q&A count
        cursor.execute('SELECT COUNT(*) FROM product_qa WHERE user_id = ? AND is_active = 1', (user_id,))
        qa_count = cursor.fetchone()[0]
        
        # Conversation count
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ?', (user_id,))
        conversation_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'products': product_count,
            'qa_pairs': qa_count,
            'conversations': conversation_count
        }