"""
Add image_url column to requests table
Run this script to add image upload support
"""

from src.entity.supabase_config import get_supabase

def add_image_column():
    supabase = get_supabase()
    
    print("Adding image_url column to requests table...")
    
    try:
        # Note: Supabase Python client doesn't support ALTER TABLE
        # You'll need to run this SQL in Supabase Dashboard -> SQL Editor:
        
        sql_command = """
        ALTER TABLE requests 
        ADD COLUMN IF NOT EXISTS image_url TEXT;
        """
        
        print("\n" + "="*80)
        print("PLEASE RUN THIS SQL IN SUPABASE DASHBOARD:")
        print("="*80)
        print(sql_command)
        print("="*80)
        print("\nSteps:")
        print("1. Go to Supabase Dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL above")
        print("4. Click 'Run'")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    add_image_column()
