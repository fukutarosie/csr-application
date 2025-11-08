"""
Debug script to verify service types data flow
"""
import requests
import json

print("=" * 60)
print("SERVICE TYPES DEBUG TEST")
print("=" * 60)

# Test 1: Backend API directly
print("\n1. Testing Backend API (http://localhost:5000/api/requests/service-types)")
try:
    response = requests.get('http://localhost:5000/api/requests/service-types', timeout=5)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Data Count: {len(data.get('data', []))}")
        print(f"\n   Service Types:")
        for item in data.get('data', []):
            print(f"      - ID: {item.get('id')}, Name: {item.get('service_name')}")
    else:
        print(f"   Error: {response.text}")
except requests.exceptions.ConnectionError:
    print("   ❌ ERROR: Cannot connect to Flask backend")
    print("   ℹ️  Make sure Flask is running on http://localhost:5000")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 2: Frontend API through Next.js proxy
print("\n2. Testing Frontend API Call (http://localhost:3000)")
try:
    response = requests.get('http://localhost:3000/api/requests/service-types', timeout=5)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Data Count: {len(data.get('data', []))}")
    else:
        print(f"   Response: {response.text[:200]}")
except requests.exceptions.ConnectionError:
    print("   ❌ ERROR: Cannot connect to Next.js")
    print("   ℹ️  This is expected - Next.js doesn't have this route")
except Exception as e:
    print(f"   Note: {str(e)}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)
print("✓ Frontend should call: http://localhost:5000/api/requests/service-types")
print("✓ Expected response format:")
print("  {")
print('    "success": true,')
print('    "data": [')
print('      {"id": 7, "service_name": "Companionship Visit"},')
print('      {"id": 8, "service_name": "Grocery Shopping"},')
print("      ...")
print("    ]")
print("  }")
print("=" * 60)
