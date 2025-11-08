"""
Get Shortlist Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers


class GetShortlistController:
    """
    Get Shortlist Controller - TRUE OOP
    
    Usage:
        controller = GetShortlistController(auth_token, status_filter, page, limit)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, status_filter: str = None, page: str = None, limit: str = None):
        """
        Initialize controller
        
        Args:
            auth_token: JWT authentication token
            status_filter: Optional status filter
            page: Page number for pagination
            limit: Items per page
        """
        self.auth_token = auth_token
        self.status_filter = status_filter
        self.page = page
        self.limit = limit
        self.user = None
        self.shortlist_items = []
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def parse_pagination(self) -> Tuple[int, int]:
        """Parse pagination parameters"""
        try:
            page = int(self.page) if self.page else 1
            limit = int(self.limit) if self.limit else 50
        except:
            page = 1
            limit = 50
        return page, limit
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute shortlist retrieval
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Parse pagination
            page, limit = self.parse_pagination()
            offset = (page - 1) * limit
            
            # Get Shortlist objects (factory method)
            # If status_filter is None or empty, show ALL items
            self.shortlist_items = Shortlist.search(
                csr_user_id=self.user.id,
                status=self.status_filter if self.status_filter else None
            )
            
            # Convert to dictionaries
            shortlist_data = [item.to_dict() for item in self.shortlist_items]
            
            return (ResponseHelpers.success_response(
                data=shortlist_data,
                message='Shortlist retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
