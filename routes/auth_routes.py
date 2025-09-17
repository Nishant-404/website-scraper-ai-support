#!/usr/bin/env python3
"""
File: auth_routes.py
Purpose: Handle authentication-related Flask routes (login, signup, logout)
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains all Flask routes related to user authentication
including user registration, login, logout, and session management.
It uses the modular functions for actual business logic.

Dependencies:
- flask: For route handling and request/response management
- functions.user.create_user: For user registration functionality
- functions.user.authenticate_user: For login authentication
- session management utilities

Usage:
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

Notes:
- All routes include proper error handling and validation
- Session management is handled securely
- Flash messages provide user feedback
- Redirects maintain proper user flow
- Input validation prevents security issues
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import our modular functions
from functions.user.create_user import create_new_user
from functions.user.authenticate_user import authenticate_user_login, verify_user_session

# Create Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user registration (signup) requests.
    
    This route handles both GET requests to display the signup form
    and POST requests to process user registration. It uses the
    modular create_new_user function for actual user creation.
    
    GET: Display the signup form template
    POST: Process registration form data and create new user account
    
    Form Fields (POST):
        - username (str): Unique username for the account
        - email (str): Valid email address
        - password (str): Password meeting security requirements
        - company_name (str): Name of user's company
        - website_url (str): Website URL for scraping
    
    Returns:
        GET: Rendered signup.html template
        POST: Redirect to login on success, or signup form with errors
    
    Flash Messages:
        - Success: "Account created successfully! Please login."
        - Error: Specific validation or creation error messages
    
    Example Usage:
        GET /signup - Shows registration form
        POST /signup - Processes registration data
    
    Notes:
        - All input validation is handled by create_new_user function
        - Passwords are securely hashed before storage
        - Duplicate username/email checks are performed
        - Detailed error messages help users fix issues
        - Successful registration redirects to login page
    """
    # Handle GET request - display signup form
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request - process registration
    try:
        # Extract form data with validation
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        company_name = request.form.get('company_name', '').strip()
        website_url = request.form.get('website_url', '').strip()
        
        # Check if all required fields are provided
        if not all([username, email, password, company_name, website_url]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        # Call modular function to create user
        result = create_new_user(
            username=username,
            email=email,
            password=password,
            company_name=company_name,
            website_url=website_url
        )
        
        # Check if user creation was successful
        if result['success']:
            # Success - redirect to login with success message
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            # Failure - show error messages and return to form
            flash(result['message'], 'error')
            
            # Add individual error messages for better UX
            for error in result.get('errors', []):
                flash(error, 'error')
            
            return render_template('signup.html')
    
    except Exception as e:
        # Handle any unexpected errors during signup
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user authentication (login) requests.
    
    This route handles both GET requests to display the login form
    and POST requests to process user authentication. It uses the
    modular authenticate_user_login function for actual authentication.
    
    GET: Display the login form template
    POST: Process login credentials and create user session
    
    Form Fields (POST):
        - username (str): Username or email address
        - password (str): User's password
    
    Returns:
        GET: Rendered login.html template
        POST: Redirect to dashboard on success, or login form with errors
    
    Session Variables Set:
        - user_id: Unique user identifier
        - username: User's username
        - company_name: User's company name
        - website_url: User's website URL
    
    Flash Messages:
        - Success: "Login successful!"
        - Error: Authentication failure or validation error messages
    
    Example Usage:
        GET /login - Shows login form
        POST /login - Processes login credentials
    
    Notes:
        - Supports login with username or email
        - Rate limiting is handled by authenticate_user_login function
        - Session data is set for authenticated users
        - Failed attempts are tracked for security
        - Successful login redirects to dashboard
    """
    # Handle GET request - display login form
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request - process authentication
    try:
        # Extract form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic input validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Call modular function to authenticate user
        result = authenticate_user_login(username, password)
        
        # Check if authentication was successful
        if result['success']:
            # Success - create user session
            user_data = result['user_data']
            
            # Set session variables for authenticated user
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['company_name'] = user_data['company_name']
            session['website_url'] = user_data['website_url']
            
            # Flash success message and redirect to dashboard
            flash(result['message'], 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Failure - show error message and return to form
            flash(result['message'], 'error')
            return render_template('login.html')
    
    except Exception as e:
        # Handle any unexpected errors during login
        flash(f'An unexpected error occurred during login: {str(e)}', 'error')
        return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout requests.
    
    This route handles user logout by clearing the session data
    and redirecting to the home page. It provides a clean way
    for users to end their authenticated session.
    
    Returns:
        Redirect to home page with success message
    
    Session Actions:
        - Clears all session data
        - Removes user authentication state
        - Invalidates current session
    
    Flash Messages:
        - Success: "Logged out successfully"
    
    Example Usage:
        GET /logout - Logs out current user
    
    Notes:
        - Clears all session data for security
        - No authentication required (can be called by anyone)
        - Redirects to home page after logout
        - Provides confirmation message to user
        - Session is completely invalidated
    """
    try:
        # Get user info for cleanup if needed
        user_id = session.get('user_id')
        username = session.get('username')
        
        # Clear all session data
        session.clear()
        
        # Flash success message with personalization if possible
        if username:
            flash(f'Goodbye, {username}! You have been logged out successfully.', 'success')
        else:
            flash('Logged out successfully', 'success')
        
        # Redirect to home page
        return redirect(url_for('main.home'))
    
    except Exception as e:
        # Handle any unexpected errors during logout
        # Still clear session and redirect, but log the error
        session.clear()
        flash('Logged out successfully', 'success')
        return redirect(url_for('main.home'))


def require_authentication(f):
    """
    Decorator to require authentication for protected routes.
    
    This decorator function checks if a user is authenticated
    before allowing access to protected routes. It verifies
    the session and redirects unauthenticated users to login.
    
    Args:
        f (function): The route function to protect
    
    Returns:
        function: Wrapped function with authentication check
    
    Usage:
        @require_authentication
        @app.route('/protected')
        def protected_route():
            return "This requires authentication"
    
    Notes:
        - Checks for valid user_id in session
        - Verifies user still exists and is active
        - Redirects to login if authentication fails
        - Preserves original function behavior if authenticated
        - Can be applied to any route that needs protection
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id exists in session
        user_id = session.get('user_id')
        
        if not user_id:
            # No user_id in session - redirect to login
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Verify session is still valid
        session_result = verify_user_session(user_id)
        
        if not session_result['valid']:
            # Session is invalid - clear and redirect to login
            session.clear()
            flash('Your session has expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Authentication successful - call original function
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Get current authenticated user information from session.
    
    This utility function retrieves the current user's information
    from the session. It's used by other routes that need access
    to the current user's data.
    
    Returns:
        Dict[str, any]: Current user data from session, or None if not authenticated
    
    Example:
        >>> user = get_current_user()
        >>> if user:
        ...     print(f"Current user: {user['username']}")
        ... else:
        ...     print("No user logged in")
    
    Notes:
        - Returns None if no user is authenticated
        - Does not verify session validity (use require_authentication for that)
        - Provides quick access to session user data
        - Used by templates and other route functions
    """
    # Check if user is authenticated
    user_id = session.get('user_id')
    
    if not user_id:
        return None
    
    # Return user data from session
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'company_name': session.get('company_name'),
        'website_url': session.get('website_url')
    }


