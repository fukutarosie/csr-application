#!/usr/bin/env python
"""Refresh database with fresh test data"""

from src.config.supabase import get_supabase
from werkzeug.security import generate_password_hash

supabase = get_supabase()

print("=" * 80)
print("DATABASE REFRESH - Creating Fresh Test Data")
print("=" * 80)

# Step 1: Clear existing users
print("\n1. Clearing existing users...")
try:
    supabase.table('users').delete().neq('id', 0).execute()
    print("✓ Users cleared")
except Exception as e:
    print(f"✗ Error clearing users: {e}")

# Step 2: Create test users with consistent password: 'password123'
print("\n2. Creating test users...")
test_password = 'password123'
# Use pbkdf2:sha256 to avoid requiring cryptography library
hashed_password = generate_password_hash(test_password, method='pbkdf2:sha256')

test_users = [
    # Admin users
    {'username': 'admin1', 'full_name': 'Admin One', 'email': 'admin1@test.com', 'role_id': 1},
    {'username': 'admin2', 'full_name': 'Admin Two', 'email': 'admin2@test.com', 'role_id': 1},
    {'username': 'admin3', 'full_name': 'Admin Three', 'email': 'admin3@test.com', 'role_id': 1},
    
    # PIN users
    {'username': 'pin_user1', 'full_name': 'PIN User One', 'email': 'pin1@test.com', 'role_id': 2},
    {'username': 'pin_user2', 'full_name': 'PIN User Two', 'email': 'pin2@test.com', 'role_id': 2},
    {'username': 'pin_user3', 'full_name': 'PIN User Three', 'email': 'pin3@test.com', 'role_id': 2},
    
    # CSR Rep users
    {'username': 'csr_rep1', 'full_name': 'CSR Rep One', 'email': 'csr1@test.com', 'role_id': 3},
    {'username': 'csr_rep2', 'full_name': 'CSR Rep Two', 'email': 'csr2@test.com', 'role_id': 3},
    {'username': 'csr_rep3', 'full_name': 'CSR Rep Three', 'email': 'csr3@test.com', 'role_id': 3},
    
    # Platform Management users
    {'username': 'platform_mgr1', 'full_name': 'Platform Manager One', 'email': 'platform1@test.com', 'role_id': 4},
    {'username': 'platform_mgr2', 'full_name': 'Platform Manager Two', 'email': 'platform2@test.com', 'role_id': 4},
]

created_count = 0
for user in test_users:
    try:
        user_data = {
            'username': user['username'],
            'password': hashed_password,
            'email': user['email'],
            'full_name': user['full_name'],
            'role_id': user['role_id'],
            'is_active': True,
        }
        
        result = supabase.table('users').insert(user_data).execute()
        print(f"  ✓ Created {user['username']}")
        created_count += 1
    except Exception as e:
        print(f"  ✗ Failed to create {user['username']}: {e}")

print(f"\n✓ Successfully created {created_count}/{len(test_users)} test users")

print("\n" + "=" * 80)
print("DATABASE REFRESH COMPLETE!")
print("=" * 80)
print("\n📝 TEST CREDENTIALS:")
print(f"  Password: {test_password}")
print(f"  Usernames: See list above")
print("\n✓ All users are now active and can login")
print("=" * 80)
