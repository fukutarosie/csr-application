"""UpdatePINRequest Boundary - HTTP layer for updating PIN requests"""

from flask import Blueprint, request, jsonify
from src.controller.request.update_pin_request_controller import UpdatePINRequestController
from src.controller.auth.auth_middleware import require_role

update_pin_request_boundary = Blueprint(
    'update_pin_request',
    __name__,
    url_prefix='/api/requests'
)

@update_pin_request_boundary.route('/<int:request_id>', methods=['PUT'])
@require_role('PIN')
def update_request(request_id):
    """Update a request"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = request.get_json()
    
    controller = UpdatePINRequestController(auth_token, request_id, payload)
    response, status = controller.execute()
    return jsonify(response), status
