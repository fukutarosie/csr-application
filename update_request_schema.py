"""
Database Schema Update Script
Simplifies the requests table by removing unnecessary fields
"""

print("=" * 70)
print("DATABASE SCHEMA UPDATE - REQUESTS TABLE")
print("=" * 70)
print()
print("INSTRUCTIONS:")
print("1. Open your Supabase Dashboard")
print("2. Navigate to SQL Editor")
print("3. Copy and paste the SQL commands below")
print("4. Run each command one by one")
print()
print("=" * 70)
print()

print("STEP 1: Remove unnecessary columns")
print("-" * 70)
print("""
-- Remove category column (not needed)
ALTER TABLE requests 
DROP COLUMN IF EXISTS category;

-- Remove priority column (not needed)
ALTER TABLE requests 
DROP COLUMN IF EXISTS priority;

-- Remove location_detail column (not needed)
ALTER TABLE requests 
DROP COLUMN IF EXISTS location_detail;
""")

print()
print("STEP 2: Rename location_city to region")
print("-" * 70)
print("""
-- Rename location_city to region
ALTER TABLE requests 
RENAME COLUMN location_city TO region;
""")

print()
print("STEP 3: Drop request_categories table (no longer needed)")
print("-" * 70)
print("""
-- Drop the request_categories table
DROP TABLE IF EXISTS request_categories CASCADE;
""")

print()
print("=" * 70)
print("VERIFICATION QUERIES (Run after updates)")
print("=" * 70)
print("""
-- Check updated schema
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'requests'
ORDER BY ordinal_position;

-- Check remaining tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
""")

print()
print("=" * 70)
print("NOTE: Run update_service_types.py after this to add new service types")
print("=" * 70)
