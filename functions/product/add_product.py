#!/usr/bin/env python3
"""
File: add_product.py
Purpose: Handle adding new products to the database with validation
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains the core functionality for adding new products
to the AI Customer Support Platform database. It handles product
data validation, JSON formatting, and secure database storage.

Dependencies:
- json: For handling product features and specifications as JSON
- database.Database: For database operations and product storage
- typing: For type hints and better code documentation
- re: For URL and data validation using regex patterns

Usage:
    from functions.product.add_product import add_new_product
    
    result = add_new_product(
        user_id=1,
        name="Product Name",
        description="Product description",
        price="$99.99",
        category="Electronics",
        url="https://example.com/product",
        image_url="https://example.com/image.jpg",
        features={"feature1": "value1"},
        specifications={"spec1": "value1"}
    )

Notes:
- All product data is validated before storage
- Features and specifications are stored as JSON
- Products are active by default (is_active=True)
- Supports both required and optional fields
- Returns detailed success/error information
"""

import json
import re
from typing import Dict, Optional, Union, List
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import Database


def validate_product_name(name: str) -> Tuple[bool, str]:
    """
    Validate product name for length and content requirements.
    
    This function checks if the product name meets the platform's
    requirements for length, content, and format. Product names
    are essential for search and display functionality.
    
    Args:
        name (str): The product name to validate
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if name is valid, False otherwise
            - error_message: Description of validation failure
    
    Example:
        >>> validate_product_name("iPhone 14 Pro")
        (True, "")
        >>> validate_product_name("")
        (False, "Product name is required")
    
    Notes:
        - Minimum 2 characters, maximum 200 characters
        - Cannot be empty or whitespace only
        - Allows letters, numbers, spaces, and common symbols
    """
    # Check if name is provided and not empty
    if not name or not name.strip():
        return False, "Product name is required"
    
    # Clean the name for validation
    clean_name = name.strip()
    
    # Check minimum length (2 characters)
    if len(clean_name) < 2:
        return False, "Product name must be at least 2 characters long"
    
    # Check maximum length (200 characters)
    if len(clean_name) > 200:
        return False, "Product name must be less than 200 characters"
    
    # Check for valid characters (letters, numbers, spaces, common symbols)
    if not re.match(r'^[a-zA-Z0-9\s\-_.,()&+/]+$', clean_name):
        return False, "Product name contains invalid characters"
    
    # Name is valid
    return True, ""


def validate_product_url(url: str) -> Tuple[bool, str]:
    """
    Validate product URL format and structure.
    
    This function checks if the provided product URL is properly
    formatted and follows standard URL conventions. The URL is
    used for linking back to the original product page.
    
    Args:
        url (str): The product URL to validate
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if URL is valid, False otherwise
            - error_message: Description of validation failure
    
    Example:
        >>> validate_product_url("https://example.com/product/123")
        (True, "")
        >>> validate_product_url("invalid-url")
        (False, "Invalid URL format")
    
    Notes:
        - URL is optional, but if provided must be valid
        - Accepts both HTTP and HTTPS protocols
        - Validates domain name structure
        - Does not check actual URL accessibility
    """
    # URL is optional, so empty is valid
    if not url or not url.strip():
        return True, ""
    
    # Clean the URL for validation
    clean_url = url.strip()
    
    # URL validation regex pattern
    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/.*)?$'
    
    # Check if URL matches the pattern
    if not re.match(url_pattern, clean_url):
        return False, "Invalid URL format. Please use format: https://example.com/product"
    
    # Check URL length (reasonable limit)
    if len(clean_url) > 500:
        return False, "URL is too long (maximum 500 characters)"
    
    # URL is valid
    return True, ""


def validate_product_price(price: str) -> Tuple[bool, str]:
    """
    Validate product price format and content.
    
    This function checks if the product price is in a valid
    format. Price can be in various formats including currency
    symbols, decimal numbers, or text descriptions.
    
    Args:
        price (str): The product price to validate
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if price is valid, False otherwise
            - error_message: Description of validation failure
    
    Example:
        >>> validate_product_price("$99.99")
        (True, "")
        >>> validate_product_price("Free")
        (True, "")
        >>> validate_product_price("A" * 101)
        (False, "Price is too long (maximum 100 characters)")
    
    Notes:
        - Price is optional field
        - Accepts various formats: $99.99, 99.99, Free, etc.
        - Maximum 100 characters allowed
        - No strict format enforcement for flexibility
    """
    # Price is optional, so empty is valid
    if not price or not price.strip():
        return True, ""
    
    # Clean the price for validation
    clean_price = price.strip()
    
    # Check maximum length (100 characters)
    if len(clean_price) > 100:
        return False, "Price is too long (maximum 100 characters)"
    
    # Price is valid (flexible format)
    return True, ""


