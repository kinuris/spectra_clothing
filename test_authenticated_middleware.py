#!/usr/bin/env python
"""
Test script to verify authenticated user behavior with non-existent routes.
"""

import requests
import sys
from django.contrib.auth import get_user_model
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spectra_clothing.settings')
django.setup()

def test_authenticated_user_behavior():
    base_url = "http://127.0.0.1:8002"
    
    print("Testing Authenticated User Middleware Behavior")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, get the login page to obtain CSRF token
    print("1. Getting login page...")
    login_page = session.get(f"{base_url}/accounts/login/")
    print(f"   Login page status: {login_page.status_code}")
    
    if login_page.status_code != 200:
        print("❌ FAIL: Cannot access login page")
        return
    
    # Extract CSRF token from the login page
    csrf_token = None
    for line in login_page.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    if not csrf_token:
        print("❌ FAIL: Could not extract CSRF token")
        return
    
    print(f"   CSRF token obtained: {csrf_token[:20]}...")
    
    # Attempt to login with test credentials
    print("\n2. Attempting to login...")
    login_data = {
        'username': 'testuser',  # Test user we just created
        'password': 'testpass123',  # Test password
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{base_url}/accounts/login/", data=login_data, allow_redirects=False)
    print(f"   Login response status: {login_response.status_code}")
    
    if login_response.status_code in [302, 303]:
        redirect_url = login_response.headers.get('Location', '')
        print(f"   Redirected to: {redirect_url}")
        
        if '/dashboard/' in redirect_url:
            print("✅ SUCCESS: Successfully logged in")
            
            # Now test non-existent routes as authenticated user
            print("\n3. Testing non-existent routes as authenticated user...")
            
            test_routes = [
                '/nonexistent-route',
                '/invalid/path',
                '/products/nonexistent',
                '/dashboard/invalid-section'
            ]
            
            for route in test_routes:
                print(f"\n   Testing route: {route}")
                response = session.get(f"{base_url}{route}", allow_redirects=False)
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [302, 303]:
                    redirect_location = response.headers.get('Location', '')
                    print(f"   Redirects to: {redirect_location}")
                    
                    if '/dashboard/' in redirect_location:
                        print("   ✅ PASS: Correctly redirects authenticated user to dashboard")
                    else:
                        print(f"   ❌ FAIL: Should redirect to dashboard, but redirects to {redirect_location}")
                else:
                    print(f"   ❌ FAIL: Expected redirect but got status {response.status_code}")
        else:
            print(f"❌ FAIL: Login should redirect to dashboard, but redirected to {redirect_url}")
    else:
        print("❌ FAIL: Login unsuccessful")
        print(f"   Response content: {login_response.text[:200]}...")

if __name__ == "__main__":
    test_authenticated_user_behavior()