# Template context processor to make current user available in all templates
@auth_bp.app_context_processor
def inject_current_user():
    """
    Inject current user data into all template contexts.
    
    This context processor makes the current user information
    available in all templates without explicitly passing it
    from each route function.
    
    Returns:
        Dict[str, any]: Dictionary with current_user key
    
    Template Usage:
        {% if current_user %}
            Welcome, {{ current_user.username }}!
        {% else %}
            Please log in.
        {% endif %}
    
    Notes:
        - Automatically available in all templates
        - Returns None if no user is authenticated
        - Reduces code duplication across routes
        - Enables consistent user display in templates
    """
    return {
        'current_user': get_current_user()
    }


# Error handlers for authentication-related errors
@auth_bp.errorhandler(401)
def unauthorized(error):
    """
    Handle 401 Unauthorized errors.
    
    This error handler provides a consistent response for
    authentication failures and unauthorized access attempts.
    
    Args:
        error: The 401 error object
    
    Returns:
        Rendered error template or redirect to login
    
    Notes:
        - Provides user-friendly error message
        - Redirects to login for web requests
        - Returns JSON for API requests
    """
    # Check if this is an API request
    if request.is_json or request.path.startswith('/api/'):
        return {'error': 'Authentication required'}, 401
    
    # Web request - redirect to login
    flash('Please log in to access this page', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.errorhandler(403)
def forbidden(error):
    """
    Handle 403 Forbidden errors.
    
    This error handler provides a consistent response for
    access denied situations where user is authenticated
    but doesn't have permission.
    
    Args:
        error: The 403 error object
    
    Returns:
        Rendered error template with appropriate message
    
    Notes:
        - User is authenticated but lacks permission
        - Provides clear error message
        - Suggests appropriate action
    """
    # Check if this is an API request
    if request.is_json or request.path.startswith('/api/'):
        return {'error': 'Access denied'}, 403
    
    # Web request - show error page
    flash('You do not have permission to access this resource', 'error')
    return render_template('error.html', 
                         error_code=403, 
                         error_message='Access Denied'), 403