"""
Reset passwords for test users
"""

from src.entity import User, Role
from werkzeug.security import generate_password_hash

print("=" * 80)
print("RESETTING TEST USER PASSWORDS")
print("=" * 80)

# Define test users with new passwords (min 8 characters)
test_users = [
    ('admin1', 'admin123', 'User Admin'),
    ('csr_rep1', 'csrrep123', 'CSR Rep'),
    ('pin_user1', 'pinuser123', 'PIN'),
    ('platform_mgr1', 'platform123', 'Platform Management'),
]

for username, new_password, expected_role in test_users:
    print(f"\nProcessing: {username}")
    
    # Find user
    user = User.find_by_username(username)
    if not user:
        print(f"  [X] User not found - skipping")
        continue
    
    print(f"  [OK] User found: {user.full_name}")
    
    # Update password
    try:
        user.set_password(new_password)
        if user.save():
            print(f"  [SUCCESS] Password updated to: {new_password}")
        else:
            print(f"  [FAIL] Failed to save password")
    except Exception as e:
        print(f"  [FAIL] Error: {str(e)}")

print("\n" + "=" * 80)
print("PASSWORD RESET COMPLETE")
print("=" * 80)
print("\nYou can now login with:")
print("  - admin1 / admin123 (User Admin)")
print("  - csr_rep1 / csr123 (CSR Rep)")
print("  - pin_user1 / pin123 (PIN)")
print("  - platform_mgr1 / platform123 (Platform Management)")
print("=" * 80)

