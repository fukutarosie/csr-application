"""AddToShortlist Boundary - HTTP layer for CSR shortlist operations"""

from flask import Blueprint, request, jsonify
from src.controller.shortlist.add_to_shortlist_controller import AddToShortlistController
from src.controller.auth.auth_middleware import require_role

add_to_shortlist_boundary = Blueprint(
    'add_to_shortlist',
    __name__,
    url_prefix='/api/shortlist'
)

@add_to_shortlist_boundary.route('', methods=['POST'])
@require_role('CSR Rep')
def add_shortlist():
    """Add a request to CSR's shortlist"""
    auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = request.get_json()
    
    # TRUE OOP: Create controller object, call instance method
    controller = AddToShortlistController(auth_token, payload)
    response, status = controller.execute()
    return jsonify(response), status
