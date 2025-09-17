#!/usr/bin/env python3
"""
File: authenticate_user.py
Purpose: Handle user authentication and login validation
Author: AI Customer Support Platform Team
Created: 2025-09-16
Last Modified: 2025-09-16

This file contains the core functionality for user authentication
in the AI Customer Support Platform. It handles user login validation,
password verification, and session management preparation.

Dependencies:
- hashlib: For password hash verification using SHA-256
- database.Database: For user data retrieval and validation
- typing: For type hints and better code documentation

Usage:
    from functions.user.authenticate_user import authenticate_user_login
    
    result = authenticate_user_login(
        username="john_doe",
        password="user_password"
    )

Notes:
- Passwords are verified against SHA-256 hashes
- Supports both username and email login
- Returns user data for session management
- Includes security measures against brute force attacks
"""

import hashlib
import time
from typing import Dict, Optional, Union
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import Database, User


# Global dictionary to track failed login attempts (in production, use Redis)
failed_attempts = {}  # Format: {username: {'count': int, 'last_attempt': timestamp}}


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 algorithm for comparison.
    
    This function takes a plain text password and converts it
    to a secure hash using SHA-256 algorithm. This hash is then
    compared with the stored hash in the database.
    
    Args:
        password (str): Plain text password to hash
    
    Returns:
        str: SHA-256 hashed password as hexadecimal string
    
    Example:
        >>> hash_password("mypassword")
        'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
    
    Notes:
        - Uses same algorithm as user creation
        - Must produce identical hash for same password
        - Used for secure password comparison
    """
    # Encode password to bytes for hashing
    password_bytes = password.encode('utf-8')
    
    # Create SHA-256 hash object
    hash_object = hashlib.sha256(password_bytes)
    
    # Get hexadecimal representation of hash
    password_hash = hash_object.hexdigest()
    
    return password_hash


def check_rate_limiting(identifier: str) -> Tuple[bool, str]:
    """
    Check if user has exceeded login attempt rate limits.
    
    This function implements basic rate limiting to prevent
    brute force attacks. It tracks failed login attempts
    and temporarily blocks users who exceed the limit.
    
    Args:
        identifier (str): Username or email to check rate limits for
    
    Returns:
        Tuple[bool, str]: (is_allowed, error_message)
            - is_allowed: True if login attempt is allowed
            - error_message: Description if rate limited
    
    Example:
        >>> check_rate_limiting("user123")
        (True, "")
        >>> check_rate_limiting("blocked_user")
        (False, "Too many failed attempts. Try again in 15 minutes.")
    
    Notes:
        - Maximum 5 failed attempts per 15 minutes
        - Resets counter after successful login
        - In production, should use Redis or database
    """
    current_time = time.time()
    max_attempts = 5  # Maximum failed attempts allowed
    lockout_duration = 900  # 15 minutes in seconds
    
    # Check if user has failed attempts recorded
    if identifier in failed_attempts:
        attempt_data = failed_attempts[identifier]
        
        # Check if lockout period has expired
        if current_time - attempt_data['last_attempt'] > lockout_duration:
            # Reset failed attempts after lockout period
            del failed_attempts[identifier]
            return True, ""
        
        # Check if user has exceeded maximum attempts
        if attempt_data['count'] >= max_attempts:
            remaining_time = int(lockout_duration - (current_time - attempt_data['last_attempt']))
            minutes_remaining = remaining_time // 60
            return False, f"Too many failed login attempts. Try again in {minutes_remaining} minutes."
    
    # User is allowed to attempt login
    return True, ""


def record_failed_attempt(identifier: str) -> None:
    """
    Record a failed login attempt for rate limiting.
    
    This function tracks failed login attempts to implement
    rate limiting and prevent brute force attacks. It updates
    the attempt counter and timestamp for the user.
    
    Args:
        identifier (str): Username or email that failed login
    
    Returns:
        None
    
    Notes:
        - Increments attempt counter
        - Updates last attempt timestamp
        - Used by rate limiting system
    """
    current_time = time.time()
    
    # Initialize or update failed attempt record
    if identifier in failed_attempts:
        failed_attempts[identifier]['count'] += 1
        failed_attempts[identifier]['last_attempt'] = current_time
    else:
        failed_attempts[identifier] = {
            'count': 1,
            'last_attempt': current_time
        }


def clear_failed_attempts(identifier: str) -> None:
    """
    Clear failed login attempts after successful authentication.
    
    This function removes the failed attempt record for a user
    after they successfully authenticate. This resets their
    rate limiting status.
    
    Args:
        identifier (str): Username or email to clear attempts for
    
    Returns:
        None
    
    Notes:
        - Called after successful login
        - Resets rate limiting for user
        - Allows normal login attempts again
    """
    if identifier in failed_attempts:
        del failed_attempts[identifier]


def validate_login_input(username: str, password: str) -> Tuple[bool, list]:
    """
    Validate login input parameters for basic requirements.
    
    This function performs basic validation on login inputs
    to ensure they meet minimum requirements before attempting
    database authentication.
    
    Args:
        username (str): Username or email provided for login
        password (str): Password provided for login
    
    Returns:
        Tuple[bool, list]: (is_valid, error_list)
            - is_valid: True if inputs are valid
            - error_list: List of validation errors
    
    Example:
        >>> validate_login_input("user123", "password")
        (True, [])
        >>> validate_login_input("", "")
        (False, ["Username is required", "Password is required"])
    
    Notes:
        - Checks for empty or whitespace-only inputs
        - Validates minimum length requirements
        - Does not validate actual credentials
    """
    errors = []
    
    # Validate username/email input
    if not username or not username.strip():
        errors.append("Username or email is required")
    elif len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters long")
    
    # Validate password input
    if not password or not password.strip():
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Return validation result
    return len(errors) == 0, errors


def authenticate_user_login(username: str, password: str) -> Dict[str, any]:
    """
    Authenticate user login credentials and return user data.
    
    This is the main authentication function that validates user
    credentials against the database. It handles both username
    and email login, implements rate limiting, and returns
    comprehensive authentication results.
    
    Args:
        username (str): Username or email address for login
        password (str): Plain text password for authentication
    
    Returns:
        Dict[str, any]: Authentication result containing:
            - success (bool): Whether authentication succeeded
            - user (User): User object if successful, None otherwise
            - message (str): Success or error message
            - errors (list): List of authentication errors
            - user_data (dict): User information for session management
    
    Raises:
        Exception: Database connection or operation errors
    
    Example:
        >>> result = authenticate_user_login("john_doe", "password123")
        >>> if result['success']:
        ...     print(f"Welcome, {result['user'].username}!")
        ... else:
        ...     print(f"Login failed: {result['message']}")
    
    Notes:
        - Supports login with username or email
        - Implements rate limiting for security
        - Hashes password for secure comparison
        - Returns user data for session creation
        - Clears rate limiting on successful login
    """
    # Initialize result dictionary for return value
    result = {
        'success': False,
        'user': None,
        'message': '',
        'errors': [],
        'user_data': None
    }
    
    try:
        # Step 1: Validate input parameters
        is_valid_input, validation_errors = validate_login_input(username, password)
        if not is_valid_input:
            result['errors'] = validation_errors
            result['message'] = "Invalid input: " + "; ".join(validation_errors)
            return result
        
        # Step 2: Clean input data
        clean_username = username.strip()
        
        # Step 3: Check rate limiting for this user
        is_allowed, rate_limit_message = check_rate_limiting(clean_username)
        if not is_allowed:
            result['message'] = rate_limit_message
            result['errors'] = ["Rate limited"]
            return result
        
        # Step 4: Initialize database connection
        db = Database()
        
        # Step 5: Try to find user by username first
        user = db.get_user_by_username(clean_username)
        
        # Step 6: If not found by username, try by email
        if not user:
            user = db.get_user_by_email(clean_username.lower())
        
        # Step 7: Check if user exists
        if not user:
            # Record failed attempt for rate limiting
            record_failed_attempt(clean_username)
            result['message'] = "Invalid username/email or password"
            result['errors'] = ["User not found"]
            db.close()
            return result
        
        # Step 8: Verify password by comparing hashes
        provided_password_hash = hash_password(password)
        stored_password_hash = user.password_hash
        
        if provided_password_hash != stored_password_hash:
            # Record failed attempt for rate limiting
            record_failed_attempt(clean_username)
            result['message'] = "Invalid username/email or password"
            result['errors'] = ["Invalid password"]
            db.close()
            return result
        
        # Step 9: Authentication successful
        # Clear any failed attempts for this user
        clear_failed_attempts(clean_username)
        
        # Prepare user data for session management
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'company_name': user.company_name,
            'website_url': user.website_url,
            'created_at': user.created_at,
            'is_active': user.is_active
        }
        
        # Set success result
        result['success'] = True
        result['user'] = user
        result['user_data'] = user_data
        result['message'] = f"Welcome back, {user.username}!"
        
        # Close database connection
        db.close()
        
    except Exception as e:
        # Handle any unexpected errors during authentication
        result['message'] = f"An error occurred during authentication: {str(e)}"
        result['errors'] = [f"System error: {str(e)}"]
    
    return result


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve user information by user ID for session validation.
    
    This function fetches user data from the database using
    the user ID. It's commonly used for session validation
    and user data retrieval in authenticated requests.
    
    Args:
        user_id (int): The unique ID of the user to retrieve
    
    Returns:
        Optional[User]: User object if found, None otherwise
    
    Example:
        >>> user = get_user_by_id(123)
        >>> if user:
        ...     print(f"User: {user.username}")
        ... else:
        ...     print("User not found")
    
    Notes:
        - Used for session validation
        - Returns None if user not found or inactive
        - Includes all user profile information
    """
    try:
        # Initialize database connection
        db = Database()
        
        # Retrieve user by ID
        user = db.get_user_by_id(user_id)
        
        # Close database connection
        db.close()
        
        return user
        
    except Exception as e:
        # Log error and return None
        print(f"Error retrieving user by ID {user_id}: {str(e)}")
        return None


