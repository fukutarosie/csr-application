"""Create User Profile Boundary - Handles HTTP interface for role creation"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.create_user_profile_controller import CreateUserProfileController

create_user_profile_boundary = Blueprint('create_user_profile', __name__, url_prefix='/api/userProfile')


@create_user_profile_boundary.route('', methods=['POST'])
@require_role(Role.USER_ADMIN)
def create_user_profile():
    try:
        payload = request.get_json()
        controller = CreateUserProfileController(payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
