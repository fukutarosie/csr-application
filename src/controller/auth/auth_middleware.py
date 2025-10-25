from functools import wraps
from flask import request, jsonify
from src.entity import User, Role

def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
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
            if not role:
                return jsonify({
                    'success': False,
                    'message': 'User role not found'
                }), 403

            # Check if user's role is in allowed roles
            if role['role_name'] not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator