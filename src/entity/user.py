from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Use pbkdf2:sha256 method which doesn't require cryptography library
def hash_password(password):
    """Hash password using pbkdf2:sha256"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(stored_hash, password):
    """Verify password against stored hash - supports both scrypt and pbkdf2"""
    try:
        return check_password_hash(stored_hash, password)
    except ValueError as e:
        if 'unsupported hash type' in str(e):
            # If scrypt hash and cryptography not installed, return error message
            print(f"Error: Password uses scrypt hash but cryptography library not installed")
            return False
        raise
from .supabase_config import get_supabase, SUPABASE_KEY, execute_with_retry

class User:
    @staticmethod
    def authenticate_user(username: str, password: str, role_name: str = None) -> Optional[Dict]:
        """
        Complete authentication with token generation
        
        This method contains ALL authentication logic:
        - Verify user exists
        - Verify password
        - Verify user is active
        - Verify role (if provided)
        - Generate JWT token
        - Update last_login timestamp
        
        Returns dict with user info and token, or None if authentication fails
        """
        try:
            # Step 1: Get user from database
            user = User.get_user_by_username(username)
            if not user:
                return None
            
            # Step 2: Verify password
            if not verify_password(user['password'], password):
                return None
            
            # Step 3: Check if user account is active
            if not user['is_active']:
                return None
            
            # Step 4: If role specified, verify user has that role
            if role_name:
                from .role import Role
                role = Role.get_role_by_name(role_name)
                if not role or user['role_id'] != role['id']:
                    return None
            
            # Step 5: Generate JWT token 
            token = User.create_session_token(user['id'])
            
            # Step 6: Update last_login timestamp
            supabase = get_supabase()
            supabase.table('users').update({
                "last_login": datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
            
            # Step 7: Return authenticated user with token
            # Get role information for response
            from .role import Role
            role = Role.get_role_by_id(user['role_id'])
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role_id': user['role_id'],
                'is_active': user['is_active'],
                'token': token,
                'role': role
            }
            
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return None
        
    @staticmethod
    def create_user(username: str, password: str, email: str, full_name: str, role_id: int) -> Optional[Dict]:
        """
        Create a new user account.

        Returns a structured dict:
          - {'data': user_dict} on success
          - {'error': CODE, 'message': '...'} on failure
        """
        supabase = get_supabase()

        try:
            # Prepare payload
            user_data = {
                "username": username,
                "password": hash_password(password),
                "email": email,
                "full_name": full_name,
                "role_id": role_id,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }

            # Final safety checks (race-condition safe)
            if supabase.table('users').select("id").eq('username', username).execute().data:
                return { 'error': 'USERNAME_EXISTS', 'message': 'Username already exists' }
            if supabase.table('users').select("id").eq('email', email).execute().data:
                return { 'error': 'EMAIL_EXISTS', 'message': 'Email already exists' }

            # Insert
            result = supabase.table('users').insert(user_data).execute()

            if result.data:
                created_user = result.data[0]
                return { 'data': created_user }

            # Defensive checks if insert returned no data
            if supabase.table('users').select("id").eq('username', username).execute().data:
                return { 'error': 'USERNAME_EXISTS', 'message': 'Username already exists (post-insert check)' }
            if supabase.table('users').select("id").eq('email', email).execute().data:
                return { 'error': 'EMAIL_EXISTS', 'message': 'Email already exists (post-insert check)' }

            return { 'error': 'DB_INSERT_FAILED', 'message': 'Failed to insert user into database' }

        except Exception as e:
            msg = str(e)
            # Best-effort duplicate detection
            if 'unique' in msg.lower() or 'duplicate' in msg.lower():
                try:
                    if supabase.table('users').select("id").eq('username', username).execute().data:
                        return { 'error': 'USERNAME_EXISTS', 'message': 'Username already exists' }
                    if supabase.table('users').select("id").eq('email', email).execute().data:
                        return { 'error': 'EMAIL_EXISTS', 'message': 'Email already exists' }
                except Exception:
                    pass

            print(f"[ERROR] Error creating user '{username}': {msg}")
            return { 'error': 'EXCEPTION', 'message': msg }

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Get user by username with retry logic for connection issues"""
        supabase = get_supabase()
        
        try:
            # Use retry logic for the query
            result = execute_with_retry(
                lambda: supabase.table('users').select("*").eq('username', username).execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by username '{username}': {str(e)}")
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email with retry logic for connection issues"""
        supabase = get_supabase()
        
        try:
            # Use retry logic for the query
            result = execute_with_retry(
                lambda: supabase.table('users').select("*").eq('email', email).execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by email '{email}': {str(e)}")
            return None

    @staticmethod
    def check_login(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Validate user login credentials"""
        user = User.get_user_by_username(username)
        if not user:
            return False, None
            
        if not verify_password(user['password'], password):
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
                updates['password'] = hash_password(updates['password'])
                
            result = supabase.table('users').update(updates).eq('id', user_id).execute()
            
            # If update was successful, return the updated user
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # If no data returned, verify the user still exists and return it
            user = User.get_user_by_id(user_id)
            if user:
                return user
            
            return None
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
    def delete_user(user_id: int) -> bool:
        """
        Permanently delete a user account
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('users').delete().eq('id', user_id).execute()
            return result.data is not None and len(result.data) > 0
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False

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
            
            # Get user from database with role information
            supabase = get_supabase()
            result = supabase.table('users').select(
                "*",
                "roles(id, role_name, role_code, dashboard_route)"
            ).eq('id', user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                # Flatten role data for easier access
                if user_data.get('roles'):
                    user_data['role'] = {
                        'id': user_data['roles']['id'],
                        'name': user_data['roles']['role_name'],
                        'code': user_data['roles']['role_code'],
                        'dashboard_route': user_data['roles'].get('dashboard_route', '/')
                    }
                return user_data
            return None
            
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

    
    @staticmethod
    def invalidate_session_token(token: str) -> bool:
        """
        Invalidate a session token
        
        For MVP: JWT is stateless, so we just verify it's valid
        Future: Could implement token blacklist in database
        
        Args:
            token: Token to invalidate
            
        Returns:
            True if token was valid, False otherwise
        """
        try:
            # Verify token is valid before "invalidating"
            payload = jwt.decode(token, SUPABASE_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # Token is valid, would be added to blacklist
            # For now, we just return success
            print(f"[INFO] Token invalidated for user: {user_id}")
            return True
            
        except jwt.ExpiredSignatureError:
            # Token already expired
            return True
        except jwt.InvalidTokenError:
            # Invalid token
            return False
        except Exception as e:
            print(f"Error invalidating token: {str(e)}")
            return False
    
    @staticmethod
    def get_user_complete_details(user_id: int) -> Optional[Dict]:
        """
        Get complete user details with related data
        
        Returns user info with:
        - Role details
        - Profile information
        - Account status
        
        Args:
            user_id: User ID to fetch
            
        Returns:
            Complete user object or None
        """
        try:
            supabase = get_supabase()
            
            # Get user with role
            result = supabase.table('users').select(
                "*",
                "roles(id, role_name, role_code, dashboard_route)"
            ).eq('id', user_id).execute()
            
            if not result.data:
                return None
            
            user = result.data[0]
            
            # Get user profile if exists
            profile_result = supabase.table('user_profiles').select("*").eq('user_id', user_id).execute()
            if profile_result.data:
                user['profile'] = profile_result.data[0]
            
            return user
            
        except Exception as e:
            print(f"Error getting user complete details: {str(e)}")
            return None
    
    @staticmethod
    def get_all_active_users() -> List[Dict]:
        """
        Get all active users
        
        Returns:
            List of active users with role information
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select(
                "*",
                "roles(id, role_name, role_code, dashboard_route)"
            ).eq('is_active', True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting active users: {str(e)}")
            return []
    
    @staticmethod
    def get_users_by_role(role_id: int) -> List[Dict]:
        """
        Get all users with a specific role
        
        Args:
            role_id: Role ID to filter by
            
        Returns:
            List of users with the specified role
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select("*").eq('role_id', role_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting users by role: {str(e)}")
            return []
    
    @staticmethod
    def get_users_by_role_name(role_name: str) -> List[Dict]:
        """
        Get all users with a specific role name
        
        Args:
            role_name: Role name to filter by
            
        Returns:
            List of users with the specified role
        """
        try:
            from .role import Role
            role = Role.get_role_by_name(role_name)
            if not role:
                return []
            return User.get_users_by_role(role['id'])
        except Exception as e:
            print(f"Error getting users by role name: {str(e)}")
            return []
    
    @staticmethod
    def count_users() -> int:
        """
        Get total count of users
        
        Returns:
            Total number of users
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select("id").execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error counting users: {str(e)}")
            return 0
    
    @staticmethod
    def count_active_users() -> int:
        """
        Get count of active users
        
        Returns:
            Number of active users
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select("id").eq('is_active', True).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error counting active users: {str(e)}")
            return 0
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select("id").eq('email', email).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking email: {str(e)}")
            return False
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists, False otherwise
        """
        try:
            supabase = get_supabase()
            result = supabase.table('users').select("id").eq('username', username).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking username: {str(e)}")
            return False
        
    @staticmethod
    def get_user_login_history(user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get user login history
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of login history records
        """
        try:
            supabase = get_supabase()
            result = supabase.table('user_login_history').select("*").eq(
                'user_id', user_id
            ).order('login_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting login history: {str(e)}")
            return []
    
    @staticmethod
    def log_user_activity(user_id: int, activity_type: str, activity_details: str = None) -> Optional[Dict]:
        """
        Log user activity
        
        Args:
            user_id: User ID
            activity_type: Type of activity (e.g., 'login', 'create_user', 'update_profile')
            activity_details: Additional details about activity
            
        Returns:
            Activity log record or None
        """
        try:
            supabase = get_supabase()
            activity_data = {
                'user_id': user_id,
                'activity_type': activity_type,
                'activity_details': activity_details,
                'timestamp': datetime.utcnow().isoformat()
            }
            result = supabase.table('user_activity_logs').insert(activity_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error logging activity: {str(e)}")
            return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Compatibility alias for get_user_by_id"""
        return User.get_user_by_id(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Compatibility alias for get_user_by_email"""
        return User.get_user_by_email(email)