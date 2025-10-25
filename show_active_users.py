#!/usr/bin/env python3
"""Simple script to show active users"""
from src.config.supabase import get_supabase

supabase = get_supabase()
users = supabase.table('users').select('id,username,email,full_name,role_id,is_active').eq('is_active', True).execute()

print("\n=== ACTIVE USERS (Can Login) ===\n")
for u in users.data:
    role_name = {1: "User Admin", 2: "PIN", 3: "CSR Rep", 4: "Platform Management"}.get(u['role_id'], "Unknown")
    print(f"Username: {u['username']:20} | Role: {role_name:20} | Name: {u['full_name']}")

print(f"\nTotal active users: {len(users.data)}")
print("\n📝 To login, use any of the usernames above with 'csr123' as password")
print("   (The default test password used when creating these users)")
