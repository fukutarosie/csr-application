"""
Get Shortlist Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from datetime import datetime
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
    
    def __init__(
        self,
        auth_token: str,
        status_filter: str = None,
        page: str = None,
        limit: str = None,
        start_date: str = None,
        end_date: str = None,
        service_type: str = None
    ):
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
        self.start_date = start_date
        self.end_date = end_date
        self.service_type = service_type.lower() if service_type else None
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
            
            # Apply date filters
            if self.start_date or self.end_date:
                self.shortlist_items = [
                    item for item in self.shortlist_items
                    if self._within_date_range(item)
                ]

            # Apply service type filter
            if self.service_type:
                self.shortlist_items = [
                    item for item in self.shortlist_items
                    if (item.requests or {}).get('service_type', '').lower() == self.service_type
                ]
            
            # Convert to dictionaries (apply pagination after filtering if needed)
            shortlist_data = [item.to_dict() for item in self.shortlist_items]
            
            return (ResponseHelpers.success_response(
                data=shortlist_data,
                message='Shortlist retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)

    def _within_date_range(self, item: Shortlist) -> bool:
        """Check if shortlist item falls within the provided date range"""
        date_candidate = item.completion_date or item.shortlisted_at
        item_date = self._parse_date(date_candidate)
        if not item_date:
            return False
        
        if self.start_date:
            start_date = self._parse_date(self.start_date)
            if not start_date or item_date.date() < start_date.date():
                return False
        
        if self.end_date:
            end_date = self._parse_date(self.end_date)
            if not end_date or item_date.date() > end_date.date():
                return False
        
        return True

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        try:
            cleaned = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(cleaned)
        except Exception:
            return None
