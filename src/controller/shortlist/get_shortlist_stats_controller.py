"""
Get Shortlist Statistics Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers


class GetShortlistStatsController:
    """
    Get Shortlist Statistics Controller - TRUE OOP
    
    Usage:
        controller = GetShortlistStatsController(auth_token)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str):
        """Initialize controller"""
        self.auth_token = auth_token
        self.user = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute statistics retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Get all shortlist items for this CSR user
            shortlist_items = Shortlist.by_csr_user(self.user.id)
            
            # Calculate statistics
            stats = {
                'total_shortlisted': len(shortlist_items),
                'in_progress': len([s for s in shortlist_items if s.status == 'IN_PROGRESS']),
                'completed': len([s for s in shortlist_items if s.status == 'COMPLETED']),
                'shortlisted': len([s for s in shortlist_items if s.status == 'SHORTLISTED']),
                'total_hours': sum(s.volunteered_hours or 0 for s in shortlist_items if s.volunteered_hours)
            }
            
            return (ResponseHelpers.success_response(
                data=stats,
                message='Statistics retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get statistics failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
