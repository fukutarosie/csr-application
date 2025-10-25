"""Logout Controller - Handles all logout logic"""

from flask import Blueprint, request, jsonify
from src.entity import User

logout_blueprint = Blueprint('logout', __name__, url_prefix='/api/auth')

class LogoutController:
    @logout_blueprint.route('/logout', methods=['POST'])
    def logout():
        """Handle user logout and token invalidation"""
        try:
            auth_token = request.headers.get('Authorization')
            if not auth_token:
                return jsonify({
                    'success': False,
                    'message': 'No token provided'
                }), 401

            # Remove "Bearer " prefix if present
            if auth_token.startswith('Bearer '):
                auth_token = auth_token[7:]

            # Invalidate token
            success = User.invalidate_session_token(auth_token)
            
            return jsonify({
                'success': success,
                'message': 'Logout successful' if success else 'Logout failed'
            }), 200 if success else 500

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
