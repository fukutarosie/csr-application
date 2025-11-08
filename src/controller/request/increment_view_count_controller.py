"""
Increment View Count Controller - Track CSR views (Control Layer)
Supports US-27: PIN views number of times request has been viewed
"""

from src.entity.request import Request
from src.utils.helpers import ResponseHelpers

class IncrementViewCountController:
    """
    Increment view count when CSR views a request
    Supports US-27 analytics tracking
    """
    
    @staticmethod
    def increment_view(request_id):
        """
        Increment view count for a request
        
        Returns: (response_dict, status_code)
        """
        try:
            # Verify request exists
            req = Request.get_request(request_id)
            if not req:
                return (ResponseHelpers.error_response('Request not found', 404), 404)
            
            # Only track views for ACTIVE requests
            if req.get('status') != 'ACTIVE':
                return (ResponseHelpers.success_response(
                    message='View not tracked for non-active request'
                ), 200)
            
            # Call ENTITY layer to increment view count
            success = Request.increment_view_count(request_id)
            
            if success:
                return (ResponseHelpers.success_response(
                    message='View recorded successfully'
                ), 200)
            else:
                return (ResponseHelpers.error_response('Failed to record view'), 500)
            
        except Exception as e:
            print(f"[ERROR] Increment view count failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return (ResponseHelpers.error_response('Internal server error'), 500)
