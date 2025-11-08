#!/usr/bin/env python3
"""Reset ALL user passwords to 'password123' for consistency"""
from src.entity.supabase_config import get_supabase
from werkzeug.security import generate_password_hash

supabase = get_supabase()

# The standard password for all test accounts
STANDARD_PASSWORD = 'password123'

print(f"\n{'='*70}")
print("RESETTING ALL USER PASSWORDS TO 'password123'")
print(f"{'='*70}\n")
print("This will update ALL users in the database for consistency.\n")

# Hash the password once (pbkdf2:sha256 method)
hashed_password = generate_password_hash(STANDARD_PASSWORD, method='pbkdf2:sha256')

try:
    # Get all users
    users_result = supabase.table('users').select('id, username, is_active').execute()
    
    if not users_result.data:
        print("No users found in database!")
    else:
        total_users = len(users_result.data)
        active_users = [u for u in users_result.data if u['is_active']]
        
        print(f"Found {total_users} users ({len(active_users)} active, {total_users - len(active_users)} inactive)")
        print("\nUpdating passwords...\n")
        
        success_count = 0
        error_count = 0
        
        for user in users_result.data:
            try:
                # Update password
                supabase.table('users').update({
                    'password': hashed_password
                }).eq('id', user['id']).execute()
                
                status = "[ACTIVE]" if user['is_active'] else "[INACTIVE]"
                print(f"{status} {user['username']:<30} -> password123")
                success_count += 1
                
            except Exception as e:
                print(f"[ERROR] {user['username']:<30} -> Error: {str(e)}")
                error_count += 1
        
        print(f"\n{'='*70}")
        print("PASSWORD RESET COMPLETE!")
        print(f"{'='*70}")
        print(f"\nSuccessfully updated: {success_count} users")
        if error_count > 0:
            print(f"Errors: {error_count} users")
        
        print(f"\n{'='*70}")
        print("ALL USERS NOW HAVE THE SAME PASSWORD:")
        print(f"{'='*70}")
        print("\n  Username: [any username in database]")
        print("  Password: password123")
        print("\nExample logins:")
        print("  - admin1 / password123")
        print("  - pin_user1 / password123")
        print("  - csr_rep1 / password123")
        print("  - platform_mgr1 / password123")
        print(f"\n{'='*70}\n")
        
except Exception as e:
    print(f"[ERROR] Error: {str(e)}")
