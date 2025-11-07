"""
Get Shortlist Statistics Controller - CSR views volunteering statistics (Control Layer)
"""

from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers

class GetShortlistStatsController:
    """
    Get CSR's volunteering statistics
    """
    
    @staticmethod
    def get_stats(auth_token):
        """
        Get CSR's statistics
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            csr_user_id = user_data['id']
            
            # Call ENTITY layer
            stats = Shortlist.get_statistics(csr_user_id=csr_user_id)
            
            if stats is None:
                return (ResponseHelpers.error_response('Failed to retrieve statistics', 400), 400)
            
            # Return response
            return (ResponseHelpers.success_response(
                data=stats,
                message='Statistics retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get statistics failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
