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

            # If frontend does not provide a status filter, default to SHORTLISTED
            # to show the CSR their active shortlist items first.
            if not status_filter:
                status_filter = Shortlist.STATUS_SHORTLISTED
            
            # Parse pagination
            try:
                page = int(page_str) if page_str else 1
                limit = int(limit_str) if limit_str else 50
            except:
                page = 1
                limit = 50
            
            # Calculate offset from page number
            offset = (page - 1) * limit
            
            # Call ENTITY layer with offset
            shortlist_items = Shortlist.search_shortlist(
                csr_user_id=csr_user_id,
                status=status_filter,
                limit=limit,
                offset=offset
            )
            
            print(f"[DEBUG] Shortlist controller - User ID: {csr_user_id}, Status filter: {status_filter}, Items found: {len(shortlist_items)}")
            if shortlist_items:
                print(f"[DEBUG] First item: {shortlist_items[0]}")
            
            # Return response
            return (ResponseHelpers.success_response(
                data=shortlist_items,
                message='Shortlist retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get shortlist failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return (ResponseHelpers.error_response('Internal server error'), 500)
