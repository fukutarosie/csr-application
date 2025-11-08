"""
Search PIN Request Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple, List
from src.entity.request import Request
from src.entity import User


class SearchPINRequestController:
    """
    Search PIN Request Controller - TRUE OOP
    
    Usage:
        controller = SearchPINRequestController(auth_token, keyword, category, status, priority, service_type, my_requests)
        response, status = controller.execute()
    """
    
    VALID_STATUSES = ['ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED']
    VALID_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
    
    def __init__(self, auth_token: str, keyword: str = None, category: str = None, 
                 status: str = None, priority: str = None, service_type: str = None, 
                 my_requests: bool = False):
        """Initialize controller"""
        self.auth_token = auth_token
        self.keyword = keyword
        self.category = category
        self.status = status
        self.priority = priority
        self.service_type = service_type
        self.my_requests = my_requests
        self.user = None
        self.requests = []
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def validate_filters(self) -> Tuple[bool, str]:
        """Validate filter parameters"""
        if self.status and self.status not in self.VALID_STATUSES:
            return False, f'Invalid status. Must be one of: {", ".join(self.VALID_STATUSES)}'
        
        if self.priority and self.priority not in self.VALID_PRIORITIES:
            return False, f'Invalid priority. Must be one of: {", ".join(self.VALID_PRIORITIES)}'
        
        return True, ''
    
    def apply_filters(self, requests: List[Request]) -> List[Request]:
        """Apply filters to request list"""
        filtered = []
        for req in requests:
            # Keyword filter
            if self.keyword:
                keyword_lower = self.keyword.lower()
                if keyword_lower not in req.title.lower() and keyword_lower not in req.description.lower():
                    continue
            
            # Category filter
            if self.category and req.category != self.category:
                continue
            
            # Priority filter
            if self.priority and req.priority != self.priority:
                continue
            
            # Service type filter
            if self.service_type and req.service_type != self.service_type:
                continue
            
            filtered.append(req)
        
        return filtered
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request search"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            # Validate filters
            is_valid, error_msg = self.validate_filters()
            if not is_valid:
                return ({'success': False, 'message': error_msg}, 400)
            
            # Get requests
            if self.my_requests:
                # Get user's own requests
                self.requests = Request.by_pin_user(self.user.id)
                if self.status:
                    self.requests = [r for r in self.requests if r.status == self.status]
            else:
                # Search all requests
                self.requests = Request.search(
                    keyword=self.keyword,
                    category=self.category,
                    status=self.status,
                    priority=self.priority,
                    service_type=self.service_type
                )
            
            # Apply additional filters
            filtered_requests = self.apply_filters(self.requests)
            
            # Build filters applied info
            filters_applied = {}
            if self.keyword: filters_applied['keyword'] = self.keyword
            if self.category: filters_applied['category'] = self.category
            if self.status: filters_applied['status'] = self.status
            if self.priority: filters_applied['priority'] = self.priority
            if self.service_type: filters_applied['service_type'] = self.service_type
            
            # Convert to dictionaries
            requests_data = [req.to_dict() for req in filtered_requests]
            
            return ({
                'success': True,
                'data': requests_data,
                'count': len(requests_data),
                'filters_applied': filters_applied
            }, 200)
            
        except Exception as e:
            print(f"Error searching requests: {str(e)}")
            return ({'success': False, 'message': 'Internal server error'}, 500)
