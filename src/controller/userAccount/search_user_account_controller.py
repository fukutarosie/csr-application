"""Search User Account Controller - Handles user search logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role

search_user_account_blueprint = Blueprint('search_user_account', __name__, url_prefix='/api/userAccount')

class SearchUserAccountController:
    @search_user_account_blueprint.route('/search', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def search():
        """Search user accounts by criteria"""
        try:
            data = request.get_json()
            
            users = User.search_users(
                username=data.get('username', ''),
                email=data.get('email', ''),
                full_name=data.get('full_name', '')
            )

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
