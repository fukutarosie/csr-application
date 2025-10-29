"""Suspend User Profile Controller - Handles user profile (role) delete logic"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

suspend_user_profile_blueprint = Blueprint('suspend_user_profile', __name__, url_prefix='/api/userProfile')

class SuspendUserProfileController:
    @staticmethod
    @suspend_user_profile_blueprint.route('/<int:profile_id>/delete', methods=['DELETE'])
    @require_role(Role.USER_ADMIN)
    def delete(profile_id):
        """Delete a user profile (role) - CASCADE DELETE will remove all associated users"""
        try:
            # Check if profile exists
            profile = Role.get_role_by_id(profile_id)
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'User profile not found'
                }), 404
            
            # Delete from database
            success = Role.delete_role(profile_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'User profile deleted successfully (cascading delete applied)'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to delete user profile'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
