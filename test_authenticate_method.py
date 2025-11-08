"""
Test the User.authenticate method after OOP conversion
"""

from src.entity import User

print("=" * 80)
print("TESTING User.authenticate() METHOD")
print("=" * 80)

test_cases = [
    ('admin1', 'password123', 'User Admin'),
    ('csr_rep1', 'password123', 'CSR Rep'),
    ('pin_user1', 'password123', 'PIN'),
    ('platform_mgr1', 'password123', 'Platform Management'),
]

for username, password, role_name in test_cases:
    print(f"\nTesting: {username} / {password} as '{role_name}'")
    
    try:
        user = User.authenticate(username, password, role_name)
        
        if user:
            print(f"  [SUCCESS] Authentication successful!")
            print(f"  User ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Full Name: {user.full_name}")
            print(f"  Role ID: {user.role_id}")
            print(f"  Has roles attribute: {hasattr(user, 'roles')}")
            print(f"  Roles value: {user.roles}")
            
            # Test token generation
            try:
                token = user.generate_session_token()
                print(f"  Token generated: {token[:50]}...")
            except Exception as e:
                print(f"  [ERROR] Token generation failed: {str(e)}")
                
        else:
            print(f"  [FAIL] Authentication returned None")
            
            # Debug: Try to find user
            user_check = User.find_by_username(username)
            if user_check:
                print(f"  [DEBUG] User exists: {user_check.username}")
                print(f"  [DEBUG] User active: {user_check.is_active}")
                print(f"  [DEBUG] User role_id: {user_check.role_id}")
                
                # Check password
                if user_check.verify_password(password):
                    print(f"  [DEBUG] Password is correct")
                else:
                    print(f"  [DEBUG] Password is INCORRECT")
            else:
                print(f"  [DEBUG] User not found in database")
                
    except Exception as e:
        print(f"  [ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)

