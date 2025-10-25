#!/usr/bin/env python
"""Test CRUD operations for User Accounts and User Profiles"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
TOKEN = None

def login():
    """Login and get JWT token"""
    global TOKEN
    print("\n" + "=" * 80)
    print("STEP 1: LOGIN")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin1", "password": "password123", "role_name": "User Admin"}
    )
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get('data', {}).get('token') or data.get('token')
        if TOKEN:
            print(f"[OK] Login successful")
            print(f"  Token: {TOKEN[:50]}...")
            return True
        else:
            print(f"[FAIL] Token not found in response")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return False
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def get_headers():
    """Get headers with token"""
    return {"Authorization": f"Bearer {TOKEN}"}

# ============== USER PROFILES (ROLES) CRUD ==============

def test_profile_crud():
    """Test User Profile CRUD operations"""
    print("\n" + "=" * 80)
    print("TESTING USER PROFILES (ROLES) CRUD")
    print("=" * 80)
    
    # CREATE
    print("\n1. CREATE - Adding new profile...")
    profile_data = {
        "role_name": f"Test Role {datetime.now().strftime('%H%M%S')}",
        "role_code": "TEST_ROLE",
        "description": "This is a test profile role"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/roles",
        json=profile_data,
        headers=get_headers()
    )
    
    if response.status_code == 201:
        created_profile = response.json().get('data')
        profile_id = created_profile['id']
        print(f"[OK] Profile created successfully")
        print(f"  ID: {profile_id}")
        print(f"  Name: {created_profile['role_name']}")
        print(f"  Code: {created_profile['role_code']}")
    else:
        print(f"[FAIL] Failed to create profile: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # READ
    print("\n2. READ - Fetching all profiles...")
    response = requests.get(
        f"{BASE_URL}/api/roles",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        profiles = response.json().get('data', [])
        print(f"[OK] Retrieved all profiles")
        print(f"  Total profiles: {len(profiles)}")
        for prof in profiles[:3]:
            print(f"    - {prof['role_name']} ({prof['role_code']})")
    else:
        print(f"[FAIL] Failed to fetch profiles: {response.status_code}")
        return False
    
    # UPDATE
    print("\n3. UPDATE - Modifying profile...")
    update_data = {
        "role_name": f"Updated Role {datetime.now().strftime('%H%M%S')}",
        "role_code": "UPDATED_ROLE",
        "description": "Updated description"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/roles/{profile_id}",
        json=update_data,
        headers=get_headers()
    )
    
    if response.status_code == 200:
        updated_profile = response.json().get('data')
        print(f"[OK] Profile updated successfully")
        print(f"  New name: {updated_profile['role_name']}")
        print(f"  New code: {updated_profile['role_code']}")
    else:
        print(f"[FAIL] Failed to update profile: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # DELETE
    print("\n4. DELETE - Removing profile...")
    response = requests.delete(
        f"{BASE_URL}/api/roles/{profile_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        print(f"[OK] Profile deleted successfully")
        print(f"  ID: {profile_id}")
    else:
        print(f"[FAIL] Failed to delete profile: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    return True

# ============== USER ACCOUNTS CRUD ==============

def test_user_crud():
    """Test User Account CRUD operations"""
    print("\n" + "=" * 80)
    print("TESTING USER ACCOUNTS CRUD")
    print("=" * 80)
    
    # CREATE
    print("\n1. CREATE - Adding new user...")
    user_data = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "password": "testpass123",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@test.com",
        "full_name": "Test User",
        "role_id": 1  # User Admin role
    }
    
    response = requests.post(
        f"{BASE_URL}/api/users",
        json=user_data,
        headers=get_headers()
    )
    
    if response.status_code == 201:
        created_user = response.json().get('data')
        user_id = created_user['id']
        print(f"[OK] User created successfully")
        print(f"  ID: {user_id}")
        print(f"  Username: {created_user['username']}")
        print(f"  Email: {created_user['email']}")
    else:
        print(f"[FAIL] Failed to create user: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # READ
    print("\n2. READ - Fetching all users...")
    response = requests.get(
        f"{BASE_URL}/api/users",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        users = response.json().get('data', [])
        print(f"[OK] Retrieved all users")
        print(f"  Total users: {len(users)}")
        for user in users[:3]:
            print(f"    - {user['username']} ({user['email']})")
    else:
        print(f"[FAIL] Failed to fetch users: {response.status_code}")
        return False
    
    # UPDATE
    print("\n3. UPDATE - Modifying user...")
    update_data = {
        "email": f"updated_{datetime.now().strftime('%H%M%S')}@test.com",
        "full_name": "Updated Test User",
        "role_id": 2  # Change to PIN role
    }
    
    response = requests.put(
        f"{BASE_URL}/api/users/{user_id}",
        json=update_data,
        headers=get_headers()
    )
    
    if response.status_code == 200:
        updated_user = response.json().get('data')
        print(f"[OK] User updated successfully")
        print(f"  New email: {updated_user['email']}")
        print(f"  New name: {updated_user['full_name']}")
        print(f"  New role_id: {updated_user['role_id']}")
    else:
        print(f"[FAIL] Failed to update user: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # SUSPEND (Deactivate)
    print("\n4. SUSPEND - Deactivating user...")
    response = requests.put(
        f"{BASE_URL}/api/users/{user_id}/suspend",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        print(f"[OK] User suspended successfully")
    else:
        print(f"[FAIL] Failed to suspend user: {response.status_code}")
        return False
    
    # ACTIVATE
    print("\n5. ACTIVATE - Reactivating user...")
    response = requests.put(
        f"{BASE_URL}/api/users/{user_id}/activate",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        print(f"[OK] User activated successfully")
    else:
        print(f"[FAIL] Failed to activate user: {response.status_code}")
        return False
    
    # DELETE
    print("\n6. DELETE - Removing user...")
    response = requests.delete(
        f"{BASE_URL}/api/users/{user_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        print(f"[OK] User deleted successfully")
        print(f"  ID: {user_id}")
    else:
        print(f"[FAIL] Failed to delete user: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE CRUD OPERATIONS TEST")
    print("=" * 80)
    
    # Login first
    if not login():
        print("\n[FAIL] Cannot proceed without valid token")
        return
    
    # Test Profile CRUD
    profile_success = test_profile_crud()
    
    # Test User CRUD
    user_success = test_user_crud()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"User Profiles CRUD: {'[OK] PASSED' if profile_success else '[FAIL] FAILED'}")
    print(f"User Accounts CRUD: {'[OK] PASSED' if user_success else '[FAIL] FAILED'}")
    
    if profile_success and user_success:
        print("\n[OK] ALL TESTS PASSED!")
    else:
        print("\n[FAIL] SOME TESTS FAILED")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
