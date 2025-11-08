"""
Increment View Count Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.request import Request
from src.utils.helpers import ResponseHelpers


class IncrementViewCountController:
    """
    Increment View Count Controller - TRUE OOP
    
    Usage:
        controller = IncrementViewCountController(request_id)
        response, status = controller.execute()
    """
    
    def __init__(self, request_id: int):
        """Initialize controller"""
        self.request_id = request_id
        self.request = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute view count increment"""
        try:
            # Load Request object
            self.request = Request.find(self.request_id)
            if not self.request:
                return (ResponseHelpers.error_response('Request not found', 404), 404)
            
            # Only track views for ACTIVE requests
            if self.request.status != Request.STATUS_ACTIVE:
                return (ResponseHelpers.success_response(
                    message='View not tracked for non-active request'
                ), 200)
            
            # Increment view count (instance method)
            self.request.increment_view_count()
            
            return (ResponseHelpers.success_response(
                message='View recorded successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Increment view count failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
