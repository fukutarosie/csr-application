"""SearchPINRequest Boundary - HTTP layer for searching PIN requests"""

from flask import Blueprint, request, jsonify
from src.controller.request.search_pin_request_controller import SearchPINRequestController
from src.controller.auth.auth_middleware import require_role

search_pin_request_boundary = Blueprint(
    'search_pin_request',
    __name__,
    url_prefix='/api/requests'
)

@search_pin_request_boundary.route('/search', methods=['GET'])
@require_role('PIN')
def search_requests():
    """Search and filter requests"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Parse query parameters
    keyword = request.args.get('keyword', '').strip() or None
    category = request.args.get('category', '').strip() or None
    status = request.args.get('status', '').strip() or None
    priority = request.args.get('priority', '').strip() or None
    service_type = request.args.get('service_type', '').strip() or None
    my_requests = request.args.get('my_requests', 'true').lower() == 'true'
    
    controller = SearchPINRequestController(auth_token, keyword, category, status, priority, service_type, my_requests)
    response, status_code = controller.execute()
    return jsonify(response), status_code
