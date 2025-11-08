from src.config.supabase import get_supabase

supabase = get_supabase()

# Get all CSR users
result = supabase.table('user_accounts').select('user_id, username, role_name, is_active').eq('role_name', 'CSR Representative').execute()

print("\n" + "="*60)
print("CSR USERS IN DATABASE:")
print("="*60)

if result.data:
    for user in result.data:
        status = "✅ Active" if user.get('is_active', True) else "❌ Inactive"
        print(f"{status} | ID: {user['user_id']:3} | Username: {user['username']}")
    print(f"\nTotal CSR users: {len(result.data)}")
    print("\n📝 Default password: password123")
    print("   Try logging in with any of the usernames above")
else:
    print("❌ No CSR users found in database!")
    print("\nLet's check all users:")
    all_users = supabase.table('user_accounts').select('user_id, username, role_name').limit(10).execute()
    for user in all_users.data:
        print(f"ID: {user['user_id']:3} | Username: {user['username']:20} | Role: {user['role_name']}")
