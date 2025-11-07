"""
Get Shortlist Controller - CSR views their shortlist (Control Layer)
"""

from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import ResponseHelpers

class GetShortlistController:
    """
    Get CSR's shortlist with filters and pagination
    """
    
    @staticmethod
    def get_shortlist(auth_token, status_filter, page_str, limit_str):
        """
        Get CSR's shortlist with filters
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            csr_user_id = user_data['id']
            
            # Parse pagination
            try:
                page = int(page_str) if page_str else 1
                limit = int(limit_str) if limit_str else 10
            except:
                page = 1
                limit = 10
            
            # Call ENTITY layer
            result = Shortlist.search_shortlist(
                csr_user_id=csr_user_id,
                status=status_filter,
                page=page,
                limit=limit
            )
            
            # Return response
            return (ResponseHelpers.success_response(
                data=result.get('data', []),
                message='Shortlist retrieved successfully',
                pagination=result.get('pagination')
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
