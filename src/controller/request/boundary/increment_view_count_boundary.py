"""IncrementViewCount Boundary - HTTP layer for tracking CSR views"""

from flask import Blueprint, request, jsonify
from src.controller.request.increment_view_count_controller import IncrementViewCountController
from src.controller.auth.auth_middleware import require_role

increment_view_count_boundary = Blueprint(
    'increment_view_count',
    __name__,
    url_prefix='/api/requests'
)

@increment_view_count_boundary.route('/<int:request_id>/view', methods=['POST'])
@require_role('CSR Rep')
def increment_view(request_id):
    """Increment view count for a request"""
    controller = IncrementViewCountController(request_id)
    response, status = controller.execute()
    return jsonify(response), status
