"""Update User Profile Controller - Handles user profile (role) update logic"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

update_user_profile_blueprint = Blueprint('update_user_profile', __name__, url_prefix='/api/userProfile')

class UpdateUserProfileController:
    @update_user_profile_blueprint.route('/<int:profile_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update(profile_id):
        """Update user profile (role) details"""
        try:
            data = request.get_json()
            
            result = Role.update_role(
                role_id=profile_id,
                role_name=data.get('role_name'),
                role_code=data.get('role_code'),
                description=data.get('description'),
                dashboard_route=data.get('dashboard_route')
            )

            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': 'User profile updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update user profile'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
