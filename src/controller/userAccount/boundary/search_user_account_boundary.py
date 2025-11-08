"""Search User Account Boundary - Handles HTTP interface for user search"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userAccount.search_user_account_controller import SearchUserAccountController

search_user_account_boundary = Blueprint('search_user_account', __name__, url_prefix='/api/userAccount')


@search_user_account_boundary.route('/search', methods=['POST'])
@require_role(Role.USER_ADMIN)
def search():
    """Search users"""
    try:
        payload = request.get_json()
        # TRUE OOP: Create controller object, call instance method
        controller = SearchUserAccountController(payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
