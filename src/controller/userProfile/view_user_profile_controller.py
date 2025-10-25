"""View User Profile Controller - Handles user profile (role) retrieval logic"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

view_user_profile_blueprint = Blueprint('view_user_profile', __name__, url_prefix='/api/userProfile')

class ViewUserProfileController:
    @view_user_profile_blueprint.route('', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def view_all():
        """Get all user profiles (roles)"""
        try:
            profiles = Role.get_all_roles()
            return jsonify({
                'success': True,
                'data': profiles,
                'count': len(profiles) if profiles else 0
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @view_user_profile_blueprint.route('/<int:profile_id>', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def view_by_id(profile_id):
        """Get specific user profile (role) by ID"""
        try:
            profile = Role.get_role_by_id(profile_id)
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'User profile not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': profile
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
