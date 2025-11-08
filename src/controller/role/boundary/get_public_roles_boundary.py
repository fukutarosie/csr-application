"""GetPublicRoles Boundary - HTTP layer for public role retrieval"""

from flask import Blueprint, jsonify
from src.controller.role.get_public_roles_controller import GetPublicRolesController

get_public_roles_boundary = Blueprint('get_public_roles', __name__)

@get_public_roles_boundary.route('/api/roles/public', methods=['GET'])
def get_public_roles():
    """Get all roles - Public endpoint"""
    response, status = GetPublicRolesController.get_public_roles()
    return jsonify(response), status
