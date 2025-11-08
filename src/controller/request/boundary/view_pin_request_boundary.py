"""ViewPINRequest Boundary - HTTP layer for viewing PIN requests"""

from flask import Blueprint, request, jsonify
from src.controller.request.view_pin_request_controller import ViewPINRequestsController, ViewPINRequestDetailController

view_pin_request_boundary = Blueprint(
    'view_pin_request',
    __name__,
    url_prefix='/api/requests'
)

@view_pin_request_boundary.route('', methods=['GET'])
def get_requests():
    """Get requests - PIN users see their own, CSR Reps see all ACTIVE requests"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    status_param = request.args.get('status', '').strip() or None
    
    controller = ViewPINRequestsController(auth_token, status_param)
    response, status = controller.execute()
    return jsonify(response), status

@view_pin_request_boundary.route('/<int:request_id>', methods=['GET'])
def get_request_detail(request_id):
    """Get single request detail"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    controller = ViewPINRequestDetailController(auth_token, request_id)
    response, status = controller.execute()
    return jsonify(response), status
