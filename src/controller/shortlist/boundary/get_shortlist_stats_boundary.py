"""GetShortlistStats Boundary - HTTP layer for shortlist statistics"""

from flask import Blueprint, request, jsonify
from src.controller.shortlist.get_shortlist_stats_controller import GetShortlistStatsController
from src.controller.auth.auth_middleware import require_role

get_shortlist_stats_boundary = Blueprint(
    'get_shortlist_stats',
    __name__,
    url_prefix='/api/shortlist'
)

@get_shortlist_stats_boundary.route('/stats', methods=['GET'])
@require_role('CSR Rep')
def get_stats():
    """Get statistics about CSR's shortlist"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    controller = GetShortlistStatsController(auth_token)
    response, status = controller.execute()
    return jsonify(response), status
