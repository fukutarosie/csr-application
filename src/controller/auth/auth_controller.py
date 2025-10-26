from flask import Blueprint, request, jsonify
from src.entity import User, Role

auth_blueprint = Blueprint('auth', __name__)

class AuthController:
    """
    BOUNDARY LAYER: HTTP Interface for Authentication
    
    This controller is responsible ONLY for:
    ✓ Extracting data from HTTP requests
    ✓ Validating HTTP format/structure
    ✓ Formatting HTTP responses
    ✓ Returning appropriate HTTP status codes
    
    ALL authentication logic is delegated to CONTROL layer (Entity)
    """
    
    @auth_blueprint.route('/api/auth/login', methods=['POST'])
    def login():
        """
        BOUNDARY: Login endpoint
        
        Delegates to CONTROL layer (User.authenticate_user) which handles:
        - Password verification
        - User account status check
        - Role verification
        - JWT token generation
        """
        try:
            # ===== BOUNDARY: Extract HTTP request data =====
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # ===== BOUNDARY: Validate required fields =====
            username = data.get('username')
            password = data.get('password')
            role_name = data.get('role_name')
            
            if not username or not password or not role_name:
                return jsonify({
                    'success': False,
                    'message': 'Username, password, and role_name are required'
                }), 400
            
            # ===== CALL CONTROL LAYER =====
            # User.authenticate_user() handles ALL authentication logic:
            # - User existence check
            # - Password verification
            # - User active status check
            # - Role verification
            # - JWT token generation
            result = User.authenticate_user(username, password, role_name)
            
            # ===== BOUNDARY: Handle CONTROL layer response =====
            if not result:
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials or user role mismatch'
                }), 401
            
            # ===== BOUNDARY: Format HTTP response =====
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': result['token'],
                    'user': {
                        'id': result['id'],
                        'username': result['username'],
                        'full_name': result['full_name'],
                        'email': result['email'],
                        'role': {
                            'name': result['role']['role_name'],
                            'code': result['role']['role_code'],
                            'dashboard_route': result['role']['dashboard_route']
                        }
                    }
                }
            }), 200
        
        except Exception as e:
            # ===== BOUNDARY: Catch and format exceptions =====
            print(f"[ERROR] Login endpoint error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during login'
            }), 500

    @auth_blueprint.route('/api/auth/logout', methods=['POST'])
    def logout():
        """
        BOUNDARY: Logout endpoint
        
        Delegates to CONTROL layer which handles:
        - Token validation
        - Token invalidation
        """
        try:
            # ===== BOUNDARY: Extract HTTP header =====
            auth_token = request.headers.get('Authorization')
            
            if not auth_token:
                return jsonify({
                    'success': False,
                    'message': 'No token provided'
                }), 401
            
            # ===== BOUNDARY: Parse token format =====
            if auth_token.startswith('Bearer '):
                auth_token = auth_token[7:]
            
            # ===== CALL CONTROL LAYER =====
            # User.invalidate_session_token() handles token invalidation logic
            success = User.invalidate_session_token(auth_token)
            
            # ===== BOUNDARY: Format HTTP response =====
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Logout successful'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Logout failed'
                }), 400
        
        except Exception as e:
            # ===== BOUNDARY: Catch and format exceptions =====
            print(f"[ERROR] Logout endpoint error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during logout'
            }), 500

    @auth_blueprint.route('/api/auth/verify', methods=['GET'])
    def verify_session():
        """
        BOUNDARY: Verify session endpoint
        
        Delegates to CONTROL layer which handles:
        - Token verification
        - User data retrieval
        """
        try:
            # ===== BOUNDARY: Extract HTTP header =====
            auth_token = request.headers.get('Authorization')
            
            if not auth_token:
                return jsonify({
                    'success': False,
                    'message': 'No token provided'
                }), 401
            
            # ===== BOUNDARY: Parse token format =====
            if auth_token.startswith('Bearer '):
                auth_token = auth_token[7:]
            
            # ===== CALL CONTROL LAYER =====
            # User.verify_session_token() handles token verification logic
            user = User.verify_session_token(auth_token)
            
            # ===== BOUNDARY: Handle CONTROL layer response =====
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token'
                }), 401
            
            # ===== CALL CONTROL LAYER for role info =====
            role = Role.get_role_by_id(user['role_id'])
            
            # ===== BOUNDARY: Format HTTP response =====
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
                        } if role else None
                    }
                }
            }), 200
        
        except Exception as e:
            # ===== BOUNDARY: Catch and format exceptions =====
            print(f"[ERROR] Verify endpoint error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during token verification'
            }), 500