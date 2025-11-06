"""
Verify Service Types in Supabase Database
"""

from src.entity.supabase_config import get_supabase

def verify_service_types():
    """Check what service types are currently in Supabase"""
    supabase = get_supabase()
    
    print("=" * 60)
    print("VERIFYING SERVICE TYPES IN SUPABASE DATABASE")
    print("=" * 60)
    
    try:
        # Fetch all service types from database
        result = supabase.table('service_types').select('*').execute()
        
        if result.data:
            print(f"\n✓ Found {len(result.data)} service types in Supabase:\n")
            for idx, service_type in enumerate(result.data, 1):
                print(f"   {idx}. {service_type['service_name']} (ID: {service_type['id']})")
        else:
            print("\n✗ No service types found in database!")
            print("   Please run: python update_service_types.py")
    
    except Exception as e:
        print(f"\n✗ Error connecting to Supabase: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    verify_service_types()
