"""SuspendPINRequest Boundary - HTTP layer for suspending PIN requests"""

from flask import Blueprint, request, jsonify
from src.controller.request.suspend_pin_request_controller import SuspendPINRequestController
from src.controller.auth.auth_middleware import require_role

suspend_pin_request_boundary = Blueprint(
    'suspend_pin_request',
    __name__,
    url_prefix='/api/requests'
)

@suspend_pin_request_boundary.route('/<int:request_id>/suspend', methods=['PUT'])
@require_role('PIN')
def suspend_request(request_id):
    """Suspend a request (mark as no longer needed)"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = request.get_json() or {}
    
    controller = SuspendPINRequestController(auth_token, request_id, payload)
    response, status = controller.execute()
    return jsonify(response), status
