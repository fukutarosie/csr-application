"""
Get PIN Requests Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers, PaginationHelpers


class GetPINRequestsController:
    """
    Get PIN Requests Controller - TRUE OOP
    
    Usage:
        controller = GetPINRequestsController(auth_token, status_param, service_type, page, limit)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, status_param: str = None, service_type: str = None, 
                 page_str: str = None, limit_str: str = None):
        """Initialize controller"""
        self.auth_token = auth_token
        self.status_param = status_param
        self.service_type = service_type
        self.page_str = page_str
        self.limit_str = limit_str
        self.user = None
        self.requests = []
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def parse_pagination(self) -> Tuple[int, int]:
        """Parse pagination parameters"""
        try:
            page = int(self.page_str) if self.page_str else 1
            limit = int(self.limit_str) if self.limit_str else 10
        except:
            page = 1
            limit = 10
        return page, limit
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Get requests for this PIN user
            self.requests = Request.by_pin_user(self.user.id)
            
            # Apply filters
            if self.status_param:
                self.requests = [r for r in self.requests if r.status == self.status_param]
            if self.service_type:
                self.requests = [r for r in self.requests if r.service_type == self.service_type]
            
            # Parse pagination
            page, limit = self.parse_pagination()
            
            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_requests = self.requests[start:end]
            
            # Convert to dictionaries
            requests_data = [req.to_dict() for req in paginated_requests]
            
            # Build pagination info
            pagination = {
                'page': page,
                'limit': limit,
                'total': len(self.requests),
                'pages': (len(self.requests) + limit - 1) // limit
            }
            
            return (ResponseHelpers.success_response(
                data=requests_data,
                message='Requests retrieved successfully',
                pagination=pagination
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get PIN requests failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
