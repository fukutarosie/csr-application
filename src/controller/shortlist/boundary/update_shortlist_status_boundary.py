"""UpdateShortlistStatus Boundary - HTTP layer for updating shortlist status"""

from flask import Blueprint, request, jsonify
from src.controller.shortlist.update_shortlist_status_controller import UpdateShortlistStatusController
from src.controller.auth.auth_middleware import require_role

update_shortlist_status_boundary = Blueprint(
    'update_shortlist_status',
    __name__,
    url_prefix='/api/shortlist'
)

@update_shortlist_status_boundary.route('/<int:shortlist_id>', methods=['PUT'])
@require_role('CSR Rep')
def update_status(shortlist_id):
    """Update shortlist entry status"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = request.get_json()
    
    response, status = UpdateShortlistStatusController.update_status(auth_token, shortlist_id, payload)
    return jsonify(response), status
