from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

update_role_blueprint = Blueprint('update_role', __name__)

class UpdateRoleController:
    """Controller for updating an existing role"""
    
    @update_role_blueprint.route('/api/roles/<int:role_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update_role(role_id):
        """Update an existing role"""
        try:
            data = request.get_json()
            
            # Check if role exists
            role = Role.get_role_by_id(role_id)
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'Role not found'
                }), 404
            
            # Update role with new data or keep existing values
            updated_role = Role.update_role(
                role_id=role_id,
                role_name=data.get('role_name', role['role_name']),
                role_code=data.get('role_code', role['role_code']),
                description=data.get('description', role['description']),
                dashboard_route=data.get('dashboard_route', role.get('dashboard_route', '/'))
            )
            
            if not updated_role:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update role'
                }), 500
            
            return jsonify({
                'success': True,
                'data': updated_role,
                'message': 'Role updated successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
