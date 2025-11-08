"""
Simulate what the frontend does when fetching data
"""

import requests
from src.entity import User

print("=" * 80)
print("SIMULATING FRONTEND DATA FETCHING")
print("=" * 80)

# Step 1: Login (what frontend does)
print("\n1. LOGIN")
print("-" * 80)
login_data = {
    'username': 'admin1',
    'password': 'password123',
    'role_name': 'User Admin'
}

try:
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Full response: {data}")
        
        # Token is nested inside 'data' key
        token = data.get('data', {}).get('token') if 'data' in data else data.get('token')
        print(f"Token: {token[:50] if token else 'None'}...")
    else:
        print(f"Error: {response.text}")
        exit(1)
except Exception as e:
    print(f"[ERROR] {str(e)}")
    exit(1)

# Step 2: Fetch User Accounts (what frontend does)
print("\n2. FETCH USER ACCOUNTS")
print("-" * 80)

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get('http://localhost:5000/api/userAccount', headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"User Count: {len(data.get('data', []))}")
        
        if data.get('data'):
            print(f"\nFirst 3 users:")
            for user in data['data'][:3]:
                print(f"  - {user['username']} ({user['full_name']}) - Role ID: {user['role_id']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"[ERROR] {str(e)}")

# Step 3: Fetch User Profiles (what frontend does)
print("\n3. FETCH USER PROFILES")
print("-" * 80)

try:
    response = requests.get('http://localhost:5000/api/userProfile', headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Profile Count: {len(data.get('data', []))}")
        
        if data.get('data'):
            print(f"\nAll profiles:")
            for profile in data['data']:
                print(f"  - {profile['role_name']} ({profile['role_code']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"[ERROR] {str(e)}")

print("\n" + "=" * 80)
print("SIMULATION COMPLETE")
print("=" * 80)

