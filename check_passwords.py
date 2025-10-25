#!/usr/bin/env python3
"""Check all users and their password hash"""
from src.config.supabase import get_supabase

supabase = get_supabase()
users = supabase.table('users').select('id,username,email,password,is_active').execute()

print(f"\n{'='*80}")
print(f"{'Username':<20} {'Email':<30} {'Password Hash':<30}")
print(f"{'='*80}")

for user in users.data:
    if user['is_active']:
        print(f"{user['username']:<20} {user['email']:<30} {user['password'][:30]}")

print(f"{'='*80}\n")
print("💡 Since password hashes are one-way, we need to know the ORIGINAL password.")
print("📝 Do you remember what password was set for these users when they were created?")
