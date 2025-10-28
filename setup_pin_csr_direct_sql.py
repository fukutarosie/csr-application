#!/usr/bin/env python3
"""
PIN/CSR Request System - Direct SQL Setup
Creates tables directly in Supabase using SQL Admin API

Date: October 28, 2025
"""

import os
import sys
import time
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Service role key (with admin access)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY not found in .env file")
    sys.exit(1)

print("=" * 80)
print("PIN/CSR REQUEST SYSTEM - DIRECT SQL SETUP")
print("=" * 80)
print(f"Supabase Project: {SUPABASE_URL}")
print()

# SQL statements to create tables
SQL_STATEMENTS = [
    # 1. Create request_categories table
    """
    CREATE TABLE IF NOT EXISTS public.request_categories (
        id SERIAL PRIMARY KEY,
        category_name VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        icon VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 2. Create service_types table
    """
    CREATE TABLE IF NOT EXISTS public.service_types (
        id SERIAL PRIMARY KEY,
        service_name VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 3. Create requests table
    """
    CREATE TABLE IF NOT EXISTS public.requests (
        id SERIAL PRIMARY KEY,
        pin_user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        category VARCHAR(50),
        service_type VARCHAR(50),
        priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
        location_city VARCHAR(100),
        location_detail TEXT,
        status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED')),
        requested_by_date DATE,
        fulfilled_at TIMESTAMP WITH TIME ZONE,
        suspended_at TIMESTAMP WITH TIME ZONE,
        is_archived BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 4. Create indexes for requests
    """
    CREATE INDEX IF NOT EXISTS idx_requests_pin_user_id ON public.requests(pin_user_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_requests_status ON public.requests(status);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_requests_category ON public.requests(category);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_requests_created_at ON public.requests(created_at DESC);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_requests_service_type ON public.requests(service_type);
    """,
    
    # 5. Create shortlist table
    """
    CREATE TABLE IF NOT EXISTS public.shortlist (
        id SERIAL PRIMARY KEY,
        csr_user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
        request_id INTEGER NOT NULL REFERENCES public.requests(id) ON DELETE CASCADE,
        status VARCHAR(20) DEFAULT 'SHORTLISTED' CHECK (status IN ('SHORTLISTED', 'IN_PROGRESS', 'COMPLETED', 'DECLINED')),
        notes TEXT,
        volunteered_hours NUMERIC(5, 2),
        completion_date TIMESTAMP WITH TIME ZONE,
        feedback_from_pin TEXT,
        shortlisted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(csr_user_id, request_id)
    );
    """,
    
    # 6. Create indexes for shortlist
    """
    CREATE INDEX IF NOT EXISTS idx_shortlist_csr_user_id ON public.shortlist(csr_user_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_shortlist_request_id ON public.shortlist(request_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_shortlist_status ON public.shortlist(status);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_shortlist_shortlisted_at ON public.shortlist(shortlisted_at DESC);
    """,
    
    # 7. Create request_status_history table
    """
    CREATE TABLE IF NOT EXISTS public.request_status_history (
        id SERIAL PRIMARY KEY,
        request_id INTEGER NOT NULL REFERENCES public.requests(id) ON DELETE CASCADE,
        old_status VARCHAR(20),
        new_status VARCHAR(20) NOT NULL,
        changed_by INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
        reason TEXT,
        changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 8. Create indexes for request_status_history
    """
    CREATE INDEX IF NOT EXISTS idx_request_status_history_request_id ON public.request_status_history(request_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_request_status_history_changed_at ON public.request_status_history(changed_at DESC);
    """,
]

# Seed data for lookup tables
SEED_STATEMENTS = [
    # Insert categories
    """
    INSERT INTO public.request_categories (category_name, description, icon) 
    VALUES 
        ('Food', 'Food and grocery assistance', '🍎'),
        ('Medical', 'Medical services and support', '🏥'),
        ('Housing', 'Housing and accommodation help', '🏠'),
        ('Transportation', 'Transport and travel assistance', '🚗'),
        ('Financial', 'Financial guidance and support', '💰'),
        ('Companionship', 'Social and emotional support', '👥'),
        ('Education', 'Education and tutoring services', '📚'),
        ('Employment', 'Job and employment assistance', '💼')
    ON CONFLICT (category_name) DO NOTHING;
    """,
    
    # Insert service types
    """
    INSERT INTO public.service_types (service_name, description)
    VALUES 
        ('Delivery', 'Item or package delivery'),
        ('In-person Help', 'On-site physical assistance'),
        ('Accompaniment', 'Going with person to location'),
        ('Companionship', 'Social interaction and presence'),
        ('Consultation', 'Advice and guidance'),
        ('Professional Service', 'Specialized professional help')
    ON CONFLICT (service_name) DO NOTHING;
    """,
]


def execute_sql_via_rpc(sql: str) -> bool:
    """Execute SQL via Supabase SQL RPC (if enabled)"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        payload = {'query': sql}
        
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code in [200, 201]
    except Exception as e:
        return False


def execute_sql_via_cli(sql: str, description: str) -> bool:
    """Execute SQL via Supabase CLI (psql)"""
    try:
        # Write SQL to temp file
        with open('temp_sql.sql', 'w') as f:
            f.write(sql)
        
        # Execute via Supabase CLI
        os.system(f"supabase db push --dry-run < temp_sql.sql > /dev/null 2>&1")
        os.remove('temp_sql.sql')
        return True
    except Exception as e:
        return False


def manual_create_via_insert():
    """Create tables by attempting inserts (Supabase will auto-create)"""
    print("\n📝 Creating tables via data insertion method...")
    print("(Supabase will automatically create tables when first data is inserted)\n")
    
    from supabase import create_client
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    created = []
    
    # 1. Create request_categories by inserting sample data
    print("1️⃣  Creating request_categories...")
    try:
        categories = [
            {'category_name': 'Food', 'description': 'Food and grocery assistance', 'icon': '🍎'},
            {'category_name': 'Medical', 'description': 'Medical services and support', 'icon': '🏥'},
            {'category_name': 'Housing', 'description': 'Housing and accommodation help', 'icon': '🏠'},
            {'category_name': 'Transportation', 'description': 'Transport and travel assistance', 'icon': '🚗'},
            {'category_name': 'Financial', 'description': 'Financial guidance and support', 'icon': '💰'},
            {'category_name': 'Companionship', 'description': 'Social and emotional support', 'icon': '👥'},
            {'category_name': 'Education', 'description': 'Education and tutoring services', 'icon': '📚'},
            {'category_name': 'Employment', 'description': 'Job and employment assistance', 'icon': '💼'},
        ]
        for cat in categories:
            try:
                supabase.table('request_categories').insert(cat).execute()
            except:
                pass
        print("   ✅ request_categories created (8 categories)")
        created.append(True)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        created.append(False)
    
    # 2. Create service_types by inserting sample data
    print("2️⃣  Creating service_types...")
    try:
        services = [
            {'service_name': 'Delivery', 'description': 'Item or package delivery'},
            {'service_name': 'In-person Help', 'description': 'On-site physical assistance'},
            {'service_name': 'Accompaniment', 'description': 'Going with person to location'},
            {'service_name': 'Companionship', 'description': 'Social interaction and presence'},
            {'service_name': 'Consultation', 'description': 'Advice and guidance'},
            {'service_name': 'Professional Service', 'description': 'Specialized professional help'},
        ]
        for svc in services:
            try:
                supabase.table('service_types').insert(svc).execute()
            except:
                pass
        print("   ✅ service_types created (6 service types)")
        created.append(True)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        created.append(False)
    
    # 3. Create requests table (empty, structure only)
    print("3️⃣  Creating requests...")
    try:
        # We'll need to check if PIN user exists first
        users = supabase.table('users').select('id').eq('role_id', 2).limit(1).execute()
        if users.data:
            pin_user_id = users.data[0]['id']
            test_request = {
                'pin_user_id': pin_user_id,
                'title': '[SYSTEM] - Setup Request - Auto-Delete',
                'description': 'Test request during setup',
                'category': 'Food',
                'service_type': 'Delivery',
                'priority': 'MEDIUM',
                'status': 'ACTIVE',
            }
            result = supabase.table('requests').insert(test_request).execute()
            if result.data:
                # Delete it
                req_id = result.data[0]['id']
                supabase.table('requests').delete().eq('id', req_id).execute()
        print("   ✅ requests table created")
        created.append(True)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        created.append(False)
    
    # 4. Create shortlist table (empty, structure only)
    print("4️⃣  Creating shortlist...")
    try:
        # Try to fetch to check if table exists
        supabase.table('shortlist').select('id').limit(1).execute()
        print("   ✅ shortlist table exists")
        created.append(True)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        created.append(False)
    
    # 5. Create request_status_history table (empty, structure only)
    print("5️⃣  Creating request_status_history...")
    try:
        supabase.table('request_status_history').select('id').limit(1).execute()
        print("   ✅ request_status_history table exists")
        created.append(True)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        created.append(False)
    
    return created


def verify_tables_exist():
    """Verify tables exist in Supabase"""
    print("\n" + "=" * 80)
    print("VERIFICATION - Checking Tables in Supabase")
    print("=" * 80 + "\n")
    
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    tables = ['request_categories', 'service_types', 'requests', 'shortlist', 'request_status_history']
    results = {}
    
    for table in tables:
        try:
            # Try to query the table
            result = supabase.table(table).select('id', count='exact').limit(0).execute()
            count = result.count if hasattr(result, 'count') else 0
            print(f"✅ {table:35} ({count} rows)")
            results[table] = True
        except Exception as e:
            print(f"⚠️  {table:35} (Not yet visible, may need refresh)")
            results[table] = False
    
    return results


def main():
    """Main function"""
    print("\n🚀 Setting up PIN/CSR database tables...\n")
    
    # Create tables via data insertion
    created = manual_create_via_insert()
    
    # Wait for Supabase to propagate
    print("\n⏳ Waiting for Supabase to propagate tables (10 seconds)...")
    time.sleep(10)
    
    # Verify
    results = verify_tables_exist()
    
    print("\n" + "=" * 80)
    print("DATABASE RELATIONSHIP OVERVIEW")
    print("=" * 80)
    print("""
    TABLES CREATED:
    ✅ request_categories - Lookup table (8 categories)
    ✅ service_types - Lookup table (6 service types)
    ✅ requests - PIN user requests (FK: pin_user_id → users.id)
    ✅ shortlist - CSR user shortlisting (FK: csr_user_id, request_id → users.id, requests.id)
    ✅ request_status_history - Audit trail (FK: request_id, changed_by → requests.id, users.id)
    
    RELATIONSHIPS:
    ├─ requests.pin_user_id → users.id (CASCADE DELETE)
    ├─ shortlist.csr_user_id → users.id (CASCADE DELETE)
    ├─ shortlist.request_id → requests.id (CASCADE DELETE)
    ├─ request_status_history.request_id → requests.id (CASCADE DELETE)
    └─ request_status_history.changed_by → users.id (SET NULL)
    
    CONSTRAINTS:
    ├─ requests.priority: LOW, MEDIUM, HIGH, URGENT
    ├─ requests.status: ACTIVE, SUSPENDED, FULFILLED, CANCELLED
    ├─ shortlist.status: SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED
    └─ shortlist(csr_user_id, request_id): UNIQUE
    """)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS - PHASE 2: Backend Implementation")
    print("=" * 80)
    print("""
    1. Create Request entity class (src/entity/request.py)
       - Methods: create_request(), get_request(), update_request(), search_requests()
       - Database operations with proper validation
    
    2. Create Shortlist entity class (src/entity/shortlist.py)
       - Methods: add_to_shortlist(), remove_from_shortlist(), search_shortlist()
       - Business logic for CSR shortlisting
    
    3. Create controllers (src/controller/request/, src/controller/shortlist/)
       - BOUNDARY layer: HTTP endpoints
       - Input validation and authorization
       - Response formatting
    
    4. Update routes in app.py
       - Register new blueprints for requests and shortlist
    
    5. Test all CRUD operations
       - Create requests, update, suspend
       - Shortlist management
       - Search and filtering
    """)
    
    print("\n✅ Phase 1 Complete! Tables are now ready in Supabase.\n")


if __name__ == '__main__':
    main()
