"""
User Entity Class - TRUE OOP Implementation
Holds user data in memory and performs operations on itself
"""

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
            print(f"Error: Password uses scrypt hash but cryptography library not installed")
            return False
        raise

from .supabase_config import get_supabase, SUPABASE_KEY, execute_with_retry


class User:
    """
    User Entity - TRUE OOP Implementation
    
    This class implements proper OOP:
    - Objects hold data in memory (instance variables)
    - Instance methods do the actual work (not wrappers)
    - Factory methods (class methods) for querying
    - No static methods for business logic
    
    Usage:
        # Create new user
        user = User()
        user.username = 'john_doe'
        user.email = 'john@example.com'
        user.password = 'password123'
        user.full_name = 'John Doe'
        user.role_id = 2
        user.save()  # Instance method does the work
        
        # Load existing user
        user = User.find_by_username('john_doe')
        user.full_name = 'John Smith'
        user.save()  # Updates database
        
        # Authenticate
        user = User.authenticate('john_doe', 'password123')
        if user:
            token = user.generate_session_token()
    """
    
    def __init__(self, user_id: Optional[int] = None, user_data: Optional[Dict] = None):
        """
        Initialize a User instance
        
        Args:
            user_id: Load existing user from database by ID
            user_data: Initialize with existing user data
            
        Example:
            user = User(user_id=42)
            user = User(user_data={'id': 42, 'username': 'john', ...})
            user = User()  # Create new empty user
        """
        # Instance variables (object state - data in memory)
        self.id: Optional[int] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.email: Optional[str] = None
        self.full_name: Optional[str] = None
        self.role_id: Optional[int] = None
        self.is_active: bool = True
        self.created_at: Optional[str] = None
        self.last_login: Optional[str] = None
        self.roles: Optional[Dict] = None  # Role information
        
        # Load data if provided
        if user_id is not None:
            self._load_from_id(user_id)
        elif user_data is not None:
            self._load_from_dict(user_data)
    
    # ============================================================================
    # PRIVATE METHODS (Internal use only)
    # ============================================================================
    
    def _load_from_id(self, user_id: int) -> None:
        """Load user data from database by ID (private method)"""
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('*, roles(*)')
            .eq('id', user_id)
            .execute()
        )
        if result and result.data:
            self._load_from_dict(result.data[0])
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.full_name = data.get('full_name')
        self.role_id = data.get('role_id')
        self.is_active = data.get('is_active', True)
        self.created_at = data.get('created_at')
        self.last_login = data.get('last_login')
        self.roles = data.get('roles')
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate user object state
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not self.email or '@' not in self.email:
            errors.append('Invalid email format')
        
        # Only validate password for new users (when password is set)
        if not self.id and (not self.password or len(self.password) < 8):
            errors.append('Password must be at least 8 characters')
        
        if not self.full_name or len(self.full_name) < 2:
            errors.append('Full name is required')
        
        if not self.role_id:
            errors.append('Role is required')
        
        return len(errors) == 0, errors
    
    def check_uniqueness(self) -> Tuple[bool, Optional[str]]:
        """
        Check if username/email already exists
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        supabase = get_supabase()
        
        # Check username (skip if updating existing user)
        query = supabase.table('users').select('id').eq('username', self.username)
        if self.id:
            query = query.neq('id', self.id)
        result = execute_with_retry(lambda: query.execute())
        if result and result.data:
            return False, f"Username '{self.username}' already exists"
        
        # Check email
        query = supabase.table('users').select('id').eq('email', self.email)
        if self.id:
            query = query.neq('id', self.id)
        result = execute_with_retry(lambda: query.execute())
        if result and result.data:
            return False, f"Email '{self.email}' already exists"
        
        return True, None
    
    # ============================================================================
    # CRUD METHODS (Instance methods - do the actual work)
    # ============================================================================
    
    def save(self) -> bool:
        """
        Save user to database (create or update)
        Instance method that DOES THE ACTUAL WORK
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If validation fails
        """
        # Validate
        is_valid, errors = self.validate()
        if not is_valid:
            raise ValueError('; '.join(errors))
        
        # Check uniqueness
        is_unique, error = self.check_uniqueness()
        if not is_unique:
            raise ValueError(error)
        
        supabase = get_supabase()
        
        if self.id:
            # Update existing user
            update_data = {
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'role_id': self.role_id,
                'is_active': self.is_active
            }
            
            result = execute_with_retry(
                lambda: supabase.table('users')
                .update(update_data)
                .eq('id', self.id)
                .execute()
            )
        else:
            # Create new user
            hashed_password = hash_password(self.password)
            insert_data = {
                'username': self.username,
                'password': hashed_password,
                'email': self.email,
                'full_name': self.full_name,
                'role_id': self.role_id,
                'is_active': self.is_active
            }
            
            result = execute_with_retry(
                lambda: supabase.table('users')
                .insert(insert_data)
                .execute()
            )
            
            if result and result.data:
                # Update object with new ID and created_at
                self.id = result.data[0]['id']
                self.created_at = result.data[0]['created_at']
                self.password = result.data[0]['password']  # Store hashed password
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this user from database
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If user has no ID
        """
        if not self.id:
            raise ValueError('Cannot delete user without ID')
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .delete()
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    def deactivate(self) -> bool:
        """Deactivate this user account"""
        self.is_active = False
        return self.save()
    
    def activate(self) -> bool:
        """Activate this user account"""
        self.is_active = True
        return self.save()
    
    def update_last_login(self) -> bool:
        """Update last login timestamp for this user"""
        if not self.id:
            return False
        
        supabase = get_supabase()
        now = datetime.now().isoformat()
        
        result = execute_with_retry(
            lambda: supabase.table('users')
            .update({'last_login': now})
            .eq('id', self.id)
            .execute()
        )
        
        if result and result.data:
            self.last_login = result.data[0]['last_login']
            return True
        return False
    
    # ============================================================================
    # PASSWORD METHODS (Instance methods)
    # ============================================================================
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password for this user
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches
        """
        if not self.password:
            return False
        return verify_password(self.password, password)
    
    def set_password(self, new_password: str) -> None:
        """
        Set new password for this user (hashes it)
        
        Args:
            new_password: Plain text password
            
        Raises:
            ValueError: If password is too short
        """
        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters')
        self.password = hash_password(new_password)
    
    # ============================================================================
    # AUTHENTICATION METHODS (Instance methods)
    # ============================================================================
    
    def generate_session_token(self) -> str:
        """
        Generate JWT session token for this user
        
        Returns:
            JWT token string
        """
        if not self.id:
            raise ValueError('Cannot generate token for user without ID')
        
        payload = {
            'user_id': self.id,
            'username': self.username,
            'role_id': self.role_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, SUPABASE_KEY, algorithm='HS256')
        return token
    
    # ============================================================================
    # UTILITY METHODS (Instance methods)
    # ============================================================================
    
    def to_dict(self, include_password: bool = False) -> Dict:
        """
        Convert instance to dictionary (for API responses)
        
        Args:
            include_password: Whether to include password hash (default: False for security)
        """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        
        if include_password:
            user_dict['password'] = self.password
        
        if self.roles:
            user_dict['roles'] = self.roles
        
        return user_dict
    
    def log_activity(self, activity_type: str, activity_details: str = None) -> bool:
        """
        Log activity for this user
        
        Args:
            activity_type: Type of activity (e.g., 'login', 'logout', 'update')
            activity_details: Additional details about the activity
            
        Returns:
            True if successful
        """
        if not self.id:
            return False
        
        supabase = get_supabase()
        
        try:
            result = execute_with_retry(
                lambda: supabase.table('user_activity_log').insert({
                    'user_id': self.id,
                    'activity_type': activity_type,
                    'activity_details': activity_details,
                    'created_at': datetime.now().isoformat()
                }).execute()
            )
            return bool(result and result.data)
        except Exception as e:
            print(f"[WARNING] Failed to log activity: {str(e)}")
            return False
    
    # ============================================================================
    # MAGIC METHODS (OOP features)
    # ============================================================================
    
    def __str__(self) -> str:
        """String representation"""
        return f"User({self.username})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Make hashable"""
        return hash(self.id) if self.id else hash(id(self))
    
    # ============================================================================
    # FACTORY METHODS (Class methods that return User objects)
    # ============================================================================
    
    @classmethod
    def find(cls, user_id: int) -> Optional['User']:
        """
        Factory method: Find and return a User instance by ID
        
        Args:
            user_id: User ID to find
            
        Returns:
            User object or None if not found
        """
        return cls(user_id=user_id) if user_id else None
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Factory method: Find user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('*, roles(*)')
            .eq('username', username)
            .execute()
        )
        
        if result and result.data:
            return cls(user_data=result.data[0])
        return None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """
        Factory method: Find user by email
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('*, roles(*)')
            .eq('email', email)
            .execute()
        )
        
        if result and result.data:
            return cls(user_data=result.data[0])
        return None
    
    @classmethod
    def all(cls, include_inactive: bool = False) -> List['User']:
        """
        Factory method: Get all users as User instances
        
        Args:
            include_inactive: Whether to include inactive users
            
        Returns:
            List of User objects
        """
        supabase = get_supabase()
        query = supabase.table('users').select('*, roles(*)')
        
        if not include_inactive:
            query = query.eq('is_active', True)
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(user_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_role(cls, role_id: int) -> List['User']:
        """
        Factory method: Get users by role ID
        
        Args:
            role_id: Role ID to filter by
            
        Returns:
            List of User objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('*, roles(*)')
            .eq('role_id', role_id)
            .execute()
        )
        
        if result and result.data:
            return [cls(user_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_role_name(cls, role_name: str) -> List['User']:
        """
        Factory method: Get users by role name
        
        Args:
            role_name: Role name to filter by
            
        Returns:
            List of User objects
        """
        from .role import Role
        role = Role.find_by_name(role_name)
        if not role:
            return []
        return cls.by_role(role.id)
    
    @classmethod
    def authenticate(cls, username: str, password: str, role_name: str = None) -> Optional['User']:
        """
        Factory method: Authenticate user and return User object
        
        Args:
            username: Username
            password: Plain text password
            role_name: Optional role name to verify
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Find user
        user = cls.find_by_username(username)
        if not user:
            return None
        
        # Verify password
        if not user.verify_password(password):
            return None
        
        # Check if active
        if not user.is_active:
            return None
        
        # Verify role if specified
        if role_name:
            from .role import Role
            role = Role.find_by_name(role_name)
            if not role or user.role_id != role.id:
                return None
        
        # Update last login
        user.update_last_login()
        
        return user
    
    @classmethod
    def verify_token(cls, token: str) -> Optional['User']:
        """
        Factory method: Verify JWT token and return User object
        
        Args:
            token: JWT token to verify
            
        Returns:
            User object if token valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SUPABASE_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                return cls.find(user_id)
        except jwt.ExpiredSignatureError:
            print("[WARNING] Token expired")
        except jwt.InvalidTokenError:
            print("[WARNING] Invalid token")
        except Exception as e:
            print(f"[ERROR] Token verification error: {str(e)}")
        
        return None
    
    @classmethod
    def search(cls, username: str = '', email: str = '', full_name: str = '') -> List['User']:
        """
        Factory method: Search users by multiple criteria
        
        Args:
            username: Username to search (partial match)
            email: Email to search (partial match)
            full_name: Full name to search (partial match)
            
        Returns:
            List of User objects matching criteria
        """
        supabase = get_supabase()
        query = supabase.table('users').select('*, roles(*)')
        
        if username:
            query = query.ilike('username', f'%{username}%')
        if email:
            query = query.ilike('email', f'%{email}%')
        if full_name:
            query = query.ilike('full_name', f'%{full_name}%')
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(user_data=data) for data in result.data]
        return []
    
    @classmethod
    def count_all(cls) -> int:
        """
        Factory method: Count total users
        
        Returns:
            Total number of users
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('id', count='exact')
            .execute()
        )
        return result.count if result else 0
    
    @classmethod
    def count_active(cls) -> int:
        """
        Factory method: Count active users
        
        Returns:
            Number of active users
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('id', count='exact')
            .eq('is_active', True)
            .execute()
        )
        return result.count if result else 0
