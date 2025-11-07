"""
Update Shortlist Status Controller - CSR updates shortlist status (Control Layer)
"""

from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import RequestHelpers, ResponseHelpers

class UpdateShortlistStatusController:
    """
    Update shortlist entry status
    """
    
    @staticmethod
    def update_status(auth_token, shortlist_id, data):
        """
        Update shortlist status
        
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
            required_fields = ['status']
            is_valid, error_msg, _ = RequestHelpers.validate_required_fields(data, required_fields)
            if not is_valid:
                return (ResponseHelpers.error_response(error_msg, 400), 400)
            
            status = data.get('status')
            notes = data.get('notes')
            volunteered_hours = data.get('volunteered_hours')
            feedback_from_pin = data.get('feedback_from_pin')
            
            # Validate status
            valid_statuses = ['IN_PROGRESS', 'COMPLETED', 'DECLINED', 'SHORTLISTED']
            if status not in valid_statuses:
                return (ResponseHelpers.error_response(
                    f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    400
                ), 400)
            
            # Call ENTITY layer
            updated_entry = Shortlist.update_shortlist_status(
                shortlist_id=shortlist_id,
                csr_user_id=csr_user_id,
                new_status=status,
                notes=notes,
                volunteered_hours=volunteered_hours
            )
            
            if not updated_entry:
                return (ResponseHelpers.error_response(
                    'Failed to update status. Shortlist entry not found or unauthorized.',
                    400
                ), 400)
            
            # Return response
            return (ResponseHelpers.success_response(
                data=updated_entry,
                message='Shortlist status updated successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Update shortlist status failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
