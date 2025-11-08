"""View User Profile Boundary - Handles HTTP interface for retrieving roles"""

from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.view_user_profile_controller import ViewAllUserProfilesController, ViewOneUserProfileController

view_user_profile_boundary = Blueprint('view_user_profile', __name__, url_prefix='/api/userProfile')

# View all user profiles by METHOD: GET
@view_user_profile_boundary.route('', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_all_user_profiles():
    try:
        controller = ViewAllUserProfilesController()
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500

# View user profile by ID by METHOD: GET
@view_user_profile_boundary.route('/<int:profile_id>', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_user_profile_by_id(profile_id):
    try:
        controller = ViewOneUserProfileController(profile_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500
