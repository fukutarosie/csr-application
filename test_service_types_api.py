"""
Test the service types API endpoint
"""

import requests

def test_service_types_api():
    """Test the service types endpoint"""
    print("=" * 60)
    print("TESTING SERVICE TYPES API")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:5000/api/requests/service-types')
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse JSON:")
        print(response.json())
        
        if response.json().get('success'):
            data = response.json().get('data', [])
            print(f"\nTotal service types: {len(data)}")
            print("\nService types structure:")
            if data:
                print(f"First item: {data[0]}")
                print(f"Keys: {list(data[0].keys())}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_service_types_api()
