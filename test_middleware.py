#!/usr/bin/env python
"""
Test script to verify middleware behavior for route access control.
"""

import requests
import sys

def test_middleware_behavior():
    base_url = "http://127.0.0.1:8002"
    
    print("Testing Spectra Clothing Middleware Behavior")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Root path access (unauthenticated)",
            "url": f"{base_url}/",
            "expected": "Should redirect to login"
        },
        {
            "name": "Non-existent route (unauthenticated)",
            "url": f"{base_url}/nonexistent-route",
            "expected": "Should redirect to login"
        },
        {
            "name": "Dashboard access (unauthenticated)",
            "url": f"{base_url}/dashboard/",
            "expected": "Should redirect to login"
        },
        {
            "name": "Products access (unauthenticated)",
            "url": f"{base_url}/products/",
            "expected": "Should redirect to login"
        },
        {
            "name": "Login page access",
            "url": f"{base_url}/accounts/login/",
            "expected": "Should allow access"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"URL: {test_case['url']}")
        print(f"Expected: {test_case['expected']}")
        
        try:
            response = requests.get(test_case['url'], allow_redirects=False)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location', 'No location header')
                print(f"Redirects to: {redirect_url}")
                
                # Check if redirect is to login
                if '/accounts/login/' in redirect_url:
                    print("✅ PASS: Correctly redirects to login")
                elif '/dashboard/' in redirect_url:
                    print("✅ PASS: Correctly redirects to dashboard")
                else:
                    print(f"❌ FAIL: Unexpected redirect to {redirect_url}")
            else:
                print(f"Response received (no redirect)")
                if test_case['url'].endswith('/accounts/login/') and response.status_code == 200:
                    print("✅ PASS: Login page accessible")
                elif response.status_code == 200:
                    print("❌ FAIL: Should have redirected but didn't")
                else:
                    print(f"❌ FAIL: Unexpected status code {response.status_code}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Middleware Test Summary:")
    print("1. Unauthenticated users should be redirected to login for ANY route")
    print("2. Authenticated users accessing non-existent routes should redirect to dashboard")
    print("3. Only login, admin, static, and media paths should be accessible without authentication")

if __name__ == "__main__":
    test_middleware_behavior()
