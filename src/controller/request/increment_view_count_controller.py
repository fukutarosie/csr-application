"""
Increment View Count Controller - Track CSR views
Handles incrementing view count when CSR views a request

Supports US-27: PIN views number of times request has been viewed

CONTROL Layer (BCE Architecture)
"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity.user import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, ResponseHelpers

increment_view_count_blueprint = Blueprint(
    'increment_view_count',
    __name__,
    url_prefix='/api/requests'
)


class IncrementViewCountController:
    """
    Increment view count when CSR views a request
    Supports US-27 analytics tracking
    """
    
    @staticmethod
    @increment_view_count_blueprint.route('/<int:request_id>/view', methods=['POST'])
    @require_role('CSR Rep')  # Only CSR views are tracked
    def increment_view(request_id):
        """
        Increment view count for a request
        
        Called when CSR views request detail page
        
        Args:
            request_id: ID of the request being viewed
            
        Returns:
            {
                "success": true,
                "message": "View recorded successfully"
            }
        """
        try:
            # Verify request exists
            req = Request.get_request(request_id)
            if not req:
                return ResponseHelpers.error_response('Request not found', 404)
            
            # Only track views for ACTIVE requests
            if req.get('status') != 'ACTIVE':
                return ResponseHelpers.success_response(
                    message='View not tracked for non-active request'
                ), 200
            
            # Call ENTITY layer to increment view count
            success = Request.increment_view_count(request_id)
            
            if success:
                return ResponseHelpers.success_response(
                    message='View recorded successfully'
                ), 200
            else:
                return ResponseHelpers.error_response('Failed to record view'), 500
            
        except Exception as e:
            print(f"[ERROR] Increment view count failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return ResponseHelpers.error_response('Internal server error'), 500
