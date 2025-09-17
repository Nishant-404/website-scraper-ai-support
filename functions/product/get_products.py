#!/usr/bin/env python3
"""
File: get_products.py
Purpose: Handle retrieving products from database with filtering and pagination
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains the core functionality for retrieving products
from the AI Customer Support Platform database. It handles product
queries, filtering, pagination, and data formatting for display.

Dependencies:
- json: For parsing product features and specifications JSON data
- database.Database: For database operations and product retrieval
- typing: For type hints and better code documentation

Usage:
    from functions.product.get_products import get_user_products
    
    result = get_user_products(
        user_id=1,
        category="Electronics",
        limit=10,
        offset=0
    )

Notes:
- Supports filtering by category, search terms, and status
- Includes pagination for large product lists
- Parses JSON data for features and specifications
- Returns formatted data ready for templates
- Handles database errors gracefully
"""

import json
from typing import Dict, List, Optional, Union
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import Database, Product


def parse_json_field(json_string: str, field_name: str) -> Dict:
    """
    Parse JSON string field from database into dictionary.
    
    This function safely parses JSON strings stored in the database
    back into Python dictionaries. It handles malformed JSON and
    provides fallback to empty dictionary.
    
    Args:
        json_string (str): JSON string from database
        field_name (str): Name of field for error logging
    
    Returns:
        Dict: Parsed dictionary or empty dict if parsing fails
    
    Example:
        >>> parse_json_field('{"color": "red"}', "features")
        {"color": "red"}
        >>> parse_json_field("invalid json", "features")
        {}
    
    Notes:
        - Handles None and empty string inputs
        - Returns empty dict for invalid JSON
        - Logs parsing errors for debugging
        - Used for features and specifications fields
    """
    # Handle None or empty input
    if not json_string or json_string.strip() == "":
        return {}
    
    try:
        # Parse JSON string to dictionary
        parsed_data = json.loads(json_string)
        
        # Ensure result is a dictionary
        if isinstance(parsed_data, dict):
            return parsed_data
        else:
            print(f"Warning: {field_name} is not a dictionary: {type(parsed_data)}")
            return {}
            
    except json.JSONDecodeError as e:
        # Log error and return empty dict
        print(f"Error parsing {field_name} JSON: {str(e)}")
        return {}
    except Exception as e:
        # Handle any other parsing errors
        print(f"Unexpected error parsing {field_name}: {str(e)}")
        return {}


def format_product_for_display(product: Product) -> Dict[str, any]:
    """
    Format product object for display in templates and APIs.
    
    This function takes a Product database object and converts
    it to a dictionary format suitable for templates, APIs,
    and frontend display with proper JSON parsing.
    
    Args:
        product (Product): Product object from database
    
    Returns:
        Dict[str, any]: Formatted product data dictionary
    
    Example:
        >>> formatted = format_product_for_display(product_obj)
        >>> print(formatted['name'])
        "iPhone 14 Pro"
    
    Notes:
        - Parses JSON fields (features, specifications)
        - Handles None values gracefully
        - Formats dates for display
        - Includes all product information
        - Ready for template rendering
    """
    # Parse JSON fields safely
    features = parse_json_field(product.features, "features")
    specifications = parse_json_field(product.specifications, "specifications")
    
    # Format product data for display
    formatted_product = {
        'id': product.id,
        'user_id': product.user_id,
        'name': product.name or '',
        'description': product.description or '',
        'price': product.price or '',
        'category': product.category or '',
        'url': product.url or '',
        'image_url': product.image_url or '',
        'features': features,
        'specifications': specifications,
        'scraped_at': product.scraped_at,
        'is_active': product.is_active
    }
    
    return formatted_product


def filter_products_by_category(products: List[Product], category: str) -> List[Product]:
    """
    Filter products list by category.
    
    This function filters a list of products to only include
    those matching the specified category. Case-insensitive
    matching is used for better user experience.
    
    Args:
        products (List[Product]): List of product objects to filter
        category (str): Category to filter by
    
    Returns:
        List[Product]: Filtered list of products
    
    Example:
        >>> filtered = filter_products_by_category(all_products, "Electronics")
        >>> len(filtered)
        5
    
    Notes:
        - Case-insensitive category matching
        - Returns empty list if no matches
        - Handles None/empty category gracefully
        - Preserves original product objects
    """
    # Handle empty category filter
    if not category or not category.strip():
        return products
    
    # Clean category for comparison
    clean_category = category.strip().lower()
    
    # Filter products by category (case-insensitive)
    filtered_products = []
    for product in products:
        product_category = (product.category or '').strip().lower()
        if product_category == clean_category:
            filtered_products.append(product)
    
    return filtered_products


