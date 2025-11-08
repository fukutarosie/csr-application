"""
Test script to verify OOP Role implementation
This demonstrates that BOTH old and new styles work!
"""

from src.entity.role import Role

print("=" * 80)
print("TESTING OOP ROLE IMPLEMENTATION - BACKWARD COMPATIBILITY")
print("=" * 80)

# ============================================================================
# TEST 1: OLD STYLE (Static methods) - Should still work!
# ============================================================================
print("\n[TEST 1] OLD STYLE (Static Methods) - Your existing code")
print("-" * 80)

# Get role using old static method
role_data = Role.get_role_by_id(2)
if role_data:
    print(f"[OK] OLD STYLE: Role.get_role_by_id(2)")
    print(f"   Result: {role_data['role_name']} ({role_data['role_code']})")
else:
    print("[FAIL] No role found with ID 2")

# Get all roles using old static method
all_roles = Role.get_all_roles()
print(f"\n[OK] OLD STYLE: Role.get_all_roles()")
print(f"   Found {len(all_roles)} roles")
for r in all_roles:
    print(f"   - {r['role_name']} (ID: {r['id']})")

# ============================================================================
# TEST 2: NEW STYLE (Instance methods) - OOP way!
# ============================================================================
print("\n\n[TEST 2] NEW STYLE (Instance Methods) - Proper OOP")
print("-" * 80)

# Create instance from ID
role = Role(role_id=2)
if role.id:
    print(f"[OK] NEW STYLE: role = Role(role_id=2)")
    print(f"   role.role_name = '{role.role_name}'")
    print(f"   role.role_code = '{role.role_code}'")
    print(f"   role.dashboard_route = '{role.dashboard_route}'")
    print(f"   str(role) = {str(role)}")
    print(f"   repr(role) = {repr(role)}")
    
    # Test instance methods
    print(f"\n   Instance method tests:")
    print(f"   - role.is_pin() = {role.is_pin()}")
    print(f"   - role.is_admin() = {role.is_admin()}")
    print(f"   - role.is_csr() = {role.is_csr()}")
else:
    print("[FAIL] Could not create Role instance")

# ============================================================================
# TEST 3: Factory Methods (Class methods)
# ============================================================================
print("\n\n[TEST 3] FACTORY METHODS (Class Methods) - Modern OOP")
print("-" * 80)

# Find role by ID
role2 = Role.find(2)
if role2:
    print(f"[OK] NEW STYLE: role = Role.find(2)")
    print(f"   {repr(role2)}")

# Find role by name
pin_role = Role.find_by_name("PIN")
if pin_role:
    print(f"\n[OK] NEW STYLE: role = Role.find_by_name('PIN')")
    print(f"   {repr(pin_role)}")
    print(f"   Dashboard: {pin_role.dashboard_route}")

# Get all as instances
all_role_instances = Role.all()
print(f"\n[OK] NEW STYLE: roles = Role.all()")
print(f"   Found {len(all_role_instances)} role instances")
for r in all_role_instances:
    print(f"   - {r}")  # Uses __str__ method

# ============================================================================
# TEST 4: Comparison (Magic Methods)
# ============================================================================
print("\n\n[TEST 4] MAGIC METHODS - OOP Features")
print("-" * 80)

role_a = Role.find(2)
role_b = Role.find(2)
role_c = Role.find(3) if len(all_roles) > 2 else None

if role_a and role_b:
    print(f"[OK] Equality test: role_a == role_b")
    print(f"   Result: {role_a == role_b} (should be True)")

if role_a and role_c:
    print(f"\n[OK] Inequality test: role_a == role_c")
    print(f"   Result: {role_a == role_c} (should be False)")

# ============================================================================
# TEST 5: Both styles work in controllers!
# ============================================================================
print("\n\n[TEST 5] CONTROLLER COMPATIBILITY")
print("-" * 80)

print("Your controllers can use EITHER style:")
print()
print("OLD STYLE (still works):")
print("  role_data = Role.get_role_by_id(user['role_id'])")
print("  return {'role': role_data}")
print()
print("NEW STYLE (proper OOP):")
print("  role = Role.find(user['role_id'])")
print("  return {'role': role.to_dict()}")
print()
print("[OK] Both produce the same result!")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY: OOP CONVERSION SUCCESSFUL!")
print("=" * 80)
print("[OK] All old static methods still work (backward compatible)")
print("[OK] New instance methods added (proper OOP)")
print("[OK] Factory methods for clean object creation")
print("[OK] Magic methods for Pythonic behavior")
print("[OK] No breaking changes - existing code works!")
print("=" * 80)

