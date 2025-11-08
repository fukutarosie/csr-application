"""CreateRole Boundary - HTTP layer for role creation"""

from flask import Blueprint, request, jsonify
from src.controller.role.create_role_controller import CreateRoleController
from src.controller.auth.auth_middleware import require_role
from src.entity import Role

create_role_boundary = Blueprint('create_role', __name__)

@create_role_boundary.route('/api/roles', methods=['POST'])
@require_role(Role.USER_ADMIN)
def create_role():
    """Create a new role"""
    payload = request.get_json()
    controller = CreateRoleController(payload)
    response, status = controller.execute()
    return jsonify(response), status
