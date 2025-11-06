"""
Delete existing requests (clear test data before schema migration)
"""

from src.entity.supabase_config import get_supabase

def delete_all_requests():
    """Delete all existing requests"""
    supabase = get_supabase()
    
    print("=" * 60)
    print("DELETE ALL EXISTING REQUESTS")
    print("=" * 60)
    
    # First, check what we have
    result = supabase.table('requests').select('id, title').execute()
    
    if not result.data:
        print("\n✓ No requests to delete")
        return
    
    print(f"\nFound {len(result.data)} requests:")
    for req in result.data:
        print(f"  - ID {req['id']}: {req['title']}")
    
    print("\nDeleting all requests...")
    
    try:
        # Delete all requests
        delete_result = supabase.table('requests').delete().neq('id', 0).execute()
        print(f"\n✓ Successfully deleted all requests")
    except Exception as e:
        print(f"\n✗ Error deleting requests: {e}")
    
    # Verify deletion
    verify = supabase.table('requests').select('id').execute()
    if verify.data:
        print(f"\n⚠ Warning: {len(verify.data)} requests still remain")
    else:
        print("\n✓ Verified: All requests deleted")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Run SQL migration in Supabase Dashboard")
    print("2. Test creating new requests with mandatory fields")
    print("=" * 60)

if __name__ == '__main__':
    delete_all_requests()
