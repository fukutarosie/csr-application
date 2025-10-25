from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from ..config.supabase import get_supabase, SUPABASE_KEY

class User:
    @staticmethod
    def create_user(username: str, password: str, email: str, full_name: str, role_id: int) -> Optional[Dict]:
        """Create a new user account"""
        supabase = get_supabase()
        
        try:
            user_data = {
                "username": username,
                "password": generate_password_hash(password),
                "email": email,
                "full_name": full_name,
                "role_id": role_id,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Check if username exists
            existing = supabase.table('users').select("*").eq('username', username).execute()
            if existing.data:
                return None
            
            result = supabase.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Get user by username"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('users').select("*").eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    @staticmethod
    def check_login(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Validate user login credentials"""
        user = User.get_user_by_username(username)
        if not user:
            return False, None
            
        if not check_password_hash(user['password'], password):
            return False, None
            
        if not user['is_active']:
            return False, None
            
        # Update last_login
        supabase = get_supabase()
        supabase.table('users').update({
            "last_login": datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
            
        return True, user

    @staticmethod
    def update_user(user_id: int, updates: Dict) -> Optional[Dict]:
        """Update user details"""
        supabase = get_supabase()
        
        try:
            # If password is being updated, hash it
            if 'password' in updates:
                updates['password'] = generate_password_hash(updates['password'])
                
            result = supabase.table('users').update(updates).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return None

    @staticmethod
    def get_all_users() -> List[Dict]:
        """Get all users with their roles"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('users').select(
                "*",
                "roles(role_name, role_code, dashboard_route)"
            ).execute()
            return result.data
        except Exception as e:
            print(f"Error getting users: {str(e)}")
            return []

    @staticmethod
    def deactivate_user(user_id: int) -> Optional[Dict]:
        """Deactivate a user account"""
        return User.update_user(user_id, {"is_active": False})

    @staticmethod
    def activate_user(user_id: int) -> Optional[Dict]:
        """Activate a user account"""
        return User.update_user(user_id, {"is_active": True})

    @staticmethod
    def create_session_token(user_id: int) -> str:
        """Create a new session token for a user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SUPABASE_KEY, algorithm='HS256')

    @staticmethod
    def verify_session_token(token: str) -> Optional[Dict]:
        """Verify a session token and return the user if valid"""
        try:
            payload = jwt.decode(token, SUPABASE_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Get user from database
            supabase = get_supabase()
            result = supabase.table('users').select("*").eq('id', user_id).execute()
            
            return result.data[0] if result.data else None
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('users').select(
                "*",
                "roles(id, role_name, role_code)"
            ).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    @staticmethod
    def search_users(username: str = '', email: str = '', full_name: str = '') -> List[Dict]:
        """Search users by multiple criteria"""
        supabase = get_supabase()
        
        try:
            query = supabase.table('users').select(
                "*",
                "roles(id, role_name, role_code)"
            )
            
            if username:
                query = query.ilike('username', f'%{username}%')
            
            result = query.execute()
            
            # Client-side filtering for email and full_name
            data = result.data if result.data else []
            
            if email:
                data = [u for u in data if u.get('email', '').lower().find(email.lower()) != -1]
            if full_name:
                data = [u for u in data if u.get('full_name', '').lower().find(full_name.lower()) != -1]
            
            return data
        except Exception as e:
            print(f"Error searching users: {str(e)}")
            return []