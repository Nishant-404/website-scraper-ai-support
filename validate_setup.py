#!/usr/bin/env python3
"""
Validation script for AI Customer Support System
Checks if the system is properly configured
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if required files exist"""
    required_files = [
        '.env',
        'app.py',
        'config.py',
        'requirements.txt',
        'advanced_groq_chatbot.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        'scraped_data',
        'templates',
        'scraper',
        'processor',
        'integrations'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    print("✅ All required directories present")
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GROQ_API_KEY']
    optional_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'SMTP_USERNAME',
        'SMTP_PASSWORD'
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ Required environment variables set")
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠️  Optional environment variables not set: {', '.join(missing_optional)}")
        print("These are needed for WhatsApp and Email integrations")
    
    return True

def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'requests',
        'beautifulsoup4',
        'groq',
        'sentence_transformers',
        'python-dotenv',
        'scikit-learn',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required Python packages installed")
    return True

def test_configuration():
    """Test if configuration loads properly"""
    try:
        from config import Config
        Config.validate_required_keys()
        print("✅ Configuration loads successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_ai_connection():
    """Test AI API connection"""
    try:
        from config import Config
        if not Config.GROQ_API_KEY:
            print("⚠️  Cannot test AI connection - GROQ_API_KEY not set")
            return True
        
        from advanced_groq_chatbot import AdvancedGroqChatbot
        chatbot = AdvancedGroqChatbot()
        
        # Simple test
        result = chatbot.get_response("Hello, this is a test")
        if result.get('success'):
            print("✅ AI connection working")
            return True
        else:
            print(f"❌ AI connection failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ AI connection test failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating AI Customer Support System Setup...")
    print("=" * 60)
    
    checks = [
        ("Files", check_files),
        ("Directories", check_directories),
        ("Environment Variables", check_environment_variables),
        ("Python Packages", check_python_packages),
        ("Configuration", test_configuration),
        ("AI Connection", test_ai_connection)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name} check failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System is properly configured!")
        print("You can now run: python app.py")
        return True
    else:
        print("❌ System needs configuration fixes")
        print("Please address the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)