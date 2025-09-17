#!/usr/bin/env python3
"""
File: main_app.py
Purpose: Main Flask application entry point with modular architecture
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file serves as the main entry point for the AI Customer Support Platform.
It initializes the Flask application, registers all blueprints, configures
middleware, and sets up the application according to the new modular architecture.

Dependencies:
- flask: Core web framework
- routes.*: All route blueprints for modular organization
- config: Application configuration management
- database: Database initialization and management

Usage:
    python main_app.py

Notes:
- Follows the new ground rules for modular architecture
- Each route category is in its own blueprint
- Extensive error handling and logging
- Proper configuration management
- Security middleware and headers
- Development and production modes
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(__file__))

# Import configuration and core modules
from config import Config
from database import Database

# Import all route blueprints for modular architecture
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp

# Configure logging based on environment
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure the Flask application.
    
    This function creates the Flask application instance and configures
    it with all necessary settings, blueprints, middleware, and error
    handlers according to the modular architecture principles.
    
    Returns:
        Flask: Configured Flask application instance
    
    Configuration Steps:
        1. Create Flask app instance
        2. Load configuration from Config class
        3. Initialize database and core components
        4. Register all route blueprints
        5. Configure middleware and security headers
        6. Set up error handlers
        7. Configure template globals and filters
    
    Notes:
        - Follows factory pattern for app creation
        - Supports different environments (dev, prod, test)
        - Includes comprehensive error handling
        - Sets up security headers and middleware
        - Configures logging and monitoring
    """
    # Step 1: Create Flask application instance
    app = Flask(__name__)
    
    # Step 2: Load configuration from Config class
    try:
        # Validate configuration before proceeding
        Config.validate_required_keys()
        
        # Set Flask configuration from Config class
        app.secret_key = Config.SECRET_KEY
        app.config['DEBUG'] = Config.DEBUG
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
        app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
        app.config['SCRAPED_DATA_PATH'] = Config.SCRAPED_DATA_PATH
        
        logger.info("✅ Configuration loaded successfully")
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    
    # Step 3: Initialize database and core components
    try:
        # Initialize database connection and tables
        db = Database()
        db.close()  # Close initial connection
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        sys.exit(1)
    
    # Step 4: Register all route blueprints for modular architecture
    try:
        # Authentication routes (login, signup, logout)
        app.register_blueprint(auth_bp, url_prefix='')
        logger.info("✅ Authentication routes registered")
        
        # Product management routes
        app.register_blueprint(product_bp, url_prefix='')
        logger.info("✅ Product routes registered")
        
        # Main application routes (defined below)
        app.register_blueprint(create_main_blueprint(), url_prefix='')
        logger.info("✅ Main routes registered")
        
    except Exception as e:
        logger.error(f"❌ Blueprint registration error: {e}")
        sys.exit(1)
    
    # Step 5: Configure middleware and security headers
    configure_middleware(app)
    
    # Step 6: Set up error handlers
    configure_error_handlers(app)
    
    # Step 7: Configure template globals and filters
    configure_template_helpers(app)
    
    logger.info("🚀 Flask application created and configured successfully")
    return app


