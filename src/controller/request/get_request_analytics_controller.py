"""
Get Request Analytics Controller - US-27, US-28 (Control Layer)
Handles retrieving analytics for a PIN user's request
"""

from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers

class GetRequestAnalyticsController:
    """
    US-27: View count tracking
    US-28: Shortlist count tracking
    """
    
    @staticmethod
    def get_analytics(auth_token, request_id):
        """
        Get analytics for a specific request (view count, shortlist count)
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            pin_user_id = user_data['id']
            
            # Get request to verify ownership
            existing_request = Request.get_request(request_id)
            if not existing_request:
                return (ResponseHelpers.error_response('Request not found', 404), 404)
            
            # Verify ownership
            if existing_request['pin_user_id'] != pin_user_id:
                return (ResponseHelpers.error_response('You can only view analytics for your own requests', 403), 403)
            
            # Call ENTITY layer to get analytics
            analytics = Request.get_request_analytics(request_id)
            
            if not analytics:
                return (ResponseHelpers.error_response('Analytics not found', 404), 404)
            
            # Return response
            return (ResponseHelpers.success_response(
                data=analytics,
                message='Analytics retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get request analytics failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
