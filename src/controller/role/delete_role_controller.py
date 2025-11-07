from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

delete_role_blueprint = Blueprint('delete_role', __name__)

class DeleteRoleController:
    """Controller for deleting a role (CASCADE delete associated users)"""
    
    @delete_role_blueprint.route('/api/roles/<int:role_id>', methods=['DELETE'])
    @require_role(Role.USER_ADMIN)
    def delete_role(role_id):
        """Delete a role and cascade delete associated users"""
        try:
            # Check if role exists
            role = Role.get_role_by_id(role_id)
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'Role not found'
                }), 404
            
            # Delete the role (cascading delete handled by database constraints)
            success = Role.delete_role(role_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Role deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to delete role'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
