"""GetRequestAnalytics Boundary - HTTP layer for request analytics"""

from flask import Blueprint, request, jsonify
from src.controller.request.get_request_analytics_controller import GetRequestAnalyticsController
from src.controller.auth.auth_middleware import require_role

get_request_analytics_boundary = Blueprint(
    'get_request_analytics',
    __name__,
    url_prefix='/api/requests'
)

@get_request_analytics_boundary.route('/<int:request_id>/analytics', methods=['GET'])
@require_role('PIN')
def get_analytics(request_id):
    """Get analytics for a specific request (view count, shortlist count)"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    controller = GetRequestAnalyticsController(auth_token, request_id)
    response, status = controller.execute()
    return jsonify(response), status
