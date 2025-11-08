"""GetPINRequests Boundary - HTTP layer for getting PIN user's own requests"""

from flask import Blueprint, request, jsonify
from src.controller.request.get_pin_requests_controller import GetPINRequestsController
from src.controller.auth.auth_middleware import require_role

get_pin_requests_boundary = Blueprint(
    'get_pin_requests',
    __name__,
    url_prefix='/api/requests'
)

@get_pin_requests_boundary.route('', methods=['GET'])
@require_role('PIN')
def get_requests():
    """Get all requests for authenticated PIN user with filtering and pagination"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Parse query parameters
    status_param = request.args.get('status', '').strip() or None
    service_type = request.args.get('service_type', '').strip() or None
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    
    controller = GetPINRequestsController(auth_token, status_param, service_type, page, limit)
    response, status = controller.execute()
    return jsonify(response), status
