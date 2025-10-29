"""
Get PIN user credentials from Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

try:
    # Get one PIN user (role_id = 2)
    response = supabase.table('users').select('id, email, role_id').eq('role_id', 2).limit(1).execute()
    
    if response.data and len(response.data) > 0:
        user = response.data[0]
        print("\n✅ PIN User Found:")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Role ID: {user['role_id']} (PIN)")
        print(f"\n📧 Login with:")
        print(f"   Email: {user['email']}")
        print(f"   Password: (Use your password from setup)")
    else:
        print("❌ No PIN users found in database")
        
except Exception as e:
    print(f"Error: {e}")
