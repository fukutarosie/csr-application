"""Login Controller - Handles all login logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role

login_blueprint = Blueprint('login', __name__, url_prefix='/api/auth')

class LoginController:
    @login_blueprint.route('/login', methods=['POST'])
    def login():
        """Handle user login with credentials and role validation"""
        try:
            data = request.get_json()
            
            # Validate input
            if not data or not all(k in data for k in ['username', 'password', 'role_name']):
                return jsonify({
                    'success': False,
                    'message': 'Username, password, and role are required'
                }), 400

            username = data['username']
            password = data['password']
            role_name = data['role_name']

            # First verify if the role is valid
            role = Role.get_role_by_name(role_name)
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'Invalid role selected'
                }), 400

            # Check credentials and role
            success, user = User.check_login(username, password)
            if not success or not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials'
                }), 401

            # Verify user has the selected role
            if user['role_id'] != role['id']:
                return jsonify({
                    'success': False,
                    'message': 'User does not have the selected role'
                }), 403

            # Create session token
            token = User.create_session_token(user['id'])

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'email': user['email'],
                        'role': {
                            'name': role['role_name'],
                            'code': role['role_code'],
                            'dashboard_route': role['dashboard_route']
                        }
                    }
                }
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
