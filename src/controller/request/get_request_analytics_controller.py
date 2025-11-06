"""
Get Request Analytics Controller - US-27, US-28
Handles retrieving analytics for a PIN user's request

BOUNDARY Layer (BCE Architecture)
- Validates HTTP requests
- Calls ENTITY layer (Request)
- Returns formatted HTTP responses
"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, ResponseHelpers

get_request_analytics_blueprint = Blueprint(
    'get_request_analytics',
    __name__,
    url_prefix='/api/requests'
)


class GetRequestAnalyticsController:
    """
    US-27: View count tracking
    US-28: Shortlist count tracking
    """
    
    @staticmethod
    @get_request_analytics_blueprint.route('/<int:request_id>/analytics', methods=['GET'])
    @require_role('PIN')
    def get_analytics(request_id):
        """
        Get analytics for a specific request (view count, shortlist count)
        
        URL Parameters:
            - request_id: Request ID
        
        Returns:
            {
                "success": true,
                "data": {
                    "request_id": 1,
                    "title": "Need grocery delivery",
                    "view_count": 12,
                    "shortlist_count": 3
                },
                "message": "Analytics retrieved successfully"
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
            
            # Get request to verify ownership (CONTROL logic)
            existing_request = Request.get_request(request_id)
            if not existing_request:
                return ResponseHelpers.error_response('Request not found', 404)
            
            # Verify ownership
            if existing_request['pin_user_id'] != pin_user_id:
                return ResponseHelpers.error_response('You can only view analytics for your own requests', 403)
            
            # Call ENTITY layer to get analytics
            analytics = Request.get_request_analytics(request_id)
            
            if not analytics:
                return ResponseHelpers.error_response('Analytics not found', 404)
            
            # Return response (BOUNDARY)
            return ResponseHelpers.success_response(
                data=analytics,
                message='Analytics retrieved successfully'
            ), 200
            
        except Exception as e:
            print(f"[ERROR] Get request analytics failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
