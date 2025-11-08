"""Check database relationships and constraints"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv('environment.env')

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 70)
print("DATABASE SCHEMA CHECK - REQUESTS TABLE")
print("=" * 70)

# Check requests table structure
print("\n1. REQUESTS TABLE COLUMNS:")
print("-" * 70)
result = supabase.rpc('exec_sql', {
    'sql': """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns 
    WHERE table_name = 'requests' 
    ORDER BY ordinal_position;
    """
}).execute()

if result.data:
    for col in result.data:
        print(f"  • {col['column_name']:<25} {col['data_type']:<15} "
              f"Nullable: {col['is_nullable']:<5} Default: {col['column_default'] or 'None'}")
else:
    print("  Could not fetch columns")

# Check foreign key constraints on requests table
print("\n2. FOREIGN KEY CONSTRAINTS ON REQUESTS TABLE:")
print("-" * 70)
result = supabase.rpc('exec_sql', {
    'sql': """
    SELECT
        tc.constraint_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = 'requests';
    """
}).execute()

if result.data:
    for fk in result.data:
        print(f"  • {fk['constraint_name']}")
        print(f"    Column: {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
else:
    print("  ✗ No foreign keys found on requests table")

# Check service_types table structure
print("\n3. SERVICE_TYPES TABLE COLUMNS:")
print("-" * 70)
result = supabase.rpc('exec_sql', {
    'sql': """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns 
    WHERE table_name = 'service_types' 
    ORDER BY ordinal_position;
    """
}).execute()

if result.data:
    for col in result.data:
        print(f"  • {col['column_name']:<25} {col['data_type']:<15} "
              f"Nullable: {col['is_nullable']:<5} Default: {col['column_default'] or 'None'}")
else:
    print("  Service_types table not found or no columns")

# Check sample data from both tables
print("\n4. SAMPLE DATA COMPARISON:")
print("-" * 70)

print("\nService Types in service_types table:")
result = supabase.table('service_types').select('id, service_name').order('service_name').execute()
if result.data:
    for st in result.data:
        print(f"  • ID: {st['id']:<3} Name: {st['service_name']}")

print("\nService Types used in requests table:")
result = supabase.table('requests').select('service_type').execute()
if result.data:
    unique_types = list(set([r['service_type'] for r in result.data if r.get('service_type')]))
    unique_types.sort()
    for st in unique_types:
        print(f"  • {st}")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
print("""
If no foreign key constraint is found, you should add one to ensure:
1. Data integrity (only valid service types can be inserted)
2. Referential integrity (can't delete service types that are in use)
3. Better database design and performance

However, note that:
- requests.service_type is TEXT (stores the name like 'Grocery Shopping')
- service_types.service_name is TEXT (the name)
- service_types.id is INTEGER (the primary key)

You have two options:
A) Add FK: requests.service_type -> service_types.service_name
B) Change requests to use service_type_id INTEGER -> service_types.id
   (This is better practice but requires migration)
""")
print("=" * 70)
