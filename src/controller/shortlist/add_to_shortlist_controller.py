"""
Add to Shortlist Controller - CSR adds PIN request to shortlist
Handles CSR shortlisting PIN requests

BOUNDARY Layer (BCE Architecture)
"""

from flask import Blueprint, request, jsonify
from src.entity.shortlist import Shortlist
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers

add_to_shortlist_blueprint = Blueprint(
    'add_to_shortlist',
    __name__,
    url_prefix='/api/shortlist'
)


class AddToShortlistController:
    """
    CSR adds a PIN request to their shortlist
    """
    
    @staticmethod
    @add_to_shortlist_blueprint.route('', methods=['POST'])
    @require_role('CSR Rep')
    def add_shortlist():
        """
        Add a request to CSR's shortlist
        
        Body:
            {
                "request_id": 123,
                "notes": "Optional notes"
            }
        
        Returns:
            {
                "success": true,
                "data": {shortlist_entry},
                "message": "Request added to shortlist"
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
            required_fields = ['request_id']
            is_valid, error_msg, _ = RequestHelpers.validate_required_fields(data, required_fields)
            if not is_valid:
                return ResponseHelpers.error_response(error_msg, 400)
            
            request_id = data.get('request_id')
            notes = data.get('notes')
            
            # Call ENTITY layer
            shortlist_entry = Shortlist.add_to_shortlist(
                csr_user_id=csr_user_id,
                request_id=request_id,
                notes=notes
            )
            
            if not shortlist_entry:
                return ResponseHelpers.error_response(
                    'Failed to add to shortlist. Request may not exist, is not active, or is already shortlisted.',
                    400
                )
            
            # Increment shortlist count on the request (analytics)
            Request.increment_shortlist_count(request_id)
            
            # Return response
            return ResponseHelpers.success_response(
                data=shortlist_entry,
                message='Request added to shortlist successfully'
            ), 201
            
        except Exception as e:
            print(f"[ERROR] Add to shortlist failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
