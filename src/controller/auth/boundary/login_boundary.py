"""Login Boundary - Handles HTTP interface for authentication (login, logout, verify)"""

from flask import Blueprint, request, jsonify
from src.controller.auth.login_controller import LoginController, LogoutController, VerifyTokenController

login_boundary = Blueprint('login', __name__, url_prefix='/api/auth')

# User login by METHOD: POST
@login_boundary.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        payload = request.get_json()
        # TRUE OOP: Create controller object, call instance method
        controller = LoginController(payload)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


# User logout by METHOD: POST
@login_boundary.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        # TRUE OOP: Create controller object, call instance method
        controller = LogoutController(token)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500

# Verify session token by METHOD: GET
@login_boundary.route('/verify', methods=['GET'])
def verify():
    """Verify session token endpoint"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        # TRUE OOP: Create controller object, call instance method
        controller = VerifyTokenController(token)
        response, status = controller.execute()
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
