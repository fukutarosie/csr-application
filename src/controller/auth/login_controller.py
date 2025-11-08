"""Login Controller - Business logic for authentication (login, logout, verify)"""

from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers


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
    """Business logic for authentication"""

    @staticmethod
    def login(data):
        """
        Login business logic
        
        Args:
            data: Login data from HTTP request
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate data presence
            if not data:
                return ResponseHelpers.error_response(
                    message='Request body is required',
                    error_code='EMPTY_BODY',
                    status_code=400
                )

            # Validate required fields
            is_valid, error_msg, missing = RequestHelpers.validate_required_fields(
                data, ['username', 'password', 'role_name']
            )
            if not is_valid:
                return ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='MISSING_FIELDS',
                    status_code=400,
                    details={'missing_fields': missing}
                )

            # Sanitize input data
            sanitized_data = extract_and_sanitize_auth_data(data)
            username = sanitized_data['username']
            password = sanitized_data['password']
            role_name = sanitized_data['role_name']

            # Validate data format
            is_valid, error_msg = Validators.validate_username(username)
            if not is_valid:
                return ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_USERNAME',
                    status_code=400
                )

            is_valid, error_msg = Validators.validate_password(password)
            if not is_valid:
                return ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='INVALID_PASSWORD',
                    status_code=400
                )

            # Call Entity layer for authentication
            result = User.authenticate_user(username, password, role_name)

            if not result:
                return ResponseHelpers.error_response(
                    message='Invalid credentials or user role mismatch',
                    error_code='AUTH_FAILED',
                    status_code=401
                )

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

            # Log activity
            try:
                User.log_user_activity(result['id'], 'login', f'Logged in as {role_name}')
            except Exception:
                pass

            return ResponseHelpers.success_response(
                data=response_data,
                message='Login successful',
                status_code=200
            )

        except Exception as e:
            print(f"[ERROR] Login error: {str(e)}")
            return ResponseHelpers.error_response(
                message='An error occurred during login',
                error_code='SERVER_ERROR',
                status_code=500
            )

    @staticmethod
    def logout(token):
        """
        Logout business logic
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate token presence
            if not token:
                return {
                    'success': False,
                    'message': 'Invalid or missing token'
                }, 401
            
            # Call Entity to invalidate token
            success = User.invalidate_session_token(token)
            
            if success:
                return {
                    'success': True,
                    'message': 'Logout successful'
                }, 200
            else:
                return {
                    'success': False,
                    'message': 'Logout failed'
                }, 400
                
        except Exception as e:
            print(f"[ERROR] Logout error: {str(e)}")
            return {
                'success': False,
                'message': 'An error occurred during logout'
            }, 500

    @staticmethod
    def verify(token):
        """
        Verify session token business logic
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate token format
            if not token:
                return ResponseHelpers.error_response(
                    message='Invalid or missing token',
                    error_code='INVALID_TOKEN_FORMAT',
                    status_code=401
                )

            # Call Entity layer for verification
            user = User.verify_session_token(token)

            if not user:
                return ResponseHelpers.error_response(
                    message='Invalid or expired token',
                    error_code='INVALID_TOKEN',
                    status_code=401
                )

            # Get role info
            role = Role.get_role_by_id(user['role_id'])

            # Format response
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

            return ResponseHelpers.success_response(
                data=response_data,
                message='Token is valid',
                status_code=200
            )

        except Exception as e:
            print(f"[ERROR] Verify error: {str(e)}")
            return ResponseHelpers.error_response(
                message='An error occurred during token verification',
                error_code='SERVER_ERROR',
                status_code=500
            )

