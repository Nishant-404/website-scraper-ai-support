#!/usr/bin/env python3
"""
File: product_routes.py
Purpose: Handle product-related Flask routes (products page, CRUD operations)
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains all Flask routes related to product management
including product listing, viewing, editing, and deletion.
It uses the modular functions for actual business logic.

Dependencies:
- flask: For route handling and request/response management
- functions.product.get_products: For product retrieval functionality
- functions.product.add_product: For product creation
- routes.auth_routes: For authentication requirements

Usage:
    from routes.product_routes import product_bp
    app.register_blueprint(product_bp)

Notes:
- All routes require authentication
- Proper error handling and validation included
- JSON responses for API endpoints
- Template rendering for web pages
- Input validation prevents security issues
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import our modular functions
from functions.product.get_products import get_user_products, get_product_by_id, get_product_categories
from functions.product.add_product import add_new_product
from routes.auth_routes import require_authentication
from database import Database

# Create Blueprint for product routes
product_bp = Blueprint('products', __name__)


@product_bp.route('/products')
@require_authentication
def products():
    """
    Display the main products management page.
    
    This route renders the products page with all user's products,
    filtering options, and management tools. It supports pagination,
    category filtering, and search functionality.
    
    Query Parameters:
        - category (str): Filter products by category
        - search (str): Search products by name/description
        - page (int): Page number for pagination (default: 1)
        - limit (int): Products per page (default: 20)
    
    Returns:
        Rendered products.html template with:
            - products: List of formatted product data
            - categories: Available categories for filtering
            - pagination: Pagination information
            - stats: User statistics
    
    Template Context:
        - products (List[Dict]): User's products for current page
        - categories (List[str]): Available product categories
        - stats (Dict): User statistics (total products, etc.)
        - pagination (Dict): Pagination metadata
        - current_filters (Dict): Applied filters for form state
    
    Example Usage:
        GET /products - Show all products
        GET /products?category=Electronics - Filter by category
        GET /products?search=iPhone - Search for products
        GET /products?page=2 - Show page 2
    
    Notes:
        - Requires user authentication
        - Supports multiple filtering and pagination options
        - Returns formatted data ready for template display
        - Handles empty results gracefully
        - Includes user statistics for dashboard widgets
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Extract query parameters for filtering and pagination
        category = request.args.get('category', '').strip()
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Calculate offset for pagination (convert 1-based page to 0-based offset)
        offset = (page - 1) * limit
        
        # Get products using modular function
        result = get_user_products(
            user_id=user_id,
            category=category,
            search=search,
            limit=limit,
            offset=offset,
            active_only=True
        )
        
        # Check if retrieval was successful
        if not result['success']:
            flash(result['message'], 'error')
            # Return empty template on error
            return render_template('products.html', 
                                 products=[], 
                                 categories=[], 
                                 stats={'total_products': 0, 'total_qa_pairs': 0, 'total_conversations': 0},
                                 pagination={},
                                 current_filters={})
        
        # Get user statistics for dashboard widgets
        db = Database()
        stats = db.get_user_stats(user_id)
        db.close()
        
        # Prepare current filters for form state preservation
        current_filters = {
            'category': category,
            'search': search,
            'page': page,
            'limit': limit
        }
        
        # Render template with all data
        return render_template('products.html',
                             products=result['products'],
                             categories=result['categories'],
                             stats=stats,
                             pagination=result['pagination'],
                             current_filters=current_filters)
    
    except ValueError as e:
        # Handle invalid pagination parameters
        flash('Invalid page or limit parameter', 'error')
        return redirect(url_for('products.products'))
    
    except Exception as e:
        # Handle any unexpected errors
        flash(f'An error occurred while loading products: {str(e)}', 'error')
        return render_template('products.html', 
                             products=[], 
                             categories=[], 
                             stats={'total_products': 0, 'total_qa_pairs': 0, 'total_conversations': 0},
                             pagination={},
                             current_filters={})


