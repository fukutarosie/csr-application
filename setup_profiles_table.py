#!/usr/bin/env python3
"""
Setup script to create the profiles table in Supabase
Run this once to initialize the profiles table
"""

from src.config.supabase import get_supabase

def setup_profiles_table():
    """Create the profiles table in Supabase"""
    supabase = get_supabase()
    
    print("\n" + "="*60)
    print("SETTING UP PROFILES TABLE IN SUPABASE")
    print("="*60 + "\n")
    
    # First, check if profiles table exists
    try:
        result = supabase.table('profiles').select('*').limit(1).execute()
        print("✓ Profiles table already exists!")
        print(f"  Current profiles: {len(result.data)}")
        return True
    except Exception as e:
        print(f"⚠ Profiles table does not exist yet: {str(e)}")
        print("\nYou need to create the profiles table manually in Supabase.")
        print("\nFollow these steps:")
        print("\n1. Go to: https://app.supabase.com/project/gfmghhgmcvgiuqkapzkv/sql")
        print("\n2. Click 'New Query' and paste this SQL:")
        print("""
-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id BIGSERIAL PRIMARY KEY,
  profile_name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on profile_name for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(profile_name);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Allow anon users to read profiles
CREATE POLICY "Allow read access to profiles" ON profiles
  FOR SELECT USING (true);

-- Allow authenticated users to manage profiles (User Admin only)
CREATE POLICY "Allow authenticated users to create profiles" ON profiles
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update profiles" ON profiles
  FOR UPDATE USING (true);

CREATE POLICY "Allow authenticated users to delete profiles" ON profiles
  FOR DELETE USING (true);
        """)
        print("\n3. Click 'Run'")
        print("\n4. Then run this script again")
        print("\n" + "="*60)
        return False

def add_profile_id_to_users():
    """Add profile_id column to users table if it doesn't exist"""
    supabase = get_supabase()
    
    print("\nSetting up profile_id foreign key in users table...")
    
    try:
        # Try to query users with profile_id
        result = supabase.table('users').select('profile_id').limit(1).execute()
        print("✓ Users table already has profile_id column")
        return True
    except Exception as e:
        print(f"⚠ profile_id column missing: {str(e)}")
        print("\nYou need to add profile_id to users table manually in Supabase.")
        print("\n1. Go to: https://app.supabase.com/project/gfmghhgmcvgiuqkapzkv/sql")
        print("\n2. Click 'New Query' and paste this SQL:")
        print("""
-- Add profile_id to users table if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_id BIGINT REFERENCES profiles(id) ON DELETE SET NULL;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_profile_id ON users(profile_id);
        """)
        print("\n3. Click 'Run'")
        print("\n4. Then run this script again")
        print("\n" + "="*60)
        return False

def insert_default_profiles():
    """Insert default profiles"""
    supabase = get_supabase()
    
    print("\nInserting default profiles...")
    
    default_profiles = [
        {"profile_name": "User Admin", "description": "Administrator for user management"},
        {"profile_name": "PIN", "description": "PIN verification specialist"},
        {"profile_name": "CSR Rep", "description": "Customer Service Representative"},
        {"profile_name": "Platform Management", "description": "System administrator"}
    ]
    
    try:
        for profile in default_profiles:
            # Check if profile already exists
            existing = supabase.table('profiles').select('*').eq('profile_name', profile['profile_name']).execute()
            
            if not existing.data:
                result = supabase.table('profiles').insert(profile).execute()
                print(f"✓ Created profile: {profile['profile_name']}")
            else:
                print(f"✓ Profile already exists: {profile['profile_name']}")
        
        return True
    except Exception as e:
        print(f"✗ Error inserting profiles: {str(e)}")
        return False

def main():
    """Run setup"""
    print("\n🔧 Supabase Profile Table Setup\n")
    
    # Step 1: Setup profiles table
    if not setup_profiles_table():
        print("\n❌ Setup incomplete - Please create the profiles table manually first")
        return False
    
    # Step 2: Add profile_id to users
    if not add_profile_id_to_users():
        print("\n❌ Setup incomplete - Please add profile_id column manually first")
        return False
    
    # Step 3: Insert default profiles
    if not insert_default_profiles():
        print("\n⚠ Some profiles failed to insert, but setup is mostly complete")
        return False
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nYour Supabase database is now ready for profiles integration.")
    print("You can now:")
    print("  1. Run the application with: .\\run.ps1")
    print("  2. Create new profiles from the dashboard")
    print("  3. Create users and assign them profiles")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
