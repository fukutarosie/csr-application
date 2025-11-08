"""
Quick diagnostic script to check shortlist data in database
"""
from src.config.supabase import get_supabase

def check_shortlist_data():
    supabase = get_supabase()
    
    print("=" * 60)
    print("CHECKING SHORTLIST DATA")
    print("=" * 60)
    
    # Check all shortlist entries
    print("\n1. All Shortlist Entries:")
    shortlist = supabase.table('shortlist').select('*').execute()
    print(f"   Total entries: {len(shortlist.data)}")
    for item in shortlist.data[:5]:  # Show first 5
        print(f"   - ID: {item['id']}, CSR User: {item['csr_user_id']}, Request: {item['request_id']}, Status: {item['status']}")
    
    # Check CSR users
    print("\n2. CSR Users (role_id=3):")
    csr_users = supabase.table('users').select('id, username, email, role_id').eq('role_id', 3).execute()
    print(f"   Total CSR users: {len(csr_users.data)}")
    for user in csr_users.data[:5]:
        print(f"   - ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    
    # Check active requests
    print("\n3. Active Requests:")
    requests = supabase.table('requests').select('id, title, status').eq('status', 'ACTIVE').execute()
    print(f"   Total active requests: {len(requests.data)}")
    for req in requests.data[:5]:
        print(f"   - ID: {req['id']}, Title: {req['title']}, Status: {req['status']}")
    
    # Check shortlist with JOIN (mimics the actual query)
    print("\n4. Shortlist with JOIN (like API does):")
    shortlist_join = supabase.table('shortlist').select(
        "*",
        "requests(*)",
        "users(id, username, full_name, email)"
    ).execute()
    print(f"   Total with JOIN: {len(shortlist_join.data)}")
    for item in shortlist_join.data[:3]:
        print(f"   - Shortlist ID: {item['id']}")
        print(f"     CSR User: {item.get('users', {}).get('username', 'N/A')}")
        print(f"     Request: {item.get('requests', {}).get('title', 'N/A')}")
        print(f"     Status: {item['status']}")
    
    # If you have a specific CSR user, check their shortlist
    if csr_users.data:
        test_csr_id = csr_users.data[0]['id']
        print(f"\n5. Shortlist for CSR User ID {test_csr_id} ({csr_users.data[0]['username']}):")
        user_shortlist = supabase.table('shortlist').select(
            "*",
            "requests(*)"
        ).eq('csr_user_id', test_csr_id).execute()
        print(f"   Items: {len(user_shortlist.data)}")
        for item in user_shortlist.data:
            print(f"   - {item.get('requests', {}).get('title', 'N/A')} (Status: {item['status']})")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_shortlist_data()
