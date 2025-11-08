"""Update User Profile Boundary - Handles HTTP interface for updating roles"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.update_user_profile_controller import UpdateUserProfileController

update_user_profile_boundary = Blueprint('update_user_profile', __name__, url_prefix='/api/userProfile')


@update_user_profile_boundary.route('/<int:profile_id>', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def update_user_profile(profile_id):
    try:
        payload = request.get_json()
        controller = UpdateUserProfileController(profile_id, payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500
