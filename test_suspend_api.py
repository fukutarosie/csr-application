"""Test suspend API endpoint"""
import requests
import json

print("=" * 60)
print("SUSPEND REQUEST API TEST")
print("=" * 60)

# First, get a token by logging in as a PIN user
print("\n1. Logging in as PIN user...")
login_response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'pin_user1',
    'password': 'password123',
    'role_name': 'PIN'
})

if login_response.status_code == 200:
    token = login_response.json()['data']['token']
    print(f"   ✓ Login successful, got token")
    
    # Get list of requests to find an ACTIVE one
    print("\n2. Getting list of ACTIVE requests...")
    requests_response = requests.get(
        'http://localhost:5000/api/requests?status=ACTIVE',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if requests_response.status_code == 200:
        requests_data = requests_response.json()
        if requests_data['data']:
            request_id = requests_data['data'][0]['id']
            print(f"   ✓ Found ACTIVE request ID: {request_id}")
            
            # Now try to suspend it
            print(f"\n3. Attempting to suspend request {request_id}...")
            suspend_response = requests.put(
                f'http://localhost:5000/api/requests/{request_id}/suspend',
                headers={'Authorization': f'Bearer {token}'},
                json={'reason': 'Test suspension from API test'}
            )
            
            print(f"   Status Code: {suspend_response.status_code}")
            print(f"   Response: {json.dumps(suspend_response.json(), indent=2)}")
            
            if suspend_response.status_code == 200:
                print("\n   ✓ SUSPEND API WORKS!")
            else:
                print("\n   ✗ SUSPEND API FAILED")
        else:
            print("   ℹ️  No ACTIVE requests found to test suspension")
    else:
        print(f"   ✗ Failed to get requests: {requests_response.status_code}")
else:
    print(f"   ✗ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")

print("\n" + "=" * 60)
