"""
Add to Shortlist Controller - CSR adds PIN request to shortlist (Control Layer)
"""

from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import RequestHelpers, ResponseHelpers

class AddToShortlistController:
    """
    CSR adds a PIN request to their shortlist
    """
    
    @staticmethod
    def add_shortlist(auth_token, data):
        """
        Add a request to CSR's shortlist
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            csr_user_id = user_data['id']
            
            # Extract request body
            if not data:
                return (ResponseHelpers.error_response('Request body is required', 400), 400)
            
            # Validate required fields
            required_fields = ['request_id']
            is_valid, error_msg, _ = RequestHelpers.validate_required_fields(data, required_fields)
            if not is_valid:
                return (ResponseHelpers.error_response(error_msg, 400), 400)
            
            request_id = data.get('request_id')
            notes = data.get('notes')
            
            # Call ENTITY layer
            shortlist_entry = Shortlist.add_to_shortlist(
                csr_user_id=csr_user_id,
                request_id=request_id,
                notes=notes
            )
            
            if not shortlist_entry:
                return (ResponseHelpers.error_response(
                    'Failed to add to shortlist. Request may not exist, is not active, or is already shortlisted.',
                    400
                ), 400)
            
            # Note: shortlist_count is automatically incremented by Shortlist.add_to_shortlist() in Entity layer
            
            # Return response
            return (ResponseHelpers.success_response(
                data=shortlist_entry,
                message='Request added to shortlist successfully'
            ), 201)
            
        except Exception as e:
            print(f"[ERROR] Add to shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
