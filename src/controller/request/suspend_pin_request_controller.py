"""
Suspend PIN Request Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.request import Request
from src.entity import User


class SuspendPINRequestController:
    """
    Suspend PIN Request Controller - TRUE OOP
    
    Usage:
        controller = SuspendPINRequestController(auth_token, request_id, data)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_id: int, data: Dict):
        """Initialize controller"""
        self.auth_token = auth_token
        self.request_id = request_id
        self.data = data
        self.user = None
        self.request = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request suspension"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            # Load Request object
            self.request = Request.find(self.request_id)
            if not self.request:
                return ({'success': False, 'message': 'Request not found'}, 404)
            
            # Verify ownership
            if self.request.pin_user_id != self.user.id:
                return ({'success': False, 'message': 'Unauthorized'}, 403)
            
            # Verify status is ACTIVE
            if self.request.status != Request.STATUS_ACTIVE:
                return ({'success': False, 'message': 'Only ACTIVE requests can be suspended'}, 400)
            
            # Suspend request (instance method)
            reason = self.data.get('reason', '').strip() if self.data else None
            self.request.suspend(reason)
            
            return ({
                'success': True,
                'data': self.request.to_dict(),
                'message': 'Request suspended successfully'
            }, 200)
            
        except Exception as e:
            print(f"Error suspending request: {str(e)}")
            return ({'success': False, 'message': 'Internal server error'}, 500)
