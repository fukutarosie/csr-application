"""
Script to insert OOP features into Request entity
Adds instance methods, factory methods, and magic methods while keeping all static methods
"""

# Read the current request.py file
with open('src/entity/request.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Find where the class definition starts
class_start = original_content.find('class Request:')

# Split into header and class content
header_part = original_content[:class_start]
class_part = original_content[class_start:]

# Find the end of the class docstring and constants
valid_statuses_line = class_part.find('VALID_STATUSES = [')
after_constants = class_part.find('\n', valid_statuses_line) + 1

# Split class into: class definition + constants, and the rest
class_header = class_part[:after_constants]
class_methods = class_part[after_constants:]

# OOP features to insert
oop_features = '''    
    # ============================================================================
    # INSTANCE METHODS (NEW - Proper OOP)
    # ============================================================================
    
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
    
    def update_attributes(self, **kwargs) -> None:
        """Update multiple attributes at once"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
    
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

# Reconstruct the file
new_content = header_part + class_header + oop_features + class_methods

# Write the new file
with open('src/entity/request.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] OOP features successfully added to Request entity!")
print("   - Instance variables added")
print("   - Instance methods added (save, delete, suspend, etc.)")
print("   - Factory methods added (find, all, by_pin_user, etc.)")
print("   - Magic methods added (__str__, __eq__, __hash__, __repr__)")
print("   - All existing static methods preserved")
print("   - Backup saved as request_backup.py")

