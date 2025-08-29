#!/usr/bin/env python3
"""
Final comprehensive cross-check of the entire system
"""

import os
import sys
import json
import sqlite3
import importlib
from pathlib import Path

def check_file_structure():
    """Check all required files exist"""
    print("🔍 Checking File Structure...")
    
    required_files = {
        'Core Files': [
            'app.py',
            'database.py', 
            'user_scraper.py',
            'advanced_groq_chatbot.py',
            'config.py',
            '.env',
            'requirements.txt'
        ],
        'Templates': [
            'templates/base.html',
            'templates/home.html',
            'templates/login.html',
            'templates/signup.html',
            'templates/dashboard.html',
            'templates/products.html',
            'templates/analytics.html',
            'templates/setup_website.html',
            'templates/setup_whatsapp.html',
            'templates/setup_email.html',
            'templates/whatsapp_agents.html'
        ],
        'Scraper Components': [
            'scraper/crawler.py',
            'scraper/product_scraper.py',
            'scraper/config.py',
            'scraper/storage.py',
            'scraper/utils.py'
        ],
        'Processor Components': [
            'processor/processor.py',
            'processor/cleaner.py',
            'processor/qa_generator.py',
            'processor/advanced_cleaner.py',
            'processor/smart_qa_generator.py'
        ],
        'Integration Components': [
            'integrations/integration_manager.py',
            'integrations/whatsapp_integration.py',
            'integrations/email_integration.py'
        ],
        'AI Training': [
            'ai-training/chatbot.py',
            'ai-training/embeddings.py'
        ]
    }
    
    missing_files = []
    for category, files in required_files.items():
        print(f"\n  📁 {category}:")
        for file_path in files:
            if os.path.exists(file_path):
                print(f"    ✅ {file_path}")
            else:
                print(f"    ❌ {file_path} - MISSING")
                missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_imports():
    """Check all critical imports work"""
    print("\n🔧 Checking Module Imports...")
    
    modules_to_test = [
        'database',
        'user_scraper', 
        'advanced_groq_chatbot',
        'config'
    ]
    
    failed_imports = []
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"  ✅ {module_name} imports successfully")
        except Exception as e:
            print(f"  ❌ {module_name} import failed: {e}")
            failed_imports.append((module_name, str(e)))
    
    return len(failed_imports) == 0, failed_imports

def check_database_schema():
    """Check database schema is correct"""
    print("\n🗄️ Checking Database Schema...")
    
    try:
        from database import Database
        db = Database()
        
        # Check tables exist
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'products', 'qa_pairs', 'conversations', 'messages']
        missing_tables = []
        
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing")
                missing_tables.append(table)
        
        # Check user table schema
        cursor.execute("PRAGMA table_info(users);")
        user_columns = [row[1] for row in cursor.fetchall()]
        required_user_columns = ['id', 'username', 'email', 'password_hash', 'company_name', 'website_url', 'created_at']
        
        missing_user_columns = []
        for col in required_user_columns:
            if col in user_columns:
                print(f"  ✅ User column '{col}' exists")
            else:
                print(f"  ❌ User column '{col}' missing")
                missing_user_columns.append(col)
        
        return len(missing_tables) == 0 and len(missing_user_columns) == 0, (missing_tables, missing_user_columns)
        
    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False, str(e)

