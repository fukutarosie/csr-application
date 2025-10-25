#!/usr/bin/env python3
"""
Debug script to troubleshoot login issues
"""

from src.config.supabase import get_supabase
from src.entity import User, Role
from werkzeug.security import generate_password_hash

print("\n" + "="*60)
print("CSR APP - LOGIN DEBUG SCRIPT")
print("="*60 + "\n")

supabase = get_supabase()

# 1. Check if roles exist
print("1. Checking Roles in Database...")
print("-" * 60)
try:
    roles_data = supabase.table('roles').select("*").execute()
    if roles_data.data:
        print(f"✓ Found {len(roles_data.data)} role(s):\n")
        for role in roles_data.data:
            print(f"   ID: {role['id']}")
            print(f"   Name: {role['role_name']}")
            print(f"   Code: {role['role_code']}")
            print(f"   Route: {role['dashboard_route']}")
            print()
    else:
        print("✗ No roles found in database!")
except Exception as e:
    print(f"✗ Error fetching roles: {str(e)}\n")

# 2. Check if users exist
print("\n2. Checking Users in Database...")
print("-" * 60)
try:
    users_data = supabase.table('users').select("*").execute()
    if users_data.data:
        print(f"✓ Found {len(users_data.data)} user(s):\n")
        for user in users_data.data:
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Full Name: {user['full_name']}")
            print(f"   Role ID: {user['role_id']}")
            print(f"   Is Active: {user['is_active']}")
            print()
    else:
        print("✗ No users found in database!")
        print("\nDo you want to create a test user? (Yes/No)")
        response = input("> ").strip().lower()
        if response in ['yes', 'y']:
            print("\nCreating test user...")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            email = input("Email: ").strip()
            full_name = input("Full Name: ").strip()
            role_id = input("Role ID (usually 1 for User Admin): ").strip()
            
            try:
                success, status = User.create_user(username, password, email, full_name, int(role_id))
                if success:
                    print(f"✓ Test user '{username}' created successfully!")
                    print(f"  You can now login with:")
                    print(f"  - Username: {username}")
                    print(f"  - Password: {password}")
                else:
                    print(f"✗ Failed to create user (Status: {status})")
            except Exception as e:
                print(f"✗ Error creating user: {str(e)}")
except Exception as e:
    print(f"✗ Error fetching users: {str(e)}\n")

# 3. Test login with provided credentials
print("\n3. Testing Login Credentials...")
print("-" * 60)
test_username = input("Enter username to test (or press Enter to skip): ").strip()
if test_username:
    test_password = input("Enter password: ").strip()
    
    print(f"\nTesting login for '{test_username}'...")
    
    # Get user
    user = User.get_user_by_username(test_username)
    if not user:
        print(f"✗ User '{test_username}' not found in database")
    else:
        print(f"✓ User found: {user['full_name']}")
        print(f"  Username: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"  Role ID: {user['role_id']}")
        print(f"  Is Active: {user['is_active']}")
        
        # Check password
        from werkzeug.security import check_password_hash
        if check_password_hash(user['password'], test_password):
            print(f"✓ Password is correct!")
        else:
            print(f"✗ Password is incorrect!")
        
        # Check if active
        if not user['is_active']:
            print(f"✗ User is inactive - cannot login")
        else:
            print(f"✓ User is active")

print("\n" + "="*60)
print("Debug script completed")
print("="*60 + "\n")
