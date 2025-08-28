#!/usr/bin/env python3
"""
AI Customer Support Platform - Main Web Application
Customer-focused website with multi-agent WhatsApp and Email integration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
import uuid
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Import our core modules
from advanced_groq_chatbot import AdvancedGroqChatbot
from integrations.integration_manager import IntegrationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Global variables
integration_managers = {}  # Store integration managers per user
user_sessions = {}  # Store user session data

class CustomerSupportPlatform:
    """Main platform class for managing customer support instances"""
    
    def __init__(self):
        self.users = self.load_users()
        self.active_sessions = {}
    
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists('users.json'):
                with open('users.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            with open('users.json', 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def create_user(self, email, password, company_name, website_url):
        """Create new user account"""
        if email in self.users:
            return False, "Email already exists"
        
        user_id = str(uuid.uuid4())
        self.users[email] = {
            'user_id': user_id,
            'password_hash': generate_password_hash(password),
            'company_name': company_name,
            'website_url': website_url,
            'created_at': datetime.now().isoformat(),
            'plan': 'free',
            'integrations': {
                'whatsapp': {'enabled': False},
                'email': {'enabled': False}
            },
            'usage': {
                'messages_this_month': 0,
                'websites_scraped': 0
            }
        }
        self.save_users()
        return True, user_id
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        if email not in self.users:
            return False, "User not found"
        
        user = self.users[email]
        if check_password_hash(user['password_hash'], password):
            return True, user
        return False, "Invalid password"

# Initialize platform
platform = CustomerSupportPlatform()

def scrape_website_for_user(user_email: str, website_url: str):
    """Scrape website and create knowledge base for user"""
    try:
        logger.info(f"Starting website scraping for {user_email}: {website_url}")
        
        # Import scraping modules
        from scraper.crawler import WebCrawler
        from processor.advanced_cleaner import AdvancedContentCleaner
        from processor.smart_qa_generator import SmartQAGenerator
        
        # Extract domain name for folder
        from urllib.parse import urlparse
        domain = urlparse(website_url).netloc.replace('www.', '').replace('.', '-')
        
        # Initialize scraper
        crawler = WebCrawler(
            base_url=website_url,
            max_pages=100,  # Limit for performance
            delay=1
        )
        
        # Scrape website
        logger.info(f"Scraping {website_url}...")
        scraped_pages = crawler.crawl()
        
        if not scraped_pages:
            logger.error(f"No data scraped from {website_url}")
            return
        
        logger.info(f"Scraped {len(scraped_pages)} pages from {website_url}")
        
        # Clean and process content
        cleaner = AdvancedContentCleaner()
        cleaned_data = []
        
        for page in scraped_pages:
            cleaned_content = cleaner.clean_content(
                page.content,
                page.url,
                page.title
            )
            if cleaned_content:
                cleaned_data.append(cleaned_content)
        
        logger.info(f"Cleaned {len(cleaned_data)} pages")
        
        # Generate Q&A pairs
        qa_generator = SmartQAGenerator()
        qa_pairs = []
        
        for content in cleaned_data:
            pairs = qa_generator.generate_qa_pairs(content)
            qa_pairs.extend(pairs)
        
        logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
        
        # Save Q&A pairs for this user
        import os
        user_data_dir = f"scraped_data/{domain}"
        os.makedirs(f"{user_data_dir}/qa_pairs", exist_ok=True)
        
        qa_file_path = f"{user_data_dir}/qa_pairs/qa_pairs.json"
        
        import json
        with open(qa_file_path, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        
        # Update user's integration manager with new knowledge base
        if user_email in integration_managers:
            manager = integration_managers[user_email]
            manager.config['chatbot']['qa_file'] = qa_file_path
            
            # Reinitialize chatbot with new data
            manager.init_chatbot()
            
            logger.info(f"Updated chatbot for {user_email} with {len(qa_pairs)} Q&A pairs")
        
        # Update user stats
        platform.users[user_email]['usage']['websites_scraped'] += 1
        platform.save_users()
        
        logger.info(f"Website scraping completed for {user_email}")
        
    except Exception as e:
        logger.error(f"Error scraping website for {user_email}: {e}")

platform = CustomerSupportPlatform()

@app.route('/')
def home():
    """Landing page"""
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        website_url = request.form.get('website_url')
        
        if not all([email, password, company_name, website_url]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        success, result = platform.create_user(email, password, company_name, website_url)
        
        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        success, result = platform.authenticate_user(email, password)
        
        if success:
            session['user_email'] = email
            session['user_data'] = result
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result, 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    user_data = platform.users[user_email]
    
    # Get or create integration manager for this user
    if user_email not in integration_managers:
        integration_managers[user_email] = IntegrationManager()
    
    manager = integration_managers[user_email]
    analytics = manager.get_analytics()
    test_results = manager.test_integrations()
    
    return render_template('dashboard.html', 
                         user_data=user_data,
                         analytics=analytics,
                         integration_status=test_results)

@app.route('/setup-website', methods=['GET', 'POST'])
def setup_website():
    """Website scraping setup"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        website_url = request.form.get('website_url')
        user_email = session['user_email']
        
        # Update user's website URL
        platform.users[user_email]['website_url'] = website_url
        platform.save_users()
        
        # Start website scraping in background
        import threading
        scraping_thread = threading.Thread(
            target=scrape_website_for_user, 
            args=(user_email, website_url)
        )
        scraping_thread.daemon = True
        scraping_thread.start()
        
        flash('Website scraping started! This may take a few minutes. Check back soon.', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_website.html')

@app.route('/setup-whatsapp', methods=['GET', 'POST'])
def setup_whatsapp():
    """WhatsApp integration setup"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        account_sid = request.form.get('account_sid')
        auth_token = request.form.get('auth_token')
        whatsapp_number = request.form.get('whatsapp_number')
        
        user_email = session['user_email']
        
        # Update user's WhatsApp configuration
        platform.users[user_email]['integrations']['whatsapp'] = {
            'enabled': True,
            'account_sid': account_sid,
            'auth_token': auth_token,
            'whatsapp_number': whatsapp_number
        }
        platform.save_users()
        
        # Update integration manager
        if user_email in integration_managers:
            manager = integration_managers[user_email]
            manager.config['whatsapp'].update({
                'enabled': True,
                'account_sid': account_sid,
                'auth_token': auth_token,
                'whatsapp_number': whatsapp_number
            })
            manager.init_whatsapp()
        
        flash('WhatsApp integration configured successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_whatsapp.html')

@app.route('/setup-email', methods=['GET', 'POST'])
def setup_email():
    """Email integration setup"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email_address = request.form.get('email_address')
        email_password = request.form.get('email_password')
        provider = request.form.get('provider', 'gmail')
        
        user_email = session['user_email']
        
        # Update user's email configuration
        platform.users[user_email]['integrations']['email'] = {
            'enabled': True,
            'email_address': email_address,
            'password': email_password,
            'provider': provider
        }
        platform.save_users()
        
        # Update integration manager
        if user_email in integration_managers:
            manager = integration_managers[user_email]
            manager.config['email'].update({
                'enabled': True,
                'email_address': email_address,
                'password': email_password,
                'provider': provider
            })
            manager.init_email()
        
        flash('Email integration configured successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_email.html')

@app.route('/whatsapp-agents')
def whatsapp_agents():
    """Multi-agent WhatsApp management"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # TODO: Implement multi-agent system
    return render_template('whatsapp_agents.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    
    if user_email in integration_managers:
        manager = integration_managers[user_email]
        analytics_data = manager.get_analytics()
        
        return render_template('analytics.html', analytics=analytics_data)
    
    return render_template('analytics.html', analytics={'total_conversations': 0})

@app.route('/api/test-message', methods=['POST'])
def api_test_message():
    """API endpoint to test chatbot"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    
    user_email = session['user_email']
    
    if user_email in integration_managers:
        manager = integration_managers[user_email]
        if manager.chatbot:
            response = manager.chatbot.get_response(message)
            return jsonify(response)
    
    return jsonify({'error': 'Chatbot not available'}), 500

@app.route('/api/scraping-status', methods=['GET'])
def api_scraping_status():
    """Get scraping status for current user"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_email = session['user_email']
    user_data = platform.users.get(user_email, {})
    
    # Check if user has a custom knowledge base
    website_url = user_data.get('website_url', '')
    if website_url:
        from urllib.parse import urlparse
        domain = urlparse(website_url).netloc.replace('www.', '').replace('.', '-')
        qa_file_path = f"scraped_data/{domain}/qa_pairs/qa_pairs.json"
        
        import os
        if os.path.exists(qa_file_path):
            # Count Q&A pairs
            import json
            try:
                with open(qa_file_path, 'r', encoding='utf-8') as f:
                    qa_pairs = json.load(f)
                
                return jsonify({
                    'status': 'completed',
                    'website_url': website_url,
                    'qa_pairs_count': len(qa_pairs),
                    'domain': domain
                })
            except:
                pass
    
    return jsonify({
        'status': 'pending',
        'website_url': website_url,
        'qa_pairs_count': 0
    })

@app.route('/api/webhook/whatsapp', methods=['POST'])
def api_whatsapp_webhook():
    """WhatsApp webhook endpoint"""
    try:
        # Get message data from Twilio
        from_number = request.form.get('From', '')
        message_body = request.form.get('Body', '')
        
        # Find user by WhatsApp number (simplified - in production, use proper mapping)
        user_email = None
        for email, user_data in platform.users.items():
            whatsapp_config = user_data.get('integrations', {}).get('whatsapp', {})
            if whatsapp_config.get('whatsapp_number') == request.form.get('To', ''):
                user_email = email
                break
        
        if user_email and user_email in integration_managers:
            manager = integration_managers[user_email]
            result = manager.handle_whatsapp_message(from_number, message_body)
            
            if result['success']:
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'error': result.get('error')}), 500
        
        return jsonify({'status': 'error', 'error': 'User not found'}), 404
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting AI Customer Support Platform...")
    print("🌐 Website: http://localhost:5000")
    print("📱 WhatsApp webhook: http://localhost:5000/api/webhook/whatsapp")
    
    app.run(host='0.0.0.0', port=5000, debug=True)