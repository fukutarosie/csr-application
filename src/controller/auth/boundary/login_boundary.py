"""Login Boundary - Handles HTTP interface for authentication (login, logout, verify)"""

from flask import Blueprint, request, jsonify
from src.controller.auth.login_controller import LoginController

login_boundary = Blueprint('login', __name__, url_prefix='/api/auth')


@login_boundary.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        payload = request.get_json()
        response, status = LoginController.login(payload)
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


@login_boundary.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        response, status = LoginController.logout(token)
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


@login_boundary.route('/verify', methods=['GET'])
def verify():
    """Verify session token endpoint"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        response, status = LoginController.verify(token)
        return jsonify(response), status
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500
