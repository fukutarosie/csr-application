"""Search User Profile Boundary - Handles HTTP interface for searching roles"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userProfile.search_user_profile_controller import SearchUserProfileController

search_user_profile_boundary = Blueprint('search_user_profile', __name__, url_prefix='/api/userProfile')


@search_user_profile_boundary.route('/search', methods=['POST'])
@require_role(Role.USER_ADMIN)
def search_user_profile():
    try:
        payload = request.get_json()
        controller = SearchUserProfileController(payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            'success': False,
            'message': str(exc)
        }), 500
