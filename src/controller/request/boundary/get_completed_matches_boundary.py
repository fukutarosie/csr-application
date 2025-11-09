"""GetCompletedMatches Boundary - HTTP layer for viewing completed matches"""

from flask import Blueprint, request, jsonify
from src.controller.request.get_completed_matches_controller import GetCompletedMatchesController
from src.controller.auth.auth_middleware import require_role

get_completed_matches_boundary = Blueprint(
    'get_completed_matches',
    __name__,
    url_prefix='/api/requests'
)

@get_completed_matches_boundary.route('/history', methods=['GET'])
@require_role('PIN')
def get_history():
    """Get completed matches (fulfilled requests) for authenticated PIN user"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Parse query parameters
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    service_type = request.args.get('service_type', '').strip() or None
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    
    controller = GetCompletedMatchesController(auth_token, start_date, end_date, page, limit, service_type)
    response, status = controller.execute()
    return jsonify(response), status