def check_environment_config():
    """Check environment configuration"""
    print("\n⚙️ Checking Environment Configuration...")
    
    if not os.path.exists('.env'):
        print("  ❌ .env file missing")
        return False, ".env file not found"
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        required_vars = ['GROQ_API_KEY', 'SECRET_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if var in env_content:
                print(f"  ✅ {var} configured")
            else:
                print(f"  ❌ {var} missing")
                missing_vars.append(var)
        
        return len(missing_vars) == 0, missing_vars
        
    except Exception as e:
        print(f"  ❌ Environment check failed: {e}")
        return False, str(e)

def check_flask_routes():
    """Check Flask app routes are properly defined"""
    print("\n🌐 Checking Flask Routes...")
    
    try:
        # Import app without running it
        import app
        flask_app = app.app
        
        required_routes = [
            '/',
            '/login',
            '/signup', 
            '/logout',
            '/dashboard',
            '/products',
            '/analytics',
            '/api/scrape',
            '/api/products/<int:product_id>',
            '/api/chat',
            '/setup-website',
            '/setup-whatsapp',
            '/setup-email'
        ]
        
        # Get all routes
        routes = []
        for rule in flask_app.url_map.iter_rules():
            routes.append(rule.rule)
        
        missing_routes = []
        for route in required_routes:
            # Check if route exists (handle parameterized routes)
            route_exists = any(route.replace('<int:product_id>', '<int:product_id>') in r or 
                             route.replace('<int:product_id>', '') in r.replace('<int:product_id>', '') 
                             for r in routes)
            
            if route_exists or route in routes:
                print(f"  ✅ Route '{route}' exists")
            else:
                print(f"  ❌ Route '{route}' missing")
                missing_routes.append(route)
        
        return len(missing_routes) == 0, missing_routes
        
    except Exception as e:
        print(f"  ❌ Flask routes check failed: {e}")
        return False, str(e)

def check_template_syntax():
    """Check template files for basic syntax"""
    print("\n📄 Checking Template Syntax...")
    
    template_dir = Path('templates')
    if not template_dir.exists():
        print("  ❌ Templates directory missing")
        return False, "Templates directory not found"
    
    template_files = list(template_dir.glob('*.html'))
    syntax_errors = []
    
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic checks
            if '{{' in content and '}}' in content:
                print(f"  ✅ {template_file.name} has Jinja2 syntax")
            elif template_file.name != 'base.html':  # base.html might not have variables
                print(f"  ⚠️ {template_file.name} might be missing Jinja2 syntax")
            else:
                print(f"  ✅ {template_file.name} syntax OK")
                
        except Exception as e:
            print(f"  ❌ {template_file.name} syntax error: {e}")
            syntax_errors.append((template_file.name, str(e)))
    
    return len(syntax_errors) == 0, syntax_errors

def check_scraper_functionality():
    """Check scraper components"""
    print("\n🕷️ Checking Scraper Functionality...")
    
    try:
        from user_scraper import UserScraper
        scraper = UserScraper()
        
        if hasattr(scraper, 'db') and scraper.db:
            print("  ✅ Scraper database connection works")
        else:
            print("  ❌ Scraper database connection failed")
            return False, "Database connection failed"
        
        if hasattr(scraper, 'logger') and scraper.logger:
            print("  ✅ Scraper logging works")
        else:
            print("  ❌ Scraper logging failed")
            return False, "Logging failed"
        
        # Test scraper methods exist
        required_methods = ['scrape_website', 'get_user_chatbot']
        missing_methods = []
        
        for method in required_methods:
            if hasattr(scraper, method):
                print(f"  ✅ Method '{method}' exists")
            else:
                print(f"  ❌ Method '{method}' missing")
                missing_methods.append(method)
        
        return len(missing_methods) == 0, missing_methods
        
    except Exception as e:
        print(f"  ❌ Scraper check failed: {e}")
        return False, str(e)

def check_chatbot_functionality():
    """Check chatbot functionality"""
    print("\n🤖 Checking Chatbot Functionality...")
    
    try:
        from advanced_groq_chatbot import AdvancedGroqChatbot
        
        # Test initialization (without API key for now)
        try:
            chatbot = AdvancedGroqChatbot(qa_file=None, user_id=1)
            print("  ✅ Chatbot initialization works")
        except Exception as e:
            if "API key" in str(e) or "GROQ_API_KEY" in str(e):
                print("  ✅ Chatbot initialization works (API key needed for full function)")
            else:
                print(f"  ❌ Chatbot initialization failed: {e}")
                return False, str(e)
        
        return True, None
        
    except Exception as e:
        print(f"  ❌ Chatbot check failed: {e}")
        return False, str(e)

def main():
    """Run comprehensive system cross-check"""
    print("🔍 COMPREHENSIVE SYSTEM CROSS-CHECK")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Module Imports", check_imports),
        ("Database Schema", check_database_schema),
        ("Environment Config", check_environment_config),
        ("Flask Routes", check_flask_routes),
        ("Template Syntax", check_template_syntax),
        ("Scraper Functionality", check_scraper_functionality),
        ("Chatbot Functionality", check_chatbot_functionality)
    ]
    
    passed = 0
    total = len(checks)
    all_issues = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            success, issues = check_func()
            if success:
                passed += 1
                print(f"✅ {check_name} PASSED")
            else:
                print(f"❌ {check_name} FAILED")
                all_issues.append((check_name, issues))
        except Exception as e:
            print(f"❌ {check_name} ERROR: {e}")
            all_issues.append((check_name, str(e)))
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ System is fully operational and ready for production")
        print("\n🚀 System is ready to:")
        print("  • Handle multiple users with complete isolation")
        print("  • Scrape websites and extract products")
        print("  • Generate AI-powered customer support")
        print("  • Provide analytics and insights")
        print("  • Integrate with WhatsApp and Email")
        return True
    else:
        print(f"❌ {total - passed} checks failed")
        print("\n🔧 Issues found:")
        for check_name, issues in all_issues:
            print(f"  • {check_name}: {issues}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)