def validate_json_data(data: Union[Dict, str], field_name: str) -> Tuple[bool, str, Dict]:
    """
    Validate and convert JSON data for features or specifications.
    
    This function handles JSON data validation and conversion
    for product features and specifications. It accepts both
    dictionary objects and JSON strings.
    
    Args:
        data (Union[Dict, str]): The JSON data to validate
        field_name (str): Name of the field for error messages
    
    Returns:
        Tuple[bool, str, Dict]: (is_valid, error_message, parsed_data)
            - is_valid: True if data is valid JSON
            - error_message: Description of validation failure
            - parsed_data: Parsed dictionary object
    
    Example:
        >>> validate_json_data({"key": "value"}, "features")
        (True, "", {"key": "value"})
        >>> validate_json_data('{"key": "value"}', "features")
        (True, "", {"key": "value"})
        >>> validate_json_data("invalid json", "features")
        (False, "Invalid JSON format for features", {})
    
    Notes:
        - Accepts both dict and string inputs
        - Validates JSON structure
        - Returns parsed dictionary for storage
        - Handles empty or None inputs gracefully
    """
    # Handle None or empty data
    if data is None:
        return True, "", {}
    
    # If data is already a dictionary, validate it
    if isinstance(data, dict):
        try:
            # Test if dictionary can be serialized to JSON
            json.dumps(data)
            return True, "", data
        except (TypeError, ValueError) as e:
            return False, f"Invalid data structure for {field_name}: {str(e)}", {}
    
    # If data is a string, try to parse as JSON
    if isinstance(data, str):
        # Empty string is valid (becomes empty dict)
        if not data.strip():
            return True, "", {}
        
        try:
            # Parse JSON string
            parsed_data = json.loads(data.strip())
            
            # Ensure parsed data is a dictionary
            if not isinstance(parsed_data, dict):
                return False, f"{field_name} must be a JSON object (dictionary)", {}
            
            return True, "", parsed_data
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format for {field_name}: {str(e)}", {}
    
    # Invalid data type
    return False, f"{field_name} must be a dictionary or JSON string", {}


def clean_product_data(name: str, description: str, price: str, 
                      category: str, url: str, image_url: str) -> Dict[str, str]:
    """
    Clean and sanitize product data for database storage.
    
    This function takes raw product data and cleans it by
    trimming whitespace, handling None values, and ensuring
    consistent formatting for database storage.
    
    Args:
        name (str): Product name to clean
        description (str): Product description to clean
        price (str): Product price to clean
        category (str): Product category to clean
        url (str): Product URL to clean
        image_url (str): Product image URL to clean
    
    Returns:
        Dict[str, str]: Dictionary of cleaned product data
    
    Example:
        >>> clean_product_data("  Product  ", None, "$99", "", "  url  ", "")
        {
            'name': 'Product',
            'description': '',
            'price': '$99',
            'category': '',
            'url': 'url',
            'image_url': ''
        }
    
    Notes:
        - Converts None values to empty strings
        - Trims whitespace from all fields
        - Ensures consistent data format
        - Handles missing or invalid data gracefully
    """
    return {
        'name': (name or '').strip(),
        'description': (description or '').strip(),
        'price': (price or '').strip(),
        'category': (category or '').strip(),
        'url': (url or '').strip(),
        'image_url': (image_url or '').strip()
    }


