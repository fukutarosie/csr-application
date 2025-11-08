"""
Remove from Shortlist Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers


class RemoveFromShortlistController:
    """
    Remove from Shortlist Controller - TRUE OOP
    
    Usage:
        controller = RemoveFromShortlistController(auth_token, shortlist_id)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, shortlist_id: int):
        """
        Initialize controller
        
        Args:
            auth_token: JWT authentication token
            shortlist_id: ID of shortlist entry to remove
        """
        self.auth_token = auth_token
        self.shortlist_id = shortlist_id
        self.user = None
        self.shortlist = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute shortlist removal
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Load Shortlist object
            self.shortlist = Shortlist.find(self.shortlist_id)
            if not self.shortlist:
                return (ResponseHelpers.error_response('Shortlist entry not found', 404), 404)
            
            # Verify ownership
            if self.shortlist.csr_user_id != self.user.id:
                return (ResponseHelpers.error_response('Unauthorized', 403), 403)
            
            # Delete shortlist entry (instance method)
            self.shortlist.delete()
            
            return (ResponseHelpers.success_response(
                message='Removed from shortlist successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Remove from shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
