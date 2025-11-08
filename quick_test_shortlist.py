"""Quick Shortlist API Test"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Step 1: Login
print("=" * 60)
print("TEST 1: Login as CSR")
print("=" * 60)
login_data = {"username": "alice_csr", "password": "password123"}
r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    token = r.json()['token']
    csr_id = r.json()['user']['user_id']
    print(f"✅ Logged in as CSR ID: {csr_id}")
    headers = {'Authorization': f'Bearer {token}'}
else:
    print(f"❌ Login failed: {r.text}")
    exit()

# Step 2: Get shortlist (USER STORY #2 & #3)
print("\n" + "=" * 60)
print("USER STORY #2 & #3: Get Shortlist with Filters")
print("=" * 60)

print("\n--- Test: Get all shortlisted items ---")
r = requests.get(f"{BASE_URL}/api/shortlist?csr_user_id={csr_id}", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get('data', [])
    print(f"✅ Retrieved {len(items)} shortlisted items")
    if items:
        print(f"First item: {items[0].get('requests', {}).get('title', 'N/A')}")
else:
    print(f"Response: {r.text}")

# Step 3: Add to shortlist (USER STORY #1)
print("\n" + "=" * 60)
print("USER STORY #1: Add to Shortlist")
print("=" * 60)

# Get a request to shortlist
r = requests.get(f"{BASE_URL}/api/requests/pin", headers=headers)
if r.status_code == 200 and r.json().get('data'):
    req_id = r.json()['data'][0]['id']
    req_title = r.json()['data'][0]['title']
    print(f"Found request ID {req_id}: {req_title}")
    
    # Try to add it
    shortlist_data = {
        "csr_user_id": csr_id,
        "request_id": req_id,
        "notes": "Test shortlist"
    }
    r = requests.post(f"{BASE_URL}/api/shortlist/add", json=shortlist_data, headers=headers)
    print(f"Add to shortlist - Status: {r.status_code}")
    if r.status_code == 201:
        print(f"✅ Successfully added to shortlist")
    elif r.status_code == 400:
        print(f"✅ Already shortlisted (duplicate prevention works)")
    else:
        print(f"Response: {r.text}")

# Step 4: Filter by service type
print("\n--- Test: Filter by service type ---")
r = requests.get(f"{BASE_URL}/api/shortlist?csr_user_id={csr_id}&service_type=Education", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get('data', [])
    print(f"✅ Service type filter: {len(items)} Education items")

# Step 5: Filter by status
print("\n--- Test: Filter by status ---")
r = requests.get(f"{BASE_URL}/api/shortlist?csr_user_id={csr_id}&status=SHORTLISTED", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get('data', [])
    print(f"✅ Status filter: {len(items)} SHORTLISTED items")

# Step 6: Get stats
print("\n--- Test: Get shortlist stats ---")
r = requests.get(f"{BASE_URL}/api/shortlist/stats/{csr_id}", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    stats = r.json().get('data', {})
    print(f"✅ Stats: Total={stats.get('total')}, Shortlisted={stats.get('SHORTLISTED')}")

print("\n" + "=" * 60)
print("🎉 ALL TESTS COMPLETED!")
print("=" * 60)
