"""UpdateRole Boundary - HTTP layer for role updates"""

from flask import Blueprint, request, jsonify
from src.controller.role.update_role_controller import UpdateRoleController
from src.controller.auth.auth_middleware import require_role
from src.entity import Role

update_role_boundary = Blueprint('update_role', __name__)

@update_role_boundary.route('/api/roles/<int:role_id>', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def update_role(role_id):
    """Update an existing role"""
    payload = request.get_json()
    controller = UpdateRoleController(role_id, payload)
    response, status = controller.execute()
    return jsonify(response), status
