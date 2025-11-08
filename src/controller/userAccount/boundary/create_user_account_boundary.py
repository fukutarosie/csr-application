"""Create User Account Boundary - Handles HTTP interface for user creation"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userAccount.create_user_account_controller import CreateUserAccountController

create_user_account_boundary = Blueprint('create_user_account', __name__, url_prefix='/api/userAccount')


@create_user_account_boundary.route('', methods=['POST'])
@require_role(Role.USER_ADMIN)
def create():
    """Create a new user account"""
    try:
        payload = request.get_json()
        # TRUE OOP: Create controller object, call instance method
        controller = CreateUserAccountController(payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
