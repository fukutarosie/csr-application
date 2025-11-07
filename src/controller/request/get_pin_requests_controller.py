"""
Get PIN Requests Controller - US-14 (Control Layer)
Handles viewing PIN user's own requests with filtering and pagination
"""

from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers, PaginationHelpers

class GetPINRequestsController:
    """
    US-14: View existing requests (PIN user views own requests only)
    """
    
    @staticmethod
    def get_requests(auth_token, status_param, service_type, page_str, limit_str):
        """
        Get all requests for authenticated PIN user with filtering and pagination
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify token and get user
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            pin_user_id = user_data['id']
            
            # Build filters
            filters = {}
            if status_param:
                filters['status'] = status_param
            if service_type:
                filters['service_type'] = service_type
            
            # Parse pagination
            try:
                page = int(page_str) if page_str else 1
                limit = int(limit_str) if limit_str else 10
            except:
                page = 1
                limit = 10
            
            # Call ENTITY layer
            result = Request.get_requests_for_user(
                user_id=pin_user_id,
                filters=filters if filters else None,
                page=page,
                limit=limit
            )
            
            # Return response
            return (ResponseHelpers.success_response(
                data=result['data'],
                message='Requests retrieved successfully',
                pagination=result['pagination']
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get PIN requests failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
