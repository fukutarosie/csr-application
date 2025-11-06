"""
Check current service types in Supabase database
"""

from src.entity.supabase_config import get_supabase

def check_service_types():
    """Display all service types currently in the database"""
    supabase = get_supabase()
    
    print("=" * 60)
    print("CURRENT SERVICE TYPES IN DATABASE")
    print("=" * 60)
    
    try:
        result = supabase.table('service_types').select('*').execute()
        
        if result.data:
            print(f"\nTotal service types: {len(result.data)}")
            print("\nService Types:")
            print("-" * 60)
            for i, st in enumerate(result.data, 1):
                print(f"{i:2d}. {st['service_name']} (ID: {st['id']})")
        else:
            print("\n⚠ No service types found in database!")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_service_types()
