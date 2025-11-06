"""Supabase Database Configuration"""
from supabase import create_client
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Supabase client with environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Create client with timeout settings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Warm up the connection on module load
def _warmup_connection():
    """Warm up the Supabase connection to avoid cold start issues"""
    try:
        # Simple query to establish connection
        supabase.table('roles').select("id").limit(1).execute()
        print("[INFO] Supabase connection warmed up successfully")
    except Exception as e:
        print(f"[WARNING] Supabase warmup failed (will retry on first request): {str(e)}")

def get_supabase():
    """Get Supabase client instance with connection retry logic"""
    return supabase

def execute_with_retry(query_func, max_retries=2, retry_delay=0.5):
    """
    Execute a Supabase query with automatic retry on timeout/connection errors
    
    Args:
        query_func: Function that executes the query
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        Query result
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return query_func()
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            
            # Retry on timeout or connection errors
            if attempt < max_retries and ('timeout' in error_msg or 'connection' in error_msg):
                print(f"[WARNING] Query attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                # Don't retry other errors or if max retries reached
                raise
    
    # Should not reach here, but just in case
    raise last_error

# Warm up connection when module is loaded
_warmup_connection()

__all__ = ['get_supabase', 'supabase', 'SUPABASE_KEY', 'SUPABASE_URL', 'execute_with_retry']
