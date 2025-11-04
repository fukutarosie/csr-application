"""Login Controller - Consolidated Authentication Handler

This controller consolidates all authentication endpoints:
- POST /api/auth/login - User login with credentials
- POST /api/auth/logout - User logout and token invalidation
- GET /api/auth/verify - Verify session token validity

All 3 endpoints handle:
✓ HTTP request/response formatting (BOUNDARY layer)
✓ Input validation and sanitization
✓ Delegation to CONTROL layer (User entity)
✓ Appropriate HTTP status codes and error messages
"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers

login_blueprint = Blueprint('login', __name__, url_prefix='/api/auth')


def extract_and_sanitize_auth_data(data: dict) -> dict:
    """
    Extract and sanitize authentication data
    
    Args:
        data: Raw request data
        
    Returns:
        Sanitized data dictionary
    """
    return {
        'username': Sanitizers.sanitize_username(data.get('username', '')),
        'password': data.get('password', ''),  # Don't modify password
        'role_name': Sanitizers.sanitize_string(data.get('role_name', ''))
    }


class LoginController:
    """
    HTTP Interface for Authentication

    This controller is responsible for:
    ✓ Extracting data from HTTP requests
    ✓ Validating HTTP format/structure
    ✓ Formatting HTTP responses
    ✓ Returning appropriate HTTP status codes
    """

    @login_blueprint.route('/login', methods=['POST'])
    def login():
        """
        Login endpoint with comprehensive validation

        Validates:
        - HTTP format (JSON body presence)
        - Required fields presence
        - Data format (username, password strength, role)

        Delegates to CONTROL layer (User.authenticate_user)
        """
        try:
            # ===== Validate HTTP format =====
            is_valid, error_msg = RequestHelpers.validate_json_body()
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_JSON',
                    status_code=400
                )
                return jsonify(response), status

            # ===== Extract HTTP request data =====
            data = RequestHelpers.get_json_data()

            if not data:
                response, status = ResponseHelpers.error_response(
                    message='Request body is required',
                    error_code='EMPTY_BODY',
                    status_code=400
                )
                return jsonify(response), status

            # ===== Validate required fields =====
            is_valid, error_msg, missing = RequestHelpers.validate_required_fields(
                data, ['username', 'password', 'role_name']
            )
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='MISSING_FIELDS',
                    status_code=400,
                    details={'missing_fields': missing}
                )
                return jsonify(response), status

            # ===== Sanitize input data =====
            sanitized_data = extract_and_sanitize_auth_data(data)
            username = sanitized_data['username']
            password = sanitized_data['password']
            role_name = sanitized_data['role_name']

            # ===== Validate data format =====
            is_valid, error_msg = Validators.validate_username(username)
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_USERNAME',
                    status_code=400
                )
                return jsonify(response), status

            is_valid, error_msg = Validators.validate_password(password)
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_PASSWORD',
                    status_code=400
                )
                return jsonify(response), status

            # ===== CALL CONTROL LAYER =====
            # User.authenticate_user() handles ALL authentication logic:
            # - User existence check
            # - Password verification
            # - User active status check
            # - Role verification
            # - JWT token generation
            result = User.authenticate_user(username, password, role_name)

            # ===== Handle CONTROL layer response =====
            if not result:
                response, status = ResponseHelpers.error_response(
                    message='Invalid credentials or user role mismatch',
                    error_code='AUTH_FAILED',
                    status_code=401
                )
                return jsonify(response), status

            # ===== Format HTTP response =====
            response_data = {
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

            # Log successful login
            User.log_user_activity(result['id'], 'login', f'Logged in as {role_name}')

            response, status = ResponseHelpers.success_response(
                data=response_data,
                message='Login successful',
                status_code=200
            )
            return jsonify(response), status

        except Exception as e:
            print(f"[ERROR] Login endpoint error: {str(e)}")
            response, status = ResponseHelpers.error_response(
                message='An error occurred during login',
                error_code='SERVER_ERROR',
                status_code=500
            )
            return jsonify(response), status

    @login_blueprint.route('/logout', methods=['POST'])
    def logout():
        """
        Logout endpoint - Boundary layer only
        Handles token validation and invalidation response formatting
        """
        try:
            # Extract Authorization header
            auth_header = request.headers.get('Authorization')
            
            # Validate header format
            if not auth_header or 'Bearer ' not in auth_header:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or missing token'
                }), 401
            
            # Extract token
            token = auth_header.replace('Bearer ', '')
            
            # Call Entity directly to invalidate token
            success = User.invalidate_session_token(token)
            
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
            print(f"[ERROR] Logout error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during logout'
            }), 500

    @login_blueprint.route('/verify', methods=['GET'])
    def verify_session():
        """
        Token verification endpoint with improved error handling

        Validates token and returns user data with role information
        """
        try:
            # ===== Extract Authorization header =====
            auth_header = request.headers.get('Authorization')

            # ===== Validate header format =====
            is_valid, error_msg = TokenHelpers.validate_bearer_format(auth_header)
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_TOKEN_FORMAT',
                    status_code=401
                )
                return jsonify(response), status

            # ===== Extract token =====
            token = TokenHelpers.extract_bearer_token(auth_header)

            # ===== CALL CONTROL LAYER =====
            # User.verify_session_token() handles token verification logic
            user = User.verify_session_token(token)

            # ===== BOUNDARY: Handle CONTROL layer response =====
            if not user:
                response, status = ResponseHelpers.error_response(
                    message='Invalid or expired token',
                    error_code='INVALID_TOKEN',
                    status_code=401
                )
                return jsonify(response), status

            # ===== Get role info =====
            role = Role.get_role_by_id(user['role_id'])

            # ===== Format HTTP response =====
            response_data = {
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

            response, status = ResponseHelpers.success_response(
                data=response_data,
                message='Token is valid',
                status_code=200
            )
            return jsonify(response), status

        except Exception as e:
            # ===== Catch and format exceptions =====
            print(f"[ERROR] Verify endpoint error: {str(e)}")
            response, status = ResponseHelpers.error_response(
                message='An error occurred during token verification',
                error_code='SERVER_ERROR',
                status_code=500
            )
            return jsonify(response), status
