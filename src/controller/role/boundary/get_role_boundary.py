"""GetRole Boundary - HTTP layer for retrieving specific role"""

from flask import Blueprint, jsonify
from src.controller.role.get_role_controller import GetRoleController
from src.controller.auth.auth_middleware import require_role
from src.entity import Role

get_role_boundary = Blueprint('get_role', __name__)

@get_role_boundary.route('/api/roles/<int:role_id>', methods=['GET'])
@require_role(Role.USER_ADMIN)
def get_role(role_id):
    """Get specific role by ID"""
    controller = GetRoleController(role_id)
    response, status = controller.execute()
    return jsonify(response), status
