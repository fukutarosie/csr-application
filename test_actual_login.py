"""
Test login with actual user credentials
"""

from src.entity import User

print("=" * 80)
print("TESTING LOGIN WITH ACTUAL USER CREDENTIALS")
print("=" * 80)

# Test with actual users
test_cases = [
    ('admin1', 'password123', 'User Admin'),
    ('csr_rep1', 'password123', 'CSR Rep'),
    ('pin_user1', 'password123', 'PIN'),
    ('platform_mgr1', 'password123', 'Platform Management'),
]

for username, password, role_name in test_cases:
    print(f"\nTesting: {username} / {password} as '{role_name}'")
    
    # Try authentication
    auth_user = User.authenticate(username, password, role_name)
    if auth_user:
        print(f"  [SUCCESS] Login successful!")
        print(f"  User ID: {auth_user.id}")
        print(f"  Full Name: {auth_user.full_name}")
        print(f"  Role ID: {auth_user.role_id}")
        
        # Generate token
        token = auth_user.generate_session_token()
        print(f"  Token generated: {token[:50]}...")
    else:
        print(f"  [FAIL] Login failed")
        
        # Try without role check to see if password is wrong
        auth_no_role = User.authenticate(username, password)
        if auth_no_role:
            print(f"  [INFO] Password correct but role mismatch")
            print(f"  [INFO] User's actual role_id: {auth_no_role.role_id}")
        else:
            print(f"  [INFO] Password incorrect or user not found")

print("\n" + "=" * 80)

