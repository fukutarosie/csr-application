"""
Script to add OOP wrappers to Request and Shortlist entities
This adds instance methods, factory methods, and magic methods while keeping all static methods
"""

import re

def add_oop_wrapper_to_request():
    """Add OOP features to Request entity"""
    
    oop_header = '''"""
Request Entity Class - PIN /CSR System
Handles all database operations for PIN requests
Part of the CONTROL/ENTITY layer (BCE Architecture)

NOW WITH PROPER OOP:
- Instance variables (object state)
- Instance methods (save, delete, etc.)
- Factory methods (find, all, etc.)
- Magic methods (__str__, __eq__, etc.)

Methods:
- create_request() - Create new request
- get_request() - Retrieve single request
- get_requests_by_pin_user() - Get all requests from a PIN user
- update_request() - Update request details
- suspend_request() - Suspend a request
- search_requests() - Search with filters
- fulfill_request() - Mark as fulfilled
- delete_request() - Hard delete (admin only)
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase


class Request:
    """Request entity - handles PIN user requests - NOW WITH PROPER OOP!"""
    
    # Request statuses
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_CANCELLED = 'CANCELLED'
    
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_SUSPENDED, STATUS_FULFILLED, STATUS_CANCELLED]
    
    # ============================================================================
    # INSTANCE METHODS (NEW - Proper OOP)
    # ============================================================================
    
    def __init__(self, request_id: Optional[int] = None, request_data: Optional[Dict] = None):
        """
        Initialize a Request instance
        
        Args:
            request_id: Load existing request from database by ID
            request_data: Initialize with existing request data
        """
        # Instance variables (object state)
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
        
        # Load data if provided
        if request_id is not None:
            self._load_from_id(request_id)
        elif request_data is not None:
            self._load_from_dict(request_data)
    
    def _load_from_id(self, request_id: int) -> None:
        """Load request data from database by ID (private method)"""
        data = Request.get_request(request_id)
        if data:
            self._load_from_dict(data)
    
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
            'updated_at': self.updated_at
        }
    
    def save(self) -> bool:
        """Save request to database (create or update)"""
        if self.id is None:
            # Create new request
            result = Request.create_request(
                pin_user_id=self.pin_user_id,
                title=self.title,
                description=self.description,
                service_type=self.service_type,
                region=self.region,
                requested_by_date=self.requested_by_date,
                image_url=self.image_url
            )
            if result:
                self._load_from_dict(result)
                return True
            return False
        else:
            # Update existing request
            updates = {
                'title': self.title,
                'description': self.description,
                'service_type': self.service_type,
                'region': self.region,
                'requested_by_date': self.requested_by_date,
                'status': self.status,
                'is_archived': self.is_archived
            }
            result = Request.update_request(self.id, updates)
            if result:
                self._load_from_dict(result)
                return True
            return False
    
    def delete(self) -> bool:
        """Delete this request from database"""
        if self.id is None:
            return False
        return Request.delete_request(self.id)
    
    def suspend(self) -> bool:
        """Suspend this request"""
        if self.id is None:
            return False
        result = Request.suspend_request(self.id)
        if result:
            self.status = Request.STATUS_SUSPENDED
            return True
        return False
    
    def activate(self) -> bool:
        """Activate this request"""
        if self.id is None:
            return False
        result = Request.activate_request(self.id)
        if result:
            self.status = Request.STATUS_ACTIVE
            return True
        return False
    
    def fulfill(self) -> bool:
        """Mark this request as fulfilled"""
        if self.id is None:
            return False
        result = Request.fulfill_request(self.id)
        if result:
            self.status = Request.STATUS_FULFILLED
            return True
        return False
    
    def increment_views(self) -> bool:
        """Increment view count"""
        if self.id is None:
            return False
        result = Request.increment_view_count(self.id)
        if result:
            self.view_count += 1
            return True
        return False
    
    # Magic methods
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
    # CLASS METHODS (Factory methods for OOP)
    # ============================================================================
    
    @classmethod
    def find(cls, request_id: int) -> Optional['Request']:
        """Factory method: Find and return a Request instance"""
        data = cls.get_request(request_id)
        if data:
            return cls(request_data=data)
        return None
    
    @classmethod
    def all(cls) -> List['Request']:
        """Factory method: Get all requests as Request instances"""
        data_list = cls.get_all_requests()
        return [cls(request_data=data) for data in data_list]
    
    @classmethod
    def by_pin_user(cls, pin_user_id: int) -> List['Request']:
        """Factory method: Get requests by PIN user"""
        data_list = cls.get_requests_by_pin_user(pin_user_id)
        return [cls(request_data=data) for data in data_list]
    
    # ============================================================================
    # STATIC METHODS (LEGACY - Backward Compatible)
    # All existing static methods remain below...
    # ============================================================================
    
'''
    
    print("OOP wrapper for Request entity created!")
    print("This header should be added to the top of request.py")
    print("All existing @staticmethod functions remain unchanged below")
    return oop_header