def add_new_product(user_id: int, name: str, description: str = "", 
                   price: str = "", category: str = "", url: str = "", 
                   image_url: str = "", features: Union[Dict, str] = None,
                   specifications: Union[Dict, str] = None,
                   is_active: bool = True) -> Dict[str, any]:
    """
    Add a new product to the database with comprehensive validation.
    
    This is the main function for adding products to the platform.
    It performs all necessary validations, processes JSON data,
    and stores the product in the database with proper error handling.
    
    Args:
        user_id (int): ID of the user who owns this product
        name (str): Product name (required, 2-200 characters)
        description (str): Product description (optional)
        price (str): Product price in any format (optional)
        category (str): Product category (optional)
        url (str): Product URL for reference (optional)
        image_url (str): Product image URL (optional)
        features (Union[Dict, str]): Product features as dict or JSON string
        specifications (Union[Dict, str]): Product specs as dict or JSON string
        is_active (bool): Whether product is active (default: True)
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether product was added successfully
            - product_id (int): ID of created product (if successful)
            - message (str): Success or error message
            - errors (list): List of validation errors (if any)
    
    Raises:
        Exception: Database connection or operation errors
    
    Example:
        >>> result = add_new_product(
        ...     user_id=1,
        ...     name="iPhone 14 Pro",
        ...     description="Latest iPhone model",
        ...     price="$999.99",
        ...     category="Electronics",
        ...     url="https://apple.com/iphone-14-pro",
        ...     features={"color": "Space Black", "storage": "128GB"}
        ... )
        >>> print(result['success'])
        True
    
    Notes:
        - All inputs are validated before processing
        - JSON data is properly formatted and stored
        - Database transactions ensure data consistency
        - Detailed error messages help with debugging
        - Products are active by default for immediate use
    """
    # Initialize result dictionary for return value
    result = {
        'success': False,
        'product_id': None,
        'message': '',
        'errors': []
    }
    
    try:
        # Step 1: Validate user_id
        if not isinstance(user_id, int) or user_id <= 0:
            result['errors'].append("Invalid user ID")
            result['message'] = "Invalid user ID provided"
            return result
        
        # Step 2: Validate required fields
        validation_errors = []
        
        # Validate product name (required field)
        is_valid_name, name_error = validate_product_name(name)
        if not is_valid_name:
            validation_errors.append(name_error)
        
        # Validate optional URL if provided
        is_valid_url, url_error = validate_product_url(url)
        if not is_valid_url:
            validation_errors.append(url_error)
        
        # Validate optional image URL if provided
        is_valid_image_url, image_url_error = validate_product_url(image_url)
        if not is_valid_image_url:
            validation_errors.append(f"Image {image_url_error}")
        
        # Validate optional price if provided
        is_valid_price, price_error = validate_product_price(price)
        if not is_valid_price:
            validation_errors.append(price_error)
        
        # If there are validation errors, return them
        if validation_errors:
            result['errors'] = validation_errors
            result['message'] = "Validation failed: " + "; ".join(validation_errors)
            return result
        
        # Step 3: Clean and prepare basic data
        clean_data = clean_product_data(name, description, price, category, url, image_url)
        
        # Step 4: Validate and process JSON data
        # Validate features JSON
        is_valid_features, features_error, clean_features = validate_json_data(features, "features")
        if not is_valid_features:
            result['errors'].append(features_error)
            result['message'] = features_error
            return result
        
        # Validate specifications JSON
        is_valid_specs, specs_error, clean_specs = validate_json_data(specifications, "specifications")
        if not is_valid_specs:
            result['errors'].append(specs_error)
            result['message'] = specs_error
            return result
        
        # Step 5: Convert JSON data to strings for database storage
        features_json = json.dumps(clean_features) if clean_features else "{}"
        specifications_json = json.dumps(clean_specs) if clean_specs else "{}"
        
        # Step 6: Initialize database connection
        db = Database()
        
        # Step 7: Add product to database
        product_id = db.add_product(
            user_id=user_id,
            name=clean_data['name'],
            description=clean_data['description'],
            price=clean_data['price'],
            category=clean_data['category'],
            url=clean_data['url'],
            image_url=clean_data['image_url'],
            features=features_json,
            specifications=specifications_json,
            is_active=is_active
        )
        
        # Step 8: Check if product creation was successful
        if product_id:
            result['success'] = True
            result['product_id'] = product_id
            result['message'] = f"Product '{clean_data['name']}' added successfully!"
        else:
            result['message'] = "Failed to add product to database. Please try again."
            result['errors'] = ["Database operation failed"]
        
        # Close database connection
        db.close()
        
    except Exception as e:
        # Handle any unexpected errors during product creation
        result['message'] = f"An error occurred while adding the product: {str(e)}"
        result['errors'] = [f"System error: {str(e)}"]
    
    return result


