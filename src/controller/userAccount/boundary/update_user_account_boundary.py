"""Update User Account Boundary - Handles HTTP interface for user update"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userAccount.update_user_account_controller import UpdateUserAccountController

update_user_account_boundary = Blueprint('update_user_account', __name__, url_prefix='/api/userAccount')


@update_user_account_boundary.route('/<int:user_id>', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def update(user_id):
    """Update user account details"""
    try:
        payload = request.get_json()
        # TRUE OOP: Create controller object, call instance method
        controller = UpdateUserAccountController(user_id, payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
