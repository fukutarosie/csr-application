"""
Debug login issues for all 4 actors
"""

from src.entity import User, Role

print("=" * 80)
print("TESTING LOGIN FOR ALL 4 ACTORS")
print("=" * 80)

# Get all roles
print("\n1. CHECKING ROLES IN DATABASE:")
print("-" * 80)
roles = Role.all()
for role in roles:
    print(f"  - {role.role_name} (ID: {role.id}, Code: {role.role_code})")

# Get all users
print("\n2. CHECKING USERS IN DATABASE:")
print("-" * 80)
users = User.all()
for user in users:
    role = Role.find(user.role_id)
    role_name = role.role_name if role else "Unknown"
    print(f"  - {user.username} ({role_name}) - Active: {user.is_active}")

# Test authentication for each role
print("\n3. TESTING AUTHENTICATION:")
print("-" * 80)

test_users = [
    ('admin_user', 'admin123', 'User Admin'),
    ('csr_user', 'csr123', 'CSR Rep'),
    ('pin_user', 'pin123', 'PIN'),
    ('platform_user', 'platform123', 'Platform Management')
]

for username, password, role_name in test_users:
    print(f"\nTesting: {username} with role '{role_name}'")
    
    # Check if user exists
    user = User.find_by_username(username)
    if not user:
        print(f"  [X] User '{username}' not found in database")
        continue
    
    print(f"  [OK] User found: {user.username}")
    print(f"  [OK] User role_id: {user.role_id}")
    print(f"  [OK] User is_active: {user.is_active}")
    
    # Check role
    role = Role.find_by_name(role_name)
    if not role:
        print(f"  [X] Role '{role_name}' not found")
        continue
    
    print(f"  [OK] Role found: {role.role_name} (ID: {role.id})")
    
    # Check if user's role matches
    if user.role_id != role.id:
        print(f"  [X] Role mismatch: user.role_id={user.role_id}, role.id={role.id}")
        continue
    
    print(f"  [OK] Role matches!")
    
    # Try authentication
    auth_user = User.authenticate(username, password, role_name)
    if auth_user:
        print(f"  [SUCCESS] AUTHENTICATION SUCCESS!")
    else:
        print(f"  [FAIL] AUTHENTICATION FAILED")
        
        # Try without role check
        auth_user_no_role = User.authenticate(username, password)
        if auth_user_no_role:
            print(f"  [WARN] Auth works WITHOUT role check - role matching issue!")
        else:
            print(f"  [WARN] Auth fails even without role check - password issue!")

print("\n" + "=" * 80)

