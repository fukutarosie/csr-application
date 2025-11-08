"""View User Account Boundary - Handles HTTP interface for viewing users"""

from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userAccount.view_user_account_controller import ViewAllUserAccountsController, ViewOneUserAccountController

view_user_account_boundary = Blueprint('view_user_account', __name__, url_prefix='/api/userAccount')


@view_user_account_boundary.route('', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_all():
    """Get all users"""
    try:
        # TRUE OOP: Create controller object, call instance method
        controller = ViewAllUserAccountsController()
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


@view_user_account_boundary.route('/<int:user_id>', methods=['GET'])
@require_role(Role.USER_ADMIN)
def view_one(user_id):
    """Get one user by ID"""
    try:
        # TRUE OOP: Create controller object, call instance method
        controller = ViewOneUserAccountController(user_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
