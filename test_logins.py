#!/usr/bin/env python
"""Test login credentials for various users"""

import requests
import json
import time

# Give backend a moment to start
time.sleep(1)

test_users = [
    {'username': 'admin1', 'password': 'csr123'},
    {'username': 'admin2', 'password': 'csr123'},
    {'username': 'admin3', 'password': 'csr123'},
    {'username': 'pin_user1', 'password': 'csr123'},
    {'username': 'pin_user2', 'password': 'csr123'},
    {'username': 'csr_rep1', 'password': 'csr123'},
    {'username': 'csr_rep2', 'password': 'csr123'},
    {'username': 'platform_mgr1', 'password': 'csr123'},
]

print("=" * 60)
print("TESTING LOGIN CREDENTIALS")
print("=" * 60)

for user in test_users:
    try:
        response = requests.post('http://localhost:5000/api/auth/login', json=user, timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {user['username']:20s} - SUCCESS")
        else:
            print(f"✗ {user['username']:20s} - FAILED ({response.status_code})")
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"✗ {user['username']:20s} - ERROR: {str(e)}")

print("=" * 60)
print("All logins should work with password: csr123")
print("=" * 60)
