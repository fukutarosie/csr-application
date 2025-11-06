"""
Get Completed Matches Controller - US-29, US-30
Handles retrieving completed matches (fulfilled requests) for a PIN user

BOUNDARY Layer (BCE Architecture)
- Validates HTTP requests
- Calls ENTITY layer (Request)
- Returns formatted HTTP responses
"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, ResponseHelpers, PaginationHelpers

get_completed_matches_blueprint = Blueprint(
    'get_completed_matches',
    __name__,
    url_prefix='/api/requests'
)


class GetCompletedMatchesController:
    """
    US-29: Search completed matches by service category
    US-30: Filter completed matches by date
    """
    
    @staticmethod
    @get_completed_matches_blueprint.route('/history', methods=['GET'])
    @require_role('PIN')
    def get_history():
        """
        Get completed matches (fulfilled requests) for authenticated PIN user
        
        Query Parameters:
            - start_date: Filter by fulfilled_at >= start_date (ISO format)
            - end_date: Filter by fulfilled_at <= end_date (ISO format)
            - page: Page number (default: 1)
            - limit: Results per page (default: 10)
        
        Returns:
            {
                "success": true,
                "data": [
                    {
                        "id": 1,
                        "title": "Grocery delivery",
                        "status": "FULFILLED",
                        "fulfilled_at": "2024-10-20T10:30:00Z",
                        "matched_csr": [
                            {
                                "id": 5,
                                "csr_user_id": 3,
                                "status": "COMPLETED",
                                "volunteered_hours": 2.5,
                                "feedback_from_pin": "Great help!"
                            }
                        ]
                    }
                ],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 8,
                    "total_pages": 1
                },
                "message": "Completed matches retrieved successfully"
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
            if request.args.get('start_date'):
                filters['start_date'] = request.args.get('start_date')
            if request.args.get('end_date'):
                filters['end_date'] = request.args.get('end_date')
            
            # Extract pagination parameters
            page, limit = PaginationHelpers.get_pagination_params(request)
            
            # Call ENTITY layer
            result = Request.get_completed_matches(
                user_id=pin_user_id,
                filters=filters if filters else None,
                page=page,
                limit=limit
            )
            
            # Return response (BOUNDARY)
            return ResponseHelpers.success_response(
                data=result['data'],
                message='Completed matches retrieved successfully',
                pagination=result['pagination']
            ), 201
            
        except Exception as e:
            print(f"[ERROR] Get completed matches failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
