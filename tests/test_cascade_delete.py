#!/usr/bin/env python
"""Test CASCADE DELETE constraint - verify that deleting a role deletes its users"""

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
            print("[OK] Login successful")
            return True
        else:
            print("[FAIL] Token not found in response")
            return False
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        return False

def get_headers():
    """Get headers with token"""
    return {"Authorization": f"Bearer {TOKEN}"}

def test_cascade_delete():
    """Test CASCADE DELETE by creating a role and users, then deleting the role"""
    
    print("\n" + "=" * 80)
    print("CASCADE DELETE TEST")
    print("=" * 80)
    
    timestamp = datetime.now().strftime('%H%M%S')
    
    # Step 1: Create a test role
    print("\n1. CREATE TEST ROLE...")
    role_data = {
        "role_name": f"CASCADE_TEST_ROLE_{timestamp}",
        "role_code": f"CASCADE_TEST_{timestamp}",
        "description": "Test role for CASCADE DELETE verification"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/roles",
        json=role_data,
        headers=get_headers()
    )
    
    if response.status_code != 201:
        print(f"[FAIL] Failed to create test role: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    role = response.json().get('data')
    role_id = role['id']
    print(f"[OK] Test role created with ID: {role_id}")
    print(f"    Role name: {role['role_name']}")
    
    # Step 2: Create 3 users with this role
    print("\n2. CREATE 3 USERS WITH THIS ROLE...")
    user_ids = []
    
    for i in range(1, 4):
        user_data = {
            "username": f"cascade_test_user_{timestamp}_{i}",
            "password": "testpass123",
            "email": f"cascade_test_{timestamp}_{i}@test.com",
            "full_name": f"Cascade Test User {i}",
            "role_id": role_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/users",
            json=user_data,
            headers=get_headers()
        )
        
        if response.status_code != 201:
            print(f"[FAIL] Failed to create user {i}: {response.status_code}")
            return False
        
        user = response.json().get('data')
        user_ids.append(user['id'])
        print(f"[OK] User {i} created with ID: {user['id']}")
    
    print(f"    Total users created: {len(user_ids)}")
    
    # Step 3: Verify users exist before deletion
    print("\n3. VERIFY USERS EXIST (Before deletion)...")
    response = requests.get(
        f"{BASE_URL}/api/users",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Failed to fetch users: {response.status_code}")
        return False
    
    all_users = response.json().get('data', [])
    cascade_users_before = [u for u in all_users if u['id'] in user_ids]
    print(f"[OK] Found {len(cascade_users_before)} users with CASCADE_TEST role")
    for user in cascade_users_before:
        print(f"    - {user['username']} (ID: {user['id']}, role_id: {user['role_id']})")
    
    # Step 4: DELETE THE ROLE (this should trigger CASCADE DELETE)
    print("\n4. DELETE TEST ROLE (this should trigger CASCADE DELETE)...")
    response = requests.delete(
        f"{BASE_URL}/api/roles/{role_id}",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Failed to delete role: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    print(f"[OK] Role deleted (ID: {role_id})")
    
    # Step 5: Verify users were CASCADE DELETED
    print("\n5. VERIFY USERS WERE CASCADE DELETED (After role deletion)...")
    response = requests.get(
        f"{BASE_URL}/api/users",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Failed to fetch users: {response.status_code}")
        return False
    
    all_users_after = response.json().get('data', [])
    cascade_users_after = [u for u in all_users_after if u['id'] in user_ids]
    
    if len(cascade_users_after) == 0:
        print(f"[OK] CASCADE DELETE WORKS!")
        print(f"    - All {len(user_ids)} users were automatically deleted when role was deleted")
        return True
    else:
        print(f"[FAIL] CASCADE DELETE DID NOT WORK!")
        print(f"    - Expected 0 users remaining, but found {len(cascade_users_after)}")
        for user in cascade_users_after:
            print(f"      - {user['username']} (ID: {user['id']})")
        return False

def main():
    """Run CASCADE DELETE test"""
    print("\n" + "=" * 80)
    print("CASCADE DELETE VERIFICATION TEST")
    print("=" * 80)
    print("\nThis test verifies that when a role is deleted,")
    print("all users assigned to that role are automatically deleted.")
    
    # Login first
    if not login():
        print("\n[FAIL] Cannot proceed without valid token")
        return
    
    # Run CASCADE DELETE test
    success = test_cascade_delete()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("[OK] CASCADE DELETE VERIFIED!")
        print("\nYour database is properly configured.")
        print("When you delete a role from the admin dashboard,")
        print("all users with that role will be automatically removed.")
    else:
        print("[FAIL] CASCADE DELETE NOT WORKING")
        print("\nPlease verify:")
        print("1. You ran the SQL in Supabase Dashboard")
        print("2. The constraint was created successfully")
        print("3. Check Supabase: Table 'users' -> Relationships")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
