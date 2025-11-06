#!/usr/bin/env python3
"""Fix plain text passwords by hashing them"""
from src.config.supabase import get_supabase
from werkzeug.security import generate_password_hash

supabase = get_supabase()

# Map of plain text passwords to fix
plain_passwords = {
    'admin1': 'admin123',
    'pin_user1': 'pin123',
    'platform_mgr1': 'platform123'
}

print(f"\n{'='*60}")
print("🔐 FIXING PLAIN TEXT PASSWORDS")
print(f"{'='*60}\n")

for username, password in plain_passwords.items():
    try:
        # Get user
        user = supabase.table('users').select('id,username').eq('username', username).execute()
        
        if user.data:
            user_id = user.data[0]['id']
            # Use pbkdf2:sha256 to avoid requiring cryptography library
            hashed = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Update with hashed password
            supabase.table('users').update({
                'password': hashed
            }).eq('id', user_id).execute()
            
            print(f"✓ {username:20} -> Password hashed securely")
            print(f"  (Still login with: {password})")
        else:
            print(f"✗ {username} not found")
    except Exception as e:
        print(f"✗ Error updating {username}: {str(e)}")

print(f"\n{'='*60}")
print("✅ All passwords are now securely hashed!")
print(f"{'='*60}\n")
