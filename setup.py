#!/usr/bin/env python3
"""
Setup script for AI Customer Support System
Helps users configure their environment variables
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and add your API keys")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'scraped_data',
        'uploads',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_requirements():
    """Check if requirements are installed"""
    try:
        import flask
        import requests
        import beautifulsoup4
        import groq
        import sentence_transformers
        import dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def setup_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Scraped data (optional - uncomment if you don't want to track scraped data)
# scraped_data/

# Uploads
uploads/

# Backups
backups/

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Created/updated .gitignore file")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Customer Support System...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Setup .gitignore
    setup_gitignore()
    
    # Check requirements
    if not check_requirements():
        print("\n📦 Install requirements first:")
        print("pip install -r requirements.txt")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GROQ_API_KEY (required)")
    print("   - TWILIO_ACCOUNT_SID & TWILIO_AUTH_TOKEN (for WhatsApp)")
    print("   - SMTP credentials (for email)")
    print("\n2. Run the application:")
    print("   python app.py")
    print("\n3. Open http://localhost:5000 in your browser")
    print("\n📚 Documentation:")
    print("   - Check README.md for detailed setup instructions")
    print("   - See .env.example for all available configuration options")

if __name__ == "__main__":
    main()