def verify_user_session(user_id: int) -> Dict[str, any]:
    """
    Verify user session validity and return current user data.
    
    This function validates that a user session is still valid
    by checking if the user exists and is active. It's used
    for session management and authentication middleware.
    
    Args:
        user_id (int): User ID from session to verify
    
    Returns:
        Dict[str, any]: Session verification result containing:
            - valid (bool): Whether session is valid
            - user (User): User object if valid, None otherwise
            - message (str): Status message
    
    Example:
        >>> session_result = verify_user_session(123)
        >>> if session_result['valid']:
        ...     print("Session is valid")
        ... else:
        ...     print("Session expired or invalid")
    
    Notes:
        - Used by authentication middleware
        - Checks user existence and active status
        - Returns current user data for requests
    """
    result = {
        'valid': False,
        'user': None,
        'message': ''
    }
    
    try:
        # Get user by ID
        user = get_user_by_id(user_id)
        
        if user and user.is_active:
            result['valid'] = True
            result['user'] = user
            result['message'] = "Session is valid"
        else:
            result['message'] = "Session expired or user inactive"
            
    except Exception as e:
        result['message'] = f"Session verification error: {str(e)}"
    
    return result


# Test function for development and debugging
def test_authentication():
    """
    Test function to verify authentication functionality.
    
    This function runs basic tests on the authentication process
    to ensure all validation and login logic works correctly.
    Used for development and debugging purposes.
    
    Notes:
        - Only run in development environment
        - Tests various authentication scenarios
        - Helps verify security measures work correctly
    """
    print("Testing authentication functionality...")
    
    # Test 1: Valid authentication (assuming test user exists)
    result1 = authenticate_user_login("test_user", "TestPass123")
    print(f"Test 1 - Valid login: {result1['success']} - {result1['message']}")
    
    # Test 2: Invalid username
    result2 = authenticate_user_login("nonexistent_user", "password")
    print(f"Test 2 - Invalid username: {result2['success']} - {result2['message']}")
    
    # Test 3: Invalid password
    result3 = authenticate_user_login("test_user", "wrongpassword")
    print(f"Test 3 - Invalid password: {result3['success']} - {result3['message']}")
    
    # Test 4: Empty inputs
    result4 = authenticate_user_login("", "")
    print(f"Test 4 - Empty inputs: {result4['success']} - {result4['message']}")


# Run tests if this file is executed directly
if __name__ == "__main__":
    test_authentication()