"""GetAllRoles Boundary - HTTP layer for admin role retrieval"""

from flask import Blueprint, jsonify
from src.controller.role.get_all_roles_controller import GetAllRolesController
from src.controller.auth.auth_middleware import require_role
from src.entity import Role

get_all_roles_boundary = Blueprint('get_all_roles', __name__)

@get_all_roles_boundary.route('/api/roles', methods=['GET'])
@require_role(Role.USER_ADMIN)
def get_all_roles():
    """Get all roles - Admin only"""
    controller = GetAllRolesController()
    response, status = controller.execute()
    return jsonify(response), status
