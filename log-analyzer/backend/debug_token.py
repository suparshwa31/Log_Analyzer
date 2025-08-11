#!/usr/bin/env python3
"""
Debug script to test JWT token validation
"""

import requests
import json
from supabase import create_client
from config import Config

def test_token_validation():
    """Test token validation with your backend"""
    
    # Get your JWT token (replace with your actual token)
    token = input("JWT Token: ").strip()
    
    if not token:
        return
    
    
    # Test 1: Verify token with Supabase directly
    try:
        config = Config()
        client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
        
        user = client.auth.get_user(token)
        if user and user.user:
            pass  # Validation successful
        else:
            pass  # Validation failed
            
    except Exception as e:
        pass  # Validation error
    
    # Test 2: Test your backend auth endpoint
    try:
        url = "http://localhost:5001/api/auth/verify"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(url, headers=headers)
        # Backend auth verification
            
    except Exception as e:
        pass  # Backend test error
    
    # Test 3: Test upload endpoint
    try:
        url = "http://localhost:5001/api/upload/files"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)
        # Upload endpoint test
            
    except Exception as e:
        pass  # Upload test error

def create_test_user():
    """Create a test user and get token"""
    
    try:
        config = Config()
        client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        email = "test@example.com"
        password = "testpassword123"
        
        # Try to sign up
        try:
            response = client.auth.sign_up({
                'email': email,
                'password': password
            })
            pass  # User created
        except Exception as e:
            pass  # User might already exist
        
        # Sign in to get token
        sign_in = client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if sign_in.session:
            token = sign_in.session.access_token
            return token
        else:
            return None
            
    except Exception as e:
        return None

def main():
    """Main function"""
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_token_validation()
    elif choice == "2":
        token = create_test_user()
        if token:
            # Update the token for testing
            import sys
            sys.stdin = open('/dev/tty', 'r')  # Reopen stdin for input
            test_token_validation()

if __name__ == "__main__":
    main()
