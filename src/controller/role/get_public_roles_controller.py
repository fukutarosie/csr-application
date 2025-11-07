from flask import Blueprint, jsonify
from src.entity import Role

get_public_roles_blueprint = Blueprint('get_public_roles', __name__)

class GetPublicRolesController:
    """Controller for fetching roles without authentication (for login page)"""
    
    @get_public_roles_blueprint.route('/api/roles/public', methods=['GET'])
    def get_public_roles():
        """Get all roles - Public endpoint for login page (no authentication required)"""
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
