"""
Shortlist Entity Class - TRUE OOP Implementation
Holds shortlist data in memory and performs operations on itself
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase, execute_with_retry


class Shortlist:
    """
    Shortlist Entity - TRUE OOP Implementation
    
    This class implements proper OOP:
    - Objects hold data in memory (instance variables)
    - Instance methods do the actual work (not wrappers)
    - Factory methods (class methods) for querying
    - No static methods for business logic
    
    Usage:
        # Create new shortlist entry
        shortlist = Shortlist()
        shortlist.csr_user_id = 42
        shortlist.request_id = 10
        shortlist.notes = 'Interested in this request'
        shortlist.save()  # Instance method does the work
        
        # Load existing shortlist
        shortlist = Shortlist.find(1)
        shortlist.status = 'IN_PROGRESS'
        shortlist.save()  # Updates database
    """
    
    # Shortlist statuses
    STATUS_SHORTLISTED = 'SHORTLISTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_DECLINED = 'DECLINED'
    
    VALID_STATUSES = [STATUS_SHORTLISTED, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_DECLINED]
    
    def __init__(self, shortlist_id: Optional[int] = None, shortlist_data: Optional[Dict] = None):
        """
        Initialize a Shortlist instance
        
        Args:
            shortlist_id: Load existing shortlist item from database by ID
            shortlist_data: Initialize with existing shortlist data
            
        Example:
            shortlist = Shortlist(shortlist_id=1)
            shortlist = Shortlist(shortlist_data={...})
            shortlist = Shortlist()  # Create new
        """
        # Instance variables (object state - data in memory)
        self.id: Optional[int] = None
        self.csr_user_id: Optional[int] = None
        self.request_id: Optional[int] = None
        self.status: str = Shortlist.STATUS_SHORTLISTED
        self.notes: Optional[str] = None
        self.volunteered_hours: Optional[float] = None
        self.completion_date: Optional[str] = None
        self.feedback_from_pin: Optional[str] = None
        self.shortlisted_at: Optional[str] = None
        self.updated_at: Optional[str] = None
        self.requests: Optional[Dict] = None  # Store joined request data
        
        # Load data if provided
        if shortlist_id is not None:
            self._load_from_id(shortlist_id)
        elif shortlist_data is not None:
            self._load_from_dict(shortlist_data)
    
    # ============================================================================
    # PRIVATE METHODS (Internal use only)
    # ============================================================================
    
    def _load_from_id(self, shortlist_id: int) -> None:
        """Load shortlist data from database by ID (private method)"""
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .select('*, requests(*)')
            .eq('id', shortlist_id)
            .execute()
        )
        if result and result.data:
            self._load_from_dict(result.data[0])
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.csr_user_id = data.get('csr_user_id')
        self.request_id = data.get('request_id')
        self.status = data.get('status', Shortlist.STATUS_SHORTLISTED)
        self.notes = data.get('notes')
        self.volunteered_hours = data.get('volunteered_hours')
        self.completion_date = data.get('completion_date')
        self.feedback_from_pin = data.get('feedback_from_pin')
        self.shortlisted_at = data.get('shortlisted_at')
        self.updated_at = data.get('updated_at')
        self.requests = data.get('requests')  # Store joined request data
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate shortlist object state
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.csr_user_id:
            errors.append('CSR user ID is required')
        
        if not self.request_id:
            errors.append('Request ID is required')
        
        if self.status not in Shortlist.VALID_STATUSES:
            errors.append(f'Invalid status: {self.status}')
        
        return len(errors) == 0, errors
    
    def check_duplicate(self) -> tuple[bool, Optional[str]]:
        """
        Check if this CSR user already shortlisted this request
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        if not self.csr_user_id or not self.request_id:
            return True, None
        
        # Skip check if updating existing shortlist
        if self.id:
            return True, None
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .select('id')
            .eq('csr_user_id', self.csr_user_id)
            .eq('request_id', self.request_id)
            .execute()
        )
        
        if result and result.data:
            return False, 'Request already shortlisted by this user'
        
        return True, None
    
    def validate_request_active(self) -> tuple[bool, Optional[str]]:
        """
        Validate that the request is active
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.request_id:
            return False, 'Request ID is required'
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .select('id, status')
            .eq('id', self.request_id)
            .execute()
        )
        
        if not result or not result.data:
            return False, 'Request not found'
        
        if result.data[0]['status'] != 'ACTIVE':
            return False, 'Request is not active'
        
        return True, None
    
    # ============================================================================
    # CRUD METHODS (Instance methods - do the actual work)
    # ============================================================================
    
    def save(self) -> bool:
        """
        Save shortlist to database (create or update)
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
        
        # Check for duplicates (only for new shortlist)
        if not self.id:
            is_unique, error = self.check_duplicate()
            if not is_unique:
                raise ValueError(error)
            
            # Validate request is active
            is_active, error = self.validate_request_active()
            if not is_active:
                raise ValueError(error)
        
        supabase = get_supabase()
        
        if self.id:
            # Update existing shortlist
            update_data = {
                'status': self.status,
                'notes': self.notes,
                'volunteered_hours': self.volunteered_hours,
                'completion_date': self.completion_date,
                'feedback_from_pin': self.feedback_from_pin,
                'updated_at': datetime.now().isoformat()
            }
            
            result = execute_with_retry(
                lambda: supabase.table('shortlist')
                .update(update_data)
                .eq('id', self.id)
                .execute()
            )
            
            if result and result.data:
                self.updated_at = result.data[0]['updated_at']
        else:
            # Create new shortlist entry
            insert_data = {
                'csr_user_id': self.csr_user_id,
                'request_id': self.request_id,
                'status': self.status,
                'notes': self.notes
            }
            
            result = execute_with_retry(
                lambda: supabase.table('shortlist')
                .insert(insert_data)
                .execute()
            )
            
            if result and result.data:
                # Update object with new ID and timestamps
                self.id = result.data[0]['id']
                self.shortlisted_at = result.data[0]['shortlisted_at']
                self.updated_at = result.data[0]['updated_at']
                
                # Increment shortlist_count in requests table
                try:
                    from .request import Request
                    request = Request.find(self.request_id)
                    if request:
                        request.increment_shortlist_count()
                except Exception as e:
                    print(f"[WARNING] Failed to increment shortlist count: {str(e)}")
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this shortlist entry from database
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If shortlist has no ID
        """
        if not self.id:
            raise ValueError('Cannot delete shortlist without ID')
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .delete()
            .eq('id', self.id)
            .execute()
        )
        
        # Decrement shortlist_count in requests table
        if result and result.data:
            try:
                from .request import Request
                request = Request.find(self.request_id)
                if request:
                    request.decrement_shortlist_count()
            except Exception as e:
                print(f"[WARNING] Failed to decrement shortlist count: {str(e)}")
        
        return bool(result and result.data)
    
    # ============================================================================
    # STATUS METHODS (Instance methods)
    # ============================================================================
    
    def mark_in_progress(self) -> bool:
        """Mark this shortlist item as in progress"""
        self.status = Shortlist.STATUS_IN_PROGRESS
        return self.save()
    
    def mark_completed(self, volunteered_hours: float = None, feedback: str = None) -> bool:
        """
        Mark this shortlist item as completed
        
        Args:
            volunteered_hours: Hours volunteered
            feedback: Feedback from PIN user
            
        Returns:
            True if successful
        """
        self.status = Shortlist.STATUS_COMPLETED
        self.completion_date = datetime.now().isoformat()
        if volunteered_hours is not None:
            self.volunteered_hours = volunteered_hours
        if feedback:
            self.feedback_from_pin = feedback
        return self.save()
    
    # ============================================================================
    # UTILITY METHODS (Instance methods)
    # ============================================================================
    
    def to_dict(self) -> Dict:
        """Convert instance to dictionary (for API responses)"""
        return {
            'id': self.id,
            'csr_user_id': self.csr_user_id,
            'request_id': self.request_id,
            'status': self.status,
            'notes': self.notes,
            'volunteered_hours': self.volunteered_hours,
            'completion_date': self.completion_date,
            'feedback_from_pin': self.feedback_from_pin,
            'shortlisted_at': self.shortlisted_at,
            'updated_at': self.updated_at,
            'requests': self.requests  # Include joined request data
        }

    def get_csr_user(self):
        """Fetch the CSR user associated with this shortlist entry."""
        if not self.csr_user_id:
            return None
        from .user import User  # Local import to avoid circular dependency
        try:
            return User.find(self.csr_user_id)
        except Exception:
            return None

    def to_assignment_dict(self) -> Dict:
        """Convert shortlist entry into assignment-focused dictionary with CSR info."""
        data = self.to_dict()
        csr_user = self.get_csr_user()
        if csr_user:
            data['csr_user'] = {
                'id': csr_user.id,
                'full_name': csr_user.full_name,
                'email': csr_user.email,
            }
        return data
    
    # ============================================================================
    # MAGIC METHODS (OOP features)
    # ============================================================================
    
    def __str__(self) -> str:
        """String representation"""
        return f"Shortlist(csr_user_id={self.csr_user_id}, request_id={self.request_id})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Shortlist(id={self.id}, csr_user_id={self.csr_user_id}, request_id={self.request_id}, status='{self.status}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Shortlist):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Make hashable"""
        return hash(self.id) if self.id else hash(id(self))
    
    # ============================================================================
    # FACTORY METHODS (Class methods that return Shortlist objects)
    # ============================================================================
    
    @classmethod
    def find(cls, shortlist_id: int) -> Optional['Shortlist']:
        """
        Factory method: Find and return a Shortlist instance by ID
        
        Args:
            shortlist_id: Shortlist ID to find
            
        Returns:
            Shortlist object or None if not found
        """
        return cls(shortlist_id=shortlist_id) if shortlist_id else None
    
    @classmethod
    def all(cls) -> List['Shortlist']:
        """
        Factory method: Get all shortlist entries as Shortlist instances
        
        Returns:
            List of Shortlist objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .select('*, requests(*)')
            .execute()
        )
        
        if result and result.data:
            return [cls(shortlist_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_csr_user(cls, csr_user_id: int, status: str = None) -> List['Shortlist']:
        """
        Factory method: Get shortlist entries by CSR user
        
        Args:
            csr_user_id: CSR user ID
            status: Optional status filter
            
        Returns:
            List of Shortlist objects
        """
        supabase = get_supabase()
        query = supabase.table('shortlist').select('*, requests(*)').eq('csr_user_id', csr_user_id)
        
        if status:
            query = query.eq('status', status)
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(shortlist_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_request(cls, request_id: int) -> List['Shortlist']:
        """
        Factory method: Get shortlist entries by request
        
        Args:
            request_id: Request ID
            
        Returns:
            List of Shortlist objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .select('*, requests(*)')
            .eq('request_id', request_id)
            .execute()
        )
        
        if result and result.data:
            return [cls(shortlist_data=data) for data in result.data]
        return []

    @classmethod
    def active_assignment_for_request(cls, request_id: int) -> Optional['Shortlist']:
        """
        Factory method: Get the active assignment for a request (IN_PROGRESS or COMPLETED)
        """
        entries = cls.by_request(request_id)
        for entry in entries:
            if entry.status in (cls.STATUS_IN_PROGRESS, cls.STATUS_COMPLETED):
                return entry
        return None
    
    @classmethod
    def search(cls,
               csr_user_id: int = None,
               request_id: int = None,
               status: str = None) -> List['Shortlist']:
        """
        Factory method: Search shortlist entries by multiple criteria
        
        Args:
            csr_user_id: Filter by CSR user
            request_id: Filter by request
            status: Filter by status
            
        Returns:
            List of Shortlist objects matching criteria
        """
        supabase = get_supabase()
        query = supabase.table('shortlist').select('*, requests(*)')
        
        if csr_user_id:
            query = query.eq('csr_user_id', csr_user_id)
        if request_id:
            query = query.eq('request_id', request_id)
        if status:
            query = query.eq('status', status)
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(shortlist_data=data) for data in result.data]
        return []
    
    @classmethod
    def find_by_csr_and_request(cls, csr_user_id: int, request_id: int) -> Optional['Shortlist']:
        """
        Factory method: Find shortlist entry by CSR user and request
        
        Args:
            csr_user_id: CSR user ID
            request_id: Request ID
            
        Returns:
            Shortlist object or None if not found
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('shortlist')
            .select('*, requests(*)')
            .eq('csr_user_id', csr_user_id)
            .eq('request_id', request_id)
            .execute()
        )
        
        if result and result.data:
            return cls(shortlist_data=result.data[0])
        return None
