from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

create_role_blueprint = Blueprint('create_role', __name__)

class CreateRoleController:
    """Controller for creating a new role"""
    
    @create_role_blueprint.route('/api/roles', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create_role():
        """Create a new role"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('role_name') or not data.get('role_code') or not data.get('description'):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: role_name, role_code, description'
                }), 400
            
            new_role = Role.create_role(
                role_name=data['role_name'],
                role_code=data['role_code'],
                description=data['description'],
                dashboard_route=data.get('dashboard_route', '/')
            )
            
            if not new_role:
                return jsonify({
                    'success': False,
                    'message': 'Role already exists or failed to create'
                }), 400
            
            return jsonify({
                'success': True,
                'data': new_role,
                'message': 'Role created successfully'
            }), 201
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
