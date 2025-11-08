"""RemoveFromShortlist Boundary - HTTP layer for removing from shortlist"""

from flask import Blueprint, request, jsonify
from src.controller.shortlist.remove_from_shortlist_controller import RemoveFromShortlistController
from src.controller.auth.auth_middleware import require_role

remove_from_shortlist_boundary = Blueprint(
    'remove_from_shortlist',
    __name__,
    url_prefix='/api/shortlist'
)

@remove_from_shortlist_boundary.route('/<int:shortlist_id>', methods=['DELETE'])
@require_role('CSR Rep')
def remove_shortlist(shortlist_id):
    """Remove a request from CSR's shortlist"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Use OOP instance method
    controller = RemoveFromShortlistController(auth_token, shortlist_id)
    response, status = controller.execute()
    return jsonify(response), status
