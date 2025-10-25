from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .supabase_config import get_supabase

class Profile:
    @staticmethod
    def create_profile(profile_name: str, description: str = '') -> Tuple[bool, int]:
        """Create a new user profile"""
        supabase = get_supabase()
        
        try:
            profile_data = {
                "profile_name": profile_name,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Check if profile exists
            existing = supabase.table('profiles').select("*").eq('profile_name', profile_name).execute()
            if existing.data:
                return False, 409  # Conflict - profile already exists
            
            result = supabase.table('profiles').insert(profile_data).execute()
            return True, 201
            
        except Exception as e:
            print(f"Error creating profile: {str(e)}")
            return False, 500

    @staticmethod
    def get_profile_by_id(profile_id: int) -> Optional[Dict]:
        """Get profile by ID"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('profiles').select("*").eq('id', profile_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting profile: {str(e)}")
            return None

    @staticmethod
    def get_profile_by_name(profile_name: str) -> Optional[Dict]:
        """Get profile by name"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('profiles').select("*").eq('profile_name', profile_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting profile: {str(e)}")
            return None

    @staticmethod
    def get_all_profiles() -> List[Dict]:
        """Get all user profiles"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('profiles').select("*").order('created_at', desc=False).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting profiles: {str(e)}")
            return []

    @staticmethod
    def update_profile(profile_id: int, updates: Dict) -> Tuple[bool, int]:
        """Update profile details"""
        supabase = get_supabase()
        
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            result = supabase.table('profiles').update(updates).eq('id', profile_id).execute()
            
            if result.data:
                return True, 200
            else:
                return False, 404
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return False, 500

    @staticmethod
    def delete_profile(profile_id: int) -> Tuple[bool, int]:
        """Delete profile and cascade delete associated users"""
        supabase = get_supabase()
        
        try:
            # First, get all users with this profile
            users_result = supabase.table('users').select('id').eq('profile_id', profile_id).execute()
            user_ids = [u['id'] for u in users_result.data] if users_result.data else []
            
            # Delete all associated users
            if user_ids:
                for user_id in user_ids:
                    supabase.table('users').delete().eq('id', user_id).execute()
            
            # Delete the profile
            result = supabase.table('profiles').delete().eq('id', profile_id).execute()
            
            return True, 200
        except Exception as e:
            print(f"Error deleting profile: {str(e)}")
            return False, 500

    @staticmethod
    def search_profiles(query: str = '') -> List[Dict]:
        """Search profiles by name or description"""
        supabase = get_supabase()
        
        try:
            if not query:
                return Profile.get_all_profiles()
            
            result = supabase.table('profiles').select("*").execute()
            
            # Client-side filtering
            profiles = result.data if result.data else []
            filtered = [
                p for p in profiles
                if query.lower() in p.get('profile_name', '').lower() or 
                   query.lower() in p.get('description', '').lower()
            ]
            
            return filtered
        except Exception as e:
            print(f"Error searching profiles: {str(e)}")
            return []