from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

role_blueprint = Blueprint('roles', __name__, url_prefix='/api/roles')

class RoleController:
    @role_blueprint.route('/public', methods=['GET'])
    def get_roles_public():
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

    @role_blueprint.route('', methods=['GET'])
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

    @role_blueprint.route('/<int:role_id>', methods=['GET'])
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

    @role_blueprint.route('', methods=['POST'])
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

    @role_blueprint.route('/<int:role_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update_role(role_id):
        """Update an existing role"""
        try:
            data = request.get_json()
            
            role = Role.get_role_by_id(role_id)
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'Role not found'
                }), 404
            
            updated_role = Role.update_role(
                role_id=role_id,
                role_name=data.get('role_name', role['role_name']),
                role_code=data.get('role_code', role['role_code']),
                description=data.get('description', role['description']),
                dashboard_route=data.get('dashboard_route', role.get('dashboard_route', '/'))
            )
            
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

    @role_blueprint.route('/<int:role_id>', methods=['DELETE'])
    @require_role(Role.USER_ADMIN)
    def delete_role(role_id):
        """Delete a role and cascade delete associated users"""
        try:
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