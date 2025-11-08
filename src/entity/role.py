"""
Role Entity Class - TRUE OOP Implementation
Holds role data in memory and performs operations on itself
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase, execute_with_retry


class Role:
    """
    Role Entity - TRUE OOP Implementation
    
    This class implements proper OOP:
    - Objects hold data in memory (instance variables)
    - Instance methods do the actual work (not wrappers)
    - Factory methods (class methods) for querying
    - No static methods for business logic
    
    Usage:
        # Create new role
        role = Role()
        role.role_name = 'CSR Rep'
        role.role_code = 'CSR'
        role.description = 'CSR Representative'
        role.dashboard_route = '/csr/dashboard'
        role.save()  # Instance method does the work
        
        # Load existing role
        role = Role.find_by_name('CSR Rep')
        role.description = 'Updated description'
        role.save()  # Updates database
    """
    
    # ============================================================================
    # CLASS CONSTANTS (Shared across all instances)
    # ============================================================================
    USER_ADMIN = "User Admin"
    PIN = "PIN"
    CSR_REP = "CSR Rep"
    PLATFORM_MANAGEMENT = "Platform Management"

    ROLE_ROUTES = {
        USER_ADMIN: "/admin/dashboard",
        PIN: "/pin/dashboard",
        CSR_REP: "/csr/dashboard",
        PLATFORM_MANAGEMENT: "/platform/dashboard"
    }
    
    def __init__(self, role_id: Optional[int] = None, role_data: Optional[Dict] = None):
        """
        Initialize a Role instance
        
        Args:
            role_id: Load existing role from database by ID
            role_data: Initialize with existing role data
            
        Example:
            role = Role(role_id=2)
            role = Role(role_data={'id': 2, 'role_name': 'PIN', ...})
            role = Role()  # Create new empty role
        """
        # Instance variables (object state - data in memory)
        self.id: Optional[int] = None
        self.role_name: Optional[str] = None
        self.role_code: Optional[str] = None
        self.description: Optional[str] = None
        self.dashboard_route: Optional[str] = None
        self.created_at: Optional[str] = None
        
        # Load data if provided
        if role_id is not None:
            self._load_from_id(role_id)
        elif role_data is not None:
            self._load_from_dict(role_data)
    
    # ============================================================================
    # PRIVATE METHODS (Internal use only)
    # ============================================================================
    
    def _load_from_id(self, role_id: int) -> None:
        """Load role data from database by ID (private method)"""
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .select('*')
            .eq('id', role_id)
            .execute()
        )
        if result and result.data:
            self._load_from_dict(result.data[0])
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.role_name = data.get('role_name')
        self.role_code = data.get('role_code')
        self.description = data.get('description')
        self.dashboard_route = data.get('dashboard_route')
        self.created_at = data.get('created_at')
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate role object state
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.role_name or len(self.role_name) < 2:
            errors.append('Role name must be at least 2 characters')
        
        if not self.role_code or len(self.role_code) < 2:
            errors.append('Role code must be at least 2 characters')
        
        if not self.dashboard_route:
            errors.append('Dashboard route is required')
        
        return len(errors) == 0, errors
    
    def check_uniqueness(self) -> tuple[bool, Optional[str]]:
        """
        Check if role_name or role_code already exists
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        supabase = get_supabase()
        
        # Check role_name (skip if updating existing role)
        query = supabase.table('roles').select('id').eq('role_name', self.role_name)
        if self.id:
            query = query.neq('id', self.id)
        result = execute_with_retry(lambda: query.execute())
        if result and result.data:
            return False, f"Role name '{self.role_name}' already exists"
        
        # Check role_code
        query = supabase.table('roles').select('id').eq('role_code', self.role_code)
        if self.id:
            query = query.neq('id', self.id)
        result = execute_with_retry(lambda: query.execute())
        if result and result.data:
            return False, f"Role code '{self.role_code}' already exists"
        
        return True, None
    
    # ============================================================================
    # CRUD METHODS (Instance methods - do the actual work)
    # ============================================================================
    
    def save(self) -> bool:
        """
        Save role to database (create or update)
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
            # Update existing role
            update_data = {
                'role_name': self.role_name,
                'role_code': self.role_code,
                'description': self.description,
                'dashboard_route': self.dashboard_route
            }
            
            result = execute_with_retry(
                lambda: supabase.table('roles')
                .update(update_data)
                .eq('id', self.id)
                .execute()
            )
        else:
            # Create new role
            insert_data = {
                'role_name': self.role_name,
                'role_code': self.role_code,
                'description': self.description or '',
                'dashboard_route': self.dashboard_route
            }
            
            result = execute_with_retry(
                lambda: supabase.table('roles')
                .insert(insert_data)
                .execute()
            )
            
            if result and result.data:
                # Update object with new ID and created_at
                self.id = result.data[0]['id']
                self.created_at = result.data[0]['created_at']
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this role from database
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If role has no ID
        """
        if not self.id:
            raise ValueError('Cannot delete role without ID')
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .delete()
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    def update(self, updates: Dict = None) -> bool:
        """
        Update this role in database
        
        Args:
            updates: Dictionary of fields to update (optional, uses instance attributes if not provided)
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If role has no ID or validation fails
        """
        if not self.id:
            raise ValueError('Cannot update role without ID')
        
        # If updates dict provided, apply to instance
        if updates:
            if 'role_name' in updates:
                self.role_name = updates['role_name']
            if 'role_code' in updates:
                self.role_code = updates['role_code']
            if 'description' in updates:
                self.description = updates['description']
            if 'dashboard_route' in updates:
                self.dashboard_route = updates['dashboard_route']
        
        # Validate
        is_valid, errors = self.validate()
        if not is_valid:
            raise ValueError('; '.join(errors))
        
        # Prepare update data
        update_data = {
            'role_name': self.role_name,
            'role_code': self.role_code,
            'description': self.description,
            'dashboard_route': self.dashboard_route
        }
        
        # Update in database
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .update(update_data)
            .eq('id', self.id)
            .execute()
        )
        
        if result and result.data:
            # Reload from database to sync
            self._load_from_dict(result.data[0])
            return True
        return False
    
    # ============================================================================
    # UTILITY METHODS (Instance methods)
    # ============================================================================
    
    def to_dict(self) -> Dict:
        """Convert instance to dictionary (for API responses)"""
        return {
            'id': self.id,
            'role_name': self.role_name,
            'role_code': self.role_code,
            'description': self.description,
            'dashboard_route': self.dashboard_route,
            'created_at': self.created_at
        }
    
    def get_dashboard_route(self) -> str:
        """Get dashboard route for this role"""
        return self.dashboard_route or self.ROLE_ROUTES.get(self.role_name, '/dashboard')
    
    # ============================================================================
    # MAGIC METHODS (OOP features)
    # ============================================================================
    
    def __str__(self) -> str:
        """String representation"""
        return f"Role({self.role_name})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Role(id={self.id}, role_name='{self.role_name}', role_code='{self.role_code}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Role):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Make hashable"""
        return hash(self.id) if self.id else hash(id(self))
    
    # ============================================================================
    # FACTORY METHODS (Class methods that return Role objects)
    # ============================================================================
    
    @classmethod
    def find(cls, role_id: int) -> Optional['Role']:
        """
        Factory method: Find and return a Role instance by ID
        
        Args:
            role_id: Role ID to find
            
        Returns:
            Role object or None if not found
        """
        return cls(role_id=role_id) if role_id else None
    
    @classmethod
    def find_by_name(cls, role_name: str) -> Optional['Role']:
        """
        Factory method: Find role by name
        
        Args:
            role_name: Role name to search for
            
        Returns:
            Role object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .select('*')
            .eq('role_name', role_name)
            .execute()
        )
        
        if result and result.data:
            return cls(role_data=result.data[0])
        return None
    
    @classmethod
    def find_by_code(cls, role_code: str) -> Optional['Role']:
        """
        Factory method: Find role by code
        
        Args:
            role_code: Role code to search for
            
        Returns:
            Role object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .select('*')
            .eq('role_code', role_code)
            .execute()
        )
        
        if result and result.data:
            return cls(role_data=result.data[0])
        return None
    
    @classmethod
    def all(cls) -> List['Role']:
        """
        Factory method: Get all roles as Role instances
        
        Returns:
            List of Role objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('roles')
            .select('*')
            .execute()
        )
        
        if result and result.data:
            return [cls(role_data=data) for data in result.data]
        return []
    
    @classmethod
    def public_roles(cls) -> List['Role']:
        """
        Factory method: Get public roles (non-admin roles)
        
        Returns:
            List of Role objects excluding admin roles
        """
        all_roles = cls.all()
        # Filter out admin roles (you can customize this logic)
        return [role for role in all_roles if role.role_name != cls.USER_ADMIN]
