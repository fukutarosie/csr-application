"""
Get Request Analytics Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers


class GetRequestAnalyticsController:
    """
    Get Request Analytics Controller - TRUE OOP
    
    Usage:
        controller = GetRequestAnalyticsController(auth_token, request_id)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_id: int):
        """Initialize controller"""
        self.auth_token = auth_token
        self.request_id = request_id
        self.user = None
        self.request = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute analytics retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Load Request object
            self.request = Request.find(self.request_id)
            if not self.request:
                return (ResponseHelpers.error_response('Request not found', 404), 404)
            
            # Verify ownership
            if self.request.pin_user_id != self.user.id:
                return (ResponseHelpers.error_response('You can only view analytics for your own requests', 403), 403)
            
            # Build analytics data
            analytics = {
                'request_id': self.request.id,
                'view_count': self.request.view_count or 0,
                'shortlist_count': self.request.shortlist_count or 0,
                'status': self.request.status,
                'created_at': self.request.created_at.isoformat() if self.request.created_at else None
            }
            
            return (ResponseHelpers.success_response(
                data=analytics,
                message='Analytics retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get request analytics failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
