"""
Request Entity Class - TRUE OOP Implementation
Holds request data in memory and performs operations on itself
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase, execute_with_retry


class Request:
    """
    Request Entity - TRUE OOP Implementation
    
    This class implements proper OOP:
    - Objects hold data in memory (instance variables)
    - Instance methods do the actual work (not wrappers)
    - Factory methods (class methods) for querying
    - No static methods for business logic
    
    Usage:
        # Create new request
        request = Request()
        request.pin_user_id = 42
        request.title = 'Need grocery shopping help'
        request.description = 'Heavy groceries, need help carrying'
        request.service_type = 'Grocery Shopping'
        request.region = 'Hougang'
        request.requested_by_date = '2025-12-31'
        request.image_url = '/uploads/requests/image.jpg'
        request.save()  # Instance method does the work
        
        # Load existing request
        request = Request.find(1)
        request.status = 'FULFILLED'
        request.save()  # Updates database
    """
    
    # Request statuses
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_CANCELLED = 'CANCELLED'
    
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_SUSPENDED, STATUS_FULFILLED, STATUS_CANCELLED]
    
    def __init__(self, request_id: Optional[int] = None, request_data: Optional[Dict] = None):
        """
        Initialize a Request instance
        
        Args:
            request_id: Load existing request from database by ID
            request_data: Initialize with existing request data
            
        Example:
            request = Request(request_id=1)
            request = Request(request_data={...})
            request = Request()  # Create new
        """
        # Instance variables (object state - data in memory)
        self.id: Optional[int] = None
        self.pin_user_id: Optional[int] = None
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.service_type: Optional[str] = None
        self.region: Optional[str] = None
        self.requested_by_date: Optional[str] = None
        self.image_url: Optional[str] = None
        self.status: str = Request.STATUS_ACTIVE
        self.is_archived: bool = False
        self.view_count: int = 0
        self.shortlist_count: int = 0
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
        self.fulfilled_at: Optional[str] = None
        self.suspended_at: Optional[str] = None
        
        # Load data if provided
        if request_id is not None:
            self._load_from_id(request_id)
        elif request_data is not None:
            self._load_from_dict(request_data)
    
    # ============================================================================
    # PRIVATE METHODS (Internal use only)
    # ============================================================================
    
    def _load_from_id(self, request_id: int) -> None:
        """Load request data from database by ID (private method)"""
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .select('*')
            .eq('id', request_id)
            .execute()
        )
        if result and result.data:
            self._load_from_dict(result.data[0])
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.pin_user_id = data.get('pin_user_id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.service_type = data.get('service_type')
        self.region = data.get('region')
        self.requested_by_date = data.get('requested_by_date')
        self.image_url = data.get('image_url')
        self.status = data.get('status', Request.STATUS_ACTIVE)
        self.is_archived = data.get('is_archived', False)
        self.view_count = data.get('view_count', 0)
        self.shortlist_count = data.get('shortlist_count', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.fulfilled_at = data.get('fulfilled_at')
        self.suspended_at = data.get('suspended_at')
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate request object state
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.pin_user_id:
            errors.append('PIN user ID is required')
        
        if not self.title or len(self.title) < 5:
            errors.append('Title must be at least 5 characters')
        
        if not self.description or len(self.description) < 10:
            errors.append('Description must be at least 10 characters')
        
        if not self.service_type:
            errors.append('Service type is required')
        
        if not self.region:
            errors.append('Region is required')
        
        if not self.requested_by_date:
            errors.append('Requested by date is required')
        
        if not self.image_url:
            errors.append('Image is required')
        
        if self.status not in Request.VALID_STATUSES:
            errors.append(f'Invalid status: {self.status}')
        
        return len(errors) == 0, errors
    
    def validate_pin_user(self) -> tuple[bool, Optional[str]]:
        """
        Validate that pin_user_id is a valid PIN user
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.pin_user_id:
            return False, 'PIN user ID is required'
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('users')
            .select('id, role_id')
            .eq('id', self.pin_user_id)
            .execute()
        )
        
        if not result or not result.data:
            return False, 'User not found'
        
        if result.data[0]['role_id'] != 2:  # PIN role_id = 2
            return False, 'User is not a PIN user'
        
        return True, None
    
    def validate_service_type(self) -> tuple[bool, Optional[str]]:
        """
        Validate that service_type exists in service_types table
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.service_type:
            return False, 'Service type is required'
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('service_types')
            .select('id')
            .eq('service_name', self.service_type)
            .execute()
        )
        
        if not result or not result.data:
            return False, f'Invalid service type: {self.service_type}'
        
        return True, None
    
    # ============================================================================
    # CRUD METHODS (Instance methods - do the actual work)
    # ============================================================================
    
    def save(self) -> bool:
        """
        Save request to database (create or update)
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
        
        # Validate PIN user (only for new requests)
        if not self.id:
            is_valid_user, error = self.validate_pin_user()
            if not is_valid_user:
                raise ValueError(error)
            
            # Validate service type
            is_valid_service, error = self.validate_service_type()
            if not is_valid_service:
                raise ValueError(error)
        
        supabase = get_supabase()
        
        if self.id:
            # Update existing request
            update_data = {
                'title': self.title,
                'description': self.description,
                'service_type': self.service_type,
                'region': self.region,
                'requested_by_date': self.requested_by_date,
                'image_url': self.image_url,
                'status': self.status,
                'is_archived': self.is_archived,
                'updated_at': datetime.now().isoformat()
            }
            
            result = execute_with_retry(
                lambda: supabase.table('requests')
                .update(update_data)
                .eq('id', self.id)
                .execute()
            )
            
            if result and result.data:
                self.updated_at = result.data[0]['updated_at']
        else:
            # Create new request
            insert_data = {
                'pin_user_id': self.pin_user_id,
                'title': self.title,
                'description': self.description,
                'service_type': self.service_type,
                'region': self.region,
                'requested_by_date': self.requested_by_date,
                'image_url': self.image_url,
                'status': self.status,
                'is_archived': self.is_archived,
                'view_count': self.view_count,
                'shortlist_count': self.shortlist_count
            }
            
            result = execute_with_retry(
                lambda: supabase.table('requests')
                .insert(insert_data)
                .execute()
            )
            
            if result and result.data:
                # Update object with new ID and timestamps
                self.id = result.data[0]['id']
                self.created_at = result.data[0]['created_at']
                self.updated_at = result.data[0]['updated_at']
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this request from database
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If request has no ID
        """
        if not self.id:
            raise ValueError('Cannot delete request without ID')
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .delete()
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    # ============================================================================
    # STATUS METHODS (Instance methods)
    # ============================================================================
    
    def suspend(self, reason: str = None) -> bool:
        """
        Suspend this request
        
        Args:
            reason: Optional reason for suspension
            
        Returns:
            True if successful
        """
        if not self.id:
            raise ValueError('Cannot suspend request without ID')
        
        self.status = Request.STATUS_SUSPENDED
        self.suspended_at = datetime.now().isoformat()
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({
                'status': self.status,
                'suspended_at': self.suspended_at,
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', self.id)
            .execute()
        )
        
        # Log status change if history table exists
        if result and result.data:
            try:
                execute_with_retry(
                    lambda: supabase.table('request_status_history').insert({
                        'request_id': self.id,
                        'old_status': Request.STATUS_ACTIVE,
                        'new_status': Request.STATUS_SUSPENDED,
                        'reason': reason
                    }).execute()
                )
            except Exception as e:
                print(f"[WARNING] Failed to log status change: {str(e)}")
        
        return bool(result and result.data)
    
    def fulfill(self) -> bool:
        """
        Mark this request as fulfilled
        
        Returns:
            True if successful
        """
        if not self.id:
            raise ValueError('Cannot fulfill request without ID')
        
        old_status = self.status
        self.status = Request.STATUS_FULFILLED
        self.fulfilled_at = datetime.now().isoformat()
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({
                'status': self.status,
                'fulfilled_at': self.fulfilled_at,
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', self.id)
            .execute()
        )
        
        # Log status change
        if result and result.data:
            try:
                execute_with_retry(
                    lambda: supabase.table('request_status_history').insert({
                        'request_id': self.id,
                        'old_status': old_status,
                        'new_status': Request.STATUS_FULFILLED
                    }).execute()
                )
            except Exception as e:
                print(f"[WARNING] Failed to log status change: {str(e)}")
        
        return bool(result and result.data)
    
    def archive(self) -> bool:
        """Archive this request"""
        if not self.id:
            raise ValueError('Cannot archive request without ID')
        
        self.is_archived = True
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({
                'is_archived': True,
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    # ============================================================================
    # COUNTER METHODS (Instance methods)
    # ============================================================================
    
    def increment_view_count(self) -> bool:
        """Increment view count for this request"""
        if not self.id:
            return False
        
        self.view_count += 1
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({'view_count': self.view_count})
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    def increment_shortlist_count(self) -> bool:
        """Increment shortlist count for this request"""
        if not self.id:
            return False
        
        self.shortlist_count += 1
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({'shortlist_count': self.shortlist_count})
            .eq('id', self.id)
            .execute()
        )
        
        return bool(result and result.data)
    
    def decrement_shortlist_count(self) -> bool:
        """Decrement shortlist count for this request"""
        if not self.id:
            return False
        
        self.shortlist_count = max(0, self.shortlist_count - 1)
        
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .update({'shortlist_count': self.shortlist_count})
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
            'pin_user_id': self.pin_user_id,
            'title': self.title,
            'description': self.description,
            'service_type': self.service_type,
            'region': self.region,
            'requested_by_date': self.requested_by_date,
            'image_url': self.image_url,
            'status': self.status,
            'is_archived': self.is_archived,
            'view_count': self.view_count,
            'shortlist_count': self.shortlist_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'fulfilled_at': self.fulfilled_at,
            'suspended_at': self.suspended_at
        }
    
    # ============================================================================
    # MAGIC METHODS (OOP features)
    # ============================================================================
    
    def __str__(self) -> str:
        """String representation"""
        return f"Request({self.title})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Request(id={self.id}, title='{self.title}', status='{self.status}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Request):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Make hashable"""
        return hash(self.id) if self.id else hash(id(self))
    
    # ============================================================================
    # FACTORY METHODS (Class methods that return Request objects)
    # ============================================================================
    
    @classmethod
    def find(cls, request_id: int) -> Optional['Request']:
        """
        Factory method: Find and return a Request instance by ID
        
        Args:
            request_id: Request ID to find
            
        Returns:
            Request object or None if not found
        """
        return cls(request_id=request_id) if request_id else None
    
    @classmethod
    def all(cls, include_archived: bool = False) -> List['Request']:
        """
        Factory method: Get all requests as Request instances
        
        Args:
            include_archived: Whether to include archived requests
            
        Returns:
            List of Request objects
        """
        supabase = get_supabase()
        query = supabase.table('requests').select('*')
        
        if not include_archived:
            query = query.eq('is_archived', False)
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(request_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_pin_user(cls, pin_user_id: int) -> List['Request']:
        """
        Factory method: Get requests by PIN user
        
        Args:
            pin_user_id: PIN user ID
            
        Returns:
            List of Request objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .select('*')
            .eq('pin_user_id', pin_user_id)
            .execute()
        )
        
        if result and result.data:
            return [cls(request_data=data) for data in result.data]
        return []
    
    @classmethod
    def by_status(cls, status: str) -> List['Request']:
        """
        Factory method: Get requests by status
        
        Args:
            status: Request status
            
        Returns:
            List of Request objects
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('requests')
            .select('*')
            .eq('status', status)
            .eq('is_archived', False)
            .execute()
        )
        
        if result and result.data:
            return [cls(request_data=data) for data in result.data]
        return []
    
    @classmethod
    def search(cls, 
               service_type: str = None,
               region: str = None,
               status: str = None,
               pin_user_id: int = None) -> List['Request']:
        """
        Factory method: Search requests by multiple criteria
        
        Args:
            service_type: Filter by service type
            region: Filter by region
            status: Filter by status
            pin_user_id: Filter by PIN user
            
        Returns:
            List of Request objects matching criteria
        """
        supabase = get_supabase()
        query = supabase.table('requests').select('*').eq('is_archived', False)
        
        if service_type:
            query = query.eq('service_type', service_type)
        if region:
            query = query.eq('region', region)
        if status:
            query = query.eq('status', status)
        if pin_user_id:
            query = query.eq('pin_user_id', pin_user_id)
        
        result = execute_with_retry(lambda: query.execute())
        
        if result and result.data:
            return [cls(request_data=data) for data in result.data]
        return []
    
    # ============================================================================
    # STATIC METHODS (Utility methods that don't need instance or class state)
    # ============================================================================
    
    @staticmethod
    def get_service_types() -> List[Dict]:
        """
        Get all service types from database
        
        Returns:
            List of service type dictionaries
        """
        supabase = get_supabase()
        result = execute_with_retry(
            lambda: supabase.table('service_types')
            .select('*')
            .execute()
        )
        
        if result and result.data:
            return result.data
        return []
    
    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all unique categories from requests
        
        Returns:
            List of category strings
        """
        # For now, return predefined categories
        # In future, could query database for unique values
        return [
            'Healthcare',
            'Education',
            'Transportation',
            'Food & Nutrition',
            'Housing',
            'Social Services',
            'Other'
        ]
