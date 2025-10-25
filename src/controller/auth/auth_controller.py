from flask import Blueprint, request, jsonify
from src.entity import User, Role

auth_blueprint = Blueprint('auth', __name__)

class AuthController:
    @auth_blueprint.route('/api/auth/login', methods=['POST'])
    def login():
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
            # Log for debugging
            print(f"[DEBUG] Login failed for username: {username}")
            print(f"[DEBUG] Success: {success}, User: {user}")
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

    @auth_blueprint.route('/api/auth/logout', methods=['POST'])
    def logout():
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

    @auth_blueprint.route('/api/auth/verify', methods=['GET'])
    def verify_session():
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({
                'success': False,
                'message': 'No token provided'
            }), 401

        # Remove "Bearer " prefix if present
        if auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]

        # Verify token and get user
        user = User.verify_session_token(auth_token)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401

        # Get user's role
        role = Role.get_role_by_id(user['role_id'])
        
        return jsonify({
            'success': True,
            'data': {
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