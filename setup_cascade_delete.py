#!/usr/bin/env python
"""Setup CASCADE DELETE constraint for roles -> users relationship"""

from src.config.supabase import supabase

def setup_cascade_delete():
    """
    Execute SQL to add CASCADE DELETE constraint.
    When a role is deleted, all users with that role are automatically deleted.
    """
    
    print("\n" + "=" * 80)
    print("SETTING UP CASCADE DELETE CONSTRAINT")
    print("=" * 80)
    
    # SQL to drop existing constraint and add new one with CASCADE DELETE
    sql = """
    -- Drop existing constraint if it exists
    ALTER TABLE users
    DROP CONSTRAINT IF EXISTS users_role_id_fkey;
    
    -- Add new constraint with CASCADE DELETE
    ALTER TABLE users
    ADD CONSTRAINT users_role_id_fkey
    FOREIGN KEY (role_id) REFERENCES roles(id)
    ON DELETE CASCADE;
    """
    
    try:
        print("\n[INFO] Executing CASCADE DELETE constraint setup...")
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        
        print("[OK] CASCADE DELETE constraint configured successfully!")
        print("\nDetails:")
        print("  - When a role is deleted from the 'roles' table")
        print("  - All users with that role will be automatically deleted from 'users' table")
        print("  - This happens at the database level (referential integrity)")
        
        return True
        
    except Exception as e:
        # RPC function not available - need manual setup
        print("[WARNING] Could not execute SQL directly via Python client.")
        print("\n" + "=" * 80)
        print("MANUAL SETUP INSTRUCTIONS")
        print("=" * 80)
        print("\nFollow these steps in Supabase Dashboard:")
        print("\n1. Go to: https://app.supabase.com")
        print("2. Select your project")
        print("3. Click 'SQL Editor' in the left sidebar")
        print("4. Click 'New Query'")
        print("5. Copy and paste this SQL command:")
        print("\n" + "-" * 80)
        print(sql)
        print("-" * 80)
        print("\n6. Click 'Run' button")
        print("7. You should see: 'ALTER TABLE' success message")
        print("\n" + "=" * 80)
        print("\nAfter running the SQL, all role deletes will automatically cascade!")
        print("=" * 80)
        return False

def verify_constraint():
    """Verify that the CASCADE DELETE constraint is in place"""
    
    print("\n" + "=" * 80)
    print("VERIFYING CASCADE DELETE CONSTRAINT")
    print("=" * 80)
    
    try:
        # Test query to check constraint
        result = supabase.table('users').select('*').limit(1).execute()
        print("[OK] Database connection verified")
        print("[INFO] To verify the constraint was created, check Supabase Dashboard:")
        print("       → Table 'users' → Relationships tab")
        print("       You should see: role_id -> roles(id) with 'ON DELETE: CASCADE'")
        return True
    except Exception as e:
        print(f"[FAIL] Error verifying connection: {str(e)}")
        return False

def main():
    """Run the setup"""
    print("\n" + "=" * 80)
    print("CASCADE DELETE SETUP SCRIPT")
    print("=" * 80)
    print("\nThis script sets up automatic deletion of users when their role is deleted.")
    print("Relationship: users.role_id -> roles.id (ON DELETE CASCADE)")
    
    # Setup constraint
    success = setup_cascade_delete()
    
    # Verify
    if success or True:  # Always try to verify even if setup seemed to fail
        verify_constraint()
    
    print("\n" + "=" * 80)
    if success:
        print("SETUP COMPLETE!")
        print("\nYour database now has CASCADE DELETE enabled.")
        print("Test it: Delete a role and watch users with that role disappear automatically!")
    else:
        print("MANUAL SETUP REQUIRED")
        print("\nPlease follow the SQL commands shown above in Supabase Dashboard.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
