#!/usr/bin/env python3
"""Check existing database schema"""
from src.config.supabase import get_supabase

db = get_supabase()

print("\n" + "="*60)
print("DATABASE SCHEMA CHECK")
print("="*60 + "\n")

# Check profiles table
print("1. PROFILES TABLE")
print("-" * 60)
try:
    profiles = db.table('profiles').select('*').limit(1).execute()
    if profiles.data:
        print("✓ Profiles table exists")
        print(f"  Columns: {list(profiles.data[0].keys())}")
        print(f"  Sample data: {profiles.data[0]}")
    else:
        print("✓ Profiles table exists but is empty")
        # Try to get table info
        profiles_all = db.table('profiles').select('*').execute()
        if profiles_all.data:
            print(f"  Columns: {list(profiles_all.data[0].keys())}")
        else:
            print("  (No data to determine columns)")
except Exception as e:
    print(f"✗ Error accessing profiles: {str(e)}")

print("\n2. USERS TABLE")
print("-" * 60)
try:
    users = db.table('users').select('*').limit(1).execute()
    if users.data:
        print("✓ Users table exists")
        print(f"  Columns: {list(users.data[0].keys())}")
    else:
        print("✓ Users table exists but is empty")
except Exception as e:
    print(f"✗ Error accessing users: {str(e)}")

print("\n3. ROLES TABLE")
print("-" * 60)
try:
    roles = db.table('roles').select('*').execute()
    if roles.data:
        print("✓ Roles table exists")
        print(f"  Columns: {list(roles.data[0].keys())}")
        print(f"  Roles count: {len(roles.data)}")
        for role in roles.data:
            print(f"    - {role.get('role_name', 'N/A')}")
    else:
        print("✓ Roles table exists but is empty")
except Exception as e:
    print(f"✗ Error accessing roles: {str(e)}")

print("\n" + "="*60)
print("Check complete!")
print("="*60 + "\n")
