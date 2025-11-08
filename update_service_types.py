"""
Update Service Types for CSR Platform
Adds meaningful service categories for volunteer opportunities
"""

from src.entity.supabase_config import get_supabase

def update_service_types():
    """Add practical service types for PIN-CSR matching"""
    supabase = get_supabase()
    
    # New service types based on common volunteer activities
    service_types = [
        'Companionship Visit',      # Spending time, conversation
        'Grocery Shopping',          # Shopping assistance
        'Meal Delivery',            # Food delivery
        'Transportation',           # Rides to appointments
        'Home Maintenance',         # Minor repairs, cleaning
        'Technology Help',          # Phone/computer assistance
        'Medical Escort',           # Accompany to doctor
        'Reading/Writing Help',     # Letters, forms, bills
        'Pet Care',                 # Walking, feeding pets
        'Errands',                  # General errands
    ]
    
    print("=" * 60)
    print("SERVICE TYPES UPDATE")
    print("=" * 60)
    
    # First, check current service types
    print("\n1. Checking current service types...")
    current = supabase.table('service_types').select('*').execute()
    
    if current.data:
        print(f"   Found {len(current.data)} existing service types:")
        for st in current.data:
            print(f"   - {st['service_name']}")
    else:
        print("   No existing service types found")
    
    # Clear existing service types (optional - comment out if you want to keep old ones)
    print("\n2. Clearing old service types...")
    try:
        supabase.table('service_types').delete().neq('id', 0).execute()
        print("   ✓ Old service types cleared")
    except Exception as e:
        print(f"   ⚠ Could not clear: {e}")
    
    # Insert new service types
    print("\n3. Inserting new service types...")
    success_count = 0
    
    for service_type in service_types:
        try:
            result = supabase.table('service_types').insert({
                'service_name': service_type
            }).execute()
            
            if result.data:
                print(f"   ✓ Added: {service_type}")
                success_count += 1
            else:
                print(f"   ✗ Failed: {service_type}")
        except Exception as e:
            print(f"   ✗ Error adding {service_type}: {e}")
    
    print(f"\n4. Summary: {success_count}/{len(service_types)} service types added")
    
    # Verify final state
    print("\n5. Verifying new service types...")
    final = supabase.table('service_types').select('*').execute()
    
    if final.data:
        print(f"   Total active service types: {len(final.data)}")
        print("\n   Available service types:")
        for st in final.data:
            print(f"   • {st['service_name']}")
    
    print("\n" + "=" * 60)
    print("✓ SERVICE TYPES UPDATE COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    update_service_types()
