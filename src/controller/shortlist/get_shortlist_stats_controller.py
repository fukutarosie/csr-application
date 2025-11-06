"""
Get Shortlist Statistics Controller - CSR views volunteering statistics
Handles CSR stats and analytics

BOUNDARY Layer (BCE Architecture)
"""

from flask import Blueprint, request, jsonify
from src.entity.shortlist import Shortlist
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.helpers import TokenHelpers, ResponseHelpers

get_shortlist_stats_blueprint = Blueprint(
    'get_shortlist_stats',
    __name__,
    url_prefix='/api/shortlist'
)


class GetShortlistStatsController:
    """
    Get CSR's volunteering statistics
    """
    
    @staticmethod
    @get_shortlist_stats_blueprint.route('/stats', methods=['GET'])
    @require_role('CSR Rep')
    def get_stats():
        """
        Get CSR's statistics
        
        Returns:
            {
                "success": true,
                "data": {
                    "total_shortlisted": 10,
                    "in_progress": 2,
                    "completed": 5,
                    "declined": 1,
                    "total_hours_volunteered": 12.5
                },
                "message": "Statistics retrieved successfully"
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
            
            # Call ENTITY layer
            stats = Shortlist.get_statistics(csr_user_id=csr_user_id)
            
            if stats is None:
                return ResponseHelpers.error_response('Failed to retrieve statistics', 400)
            
            # Return response
            return ResponseHelpers.success_response(
                data=stats,
                message='Statistics retrieved successfully'
            ), 200
            
        except Exception as e:
            print(f"[ERROR] Get statistics failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error'), 500
