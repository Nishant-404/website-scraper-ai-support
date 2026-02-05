#!/usr/bin/env python3
"""
Configuration module for AI Customer Support System
Centralizes all environment variable management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', os.getenv('FLASK_DEBUG', 'True')).lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///customer_support.db')
    
    # AI/ML API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    # AI Model Settings
    AI_MODEL = os.getenv('AI_MODEL', 'llama3-8b-8192')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '4000'))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    MAX_RELEVANT_CONTEXTS = int(os.getenv('MAX_RELEVANT_CONTEXTS', '3'))
    
    # Email Settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
    
    # WhatsApp Settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # WhatsApp Business API (alternative)
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')
    
    # Web Scraping Settings
    MAX_PAGES_PER_SITE = int(os.getenv('MAX_PAGES_PER_SITE', '50'))
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '1'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Webhook Settings
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5001'))
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:5001/webhook')
    
    # Security Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
    
    # Storage Settings
    SCRAPED_DATA_PATH = os.getenv('SCRAPED_DATA_PATH', 'scraped_data')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Feature Flags
    ENABLE_WHATSAPP = os.getenv('ENABLE_WHATSAPP', 'True').lower() == 'true'
    ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'True').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'
    
    # Company Settings
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Company Name')
    COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE', 'https://yourcompany.com')
    SUPPORT_HOURS = os.getenv('SUPPORT_HOURS', '9 AM - 6 PM EST')
    DEFAULT_GREETING = os.getenv('DEFAULT_GREETING', 'Hello! How can I help you today?')
    DEFAULT_FALLBACK = os.getenv('DEFAULT_FALLBACK', "I'm sorry, I don't have information about that. Let me connect you with a human agent.")
    
    @classmethod
    def validate_required_keys(cls):
        """Validate that required environment variables are set"""
        required_keys = [
            'GROQ_API_KEY',
        ]

        if cls.ENABLE_EMAIL:
            required_keys.extend([
                'SMTP_USERNAME',
                'SMTP_PASSWORD',
                'FROM_EMAIL',
            ])

        if cls.ENABLE_WHATSAPP:
            required_keys.extend([
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN',
            ])

        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

        return True
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration"""
        return {
            'url': cls.DATABASE_URL,
            'echo': cls.DEBUG
        }
    
    @classmethod
    def get_ai_config(cls):
        """Get AI model configuration"""
        return {
            'groq_api_key': cls.GROQ_API_KEY,
            'model': cls.AI_MODEL,
            'max_tokens': cls.MAX_TOKENS,
            'temperature': cls.TEMPERATURE,
            'embedding_model': cls.EMBEDDING_MODEL,
            'max_context_length': cls.MAX_CONTEXT_LENGTH,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD,
            'max_relevant_contexts': cls.MAX_RELEVANT_CONTEXTS
        }
    
    @classmethod
    def get_email_config(cls):
        """Get email configuration"""
        return {
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'username': cls.SMTP_USERNAME,
            'password': cls.SMTP_PASSWORD,
            'use_tls': cls.SMTP_USE_TLS,
            'from_email': cls.FROM_EMAIL,
            'support_email': cls.SUPPORT_EMAIL
        }
    
    @classmethod
    def get_whatsapp_config(cls):
        """Get WhatsApp configuration"""
        return {
            'twilio_account_sid': cls.TWILIO_ACCOUNT_SID,
            'twilio_auth_token': cls.TWILIO_AUTH_TOKEN,
            'twilio_whatsapp_number': cls.TWILIO_WHATSAPP_NUMBER,
            'whatsapp_access_token': cls.WHATSAPP_ACCESS_TOKEN,
            'whatsapp_phone_number_id': cls.WHATSAPP_PHONE_NUMBER_ID,
            'whatsapp_verify_token': cls.WHATSAPP_VERIFY_TOKEN
        }
    
    @classmethod
    def get_scraping_config(cls):
        """Get web scraping configuration"""
        return {
            'max_pages': cls.MAX_PAGES_PER_SITE,
            'delay': cls.SCRAPING_DELAY,
            'timeout': cls.REQUEST_TIMEOUT,
            'user_agent': cls.USER_AGENT
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with more secure defaults for production
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    @classmethod
    def validate_required_keys(cls):
        """Additional validation for production"""
        super().validate_required_keys()
        
        production_required = [
            'SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_keys = []
        for key in production_required:
            if not getattr(cls, key) or getattr(cls, key) == getattr(Config, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Production requires these environment variables: {', '.join(missing_keys)}")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
