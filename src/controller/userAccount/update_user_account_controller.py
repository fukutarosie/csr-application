"""Update User Account Controller - Handles user update logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role

update_user_account_blueprint = Blueprint('update_user_account', __name__, url_prefix='/api/userAccount')

class UpdateUserAccountController:
    @update_user_account_blueprint.route('/<int:user_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update(user_id):
        """Update user account details"""
        try:
            data = request.get_json()
            updates = {}

            # Collect valid fields to update
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
                    'data': result,
                    'message': 'User account updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update user account'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
