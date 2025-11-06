#!/usr/bin/env python3
"""
Test the service types API endpoint to verify it returns correct data
"""

import requests
import json

print("🔍 Testing Service Types API Endpoint")
print("=" * 60)

try:
    # Test the API endpoint
    url = "http://localhost:5000/api/requests/service-types"
    print(f"\n1. Making GET request to: {url}")
    
    response = requests.get(url)
    
    print(f"\n2. Response Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Success (200 OK)")
        
        # Parse JSON response
        data = response.json()
        print(f"\n3. Response Structure:")
        print(f"   - success: {data.get('success')}")
        print(f"   - message: {data.get('message')}")
        print(f"   - data type: {type(data.get('data'))}")
        print(f"   - data length: {len(data.get('data', []))}")
        
        print(f"\n4. Service Types Data:")
        service_types = data.get('data', [])
        
        if service_types:
            print(f"   Found {len(service_types)} service types:\n")
            for idx, st in enumerate(service_types, 1):
                print(f"   {idx}. ID: {st.get('id')}")
                print(f"      service_name: {st.get('service_name')}")
                print()
        else:
            print("   ⚠️  WARNING: data array is empty!")
        
        print("\n5. Raw JSON Response:")
        print(json.dumps(data, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ API TEST COMPLETE")
        
        if not service_types:
            print("\n⚠️  ISSUE FOUND: API returns empty data array")
            print("   This explains why the dropdown is empty!")
        
    else:
        print(f"   ✗ Error: Unexpected status code {response.status_code}")
        print(f"\n   Response Body:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to Flask backend")
    print("   Make sure Flask is running on http://localhost:5000")
    print("   Run: python app.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
