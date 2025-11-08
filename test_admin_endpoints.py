"""
Test User Admin endpoints that should return user accounts and profiles
"""

import requests
from src.entity import User

print("=" * 80)
print("TESTING USER ADMIN ENDPOINTS")
print("=" * 80)

# Login as admin to get token
print("\n1. Logging in as admin1...")
admin_user = User.authenticate('admin1', 'password123', 'User Admin')
if not admin_user:
    print("[FAIL] Could not login as admin")
    exit(1)

token = admin_user.generate_session_token()
print(f"[OK] Token: {token[:50]}...")

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

base_url = 'http://127.0.0.1:5000'

# Test endpoints
endpoints = [
    ('GET', '/api/userAccount', 'Get all user accounts'),
    ('GET', '/api/userProfile', 'Get all user profiles'),
    ('GET', '/api/roles', 'Get all roles'),
]

print("\n2. Testing endpoints:")
print("-" * 80)

for method, endpoint, description in endpoints:
    print(f"\n{method} {endpoint} - {description}")
    try:
        if method == 'GET':
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', 'N/A')}")
            if 'data' in data:
                print(f"  Data count: {len(data['data']) if isinstance(data['data'], list) else 'N/A'}")
                if isinstance(data['data'], list) and len(data['data']) > 0:
                    print(f"  First item keys: {list(data['data'][0].keys())}")
            print(f"  [SUCCESS] Endpoint working!")
        else:
            print(f"  Error: {response.text[:200]}")
            print(f"  [FAIL] Endpoint failed!")
            
    except Exception as e:
        print(f"  [ERROR] {str(e)}")

print("\n" + "=" * 80)

