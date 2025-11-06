"""Check database relationships - simplified version"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv('environment.env')

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 70)
print("DATABASE RELATIONSHIP CHECK")
print("=" * 70)

# Get all service types from service_types table
print("\n1. SERVICE TYPES IN DATABASE:")
print("-" * 70)
service_types_result = supabase.table('service_types').select('id, service_name').order('service_name').execute()

service_types_dict = {}
if service_types_result.data:
    for st in service_types_result.data:
        service_types_dict[st['service_name']] = st['id']
        print(f"  • ID: {st['id']:<3} Name: {st['service_name']}")
else:
    print("  No service types found")

# Get all requests and check their service_type values
print("\n2. SERVICE TYPES USED IN REQUESTS:")
print("-" * 70)
requests_result = supabase.table('requests').select('id, title, service_type').execute()

if requests_result.data:
    unique_service_types = {}
    for req in requests_result.data:
        st = req.get('service_type')
        if st:
            if st not in unique_service_types:
                unique_service_types[st] = []
            unique_service_types[st].append(req['id'])
    
    print(f"\nFound {len(unique_service_types)} unique service types in requests:")
    for st_name, req_ids in sorted(unique_service_types.items()):
        count = len(req_ids)
        status = "✓ Valid" if st_name in service_types_dict else "✗ INVALID (not in service_types table)"
        print(f"  • {st_name:<30} Used in {count} request(s) - {status}")
else:
    print("  No requests found")

# Analysis
print("\n3. ANALYSIS:")
print("-" * 70)

print("\n📊 Current Schema:")
print("  • requests.service_type: TEXT field (stores the name)")
print("  • service_types.service_name: TEXT field (primary reference)")
print("  • service_types.id: INTEGER (primary key)")

print("\n❌ ISSUE: No Foreign Key Constraint")
print("  The requests.service_type field has NO foreign key constraint")
print("  to the service_types table. This means:")
print("    - Users can enter ANY text value (including invalid ones)")
print("    - No referential integrity enforcement")
print("    - Service types can be deleted even if in use")
print("    - Data inconsistency possible (typos, case sensitivity)")

print("\n✅ RECOMMENDED FIX:")
print("  Add a foreign key constraint to enforce referential integrity.")
print("  This will ensure only valid service types can be used.")

print("\n" + "=" * 70)
print("SOLUTION: Add Foreign Key Constraint")
print("=" * 70)
print("""
Run this SQL in your Supabase SQL Editor:

-- Add foreign key constraint
ALTER TABLE requests
ADD CONSTRAINT fk_requests_service_type
FOREIGN KEY (service_type)
REFERENCES service_types(service_name)
ON DELETE RESTRICT
ON UPDATE CASCADE;

This will:
✓ Prevent invalid service types from being inserted
✓ Prevent deleting service types that are in use
✓ Automatically update requests if service type names change
✓ Maintain data integrity
""")
print("=" * 70)
