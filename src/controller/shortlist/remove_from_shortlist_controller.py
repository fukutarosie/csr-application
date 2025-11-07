"""
Remove from Shortlist Controller - CSR removes request from shortlist (Control Layer)
"""

from src.entity.shortlist import Shortlist
from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers

class RemoveFromShortlistController:
    """
    Remove a request from CSR's shortlist
    """
    
    @staticmethod
    def remove_shortlist(auth_token, shortlist_id):
        """
        Remove shortlist entry
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            csr_user_id = user_data['id']
            
            # Get shortlist entry to get request_id before deletion
            shortlist_entry = Shortlist.get_shortlist_item(shortlist_id)
            
            if shortlist_entry and shortlist_entry.get('csr_user_id') == csr_user_id:
                request_id = shortlist_entry.get('request_id')
            else:
                request_id = None
            
            # Call ENTITY layer to remove
            success = Shortlist.remove_from_shortlist(
                shortlist_id=shortlist_id,
                csr_user_id=csr_user_id
            )
            
            if not success:
                return (ResponseHelpers.error_response(
                    'Failed to remove from shortlist. Entry not found or unauthorized.',
                    400
                ), 400)
            
            # Decrement shortlist count on the request (analytics)
            if request_id:
                Request.decrement_shortlist_count(request_id)
            
            # Return response
            return (ResponseHelpers.success_response(
                message='Removed from shortlist successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Remove from shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
