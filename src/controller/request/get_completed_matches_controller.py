"""
Get Completed Matches Controller - US-29, US-30 (Control Layer)
Handles retrieving completed matches (fulfilled requests) for a PIN user
"""

from src.entity.request import Request
from src.entity import User
from src.utils.helpers import ResponseHelpers

class GetCompletedMatchesController:
    """
    US-29: Search completed matches by service category
    US-30: Filter completed matches by date
    """
    
    @staticmethod
    def get_history(auth_token, start_date, end_date, page_str, limit_str):
        """
        Get completed matches (fulfilled requests) for authenticated PIN user
        
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
            if start_date:
                filters['start_date'] = start_date
            if end_date:
                filters['end_date'] = end_date
            
            # Parse pagination
            try:
                page = int(page_str) if page_str else 1
                limit = int(limit_str) if limit_str else 10
            except:
                page = 1
                limit = 10
            
            # Call ENTITY layer
            result = Request.get_completed_matches(
                user_id=pin_user_id,
                filters=filters if filters else None,
                page=page,
                limit=limit
            )
            
            # Return response
            return (ResponseHelpers.success_response(
                data=result['data'],
                message='Completed matches retrieved successfully',
                pagination=result['pagination']
            ), 201)
            
        except Exception as e:
            print(f"[ERROR] Get completed matches failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