def add_oop_wrapper_to_shortlist():
    """Add OOP features to Shortlist entity"""
    
    oop_header = '''"""
Shortlist Entity Class - PIN/CSR System
Handles all database operations for CSR shortlisting of PIN requests
Part of the CONTROL/ENTITY layer (BCE Architecture)

NOW WITH PROPER OOP:
- Instance variables (object state)
- Instance methods (save, delete, etc.)
- Factory methods (find, all, etc.)
- Magic methods (__str__, __eq__, etc.)

Methods:
- add_to_shortlist() - Save/shortlist a request
- remove_from_shortlist() - Remove from shortlist
- search_shortlist() - Get CSR's shortlist with filters
- update_shortlist_status() - Update shortlist status
- get_shortlist_item() - Get specific shortlist entry
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase


class Shortlist:
    """Shortlist entity - handles CSR shortlisting of requests - NOW WITH PROPER OOP!"""
    
    # Shortlist statuses
    STATUS_SHORTLISTED = 'SHORTLISTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_DECLINED = 'DECLINED'
    
    VALID_STATUSES = [STATUS_SHORTLISTED, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_DECLINED]
    
    # ============================================================================
    # INSTANCE METHODS (NEW - Proper OOP)
    # ============================================================================
    
    def __init__(self, shortlist_id: Optional[int] = None, shortlist_data: Optional[Dict] = None):
        """
        Initialize a Shortlist instance
        
        Args:
            shortlist_id: Load existing shortlist item from database by ID
            shortlist_data: Initialize with existing shortlist data
        """
        # Instance variables (object state)
        self.id: Optional[int] = None
        self.csr_user_id: Optional[int] = None
        self.request_id: Optional[int] = None
        self.status: str = Shortlist.STATUS_SHORTLISTED
        self.notes: Optional[str] = None
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
        
        # Load data if provided
        if shortlist_id is not None:
            self._load_from_id(shortlist_id)
        elif shortlist_data is not None:
            self._load_from_dict(shortlist_data)
    
    def _load_from_id(self, shortlist_id: int) -> None:
        """Load shortlist data from database by ID (private method)"""
        data = Shortlist.get_shortlist_item(shortlist_id)
        if data:
            self._load_from_dict(data)
    
    def _load_from_dict(self, data: Dict) -> None:
        """Populate instance variables from dictionary (private method)"""
        self.id = data.get('id')
        self.csr_user_id = data.get('csr_user_id')
        self.request_id = data.get('request_id')
        self.status = data.get('status', Shortlist.STATUS_SHORTLISTED)
        self.notes = data.get('notes')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> Dict:
        """Convert instance to dictionary (for API responses)"""
        return {
            'id': self.id,
            'csr_user_id': self.csr_user_id,
            'request_id': self.request_id,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self) -> bool:
        """Save shortlist to database (create or update)"""
        if self.id is None:
            # Create new shortlist entry
            result = Shortlist.add_to_shortlist(
                csr_user_id=self.csr_user_id,
                request_id=self.request_id,
                notes=self.notes
            )
            if result:
                self._load_from_dict(result)
                return True
            return False
        else:
            # Update existing shortlist entry
            result = Shortlist.update_shortlist_status(
                shortlist_id=self.id,
                status=self.status,
                notes=self.notes
            )
            if result:
                self._load_from_dict(result)
                return True
            return False
    
    def delete(self) -> bool:
        """Remove this item from shortlist"""
        if self.id is None:
            return False
        return Shortlist.remove_from_shortlist(self.id)
    
    def update_status(self, status: str) -> bool:
        """Update status of this shortlist item"""
        if self.id is None or status not in Shortlist.VALID_STATUSES:
            return False
        result = Shortlist.update_shortlist_status(self.id, status)
        if result:
            self.status = status
            return True
        return False
    
    # Magic methods
    def __str__(self) -> str:
        """String representation"""
        return f"Shortlist(CSR:{self.csr_user_id}, Request:{self.request_id})"
    
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
    # CLASS METHODS (Factory methods for OOP)
    # ============================================================================
    
    @classmethod
    def find(cls, shortlist_id: int) -> Optional['Shortlist']:
        """Factory method: Find and return a Shortlist instance"""
        data = cls.get_shortlist_item(shortlist_id)
        if data:
            return cls(shortlist_data=data)
        return None
    
    @classmethod
    def by_csr_user(cls, csr_user_id: int) -> List['Shortlist']:
        """Factory method: Get shortlist items by CSR user"""
        data_list = cls.search_shortlist(csr_user_id=csr_user_id)
        return [cls(shortlist_data=data) for data in data_list]
    
    # ============================================================================
    # STATIC METHODS (LEGACY - Backward Compatible)
    # All existing @staticmethod functions remain below...
    # ============================================================================
    
'''
    
    print("OOP wrapper for Shortlist entity created!")
    print("This header should be added to the top of shortlist.py")
    print("All existing @staticmethod functions remain unchanged below")
    return oop_header


if __name__ == "__main__":
    print("=" * 80)
    print("OOP WRAPPER GENERATOR FOR REQUEST AND SHORTLIST ENTITIES")
    print("=" * 80)
    print()
    
    print("[1/2] Generating OOP wrapper for Request entity...")
    request_oop = add_oop_wrapper_to_request()
    print()
    
    print("[2/2] Generating OOP wrapper for Shortlist entity...")
    shortlist_oop = add_oop_wrapper_to_shortlist()
    print()
    
    print("=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print("1. The OOP wrappers have been generated")
    print("2. Add these to the top of request.py and shortlist.py")
    print("3. Keep all existing @staticmethod functions")
    print("4. All existing code will continue to work!")
    print("=" * 80)

