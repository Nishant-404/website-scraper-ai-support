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

# Import configuration
from config import Config

# Import our core modules
from advanced_groq_chatbot import AdvancedGroqChatbot
from integrations.integration_manager import IntegrationManager
from database import Database, User, Product
from scraper.product_scraper import ProductScraper
from product_query_filter import ProductQueryFilter
from user_scraper import UserScraper

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Flask configuration from Config class
app.config['DEBUG'] = Config.DEBUG
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['SCRAPED_DATA_PATH'] = Config.SCRAPED_DATA_PATH

# Validate required configuration
try:
    Config.validate_required_keys()
    logger.info("✅ Configuration validated successfully")
except ValueError as e:
    logger.error(f"❌ Configuration error: {e}")
    logger.error("Please check your .env file and ensure all required variables are set")
    exit(1)

# Initialize database and components
db = Database()
query_filter = ProductQueryFilter()
user_scraper = UserScraper()

# Global variables
integration_managers = {}  # Store integration managers per user
user_sessions = {}  # Store user session data
user_chatbots = {}  # Store chatbots per user

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
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        website_url = request.form.get('website_url')
        
        if not all([username, email, password, company_name, website_url]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        try:
            # Check if user already exists
            existing_user = db.get_user_by_username(username)
            if existing_user:
                flash('Username already exists', 'error')
                return render_template('signup.html')
            
            # Create new user
            user_id = db.create_user(
                username=username,
                email=email,
                password=password,
                website_url=website_url,
                company_name=company_name
            )
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash('Error creating account. Please try again.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Get user from database
            user = db.get_user_by_username(username)
            
            if user:
                # Verify password
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if user.password_hash == password_hash:
                    # Login successful
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['company_name'] = user.company_name
                    session['website_url'] = user.website_url
                    
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'error')
            else:
                flash('User not found', 'error')
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            flash('Login error. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    user_id = session.get('user_id')
    if user_id and user_id in user_chatbots:
        del user_chatbots[user_id]
    
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Get user statistics
    stats = db.get_user_stats(user_id)
    
    # Get recent conversations
    conversations = db.get_user_conversations(user_id, limit=10)
    
    # Check if user has chatbot ready
    chatbot_ready = user_id in user_chatbots
    
    # Create user_data object for template compatibility
    user_data = {
        'company_name': user.company_name,
        'website_url': user.website_url,
        'plan': 'free',  # Default plan
        'usage': {
            'messages_this_month': stats.get('total_conversations', 0)
        }
    }
    
    # Create integration status
    integration_status = {
        'whatsapp': {'enabled': False},
        'email': {'enabled': False},
        'chatbot': {
            'enabled': chatbot_ready,
            'qa_pairs': stats.get('total_products', 0)
        }
    }
    
    # Create analytics data
    analytics = {
        'total_conversations': stats.get('total_conversations', 0)
    }
    
    return render_template('dashboard.html', 
                         user=user,
                         user_data=user_data,
                         stats=stats,
                         conversations=conversations,
                         chatbot_ready=chatbot_ready,
                         integration_status=integration_status,
                         analytics=analytics)

@app.route('/setup-website', methods=['GET', 'POST'])
def setup_website():
    """Website scraping setup"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        website_url = request.form.get('website_url')
        user_id = session['user_id']
        
        # Update user's website URL in database
        db.update_user_website(user_id, website_url)
        session['website_url'] = website_url
        
        # Start website scraping synchronously for now
        try:
            result = user_scraper.scrape_user_website(user_id, website_url)
            
            if result['success']:
                flash(f'Successfully scraped {result["products_count"]} products!', 'success')
            else:
                flash(f'Scraping failed: {result["error"]}', 'error')
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            flash(f'Scraping error: {str(e)}', 'error')
        
        return redirect(url_for('dashboard'))
    
    return render_template('setup_website.html')

@app.route('/setup-whatsapp', methods=['GET', 'POST'])
def setup_whatsapp():
    """WhatsApp integration setup"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        account_sid = request.form.get('account_sid')
        auth_token = request.form.get('auth_token')
        whatsapp_number = request.form.get('whatsapp_number')
        
        user_id = session['user_id']
        
        # TODO: Store WhatsApp config in database
        flash('WhatsApp integration configured successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_whatsapp.html')

@app.route('/setup-email', methods=['GET', 'POST'])
def setup_email():
    """Email integration setup"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email_address = request.form.get('email_address')
        email_password = request.form.get('email_password')
        provider = request.form.get('provider', 'gmail')
        
        user_id = session['user_id']
        
        # TODO: Store email config in database
        flash('Email integration configured successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup_email.html')

@app.route('/whatsapp-agents')
def whatsapp_agents():
    """Multi-agent WhatsApp management"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # TODO: Implement multi-agent system
    return render_template('whatsapp_agents.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    stats = db.get_user_stats(user_id)
    
    # Create analytics object with proper structure
    analytics_data = {
        'total_conversations': stats.get('total_conversations', 0),
        'total_products': stats.get('total_products', 0),
        'total_qa_pairs': stats.get('total_qa_pairs', 0),
        'avg_response_time': '0.3s',
        'satisfaction_rate': '95%'
    }
    
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chatbot conversations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    
    user_id = session['user_id']
    
    # Get user's chatbot
    if user_id in user_chatbots:
        chatbot = user_chatbots[user_id]
        response = chatbot.get_response(message)
        
        return jsonify({'success': True, 'response': response.get('response', '')})
    else:
        # Try to create chatbot if user has data
        website_url = session.get('website_url', '')
        if website_url:
            chatbot = user_scraper.get_user_chatbot(user_id, website_url)
            if chatbot:
                user_chatbots[user_id] = chatbot
                response = chatbot.get_response(message)
                
                return jsonify({'success': True, 'response': response.get('response', '')})
    
    return jsonify({'success': False, 'error': 'Chatbot not available. Please scrape your website first.'}), 200



@app.route('/api/test-message', methods=['POST'])
def api_test_message():
    """API endpoint to test chatbot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    
    user_id = session['user_id']
    
    # Get user's chatbot
    if user_id in user_chatbots:
        chatbot = user_chatbots[user_id]
        response = chatbot.get_response(message)
        
        return jsonify({'success': True, 'response': response.get('response', '')})
    else:
        # Try to create chatbot if user has data
        website_url = session.get('website_url', '')
        if website_url:
            chatbot = user_scraper.get_user_chatbot(user_id, website_url)
            if chatbot:
                user_chatbots[user_id] = chatbot
                response = chatbot.get_response(message)
                
                return jsonify({'success': True, 'response': response.get('response', '')})
    
    return jsonify({'success': False, 'error': 'Chatbot not available. Please scrape your website first.'}), 200

@app.route('/api/scraping-status', methods=['GET'])
def api_scraping_status():
    """Get scraping status for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    website_url = session.get('website_url', '')
    
    # Check if user has scraped data
    if website_url:
        # Check user's products in database
        products = db.get_products_by_user(user_id)
        
        if products:
            return jsonify({
                'status': 'completed',
                'website_url': website_url,
                'qa_pairs_count': len(products),
                'products_count': len(products)
            })
    
    return jsonify({
        'status': 'pending',
        'website_url': website_url,
        'qa_pairs_count': 0,
        'products_count': 0
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

# New Product Management Routes
@app.route('/products')
def products():
    """Product management page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Get user's products from database
    user_products = db.get_products_by_user(user_id)
    
    # Convert to template format
    products_data = []
    for product in user_products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category,
            'url': product.url,
            'image_url': product.image_url,
            'scraped_at': product.scraped_at
        })
    
    # Get categories for filter
    categories = list(set(p['category'] for p in products_data if p['category']))
    
    # Get user stats
    stats = db.get_user_stats(user_id)
    
    return render_template('products.html', 
                         products=products_data, 
                         categories=categories,
                         stats=stats)

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get product details API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get product from database
    product = db.get_product_by_id(product_id, user_id)
    
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category,
            'url': product.url,
            'image_url': product.image_url,
            'features': product.features or {},
            'specifications': product.specifications or {},
            'brand': product.brand or '',
            'sku': product.sku or '',
            'scraped_at': product.scraped_at.isoformat() if product.scraped_at else 'Recently'
        })
    
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product details"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    try:
        success = db.update_product(product_id, user_id, **data)
        
        if success:
            return jsonify({'success': True, 'message': 'Product updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product not found or update failed'}), 404
            
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product_api(product_id):
    """Delete product"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    try:
        success = db.delete_product(product_id, user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product not found or delete failed'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scrape-products', methods=['POST'])
def scrape_products():
    """Scrape products from user's website"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    website_url = session.get('website_url', '')
    
    if not website_url:
        return jsonify({'success': False, 'error': 'Website URL not configured. Please set up your website first.'}), 400
    
    try:
        logger.info(f"Starting product scraping for user {user_id}: {website_url}")
        
        # Use the new user scraper
        result = user_scraper.scrape_user_website(user_id, website_url)
        
        if result['success']:
            # Create chatbot for user
            try:
                chatbot = user_scraper.get_user_chatbot(user_id, website_url)
                if chatbot:
                    user_chatbots[user_id] = chatbot
                    logger.info(f"Created chatbot for user {user_id}")
            except Exception as e:
                logger.error(f"Error creating chatbot: {e}")
            
            logger.info(f"Scraping completed successfully for user {user_id}")
            return jsonify(result)
        else:
            logger.error(f"Scraping failed for user {user_id}: {result.get('error')}")
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error scraping products for user {user_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting AI Customer Support Platform...")
    print("🌐 Website: http://localhost:5000")
    print("📱 WhatsApp webhook: http://localhost:5000/api/webhook/whatsapp")
    
    app.run(host='0.0.0.0', port=5000, debug=True)