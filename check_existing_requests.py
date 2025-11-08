"""
Check existing requests in database
"""

from src.entity.supabase_config import get_supabase

def check_existing_requests():
    """Display all existing requests"""
    supabase = get_supabase()
    
    print("=" * 80)
    print("EXISTING REQUESTS IN DATABASE")
    print("=" * 80)
    
    try:
        result = supabase.table('requests').select('*').execute()
        
        if result.data:
            print(f"\nTotal requests: {len(result.data)}")
            print("\nRequests:")
            print("-" * 80)
            for req in result.data:
                print(f"\nID: {req['id']}")
                print(f"  Title: {req.get('title', 'N/A')}")
                print(f"  PIN User ID: {req.get('pin_user_id', 'N/A')}")
                print(f"  Service Type: {req.get('service_type', 'N/A')}")
                print(f"  Category: {req.get('category', 'N/A')}")
                print(f"  Priority: {req.get('priority', 'N/A')}")
                print(f"  Region/Location: {req.get('region', req.get('location_city', 'N/A'))}")
                print(f"  Requested By: {req.get('requested_by_date', 'N/A')}")
                print(f"  Image URL: {req.get('image_url', 'N/A')}")
                print(f"  Status: {req.get('status', 'N/A')}")
                print(f"  Created: {req.get('created_at', 'N/A')}")
        else:
            print("\n✓ No existing requests found")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("\nRECOMMENDATION:")
    print("Since you're changing the schema, you should:")
    print("1. Delete existing test records (they have old schema)")
    print("2. Run the SQL migration to update schema")
    print("3. Create new test records with new schema")
    print("=" * 80)

if __name__ == '__main__':
    check_existing_requests()