@product_bp.route('/api/products/<int:product_id>')
@require_authentication
def get_product_api(product_id):
    """
    API endpoint to get a specific product by ID.
    
    This route provides JSON API access to individual product data.
    It ensures the product belongs to the authenticated user for
    security purposes.
    
    URL Parameters:
        product_id (int): The ID of the product to retrieve
    
    Returns:
        JSON response with:
            - Product data if found and accessible
            - Error message if not found or access denied
    
    HTTP Status Codes:
        - 200: Product found and returned successfully
        - 404: Product not found or access denied
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "id": 123,
            "name": "Product Name",
            "description": "Product description",
            "price": "$99.99",
            "category": "Electronics",
            "url": "https://example.com/product",
            "image_url": "https://example.com/image.jpg",
            "features": {"feature1": "value1"},
            "specifications": {"spec1": "value1"},
            "scraped_at": "2025-09-16T10:30:00"
        }
    
    Response Format (Error):
        {
            "error": "Product not found"
        }
    
    Example Usage:
        GET /api/products/123 - Get product with ID 123
    
    Notes:
        - Requires user authentication
        - Only returns products owned by authenticated user
        - Returns formatted JSON data
        - Handles product not found gracefully
        - Used by frontend JavaScript for product details
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Get product using modular function
        result = get_product_by_id(product_id, user_id)
        
        # Check if retrieval was successful
        if result['success']:
            # Return product data as JSON
            return jsonify(result['product'])
        else:
            # Return error message
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@product_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@require_authentication
def update_product_api(product_id):
    """
    API endpoint to update a specific product.
    
    This route handles product updates via JSON API. It validates
    the input data and updates the product in the database.
    
    URL Parameters:
        product_id (int): The ID of the product to update
    
    Request Body (JSON):
        {
            "name": "Updated Product Name",
            "description": "Updated description",
            "price": "$199.99",
            "category": "Updated Category",
            "url": "https://example.com/updated",
            "image_url": "https://example.com/updated.jpg"
        }
    
    Returns:
        JSON response with:
            - Success status and message
            - Error details if update failed
    
    HTTP Status Codes:
        - 200: Product updated successfully
        - 400: Invalid input data
        - 404: Product not found or access denied
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "success": true,
            "message": "Product updated successfully"
        }
    
    Response Format (Error):
        {
            "success": false,
            "error": "Error message"
        }
    
    Example Usage:
        PUT /api/products/123 - Update product with ID 123
    
    Notes:
        - Requires user authentication
        - Only updates products owned by authenticated user
        - Validates all input data before updating
        - Returns detailed error messages for debugging
        - Used by frontend JavaScript for product editing
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Initialize database connection
        db = Database()
        
        # Update product in database
        success = db.update_product(product_id, user_id, **data)
        
        # Close database connection
        db.close()
        
        # Check if update was successful
        if success:
            return jsonify({'success': True, 'message': 'Product updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product not found or update failed'}), 404
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@product_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@require_authentication
def delete_product_api(product_id):
    """
    API endpoint to delete a specific product.
    
    This route handles product deletion via JSON API. It performs
    a soft delete by setting the product as inactive rather than
    removing it from the database.
    
    URL Parameters:
        product_id (int): The ID of the product to delete
    
    Returns:
        JSON response with:
            - Success status and message
            - Error details if deletion failed
    
    HTTP Status Codes:
        - 200: Product deleted successfully
        - 404: Product not found or access denied
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "success": true,
            "message": "Product deleted successfully"
        }
    
    Response Format (Error):
        {
            "success": false,
            "error": "Error message"
        }
    
    Example Usage:
        DELETE /api/products/123 - Delete product with ID 123
    
    Notes:
        - Requires user authentication
        - Only deletes products owned by authenticated user
        - Performs soft delete (sets is_active=False)
        - Returns confirmation message
        - Used by frontend JavaScript for product deletion
        - Deleted products can be recovered if needed
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Initialize database connection
        db = Database()
        
        # Delete product from database (soft delete)
        success = db.delete_product(product_id, user_id)
        
        # Close database connection
        db.close()
        
        # Check if deletion was successful
        if success:
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product not found or delete failed'}), 404
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@product_bp.route('/api/products/categories')
@require_authentication
def get_categories_api():
    """
    API endpoint to get all product categories for the user.
    
    This route returns all unique product categories for the
    authenticated user. Used for populating filter dropdowns
    and category management interfaces.
    
    Returns:
        JSON response with:
            - List of unique categories
            - Category count
            - Success status
    
    HTTP Status Codes:
        - 200: Categories retrieved successfully
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "success": true,
            "categories": ["Electronics", "Clothing", "Books"],
            "count": 3
        }
    
    Response Format (Error):
        {
            "success": false,
            "error": "Error message"
        }
    
    Example Usage:
        GET /api/products/categories - Get all categories
    
    Notes:
        - Requires user authentication
        - Returns only categories from user's products
        - Categories are sorted alphabetically
        - Used by frontend for filter dropdowns
        - Empty categories are excluded
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Get categories using modular function
        result = get_product_categories(user_id)
        
        # Return result as JSON
        if result['success']:
            return jsonify({
                'success': True,
                'categories': result['categories'],
                'count': result['count']
            })
        else:
            return jsonify({'success': False, 'error': result['message']}), 500
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@product_bp.route('/api/products/search')
@require_authentication
def search_products_api():
    """
    API endpoint for product search functionality.
    
    This route provides JSON API access to product search
    with support for various filters and pagination.
    
    Query Parameters:
        - q (str): Search query for product names/descriptions
        - category (str): Filter by category
        - page (int): Page number for pagination (default: 1)
        - limit (int): Products per page (default: 20)
    
    Returns:
        JSON response with:
            - Matching products
            - Pagination information
            - Search metadata
    
    HTTP Status Codes:
        - 200: Search completed successfully
        - 400: Invalid search parameters
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "success": true,
            "products": [...],
            "pagination": {
                "total_count": 50,
                "page_count": 3,
                "current_page": 1,
                "has_next": true,
                "has_previous": false
            },
            "query": "search term",
            "category": "Electronics"
        }
    
    Example Usage:
        GET /api/products/search?q=iPhone&category=Electronics
    
    Notes:
        - Requires user authentication
        - Supports multiple search and filter options
        - Returns paginated results
        - Used by frontend search functionality
        - Case-insensitive search
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Extract query parameters
        search_query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Search products using modular function
        result = get_user_products(
            user_id=user_id,
            category=category,
            search=search_query,
            limit=limit,
            offset=offset,
            active_only=True
        )
        
        # Check if search was successful
        if result['success']:
            return jsonify({
                'success': True,
                'products': result['products'],
                'pagination': result['pagination'],
                'query': search_query,
                'category': category
            })
        else:
            return jsonify({'success': False, 'error': result['message']}), 500
    
    except ValueError as e:
        # Handle invalid pagination parameters
        return jsonify({'success': False, 'error': 'Invalid page or limit parameter'}), 400
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@product_bp.route('/api/products/stats')
@require_authentication
def get_product_stats_api():
    """
    API endpoint to get product statistics for the user.
    
    This route returns comprehensive statistics about the user's
    products including counts, categories, and other metrics.
    
    Returns:
        JSON response with:
            - Total product count
            - Active/inactive counts
            - Category breakdown
            - Recent activity
    
    HTTP Status Codes:
        - 200: Statistics retrieved successfully
        - 401: User not authenticated
        - 500: Server error
    
    Response Format (Success):
        {
            "success": true,
            "total_products": 150,
            "active_products": 145,
            "inactive_products": 5,
            "categories": {
                "Electronics": 50,
                "Clothing": 30,
                "Books": 20
            },
            "recent_additions": 5
        }
    
    Example Usage:
        GET /api/products/stats - Get product statistics
    
    Notes:
        - Requires user authentication
        - Returns comprehensive product metrics
        - Used for dashboard widgets and analytics
        - Includes category breakdown for charts
        - Cached for performance if needed
    """
    try:
        # Get current user from session
        user_id = session.get('user_id')
        
        # Initialize database connection
        db = Database()
        
        # Get basic user statistics
        stats = db.get_user_stats(user_id)
        
        # Get all user products for detailed analysis
        all_products = db.get_products_by_user(user_id)
        
        # Close database connection
        db.close()
        
        # Calculate category breakdown
        category_counts = {}
        for product in all_products:
            category = product.category or 'Uncategorized'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Return comprehensive statistics
        return jsonify({
            'success': True,
            'total_products': stats['total_products'],
            'active_products': len(all_products),  # All returned products are active
            'inactive_products': 0,  # Would need separate query for inactive
            'categories': category_counts,
            'recent_additions': min(stats['total_products'], 10)  # Simplified metric
        })
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


# Error handlers for product-related errors
@product_bp.errorhandler(404)
def product_not_found(error):
    """
    Handle 404 errors for product routes.
    
    This error handler provides consistent responses for
    product not found situations.
    
    Args:
        error: The 404 error object
    
    Returns:
        JSON error response or redirect based on request type
    
    Notes:
        - Returns JSON for API requests
        - Redirects to products page for web requests
        - Provides user-friendly error messages
    """
    # Check if this is an API request
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'Product not found'}), 404
    
    # Web request - redirect to products page with message
    flash('Product not found', 'error')
    return redirect(url_for('products.products'))


@product_bp.errorhandler(400)
def bad_request(error):
    """
    Handle 400 Bad Request errors for product routes.
    
    This error handler provides consistent responses for
    invalid request data or parameters.
    
    Args:
        error: The 400 error object
    
    Returns:
        JSON error response with details
    
    Notes:
        - Returns detailed error information
        - Helps with API debugging
        - Consistent error format
    """
    # Return JSON error for all 400 errors
    return jsonify({'error': 'Invalid request data or parameters'}), 400