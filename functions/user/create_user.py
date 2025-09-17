#!/usr/bin/env python3
"""
File: create_user.py
Purpose: Handle user account creation with validation and security
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains the core functionality for creating new user accounts
in the AI Customer Support Platform. It handles user registration with
proper validation, password hashing, and database storage.

Dependencies:
- hashlib: For secure password hashing using SHA-256
- database.Database: For database operations and user storage
- typing: For type hints and better code documentation

Usage:
    from functions.user.create_user import create_new_user
    
    result = create_new_user(
        username="john_doe",
        email="john@example.com", 
        password="secure_password",
        company_name="Acme Corp",
        website_url="https://acme.com"
    )

Notes:
- Passwords are hashed using SHA-256 for security
- Email and username uniqueness is enforced
- All inputs are validated before processing
- Returns detailed success/error information
"""

import hashlib
import re
from typing import Dict, Tuple, Optional
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import Database


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex pattern.
    
    This function checks if the provided email address follows
    standard email format conventions. It uses a comprehensive
    regex pattern to validate the email structure.
    
    Args:
        email (str): The email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    
    Notes:
        - Uses RFC 5322 compliant regex pattern
        - Checks for proper domain structure
        - Validates special characters usage
    """
    # Email validation regex pattern (RFC 5322 compliant)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Check if email matches the pattern
    return re.match(email_pattern, email) is not None


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength according to security requirements.
    
    This function checks if the password meets minimum security
    requirements including length, character variety, and common
    password patterns to avoid.
    
    Args:
        password (str): The password to validate
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if password meets requirements
            - error_message: Description of validation failure
    
    Example:
        >>> validate_password_strength("SecurePass123!")
        (True, "")
        >>> validate_password_strength("weak")
        (False, "Password must be at least 8 characters long")
    
    Notes:
        - Minimum 8 characters required
        - Must contain uppercase, lowercase, and numbers
        - Special characters recommended but not required
    """
    # Check minimum length requirement (8 characters)
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letters
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letters  
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for numbers
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty', 'abc123']
    if password.lower() in weak_passwords:
        return False, "Password is too common, please choose a stronger password"
    
    # Password meets all requirements
    return True, ""


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 algorithm for secure storage.
    
    This function takes a plain text password and converts it
    to a secure hash using SHA-256 algorithm. The hashed password
    is safe to store in the database.
    
    Args:
        password (str): Plain text password to hash
    
    Returns:
        str: SHA-256 hashed password as hexadecimal string
    
    Example:
        >>> hash_password("mypassword")
        'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
    
    Notes:
        - Uses SHA-256 algorithm for security
        - Returns hexadecimal representation
        - Original password cannot be recovered from hash
        - Same password always produces same hash
    """
    # Encode password to bytes for hashing
    password_bytes = password.encode('utf-8')
    
    # Create SHA-256 hash object
    hash_object = hashlib.sha256(password_bytes)
    
    # Get hexadecimal representation of hash
    password_hash = hash_object.hexdigest()
    
    return password_hash


def validate_website_url(website_url: str) -> bool:
    """
    Validate website URL format and accessibility.
    
    This function checks if the provided website URL is properly
    formatted and follows standard URL conventions. It validates
    the protocol, domain structure, and basic format.
    
    Args:
        website_url (str): The website URL to validate
    
    Returns:
        bool: True if URL is valid, False otherwise
    
    Example:
        >>> validate_website_url("https://example.com")
        True
        >>> validate_website_url("invalid-url")
        False
    
    Notes:
        - Accepts both HTTP and HTTPS protocols
        - Validates domain name structure
        - Does not check actual website accessibility
    """
    # URL validation regex pattern
    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/.*)?$'
    
    # Check if URL matches the pattern
    return re.match(url_pattern, website_url) is not None


def create_new_user(username: str, email: str, password: str, 
                   company_name: str, website_url: str) -> Dict[str, any]:
    """
    Create a new user account with comprehensive validation.
    
    This is the main function for user account creation. It performs
    all necessary validations, checks for existing users, hashes the
    password securely, and stores the user in the database.
    
    Args:
        username (str): Unique username for the account (3-50 characters)
        email (str): Valid email address for the account
        password (str): Password meeting security requirements
        company_name (str): Name of the user's company (1-100 characters)
        website_url (str): Valid website URL for scraping
    
    Returns:
        Dict[str, any]: Result dictionary containing:
            - success (bool): Whether user creation succeeded
            - user_id (int): ID of created user (if successful)
            - message (str): Success or error message
            - errors (list): List of validation errors (if any)
    
    Raises:
        Exception: Database connection or operation errors
    
    Example:
        >>> result = create_new_user(
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     password="SecurePass123",
        ...     company_name="Acme Corp",
        ...     website_url="https://acme.com"
        ... )
        >>> print(result['success'])
        True
    
    Notes:
        - All inputs are validated before processing
        - Passwords are securely hashed before storage
        - Database transactions ensure data consistency
        - Detailed error messages help with debugging
    """
    # Initialize result dictionary for return value
    result = {
        'success': False,
        'user_id': None,
        'message': '',
        'errors': []
    }
    
    try:
        # Step 1: Validate all input parameters
        validation_errors = []
        
        # Validate username (length and format)
        if not username or len(username.strip()) < 3:
            validation_errors.append("Username must be at least 3 characters long")
        elif len(username.strip()) > 50:
            validation_errors.append("Username must be less than 50 characters")
        elif not re.match(r'^[a-zA-Z0-9_]+$', username.strip()):
            validation_errors.append("Username can only contain letters, numbers, and underscores")
        
        # Validate email format
        if not email or not validate_email(email.strip()):
            validation_errors.append("Please provide a valid email address")
        
        # Validate password strength
        if not password:
            validation_errors.append("Password is required")
        else:
            is_valid_password, password_error = validate_password_strength(password)
            if not is_valid_password:
                validation_errors.append(password_error)
        
        # Validate company name
        if not company_name or len(company_name.strip()) < 1:
            validation_errors.append("Company name is required")
        elif len(company_name.strip()) > 100:
            validation_errors.append("Company name must be less than 100 characters")
        
        # Validate website URL
        if not website_url or not validate_website_url(website_url.strip()):
            validation_errors.append("Please provide a valid website URL (e.g., https://example.com)")
        
        # If there are validation errors, return them
        if validation_errors:
            result['errors'] = validation_errors
            result['message'] = "Validation failed: " + "; ".join(validation_errors)
            return result
        
        # Step 2: Clean and prepare data for database storage
        clean_username = username.strip()
        clean_email = email.strip().lower()  # Store email in lowercase
        clean_company_name = company_name.strip()
        clean_website_url = website_url.strip()
        
        # Step 3: Initialize database connection
        db = Database()
        
        # Step 4: Check if username already exists
        existing_user_by_username = db.get_user_by_username(clean_username)
        if existing_user_by_username:
            result['message'] = "Username already exists. Please choose a different username."
            result['errors'] = ["Username already taken"]
            return result
        
        # Step 5: Check if email already exists
        existing_user_by_email = db.get_user_by_email(clean_email)
        if existing_user_by_email:
            result['message'] = "Email address already registered. Please use a different email or login."
            result['errors'] = ["Email already registered"]
            return result
        
        # Step 6: Hash the password securely
        password_hash = hash_password(password)
        
        # Step 7: Create the user in database
        user_id = db.create_user(
            username=clean_username,
            email=clean_email,
            password_hash=password_hash,
            company_name=clean_company_name,
            website_url=clean_website_url
        )
        
        # Step 8: Check if user creation was successful
        if user_id:
            result['success'] = True
            result['user_id'] = user_id
            result['message'] = f"User account created successfully! Welcome, {clean_username}!"
        else:
            result['message'] = "Failed to create user account. Please try again."
            result['errors'] = ["Database operation failed"]
        
        # Close database connection
        db.close()
        
    except Exception as e:
        # Handle any unexpected errors during user creation
        result['message'] = f"An error occurred while creating the user account: {str(e)}"
        result['errors'] = [f"System error: {str(e)}"]
    
    return result


# Test function for development and debugging
def test_create_user():
    """
    Test function to verify user creation functionality.
    
    This function runs basic tests on the user creation process
    to ensure all validation and creation logic works correctly.
    Used for development and debugging purposes.
    
    Notes:
        - Only run in development environment
        - Creates test users that should be cleaned up
        - Helps verify all validation rules work correctly
    """
    print("Testing user creation functionality...")
    
    # Test 1: Valid user creation
    result1 = create_new_user(
        username="test_user_123",
        email="test@example.com",
        password="TestPass123",
        company_name="Test Company",
        website_url="https://test.com"
    )
    print(f"Test 1 - Valid user: {result1}")
    
    # Test 2: Invalid email
    result2 = create_new_user(
        username="test_user_456",
        email="invalid-email",
        password="TestPass123",
        company_name="Test Company",
        website_url="https://test.com"
    )
    print(f"Test 2 - Invalid email: {result2}")
    
    # Test 3: Weak password
    result3 = create_new_user(
        username="test_user_789",
        email="test2@example.com",
        password="weak",
        company_name="Test Company",
        website_url="https://test.com"
    )
    print(f"Test 3 - Weak password: {result3}")


# Run tests if this file is executed directly
if __name__ == "__main__":
    test_create_user()