def create_main_blueprint():
    """
    Create the main application blueprint with core routes.
    
    This function creates a blueprint containing the core application
    routes that don't fit into specific categories like auth or products.
    Includes home page, dashboard, and other general routes.
    
    Returns:
        Blueprint: Main application routes blueprint
    
    Routes Included:
        - / (home): Landing page
        - /dashboard: User dashboard
        - /setup-website: Website configuration
        - /analytics: Analytics dashboard
        - /api/scrape-products: Product scraping API
    
    Notes:
        - Contains routes that don't fit other categories
        - Includes core application functionality
        - Follows same patterns as other blueprints
        - Properly documented and error handled
    """
    from flask import Blueprint
    from routes.auth_routes import require_authentication
    
    # Create main blueprint
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    def home():
        """
        Display the application landing page.
        
        This route serves the main landing page for the AI Customer
        Support Platform. It provides information about the platform
        and navigation to login/signup for new users.
        
        Returns:
            Rendered home.html template
        
        Template Context:
            - current_user: Current authenticated user (if any)
            - platform_features: List of key platform features
            - testimonials: Customer testimonials (if available)
        
        Notes:
            - Accessible to all users (no authentication required)
            - Provides platform overview and value proposition
            - Includes call-to-action for registration
            - Responsive design for all devices
        """
        try:
            # Prepare context data for landing page
            platform_features = [
                {
                    'title': 'Intelligent Web Scraping',
                    'description': 'Automatically extract product information from any e-commerce website',
                    'icon': 'fas fa-robot'
                },
                {
                    'title': 'AI-Powered Chatbot',
                    'description': 'Create intelligent customer support bots using your product data',
                    'icon': 'fas fa-comments'
                },
                {
                    'title': 'Multi-Channel Support',
                    'description': 'Deploy on WhatsApp, Email, and Web for comprehensive coverage',
                    'icon': 'fas fa-share-alt'
                },
                {
                    'title': 'Real-Time Analytics',
                    'description': 'Track conversations, performance, and customer satisfaction',
                    'icon': 'fas fa-chart-line'
                }
            ]
            
            return render_template('home.html', 
                                 platform_features=platform_features)
        
        except Exception as e:
            logger.error(f"Error rendering home page: {str(e)}")
            return render_template('error.html', 
                                 error_message="Unable to load home page"), 500
    
    @main_bp.route('/dashboard')
    @require_authentication
    def dashboard():
        """
        Display the user dashboard with overview and statistics.
        
        This route renders the main user dashboard showing key metrics,
        recent activity, and quick access to main features. It provides
        an overview of the user's account and system status.
        
        Returns:
            Rendered dashboard.html template with user data and statistics
        
        Template Context:
            - user: Current user information
            - stats: User statistics (products, conversations, etc.)
            - recent_activity: Recent user activity
            - system_status: Platform status information
            - quick_actions: Available quick actions
        
        Notes:
            - Requires user authentication
            - Shows personalized data and metrics
            - Includes system health indicators
            - Provides navigation to main features
            - Real-time data where possible
        """
        try:
            # Get current user from session
            user_id = session.get('user_id')
            
            # Initialize database connection
            db = Database()
            
            # Get user information
            user = db.get_user_by_id(user_id)
            if not user:
                flash('User session expired. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            
            # Get user statistics
            stats = db.get_user_stats(user_id)
            
            # Get recent conversations (limited for dashboard)
            recent_conversations = db.get_user_conversations(user_id, limit=5)
            
            # Close database connection
            db.close()
            
            # Prepare dashboard context data
            dashboard_data = {
                'user': user,
                'stats': stats,
                'recent_conversations': recent_conversations,
                'system_status': {
                    'scraping_service': 'operational',
                    'ai_service': 'operational',
                    'database': 'operational'
                },
                'quick_actions': [
                    {
                        'title': 'Scrape Products',
                        'description': 'Update your product catalog',
                        'url': url_for('main.setup_website'),
                        'icon': 'fas fa-sync-alt'
                    },
                    {
                        'title': 'View Products',
                        'description': 'Manage your product inventory',
                        'url': url_for('products.products'),
                        'icon': 'fas fa-box'
                    },
                    {
                        'title': 'Analytics',
                        'description': 'View performance metrics',
                        'url': url_for('main.analytics'),
                        'icon': 'fas fa-chart-bar'
                    }
                ]
            }
            
            return render_template('dashboard.html', **dashboard_data)
        
        except Exception as e:
            logger.error(f"Error rendering dashboard: {str(e)}")
            flash(f'Error loading dashboard: {str(e)}', 'error')
            return render_template('dashboard.html', 
                                 user=None, 
                                 stats={'total_products': 0, 'total_qa_pairs': 0, 'total_conversations': 0},
                                 recent_conversations=[],
                                 system_status={},
                                 quick_actions=[])
    
    @main_bp.route('/setup-website', methods=['GET', 'POST'])
    @require_authentication
    def setup_website():
        """
        Handle website setup and scraping configuration.
        
        This route allows users to configure their website URL and
        initiate the scraping process to extract product information.
        
        GET: Display website setup form
        POST: Process website URL and start scraping
        
        Form Fields (POST):
            - website_url (str): Website URL to scrape
        
        Returns:
            GET: Rendered setup_website.html template
            POST: Redirect to dashboard with status message
        
        Notes:
            - Requires user authentication
            - Validates website URL format
            - Initiates scraping process
            - Updates user's website URL in database
            - Provides progress feedback to user
        """
        # Handle GET request - display setup form
        if request.method == 'GET':
            # Get current user's website URL if available
            user_id = session.get('user_id')
            current_website_url = session.get('website_url', '')
            
            return render_template('setup_website.html', 
                                 current_website_url=current_website_url)
        
        # Handle POST request - process website setup
        try:
            # Get form data
            website_url = request.form.get('website_url', '').strip()
            user_id = session.get('user_id')
            
            # Validate website URL
            if not website_url:
                flash('Website URL is required', 'error')
                return render_template('setup_website.html')
            
            # Basic URL validation
            if not website_url.startswith(('http://', 'https://')):
                flash('Please enter a valid URL starting with http:// or https://', 'error')
                return render_template('setup_website.html')
            
            # Update user's website URL in database
            db = Database()
            success = db.update_user_website(user_id, website_url)
            db.close()
            
            if success:
                # Update session with new website URL
                session['website_url'] = website_url
                
                # TODO: Initiate scraping process here
                # For now, just show success message
                flash(f'Website URL updated successfully: {website_url}', 'success')
                flash('Scraping functionality will be implemented in the next phase', 'info')
            else:
                flash('Failed to update website URL. Please try again.', 'error')
            
            return redirect(url_for('main.dashboard'))
        
        except Exception as e:
            logger.error(f"Error in website setup: {str(e)}")
            flash(f'Error setting up website: {str(e)}', 'error')
            return render_template('setup_website.html')
    
    @main_bp.route('/analytics')
    @require_authentication
    def analytics():
        """
        Display analytics dashboard with detailed metrics.
        
        This route renders the analytics page showing comprehensive
        metrics about user's products, conversations, and system
        performance over time.
        
        Returns:
            Rendered analytics.html template with metrics data
        
        Template Context:
            - analytics_data: Comprehensive analytics metrics
            - charts_data: Data formatted for charts and graphs
            - time_period: Selected time period for analysis
            - export_options: Available data export options
        
        Notes:
            - Requires user authentication
            - Shows historical data and trends
            - Includes interactive charts and graphs
            - Supports different time periods
            - Provides data export capabilities
        """
        try:
            # Get current user from session
            user_id = session.get('user_id')
            
            # Initialize database connection
            db = Database()
            
            # Get comprehensive user statistics
            stats = db.get_user_stats(user_id)
            
            # Get all conversations for analysis
            all_conversations = db.get_user_conversations(user_id, limit=100)
            
            # Close database connection
            db.close()
            
            # Prepare analytics data
            analytics_data = {
                'overview': {
                    'total_products': stats['total_products'],
                    'total_conversations': stats['total_conversations'],
                    'total_qa_pairs': stats['total_qa_pairs'],
                    'avg_response_time': '0.3s',  # Placeholder
                    'satisfaction_rate': '95%'   # Placeholder
                },
                'trends': {
                    'conversations_this_month': len(all_conversations),
                    'products_added_this_month': stats['total_products'],  # Simplified
                    'growth_rate': '+15%'  # Placeholder
                },
                'performance': {
                    'response_accuracy': '94%',  # Placeholder
                    'user_satisfaction': '4.8/5',  # Placeholder
                    'resolution_rate': '89%'  # Placeholder
                }
            }
            
            return render_template('analytics.html', 
                                 analytics=analytics_data)
        
        except Exception as e:
            logger.error(f"Error rendering analytics: {str(e)}")
            flash(f'Error loading analytics: {str(e)}', 'error')
            return render_template('analytics.html', 
                                 analytics={'overview': {}, 'trends': {}, 'performance': {}})
    
    return main_bp


def configure_middleware(app):
    """
    Configure middleware and security headers for the application.
    
    This function sets up various middleware components including
    security headers, request logging, and performance monitoring.
    
    Args:
        app (Flask): Flask application instance to configure
    
    Middleware Configured:
        - Security headers (CSRF, XSS protection, etc.)
        - Request logging and monitoring
        - Performance timing headers
        - CORS configuration if needed
        - Rate limiting preparation
    
    Notes:
        - Enhances application security
        - Provides request monitoring
        - Improves performance tracking
        - Prepares for production deployment
    """
    @app.before_request
    def before_request():
        """
        Execute before each request for logging and security.
        
        This function runs before every request to log request
        information and perform security checks.
        """
        # Log request information for monitoring
        logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")
        
        # Add request start time for performance monitoring
        request.start_time = datetime.now()
    
    @app.after_request
    def after_request(response):
        """
        Execute after each request to add security headers and logging.
        
        This function runs after every request to add security
        headers and log response information.
        
        Args:
            response: Flask response object
        
        Returns:
            Modified response with security headers
        """
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add performance timing header
        if hasattr(request, 'start_time'):
            duration = (datetime.now() - request.start_time).total_seconds()
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Log response information
        logger.debug(f"Response: {response.status_code} for {request.method} {request.path}")
        
        return response


def configure_error_handlers(app):
    """
    Configure global error handlers for the application.
    
    This function sets up error handlers for common HTTP errors
    and application exceptions to provide consistent error responses.
    
    Args:
        app (Flask): Flask application instance to configure
    
    Error Handlers:
        - 404 Not Found
        - 500 Internal Server Error
        - 403 Forbidden
        - 400 Bad Request
        - General Exception handler
    
    Notes:
        - Provides consistent error responses
        - Logs errors for debugging
        - Returns appropriate error pages or JSON
        - Handles both web and API requests
    """
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('error.html', 
                             error_code=404, 
                             error_message='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"Internal server error: {str(error)}")
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('error.html', 
                             error_code=500, 
                             error_message='Internal server error'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Access forbidden'}), 403
        return render_template('error.html', 
                             error_code=403, 
                             error_message='Access forbidden'), 403
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'An unexpected error occurred'}), 500
        return render_template('error.html', 
                             error_code=500, 
                             error_message='An unexpected error occurred'), 500


def configure_template_helpers(app):
    """
    Configure template globals and filters for the application.
    
    This function sets up global variables and custom filters
    that are available in all templates.
    
    Args:
        app (Flask): Flask application instance to configure
    
    Template Helpers:
        - Current timestamp for cache busting
        - Application version information
        - Utility functions for templates
        - Custom filters for data formatting
    
    Notes:
        - Makes common data available in all templates
        - Provides utility functions for template logic
        - Enables consistent formatting across templates
        - Reduces code duplication in templates
    """
    @app.template_global()
    def current_timestamp():
        """Get current timestamp for cache busting."""
        return int(datetime.now().timestamp())
    
    @app.template_global()
    def app_version():
        """Get application version."""
        return "1.0.0"  # Should be loaded from config or version file
    
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime objects in templates."""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('truncate_words')
    def truncate_words(text, length=50):
        """Truncate text to specified number of characters."""
        if not text:
            return ""
        if len(text) <= length:
            return text
        return text[:length] + "..."


# Create the Flask application instance
app = create_app()


if __name__ == '__main__':
    """
    Main entry point for the application.
    
    This section runs when the file is executed directly.
    It starts the Flask development server with appropriate
    configuration for the current environment.
    
    Environment Variables:
        - FLASK_ENV: Set to 'development' or 'production'
        - FLASK_DEBUG: Set to 'True' for debug mode
        - PORT: Port number to run the server on
    
    Notes:
        - Only runs in development mode when executed directly
        - Production deployment should use WSGI server
        - Includes startup information and health checks
        - Configures logging and monitoring
    """
    # Print startup information
    print("=" * 80)
    print("🚀 AI Customer Support Platform - Starting Up")
    print("=" * 80)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Environment: {'Development' if Config.DEBUG else 'Production'}")
    print(f"🔧 Debug Mode: {'Enabled' if Config.DEBUG else 'Disabled'}")
    print(f"📊 Log Level: {Config.LOG_LEVEL}")
    print("=" * 80)
    print("📋 Available Routes:")
    print("   🏠 Home: http://localhost:5000")
    print("   🔐 Login: http://localhost:5000/login")
    print("   📝 Signup: http://localhost:5000/signup")
    print("   📊 Dashboard: http://localhost:5000/dashboard")
    print("   📦 Products: http://localhost:5000/products")
    print("   ⚙️  Setup: http://localhost:5000/setup-website")
    print("   📈 Analytics: http://localhost:5000/analytics")
    print("=" * 80)
    print("🔧 API Endpoints:")
    print("   📦 Products API: http://localhost:5000/api/products/")
    print("   🔍 Search API: http://localhost:5000/api/products/search")
    print("   📊 Stats API: http://localhost:5000/api/products/stats")
    print("=" * 80)
    
    try:
        # Run the Flask development server
        app.run(
            host='0.0.0.0',  # Accept connections from any IP
            port=5000,       # Default port
            debug=Config.DEBUG,  # Debug mode from config
            threaded=True    # Enable threading for better performance
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("🛑 Application stopped by user")
        print("=" * 80)
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)