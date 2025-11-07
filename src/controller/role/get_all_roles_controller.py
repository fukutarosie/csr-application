from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

get_all_roles_blueprint = Blueprint('get_all_roles', __name__)

class GetAllRolesController:
    """Controller for fetching all roles (admin only)"""
    
    @get_all_roles_blueprint.route('/api/roles', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def get_all_roles():
        """Get all roles - Protected endpoint for admins"""
        try:
            roles = Role.get_all_roles()
            return jsonify({
                'success': True,
                'data': roles
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
