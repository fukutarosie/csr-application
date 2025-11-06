"""
Get PIN Requests Controller - US-14
Handles viewing PIN user's own requests with filtering and pagination

BOUNDARY Layer (BCE Architecture)
- Validates HTTP requests
- Calls ENTITY layer (Request)
- Returns formatted HTTP responses
"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers, PaginationHelpers

get_pin_requests_blueprint = Blueprint(
    'get_pin_requests',
    __name__,
    url_prefix='/api/requests'
)


class GetPINRequestsController:
    """
    US-14: View existing requests (PIN user views own requests only)
    """
    
    @staticmethod
    @get_pin_requests_blueprint.route('', methods=['GET'])
    @require_role('PIN')
    def get_requests():
        """
        Get all requests for authenticated PIN user with filtering and pagination
        
        Query Parameters:
            - status: Filter by status (ACTIVE, SUSPENDED, FULFILLED, CANCELLED)
            - service_type: Filter by service type
            - page: Page number (default: 1)
            - limit: Results per page (default: 10)
        
        Returns:
            {
                "success": true,
                "data": [requests],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 25,
                    "total_pages": 3
                },
                "message": "Requests retrieved successfully"
            }
        """
        try:
            # Extract and validate JWT token (BOUNDARY)
            token = TokenHelpers.extract_token_from_header(request)
            if not token:
                return ResponseHelpers.error_response('Missing authorization token', 401)
            
            # Verify token and get user
            user_data = User.verify_session_token(token)
            if not user_data:
                return ResponseHelpers.error_response('Invalid or expired token', 401)
            
            pin_user_id = user_data['id']
            
            # Extract query parameters (BOUNDARY)
            filters = {}
            if request.args.get('status'):
                filters['status'] = request.args.get('status')
            if request.args.get('service_type'):
                filters['service_type'] = request.args.get('service_type')
            
            # Extract pagination parameters
            page, limit = PaginationHelpers.get_pagination_params(request)
            
            # Call ENTITY layer
            result = Request.get_requests_for_user(
                user_id=pin_user_id,
                filters=filters if filters else None,
                page=page,
                limit=limit
            )
            
            # Return response (BOUNDARY)
            return ResponseHelpers.success_response(
                data=result['data'],
                message='Requests retrieved successfully',
                pagination=result['pagination']
            ), 200
            
        except Exception as e:
            print(f"[ERROR] Get PIN requests failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
