"""
Get Completed Matches Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from datetime import datetime
from src.entity.request import Request
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers


class GetCompletedMatchesController:
    """
    Get Completed Matches Controller - TRUE OOP
    
    Usage:
        controller = GetCompletedMatchesController(auth_token, start_date, end_date, page, limit)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, start_date: str = None, end_date: str = None,
                 page_str: str = None, limit_str: str = None, service_type: str = None):
        """Initialize controller"""
        self.auth_token = auth_token
        self.start_date = start_date
        self.end_date = end_date
        self.page_str = page_str
        self.limit_str = limit_str
        self.service_type = service_type.lower() if service_type else None
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
        """Execute completed matches retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Get fulfilled requests for this PIN user
            self.requests = Request.by_pin_user(self.user.id)
            self.requests = [r for r in self.requests if r.status == Request.STATUS_FULFILLED]
            
            # Apply date filters
            if self.start_date:
                self.requests = [
                    r for r in self.requests
                    if self._is_on_or_after(r.fulfilled_at, self.start_date)
                ]
            if self.end_date:
                self.requests = [
                    r for r in self.requests
                    if self._is_on_or_before(r.fulfilled_at, self.end_date)
                ]
            
            # Apply service type filter
            if self.service_type:
                self.requests = [
                    r for r in self.requests
                    if (r.service_type or '').lower() == self.service_type
                ]
            
            # Parse pagination
            page, limit = self.parse_pagination()
            
            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_requests = self.requests[start:end]
            
            # Convert to dictionaries
            requests_data = []
            for req in paginated_requests:
                req_dict = req.to_dict()
                assignment = Shortlist.active_assignment_for_request(req.id)
                if assignment:
                    req_dict['assignment_status'] = assignment.status
                    req_dict['active_assignment'] = assignment.to_assignment_dict()
                else:
                    req_dict['assignment_status'] = None
                    req_dict['active_assignment'] = None
                requests_data.append(req_dict)
            
            # Build pagination info
            pagination = {
                'page': page,
                'limit': limit,
                'total': len(self.requests),
                'pages': (len(self.requests) + limit - 1) // limit
            }
            
            return (ResponseHelpers.success_response(
                data=requests_data,
                message='Completed matches retrieved successfully',
                pagination=pagination
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get completed matches failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO datetime string safely"""
        if not date_str:
            return None
        try:
            cleaned = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(cleaned)
        except Exception:
            return None

    def _is_on_or_after(self, date_str: str, start_date_str: str) -> bool:
        date_val = self._parse_date(date_str)
        start_val = self._parse_date(start_date_str)
        if not date_val or not start_val:
            return False
        return date_val.date() >= start_val.date()

    def _is_on_or_before(self, date_str: str, end_date_str: str) -> bool:
        date_val = self._parse_date(date_str)
        end_val = self._parse_date(end_date_str)
        if not date_val or not end_val:
            return False
        return date_val.date() <= end_val.date()
