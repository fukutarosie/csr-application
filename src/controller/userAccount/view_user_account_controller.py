"""View User Account Controller - Handles user retrieval logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role

view_user_account_blueprint = Blueprint('view_user_account', __name__, url_prefix='/api/userAccount')

class ViewUserAccountController:
    @staticmethod
    @view_user_account_blueprint.route('', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def view_all():
        """Get all user accounts"""
        try:
            users = User.get_all_users()
            return jsonify({
                'success': True,
                'data': users,
                'count': len(users) if users else 0
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @staticmethod
    @view_user_account_blueprint.route('/<int:user_id>', methods=['GET'])
    @require_role(Role.USER_ADMIN)
    def view_by_id(user_id):
        """Get specific user account by ID"""
        try:
            user = User.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User account not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': user
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
