"""
Update Shortlist Status Controller - CSR updates shortlist status
Handles status updates (IN_PROGRESS, COMPLETED, DECLINED)

BOUNDARY Layer (BCE Architecture)
"""

from flask import Blueprint, request, jsonify
from src.entity.shortlist import Shortlist
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers

update_shortlist_status_blueprint = Blueprint(
    'update_shortlist_status',
    __name__,
    url_prefix='/api/shortlist'
)


class UpdateShortlistStatusController:
    """
    Update shortlist entry status
    """
    
    @staticmethod
    @update_shortlist_status_blueprint.route('/<int:shortlist_id>/status', methods=['PATCH'])
    @require_role('CSR Rep')
    def update_status(shortlist_id):
        """
        Update shortlist status
        
        Body:
            {
                "status": "IN_PROGRESS" | "COMPLETED" | "DECLINED",
                "notes": "Optional notes",
                "volunteered_hours": 2.5,  // For COMPLETED status
                "feedback_from_pin": "Great CSR!"  // Optional
            }
        
        Returns:
            {
                "success": true,
                "data": {updated_shortlist},
                "message": "Status updated successfully"
            }
        """
        try:
            # Extract and validate JWT token
            token = TokenHelpers.extract_token_from_header(request)
            if not token:
                return ResponseHelpers.error_response('Missing authorization token', 401)
            
            # Verify token and get user
            user_data = User.verify_session_token(token)
            if not user_data:
                return ResponseHelpers.error_response('Invalid or expired token', 401)
            
            csr_user_id = user_data['id']
            
            # Extract request body
            data = RequestHelpers.get_json_body(request)
            if not data:
                return ResponseHelpers.error_response('Request body is required', 400)
            
            # Validate required fields
            required_fields = ['status']
            is_valid, error_msg, _ = RequestHelpers.validate_required_fields(data, required_fields)
            if not is_valid:
                return ResponseHelpers.error_response(error_msg, 400)
            
            status = data.get('status')
            notes = data.get('notes')
            volunteered_hours = data.get('volunteered_hours')
            feedback_from_pin = data.get('feedback_from_pin')
            
            # Validate status
            valid_statuses = ['IN_PROGRESS', 'COMPLETED', 'DECLINED', 'SHORTLISTED']
            if status not in valid_statuses:
                return ResponseHelpers.error_response(
                    f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    400
                )
            
            # Call ENTITY layer
            updated_entry = Shortlist.update_shortlist_status(
                shortlist_id=shortlist_id,
                csr_user_id=csr_user_id,
                new_status=status,
                notes=notes,
                volunteered_hours=volunteered_hours
            )
            
            if not updated_entry:
                return ResponseHelpers.error_response(
                    'Failed to update status. Shortlist entry not found or unauthorized.',
                    400
                )
            
            # Return response
            return ResponseHelpers.success_response(
                data=updated_entry,
                message='Shortlist status updated successfully'
            ), 200
            
        except Exception as e:
            print(f"[ERROR] Update shortlist status failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
