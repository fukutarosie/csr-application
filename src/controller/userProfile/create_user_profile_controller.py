"""Create User Profile Controller - Handles user profile (role) creation logic"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

create_user_profile_blueprint = Blueprint('create_user_profile', __name__, url_prefix='/api/userProfile')

class CreateUserProfileController:
    @staticmethod
    @create_user_profile_blueprint.route('', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create():
        """Create a new user profile (role)"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(k in data for k in ['role_name', 'role_code', 'description']):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: role_name, role_code, description'
                }), 400

            result = Role.create_role(
                role_name=data['role_name'],
                role_code=data['role_code'],
                description=data['description'],
                dashboard_route=data.get('dashboard_route', '/dashboard')
            )

            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': 'User profile created successfully'
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create user profile'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
