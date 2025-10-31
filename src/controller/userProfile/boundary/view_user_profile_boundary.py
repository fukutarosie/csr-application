"""View User Profile Boundary - Handles HTTP interface for retrieving roles"""

from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.view_user_profile_controller import ViewUserProfileController

view_user_profile_boundary = Blueprint('view_user_profile', __name__, url_prefix='/api/userProfile')


@view_user_profile_boundary.route('', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_all_user_profiles():
    try:
        response, status = ViewUserProfileController.get_all_user_profiles()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500


@view_user_profile_boundary.route('/<int:profile_id>', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_user_profile_by_id(profile_id):
    try:
        response, status = ViewUserProfileController.get_user_profile_by_id(profile_id)
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500
