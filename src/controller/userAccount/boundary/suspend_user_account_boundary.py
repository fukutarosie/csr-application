"""Suspend User Account Boundary - Handles HTTP interface for user suspend/activate/delete"""

from flask import Blueprint, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role
from src.controller.userAccount.suspend_user_account_controller import (
    SuspendUserAccountController,
    ActivateUserAccountController,
    DeleteUserAccountController
)

suspend_user_account_boundary = Blueprint('suspend_user_account', __name__, url_prefix='/api/userAccount')


@suspend_user_account_boundary.route('/<int:user_id>/suspend', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def suspend(user_id):
    """Suspend (deactivate) a user account"""
    try:
        # TRUE OOP: Create controller object, call instance method
        controller = SuspendUserAccountController(user_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


@suspend_user_account_boundary.route('/<int:user_id>/activate', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def activate(user_id):
    """Activate a suspended user account"""
    try:
        # TRUE OOP: Create controller object, call instance method
        controller = ActivateUserAccountController(user_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


@suspend_user_account_boundary.route('/<int:user_id>/delete', methods=['DELETE'])
@require_role(Role.USER_ADMIN)
def delete(user_id):
    """Delete a user account"""
    try:
        # TRUE OOP: Create controller object, call instance method
        controller = DeleteUserAccountController(user_id)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
