"""DeleteRole Boundary - HTTP layer for role deletion"""

from flask import Blueprint, jsonify
from src.controller.role.delete_role_controller import DeleteRoleController
from src.controller.auth.auth_middleware import require_role
from src.entity import Role

delete_role_boundary = Blueprint('delete_role', __name__)

@delete_role_boundary.route('/api/roles/<int:role_id>', methods=['DELETE'])
@require_role(Role.USER_ADMIN)
def delete_role(role_id):
    """Delete a role and cascade delete associated users"""
    controller = DeleteRoleController(role_id)
    response, status = controller.execute()
    return jsonify(response), status
