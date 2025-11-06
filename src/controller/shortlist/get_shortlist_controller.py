"""
Get Shortlist Controller - CSR views their shortlist
Handles retrieving CSR's shortlisted requests

BOUNDARY Layer (BCE Architecture)
"""

from flask import Blueprint, request, jsonify
from src.entity.shortlist import Shortlist
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, ResponseHelpers, PaginationHelpers

get_shortlist_blueprint = Blueprint(
    'get_shortlist',
    __name__,
    url_prefix='/api/shortlist'
)


class GetShortlistController:
    """
    Get CSR's shortlist with filters and pagination
    """
    
    @staticmethod
    @get_shortlist_blueprint.route('', methods=['GET'])
    @require_role('CSR Rep')
    def get_shortlist():
        """
        Get CSR's shortlist with filters
        
        Query Parameters:
            - status: Filter by status (SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED)
            - page: Page number (default: 1)
            - limit: Results per page (default: 10)
        
        Returns:
            {
                "success": true,
                "data": [shortlist_entries],
                "pagination": {...},
                "message": "Shortlist retrieved successfully"
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
            
            # Extract query parameters
            status_filter = request.args.get('status')
            
            # Extract pagination
            page, limit = PaginationHelpers.get_pagination_params(request)
            
            # Call ENTITY layer
            result = Shortlist.search_shortlist(
                csr_user_id=csr_user_id,
                status=status_filter,
                page=page,
                limit=limit
            )
            
            # Return response
            return ResponseHelpers.success_response(
                data=result.get('data', []),
                message='Shortlist retrieved successfully',
                pagination=result.get('pagination')
            ), 200
            
        except Exception as e:
            print(f"[ERROR] Get shortlist failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