def add_multiple_products(user_id: int, products_data: List[Dict]) -> Dict[str, any]:
    """
    Add multiple products to the database in batch operation.
    
    This function allows adding multiple products at once,
    which is useful for bulk imports from web scraping or
    data migration operations.
    
    Args:
        user_id (int): ID of the user who owns these products
        products_data (List[Dict]): List of product dictionaries
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether batch operation succeeded
            - added_count (int): Number of products successfully added
            - failed_count (int): Number of products that failed
            - errors (list): List of errors for failed products
            - product_ids (list): List of created product IDs
    
    Example:
        >>> products = [
        ...     {"name": "Product 1", "price": "$10"},
        ...     {"name": "Product 2", "price": "$20"}
        ... ]
        >>> result = add_multiple_products(1, products)
        >>> print(f"Added {result['added_count']} products")
    
    Notes:
        - Processes products individually for error isolation
        - Continues processing even if some products fail
        - Returns detailed results for each product
        - Useful for bulk import operations
    """
    # Initialize result dictionary
    result = {
        'success': False,
        'added_count': 0,
        'failed_count': 0,
        'errors': [],
        'product_ids': []
    }
    
    try:
        # Validate input parameters
        if not isinstance(user_id, int) or user_id <= 0:
            result['errors'].append("Invalid user ID")
            return result
        
        if not isinstance(products_data, list) or len(products_data) == 0:
            result['errors'].append("Products data must be a non-empty list")
            return result
        
        # Process each product individually
        for i, product_data in enumerate(products_data):
            try:
                # Extract product data with defaults
                name = product_data.get('name', '')
                description = product_data.get('description', '')
                price = product_data.get('price', '')
                category = product_data.get('category', '')
                url = product_data.get('url', '')
                image_url = product_data.get('image_url', '')
                features = product_data.get('features', {})
                specifications = product_data.get('specifications', {})
                is_active = product_data.get('is_active', True)
                
                # Add individual product
                product_result = add_new_product(
                    user_id=user_id,
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    url=url,
                    image_url=image_url,
                    features=features,
                    specifications=specifications,
                    is_active=is_active
                )
                
                # Check result
                if product_result['success']:
                    result['added_count'] += 1
                    result['product_ids'].append(product_result['product_id'])
                else:
                    result['failed_count'] += 1
                    result['errors'].append(f"Product {i+1}: {product_result['message']}")
                    
            except Exception as e:
                result['failed_count'] += 1
                result['errors'].append(f"Product {i+1}: Error processing - {str(e)}")
        
        # Set overall success based on results
        if result['added_count'] > 0:
            result['success'] = True
            if result['failed_count'] == 0:
                result['message'] = f"Successfully added all {result['added_count']} products"
            else:
                result['message'] = f"Added {result['added_count']} products, {result['failed_count']} failed"
        else:
            result['message'] = "Failed to add any products"
            
    except Exception as e:
        result['message'] = f"Batch operation error: {str(e)}"
        result['errors'].append(f"System error: {str(e)}")
    
    return result


# Test function for development and debugging
def test_add_product():
    """
    Test function to verify product addition functionality.
    
    This function runs basic tests on the product addition process
    to ensure all validation and creation logic works correctly.
    Used for development and debugging purposes.
    
    Notes:
        - Only run in development environment
        - Creates test products that should be cleaned up
        - Helps verify all validation rules work correctly
    """
    print("Testing product addition functionality...")
    
    # Test 1: Valid product addition
    result1 = add_new_product(
        user_id=1,
        name="Test Product 1",
        description="This is a test product",
        price="$99.99",
        category="Test Category",
        url="https://example.com/product1",
        features={"color": "red", "size": "large"},
        specifications={"weight": "1kg", "dimensions": "10x10x10"}
    )
    print(f"Test 1 - Valid product: {result1}")
    
    # Test 2: Invalid product name
    result2 = add_new_product(
        user_id=1,
        name="",  # Empty name should fail
        description="Test description"
    )
    print(f"Test 2 - Invalid name: {result2}")
    
    # Test 3: Invalid JSON features
    result3 = add_new_product(
        user_id=1,
        name="Test Product 3",
        features="invalid json string"
    )
    print(f"Test 3 - Invalid JSON: {result3}")


# Run tests if this file is executed directly
if __name__ == "__main__":
    test_add_product()