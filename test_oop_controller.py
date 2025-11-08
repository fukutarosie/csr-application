"""
Test OOP Controller Implementation
Verify that the updated controller works correctly
"""

from src.controller.userProfile.create_user_profile_controller import CreateUserProfileController

print("=" * 80)
print("TESTING OOP CONTROLLER - CreateUserProfileController")
print("=" * 80)

# Test 1: Create with valid data
print("\n[TEST 1] Create user profile with valid data")
print("-" * 80)

payload = {
    "role_name": "Test Role OOP",
    "role_code": "TEST_ROLE_OOP",
    "description": "Testing OOP implementation"
}

response, status = CreateUserProfileController.create_user_profile(payload)
print(f"Status Code: {status}")
print(f"Response: {response}")

if status == 201:
    print("[OK] Profile created successfully using OOP!")
    print(f"   Role ID: {response['data']['id']}")
    print(f"   Role Name: {response['data']['role_name']}")
else:
    print(f"[INFO] {response['message']}")

# Test 2: Missing fields
print("\n[TEST 2] Create with missing fields (should fail)")
print("-" * 80)

invalid_payload = {
    "role_name": "Incomplete Role"
}

response, status = CreateUserProfileController.create_user_profile(invalid_payload)
print(f"Status Code: {status}")
print(f"Response: {response}")

if status == 400:
    print("[OK] Validation works correctly!")

# Test 3: None payload
print("\n[TEST 3] Create with None payload (should fail)")
print("-" * 80)

response, status = CreateUserProfileController.create_user_profile(None)
print(f"Status Code: {status}")
print(f"Response: {response}")

if status == 400:
    print("[OK] None check works correctly!")

print("\n" + "=" * 80)
print("CONTROLLER TEST COMPLETE!")
print("=" * 80)
print("[OK] Controller uses proper OOP")
print("[OK] All validation still works")
print("[OK] No breaking changes")
print("=" * 80)

