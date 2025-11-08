"""
Profile Entity Class - TRUE OOP Implementation
Holds profile data in memory and performs operations on itself
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase, execute_with_retry


class Profile:
    """
    Profile Entity - TRUE OOP Implementation
    
    This class implements proper OOP:
    - Objects hold data in memory (instance variables)
    - Instance methods do the actual work (not wrappers)
    - Factory methods (class methods) for querying
    - No static methods for business logic
    
    Usage:
        # Create new profile
        profile = Profile()
        profile.profile_name = 'Admin Profile'
        profile.description = 'Administrator profile'
        profile.save()  # Instance method does the work
        
        # Load existing profile
        profile = Profile.find_by_name('Admin Profile')
        profile.description = 'Updated description'
        profile.save()  # Updates database
    """
    
    def __init__(self, profile_id: Optional[int] = None, profile_data: Optional[Dict] = None):
        """
        Initialize a Profile instance
        
        Args:
            profile_id: Load existing profile from database by ID
            profile_data: Initialize with existing profile data
            
        Example:
            profile = Profile(profile_id=1)
            profile = Profile(profile_data={'id': 1, 'profile_name': 'Admin', ...})
            profile = Profile()  # Create new empty profile
        """
        # Instance variables (object state - data in memory)
        self.id: Optional[int] = None
        self.profile_name: Optional[str] = None
        self.description: Optional[str] = None
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
        
        # Load data if provided
        if profile_id is not None:
            self._load_from_id(profile_id)
        elif profile_data is not None:
            self._load_from_dict(profile_data)
    
    # ============================================================================
    # PRIVATE METHODS (Internal use only)
    # ============================================================================
    
    def _load_from_id(self, profile_id: int) -> None:
        """Load profile data from database by ID (private method)"""
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('profiles')
            .select('*')
            .eq('id', profile_id)
            .execute()
        )
        if result and result.data:
            self._load_from_dict(result.data[0])
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.profile_name = data.get('profile_name')
        self.description = data.get('description')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate profile object state
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.profile_name or len(self.profile_name) < 2:
            errors.append('Profile name must be at least 2 characters')
        
        return len(errors) == 0, errors
    
    def check_uniqueness(self) -> tuple[bool, Optional[str]]:
        """
        Check if profile_name already exists
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        supabase = get_supabase()
        
        # Check profile_name (skip if updating existing profile)
        query = supabase.table('profiles').select('id').eq('profile_name', self.profile_name)
        if self.id:
            query = query.neq('id', self.id)
        result = execute_with_retry(lambda: query.execute())
        if result and result.data:
            return False, f"Profile name '{self.profile_name}' already exists"
        
        return True, None
    
    # ============================================================================
    # CRUD METHODS (Instance methods - do the actual work)
    # ============================================================================
    
    def save(self) -> bool:
        """
        Save profile to database (create or update)
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
            # Update existing profile
            update_data = {
                'profile_name': self.profile_name,
                'description': self.description,
                'updated_at': datetime.now().isoformat()
            }
            
            result = execute_with_retry(
                lambda: supabase.table('profiles')
                .update(update_data)
                .eq('id', self.id)
                .execute()
            )
            
            if result and result.data:
                self.updated_at = result.data[0]['updated_at']
        else:
            # Create new profile
            insert_data = {
                'profile_name': self.profile_name,
                'description': self.description or ''
            }
            
            result = execute_with_retry(
                lambda: supabase.table('profiles')
                .insert(insert_data)
                .execute()
            )
            
            if result and result.data:
                # Update object with new ID and timestamps
                self.id = result.data[0]['id']
                self.created_at = result.data[0]['created_at']
                self.updated_at = result.data[0].get('updated_at')
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this profile from database
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If profile has no ID
        """
        if not self.id:
            raise ValueError('Cannot delete profile without ID')
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('profiles')
            .delete()
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    # ============================================================================
    # UTILITY METHODS (Instance methods)
    # ============================================================================
    
    def to_dict(self) -> Dict:
        """Convert instance to dictionary (for API responses)"""
        return {
            'id': self.id,
            'profile_name': self.profile_name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    # ============================================================================
    # MAGIC METHODS (OOP features)
    # ============================================================================
    
    def __str__(self) -> str:
        """String representation"""
        return f"Profile({self.profile_name})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Profile(id={self.id}, profile_name='{self.profile_name}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Profile):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Make hashable"""
        return hash(self.id) if self.id else hash(id(self))
    
    # ============================================================================
    # FACTORY METHODS (Class methods that return Profile objects)
    # ============================================================================
    
    @classmethod
    def find(cls, profile_id: int) -> Optional['Profile']:
        """
        Factory method: Find and return a Profile instance by ID
        
        Args:
            profile_id: Profile ID to find
            
        Returns:
            Profile object or None if not found
        """
        return cls(profile_id=profile_id) if profile_id else None
    
    @classmethod
    def find_by_name(cls, profile_name: str) -> Optional['Profile']:
        """
        Factory method: Find profile by name
        
        Args:
            profile_name: Profile name to search for
            
        Returns:
            Profile object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('profiles')
            .select('*')
            .eq('profile_name', profile_name)
            .execute()
        )
        
        if result and result.data:
            return cls(profile_data=result.data[0])
        return None
    
    @classmethod
    def all(cls) -> List['Profile']:
        """
        Factory method: Get all profiles as Profile instances
        
        Returns:
            List of Profile objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('profiles')
            .select('*')
            .execute()
        )
        
        if result and result.data:
            return [cls(profile_data=data) for data in result.data]
        return []
    
    @classmethod
    def search(cls, profile_name: str = '', description: str = '') -> List['Profile']:
        """
        Factory method: Search profiles by criteria
        
        Args:
            profile_name: Profile name to search (partial match)
            description: Description to search (partial match)
            
        Returns:
            List of Profile objects matching criteria
        """
        supabase = get_supabase()
        query = supabase.table('profiles').select('*')
        
        if profile_name:
            query = query.ilike('profile_name', f'%{profile_name}%')
        if description:
            query = query.ilike('description', f'%{description}%')
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(profile_data=data) for data in result.data]
        return []
