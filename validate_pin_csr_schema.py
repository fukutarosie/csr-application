"""
Validate PIN and CSR Entity Schema Alignment
Checks if database tables match entity class expectations
"""

from src.entity.supabase_config import get_supabase
from datetime import datetime

def validate_schema():
    supabase = get_supabase()
    
    print("=" * 80)
    print("PIN & CSR SCHEMA VALIDATION")
    print("=" * 80)
    
    # 1. Check REQUESTS table (PIN Entity)
    print("\n1. REQUESTS TABLE (PIN Entity)")
    print("-" * 80)
    try:
        result = supabase.table('requests').select('*').limit(1).execute()
        if result.data:
            sample = result.data[0]
            expected_fields = [
                'id', 'pin_user_id', 'title', 'description', 'category', 
                'service_type', 'priority', 'location_city', 'location_detail',
                'requested_by_date', 'status', 'is_archived', 'view_count',
                'shortlist_count', 'created_at', 'updated_at'
            ]
            actual_fields = list(sample.keys())
            
            print(f"✅ Table exists with {len(actual_fields)} fields")
            print(f"\nExpected fields ({len(expected_fields)}):")
            for field in expected_fields:
                if field in actual_fields:
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ MISSING: {field}")
            
            print(f"\nExtra fields in DB:")
            for field in actual_fields:
                if field not in expected_fields:
                    print(f"  ℹ️  {field}")
        else:
            print("⚠️  Table exists but has no data")
            
        # Count records
        count_result = supabase.table('requests').select('id', count='exact').execute()
        print(f"\n📊 Total requests: {count_result.count}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 2. Check SHORTLIST table (CSR Entity)
    print("\n\n2. SHORTLIST TABLE (CSR Entity)")
    print("-" * 80)
    try:
        result = supabase.table('shortlist').select('*').limit(1).execute()
        if result.data:
            sample = result.data[0]
            expected_fields = [
                'id', 'csr_user_id', 'request_id', 'status', 'notes',
                'shortlisted_at', 'updated_at', 'completed_at'
            ]
            actual_fields = list(sample.keys())
            
            print(f"✅ Table exists with {len(actual_fields)} fields")
            print(f"\nExpected fields ({len(expected_fields)}):")
            for field in expected_fields:
                if field in actual_fields:
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ MISSING: {field}")
            
            print(f"\nExtra fields in DB:")
            for field in actual_fields:
                if field not in expected_fields:
                    print(f"  ℹ️  {field}")
        else:
            print("⚠️  Table exists but has no data")
            
        # Count records
        count_result = supabase.table('shortlist').select('id', count='exact').execute()
        print(f"\n📊 Total shortlist entries: {count_result.count}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 3. Check REQUEST_CATEGORIES table
    print("\n\n3. REQUEST_CATEGORIES TABLE")
    print("-" * 80)
    try:
        result = supabase.table('request_categories').select('*').execute()
        if result.data:
            print(f"✅ Table exists with {len(result.data)} categories:")
            for cat in result.data:
                print(f"  • {cat.get('category_name', 'N/A')}")
        else:
            print("❌ Table exists but has no categories")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 4. Check SERVICE_TYPES table
    print("\n\n4. SERVICE_TYPES TABLE")
    print("-" * 80)
    try:
        result = supabase.table('service_types').select('*').execute()
        if result.data:
            print(f"✅ Table exists with {len(result.data)} service types:")
            for svc in result.data:
                print(f"  • {svc.get('service_name', 'N/A')}")
        else:
            print("❌ Table exists but has no service types")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 5. Check USERS table (role validation)
    print("\n\n5. USERS TABLE (Role Check)")
    print("-" * 80)
    try:
        # Check for PIN users (role_id = 2)
        pin_users = supabase.table('users').select('id, username, role_id').eq('role_id', 2).eq('is_active', True).execute()
        print(f"✅ Active PIN users: {len(pin_users.data)}")
        if pin_users.data:
            for user in pin_users.data[:3]:
                print(f"  • {user['username']} (ID: {user['id']})")
        
        # Check for CSR users (role_id = 3)
        csr_users = supabase.table('users').select('id, username, role_id').eq('role_id', 3).eq('is_active', True).execute()
        print(f"\n✅ Active CSR users: {len(csr_users.data)}")
        if csr_users.data:
            for user in csr_users.data[:3]:
                print(f"  • {user['username']} (ID: {user['id']})")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 6. Check ROLES table
    print("\n\n6. ROLES TABLE")
    print("-" * 80)
    try:
        result = supabase.table('roles').select('*').execute()
        if result.data:
            print(f"✅ Table exists with {len(result.data)} roles:")
            for role in result.data:
                print(f"  • ID {role['id']}: {role['role_name']} ({role['role_code']}) → {role.get('dashboard_route', 'N/A')}")
        else:
            print("❌ Table exists but has no roles")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 7. Check Foreign Key Relationships
    print("\n\n7. FOREIGN KEY VALIDATION")
    print("-" * 80)
    try:
        # Check requests.pin_user_id → users.id
        result = supabase.table('requests').select('id, pin_user_id', 'users(id, username)').limit(3).execute()
        if result.data:
            print("✅ requests.pin_user_id → users.id relationship working")
            for req in result.data:
                print(f"  Request {req['id']} → User {req.get('pin_user_id', 'N/A')}")
        
        # Check shortlist.csr_user_id → users.id
        result = supabase.table('shortlist').select('id, csr_user_id', 'users(id, username)').limit(3).execute()
        if result.data:
            print("\n✅ shortlist.csr_user_id → users.id relationship working")
            for sl in result.data:
                print(f"  Shortlist {sl['id']} → CSR User {sl.get('csr_user_id', 'N/A')}")
        
        # Check shortlist.request_id → requests.id
        result = supabase.table('shortlist').select('id, request_id', 'requests(id, title)').limit(3).execute()
        if result.data:
            print("\n✅ shortlist.request_id → requests.id relationship working")
            for sl in result.data:
                print(f"  Shortlist {sl['id']} → Request {sl.get('request_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # 8. Summary
    print("\n\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    issues = []
    
    # Check critical tables
    try:
        supabase.table('requests').select('id').limit(1).execute()
    except:
        issues.append("❌ requests table missing or inaccessible")
    
    try:
        supabase.table('shortlist').select('id').limit(1).execute()
    except:
        issues.append("❌ shortlist table missing or inaccessible")
    
    try:
        supabase.table('request_categories').select('id').limit(1).execute()
    except:
        issues.append("❌ request_categories table missing or inaccessible")
    
    try:
        supabase.table('service_types').select('id').limit(1).execute()
    except:
        issues.append("❌ service_types table missing or inaccessible")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ ALL CRITICAL TABLES EXIST AND ARE ACCESSIBLE")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    validate_schema()
