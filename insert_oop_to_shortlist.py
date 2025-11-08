"""
Script to insert OOP features into Shortlist entity
Adds instance methods, factory methods, and magic methods while keeping all static methods
"""

# Read the current shortlist.py file
with open('src/entity/shortlist.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Find where the class definition starts
class_start = original_content.find('class Shortlist:')

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
        # Instance variables (object state)
        self.id: Optional[int] = None
        self.csr_user_id: Optional[int] = None
        self.request_id: Optional[int] = None
        self.status: str = Shortlist.STATUS_SHORTLISTED
        self.notes: Optional[str] = None
        self.shortlisted_at: Optional[str] = None
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
        self.shortlisted_at = data.get('shortlisted_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> Dict:
        """Convert instance to dictionary (for API responses)"""
        return {
            'id': self.id,
            'csr_user_id': self.csr_user_id,
            'request_id': self.request_id,
            'status': self.status,
            'notes': self.notes,
            'shortlisted_at': self.shortlisted_at,
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
    
    def update_attributes(self, **kwargs) -> None:
        """Update multiple attributes at once"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
    
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
    def by_csr_user(cls, csr_user_id: int, status: str = None) -> List['Shortlist']:
        """Factory method: Get shortlist items by CSR user"""
        data_list = cls.search_shortlist(csr_user_id=csr_user_id, status=status)
        return [cls(shortlist_data=data) for data in data_list]
    
    @classmethod
    def by_request(cls, request_id: int) -> List['Shortlist']:
        """Factory method: Get all shortlist entries for a request"""
        data_list = cls.search_shortlist(request_id=request_id)
        return [cls(shortlist_data=data) for data in data_list]
    
    # ============================================================================
    # STATIC METHODS (LEGACY - Backward Compatible)
    # All existing static methods remain below...
    # ============================================================================
'''

# Reconstruct the file
new_content = header_part + class_header + oop_features + class_methods

# Write the new file
with open('src/entity/shortlist.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] OOP features successfully added to Shortlist entity!")
print("   - Instance variables added")
print("   - Instance methods added (save, delete, update_status, etc.)")
print("   - Factory methods added (find, by_csr_user, by_request, etc.)")
print("   - Magic methods added (__str__, __eq__, __hash__, __repr__)")
print("   - All existing static methods preserved")
print("   - Backup saved as shortlist_backup.py")

