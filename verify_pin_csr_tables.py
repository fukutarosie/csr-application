#!/usr/bin/env python3
"""
PIN/CSR Tables Verification Script
Checks if all new tables were created successfully in Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("PIN/CSR DATABASE VERIFICATION")
print("=" * 80)
print()

# Tables to verify
tables_to_check = {
    'request_categories': 'Lookup - Request Categories',
    'service_types': 'Lookup - Service Types',
    'requests': 'Main - PIN Requests',
    'shortlist': 'Main - CSR Shortlist',
    'request_status_history': 'Audit - Request History'
}

results = {}

for table_name, description in tables_to_check.items():
    try:
        # Try to query the table
        result = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        row_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
        print(f"✅ {table_name:30} ({description})")
        print(f"   └─ Row count: {row_count}")
        results[table_name] = True
    except Exception as e:
        print(f"❌ {table_name:30} ({description})")
        print(f"   └─ Error: {str(e)[:60]}...")
        results[table_name] = False

print()
print("=" * 80)

success_count = sum(1 for v in results.values() if v)
total_count = len(results)

if success_count == total_count:
    print(f"✅ ALL {total_count} TABLES VERIFIED - READY FOR PHASE 2!")
    print("=" * 80)
    print()
    print("📝 Next Steps:")
    print("   1. Create Request entity class (src/entity/request.py)")
    print("   2. Create Shortlist entity class (src/entity/shortlist.py)")
    print("   3. Create request controllers (src/controller/request/)")
    print("   4. Create shortlist controllers (src/controller/shortlist/)")
    print("   5. Test all CRUD operations")
    print()
else:
    print(f"⚠️  {success_count}/{total_count} tables verified")
    print("=" * 80)
    print()
    print("❌ Some tables are missing. Please:")
    print("   1. Re-run the SQL in Supabase SQL Editor")
    print("   2. Check PIN_CSR_SETUP_COMPLETE.md for instructions")
    print()

print("=" * 80)
