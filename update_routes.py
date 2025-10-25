#!/usr/bin/env python3
"""Fix dashboard routes in database"""
from src.config.supabase import get_supabase

supabase = get_supabase()

# Update routes to match Next.js folder structure
updates = [
    {'id': 1, 'dashboard_route': '/admin', 'name': 'User Admin'},
    {'id': 2, 'dashboard_route': '/pin', 'name': 'PIN'},
    {'id': 3, 'dashboard_route': '/csr', 'name': 'CSR Rep'},
    {'id': 4, 'dashboard_route': '/platform', 'name': 'Platform Management'}
]

print("\n" + "="*60)
print("UPDATING DASHBOARD ROUTES")
print("="*60 + "\n")

for update in updates:
    result = supabase.table('roles').update(
        {'dashboard_route': update['dashboard_route']}
    ).eq('id', update['id']).execute()
    print(f"✓ {update['name']:<25} -> {update['dashboard_route']}")

print("\n" + "="*60)
print("VERIFICATION")
print("="*60 + "\n")

roles = supabase.table('roles').select('*').execute()
for r in roles.data:
    print(f"Role: {r['role_name']:<25} Route: {r['dashboard_route']}")

print("\n✅ Dashboard routes updated successfully!\n")
