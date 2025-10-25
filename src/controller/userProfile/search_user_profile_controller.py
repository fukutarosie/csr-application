"""Search User Profile Controller - Handles user profile (role) search logic"""

from flask import Blueprint, request, jsonify
from src.entity import Role
from src.controller.auth.auth_middleware import require_role

search_user_profile_blueprint = Blueprint('search_user_profile', __name__, url_prefix='/api/userProfile')

class SearchUserProfileController:
    @search_user_profile_blueprint.route('/search', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def search():
        """Search user profiles (roles) by name"""
        try:
            data = request.get_json()
            search_term = data.get('search', '')
            
            # Get all roles and filter by name
            all_roles = Role.get_all_roles()
            filtered_roles = [
                role for role in all_roles 
                if search_term.lower() in role['role_name'].lower() or 
                   search_term.lower() in role['role_code'].lower()
            ] if all_roles else []

            return jsonify({
                'success': True,
                'data': filtered_roles,
                'count': len(filtered_roles)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
