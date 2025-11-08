"""CreateNewPINRequest Boundary - HTTP layer for PIN request creation"""

from flask import Blueprint, request, jsonify
from src.controller.request.create_new_pin_request_controller import CreateNewPINRequestController
from src.controller.auth.auth_middleware import require_role

create_pin_new_request_boundary = Blueprint(
    'create_pin_new_request',
    __name__,
    url_prefix='/api/requests'
)

@create_pin_new_request_boundary.route('', methods=['POST'])
@require_role('PIN')
def create_new_request():
    """Create a new PIN request"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = request.get_json()
    
    # TRUE OOP: Create controller object, call instance method
    controller = CreateNewPINRequestController(auth_token, payload)
    response, status = controller.execute()
    return jsonify(response), status
