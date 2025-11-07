from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

get_role_blueprint = Blueprint('get_role', __name__)

class GetRoleController:
    """Controller for fetching a specific role by ID"""
    
    @get_role_blueprint.route('/api/roles/<int:role_id>', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def get_role(role_id):
        """Get specific role by ID"""
        try:
            role = Role.get_role_by_id(role_id)
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'Role not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': role
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
