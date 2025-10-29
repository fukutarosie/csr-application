from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role
from src.config.supabase import supabase
import os

user_blueprint = Blueprint('users', __name__, url_prefix='/api/users')

class UserController:
    @user_blueprint.route('', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def get_all_users():
        """Get all users (User Admin only)"""
        try:
            users = User.get_all_users()
            return jsonify({
                'success': True,
                'data': users
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @user_blueprint.route('', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create_user_root():
        """Create a new user (POST endpoint at root)"""
        data = request.get_json()

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

        if not result:
            return jsonify({
                'success': False,
                'message': 'Failed to create user'
            }), 500

        if 'error' in result:
            status = 409 if result['error'] in ['USERNAME_EXISTS', 'EMAIL_EXISTS'] else 400
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': result.get('message', 'Failed to create user')
            }), status

        return jsonify({
            'success': True,
            'data': result['data'],
            'message': 'User created successfully'
        }), 201

    @user_blueprint.route('/<int:user_id>', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def get_user(user_id):
        """Get specific user by ID"""
        try:
            user = User.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': user
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @user_blueprint.route('/<int:user_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update_user(user_id):
        """Update user details"""
        data = request.get_json()
        updates = {}

        if 'email' in data:
            updates['email'] = data['email']
        if 'full_name' in data:
            updates['full_name'] = data['full_name']
        if 'role_id' in data:
            updates['role_id'] = data['role_id']

        if not updates:
            return jsonify({
                'success': False,
                'message': 'No fields to update'
            }), 400

        result = User.update_user(user_id, updates)

        if result:
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update user'
            }), 400

    @user_blueprint.route('/<int:user_id>', methods=['DELETE'])
    @require_role(Role.USER_ADMIN)
    def delete_user(user_id):
        """Delete a user"""
        try:
            # Check if user exists
            user = User.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            # Delete from database
            supabase.table('users').delete().eq('id', user_id).execute()
            
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

        if success:
            return jsonify({
                'success': True,
                'message': 'User updated successfully'
            }), status_code
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update user'
            }), status_code

    @user_blueprint.route('/<int:user_id>/suspend', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def suspend_user(user_id):
        """Suspend a user account"""
        result = User.update_user(user_id, {'is_active': False})

        if result:
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to suspend user'
            }), 400

    @user_blueprint.route('/<int:user_id>/activate', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def activate_user(user_id):
        """Activate a suspended user account"""
        result = User.update_user(user_id, {'is_active': True})

        if result:
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to activate user'
            }), 400

    @user_blueprint.route('/search', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def search_users():
        """Search users by criteria"""
        data = request.get_json()
        
        try:
            users = User.search_users(
                username=data.get('username', ''),
                email=data.get('email', ''),
                full_name=data.get('full_name', '')
            )

            return jsonify({
                'success': True,
                'data': users
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500