"""Create User Account Controller - Handles user creation logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role

create_user_account_blueprint = Blueprint('create_user_account', __name__, url_prefix='/api/userAccount')

class CreateUserAccountController:
    @create_user_account_blueprint.route('', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create():
        """Create a new user account"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(k in data for k in ['username', 'password', 'email', 'full_name', 'role_id']):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: username, password, email, full_name, role_id'
                }), 400

            result = User.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                full_name=data['full_name'],
                role_id=data['role_id']
            )

            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': 'User account created successfully'
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create user account'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
