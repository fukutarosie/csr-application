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

            if auth_token.startswith('Bearer '):
                auth_token = auth_token[7:]

            user = User.verify_token(auth_token)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token'
                }), 401

            role = Role.find(user.role_id)
            if not role:
                print(f"[AUTH] Role not found for role_id: {user.role_id}")
                return jsonify({
                    'success': False,
                    'message': 'User role not found'
                }), 403

            print(f"[AUTH] User role: {role.role_name}, Allowed roles: {allowed_roles}")
            
            if role.role_name not in allowed_roles:
                print(f"[AUTH] Access denied - '{role.role_name}' not in {allowed_roles}")
                return jsonify({
                    'success': False,
                    'message': f'You do not have permission to view requests'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_from_token():
    auth_token = request.headers.get('Authorization')
    if not auth_token:
        return None

    if auth_token.startswith('Bearer '):
        auth_token = auth_token[7:]

    if not auth_token:
        return None

    user = User.verify_token(auth_token)
    if not user:
        return None

    return user