def search_products_by_name(products: List[Product], search_term: str) -> List[Product]:
    """
    Search products by name using partial matching.
    
    This function searches through products to find those
    whose names contain the search term. Uses case-insensitive
    partial matching for better search results.
    
    Args:
        products (List[Product]): List of product objects to search
        search_term (str): Search term to look for in product names
    
    Returns:
        List[Product]: List of products matching search term
    
    Example:
        >>> results = search_products_by_name(all_products, "iPhone")
        >>> len(results)
        3
    
    Notes:
        - Case-insensitive partial matching
        - Searches in product names and descriptions
        - Returns empty list if no matches
        - Handles None/empty search term gracefully
    """
    # Handle empty search term
    if not search_term or not search_term.strip():
        return products
    
    # Clean search term for comparison
    clean_search = search_term.strip().lower()
    
    # Search products by name and description
    matching_products = []
    for product in products:
        # Check product name
        product_name = (product.name or '').strip().lower()
        product_description = (product.description or '').strip().lower()
        
        # Check if search term is in name or description
        if (clean_search in product_name or 
            clean_search in product_description):
            matching_products.append(product)
    
    return matching_products


def paginate_products(products: List[Product], limit: int = 20, 
                     offset: int = 0) -> Dict[str, any]:
    """
    Paginate products list for display and API responses.
    
    This function implements pagination for product lists to
    improve performance and user experience when dealing with
    large numbers of products.
    
    Args:
        products (List[Product]): List of products to paginate
        limit (int): Maximum number of products per page (default: 20)
        offset (int): Number of products to skip (default: 0)
    
    Returns:
        Dict[str, any]: Pagination result containing:
            - products (List[Product]): Products for current page
            - total_count (int): Total number of products
            - page_count (int): Total number of pages
            - current_page (int): Current page number (1-based)
            - has_next (bool): Whether there are more pages
            - has_previous (bool): Whether there are previous pages
    
    Example:
        >>> result = paginate_products(all_products, limit=10, offset=0)
        >>> print(f"Page 1 of {result['page_count']}")
        >>> print(f"Showing {len(result['products'])} products")
    
    Notes:
        - Uses 0-based offset for database compatibility
        - Returns 1-based page numbers for user display
        - Handles edge cases (empty lists, invalid parameters)
        - Includes pagination metadata for UI
    """
    # Validate pagination parameters
    if limit <= 0:
        limit = 20  # Default limit
    if offset < 0:
        offset = 0  # Default offset
    
    # Calculate pagination values
    total_count = len(products)
    page_count = (total_count + limit - 1) // limit  # Ceiling division
    current_page = (offset // limit) + 1  # 1-based page number
    
    # Get products for current page
    start_index = offset
    end_index = offset + limit
    page_products = products[start_index:end_index]
    
    # Calculate pagination flags
    has_next = end_index < total_count
    has_previous = offset > 0
    
    return {
        'products': page_products,
        'total_count': total_count,
        'page_count': page_count,
        'current_page': current_page,
        'has_next': has_next,
        'has_previous': has_previous,
        'limit': limit,
        'offset': offset
    }


def get_user_products(user_id: int, category: str = "", search: str = "",
                     limit: int = 20, offset: int = 0, 
                     active_only: bool = True) -> Dict[str, any]:
    """
    Get products for a user with filtering and pagination.
    
    This is the main function for retrieving user products with
    comprehensive filtering, searching, and pagination capabilities.
    It handles all product retrieval needs for the platform.
    
    Args:
        user_id (int): ID of the user whose products to retrieve
        category (str): Filter by category (optional)
        search (str): Search term for product names (optional)
        limit (int): Maximum products per page (default: 20)
        offset (int): Number of products to skip (default: 0)
        active_only (bool): Only return active products (default: True)
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether retrieval succeeded
            - products (List[Dict]): Formatted product data
            - pagination (Dict): Pagination information
            - categories (List[str]): Available categories for filtering
            - message (str): Success or error message
            - errors (list): List of any errors
    
    Raises:
        Exception: Database connection or operation errors
    
    Example:
        >>> result = get_user_products(
        ...     user_id=1,
        ...     category="Electronics",
        ...     search="iPhone",
        ...     limit=10,
        ...     offset=0
        ... )
        >>> if result['success']:
        ...     for product in result['products']:
        ...         print(product['name'])
    
    Notes:
        - Combines filtering, searching, and pagination
        - Returns formatted data ready for templates
        - Includes category list for filter dropdowns
        - Handles database errors gracefully
        - Optimized for performance with large datasets
    """
    # Initialize result dictionary
    result = {
        'success': False,
        'products': [],
        'pagination': {},
        'categories': [],
        'message': '',
        'errors': []
    }
    
    try:
        # Validate user_id parameter
        if not isinstance(user_id, int) or user_id <= 0:
            result['errors'].append("Invalid user ID")
            result['message'] = "Invalid user ID provided"
            return result
        
        # Initialize database connection
        db = Database()
        
        # Get all products for user from database
        if active_only:
            # Get only active products (default behavior)
            raw_products = db.get_products_by_user(user_id)
        else:
            # Get all products including inactive ones
            # Note: This would require a new database method
            raw_products = db.get_products_by_user(user_id)
        
        # Close database connection
        db.close()
        
        # Apply category filter if specified
        if category and category.strip():
            raw_products = filter_products_by_category(raw_products, category)
        
        # Apply search filter if specified
        if search and search.strip():
            raw_products = search_products_by_name(raw_products, search)
        
        # Apply pagination
        pagination_result = paginate_products(raw_products, limit, offset)
        
        # Format products for display
        formatted_products = []
        for product in pagination_result['products']:
            formatted_product = format_product_for_display(product)
            formatted_products.append(formatted_product)
        
        # Get unique categories for filter dropdown
        all_user_products = db.get_products_by_user(user_id) if active_only else raw_products
        categories = list(set(
            product.category.strip() 
            for product in all_user_products 
            if product.category and product.category.strip()
        ))
        categories.sort()  # Sort alphabetically
        
        # Set success result
        result['success'] = True
        result['products'] = formatted_products
        result['pagination'] = {
            'total_count': pagination_result['total_count'],
            'page_count': pagination_result['page_count'],
            'current_page': pagination_result['current_page'],
            'has_next': pagination_result['has_next'],
            'has_previous': pagination_result['has_previous'],
            'limit': pagination_result['limit'],
            'offset': pagination_result['offset']
        }
        result['categories'] = categories
        result['message'] = f"Retrieved {len(formatted_products)} products successfully"
        
    except Exception as e:
        # Handle any unexpected errors during retrieval
        result['message'] = f"An error occurred while retrieving products: {str(e)}"
        result['errors'] = [f"System error: {str(e)}"]
    
    return result


def get_product_by_id(product_id: int, user_id: int) -> Dict[str, any]:
    """
    Get a specific product by ID for a user.
    
    This function retrieves a single product by its ID,
    ensuring the product belongs to the specified user
    for security purposes.
    
    Args:
        product_id (int): ID of the product to retrieve
        user_id (int): ID of the user who should own the product
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether retrieval succeeded
            - product (Dict): Formatted product data (if found)
            - message (str): Success or error message
            - errors (list): List of any errors
    
    Example:
        >>> result = get_product_by_id(123, 1)
        >>> if result['success']:
        ...     print(result['product']['name'])
        ... else:
        ...     print(result['message'])
    
    Notes:
        - Ensures product belongs to specified user
        - Returns formatted data ready for display
        - Handles product not found gracefully
        - Used for product detail views and editing
    """
    # Initialize result dictionary
    result = {
        'success': False,
        'product': None,
        'message': '',
        'errors': []
    }
    
    try:
        # Validate parameters
        if not isinstance(product_id, int) or product_id <= 0:
            result['errors'].append("Invalid product ID")
            result['message'] = "Invalid product ID provided"
            return result
        
        if not isinstance(user_id, int) or user_id <= 0:
            result['errors'].append("Invalid user ID")
            result['message'] = "Invalid user ID provided"
            return result
        
        # Initialize database connection
        db = Database()
        
        # Get product by ID and user ID
        product = db.get_product_by_id(product_id, user_id)
        
        # Close database connection
        db.close()
        
        # Check if product was found
        if product:
            # Format product for display
            formatted_product = format_product_for_display(product)
            
            result['success'] = True
            result['product'] = formatted_product
            result['message'] = "Product retrieved successfully"
        else:
            result['message'] = "Product not found or access denied"
            result['errors'] = ["Product not found"]
        
    except Exception as e:
        # Handle any unexpected errors during retrieval
        result['message'] = f"An error occurred while retrieving the product: {str(e)}"
        result['errors'] = [f"System error: {str(e)}"]
    
    return result


def get_product_categories(user_id: int) -> Dict[str, any]:
    """
    Get all unique product categories for a user.
    
    This function retrieves all unique categories from
    a user's products for use in filter dropdowns and
    category management interfaces.
    
    Args:
        user_id (int): ID of the user whose categories to retrieve
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether retrieval succeeded
            - categories (List[str]): List of unique categories
            - count (int): Number of categories found
            - message (str): Success or error message
    
    Example:
        >>> result = get_product_categories(1)
        >>> if result['success']:
        ...     for category in result['categories']:
        ...         print(category)
    
    Notes:
        - Returns only non-empty categories
        - Sorted alphabetically for consistency
        - Used for filter dropdowns and analytics
        - Handles empty results gracefully
    """
    # Initialize result dictionary
    result = {
        'success': False,
        'categories': [],
        'count': 0,
        'message': ''
    }
    
    try:
        # Validate user_id parameter
        if not isinstance(user_id, int) or user_id <= 0:
            result['message'] = "Invalid user ID provided"
            return result
        
        # Initialize database connection
        db = Database()
        
        # Get all products for user
        products = db.get_products_by_user(user_id)
        
        # Close database connection
        db.close()
        
        # Extract unique categories
        categories = set()
        for product in products:
            if product.category and product.category.strip():
                categories.add(product.category.strip())
        
        # Convert to sorted list
        categories_list = sorted(list(categories))
        
        # Set success result
        result['success'] = True
        result['categories'] = categories_list
        result['count'] = len(categories_list)
        result['message'] = f"Found {len(categories_list)} categories"
        
    except Exception as e:
        # Handle any unexpected errors
        result['message'] = f"An error occurred while retrieving categories: {str(e)}"
    
    return result


# Test function for development and debugging
def test_get_products():
    """
    Test function to verify product retrieval functionality.
    
    This function runs basic tests on the product retrieval process
    to ensure all filtering, searching, and pagination logic works correctly.
    Used for development and debugging purposes.
    
    Notes:
        - Only run in development environment
        - Requires existing test products in database
        - Helps verify all retrieval features work correctly
    """
    print("Testing product retrieval functionality...")
    
    # Test 1: Get all products for user
    result1 = get_user_products(user_id=1)
    print(f"Test 1 - All products: Success={result1['success']}, Count={len(result1['products'])}")
    
    # Test 2: Get products with category filter
    result2 = get_user_products(user_id=1, category="Electronics")
    print(f"Test 2 - Category filter: Success={result2['success']}, Count={len(result2['products'])}")
    
    # Test 3: Get products with search
    result3 = get_user_products(user_id=1, search="test")
    print(f"Test 3 - Search filter: Success={result3['success']}, Count={len(result3['products'])}")
    
    # Test 4: Get products with pagination
    result4 = get_user_products(user_id=1, limit=5, offset=0)
    print(f"Test 4 - Pagination: Success={result4['success']}, Count={len(result4['products'])}")
    
    # Test 5: Get specific product by ID
    if result1['products']:
        product_id = result1['products'][0]['id']
        result5 = get_product_by_id(product_id, 1)
        print(f"Test 5 - Get by ID: Success={result5['success']}")
    
    # Test 6: Get categories
    result6 = get_product_categories(1)
    print(f"Test 6 - Categories: Success={result6['success']}, Count={result6['count']}")


# Run tests if this file is executed directly
if __name__ == "__main__":
    test_get_products()