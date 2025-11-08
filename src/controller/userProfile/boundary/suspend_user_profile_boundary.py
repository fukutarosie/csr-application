"""Suspend User Profile Boundary - Handles HTTP interface for deleting roles"""

from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.suspend_user_profile_controller import SuspendUserProfileController

suspend_user_profile_boundary = Blueprint('suspend_user_profile', __name__, url_prefix='/api/userProfile')


@suspend_user_profile_boundary.route('/<int:profile_id>/delete', methods=['DELETE'])
@require_role(Role.USER_ADMIN)
def delete_user_profile(profile_id):
    try:
        controller = SuspendUserProfileController(profile_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500
