"""Create User Account Controller - Business logic for user creation"""

from typing import Tuple
from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers, DataHelpers


def validate_create_user_data(data: dict) -> Tuple[bool, str]:
    """
    Validate user creation data with detailed error messages for better UX
    
    Validates in order:
    1. Data presence
    2. Required fields
    3. Format validation (username, password, email, full_name, role_id)
    4. Uniqueness checks (username, email)
    
    Args:
        data: User data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is required"
    
    # Check required fields
    required_fields = ['username', 'password', 'email', 'full_name', 'role_id']
    is_valid, error_msg, missing_fields = RequestHelpers.validate_required_fields(data, required_fields)
    if not is_valid:
        # Provide better error message with which fields are missing
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        return False, error_msg
    
    # ===== FORMAT VALIDATION PHASE =====
    # Validate username format BEFORE checking uniqueness
    username = data.get('username', '').strip()
    is_valid, error_msg = Validators.validate_username(username)
    if not is_valid:
        return False, f"Username: {error_msg}"
    
    # Validate password format
    password = data.get('password', '')
    is_valid, error_msg = Validators.validate_password(password)
    if not is_valid:
        return False, f"Password: {error_msg}"
    
    # Validate email format
    email = data.get('email', '').strip()
    is_valid, error_msg = Validators.validate_email(email)
    if not is_valid:
        return False, f"Email: {error_msg}"
    
    # Validate full name format
    full_name = data.get('full_name', '').strip()
    is_valid, error_msg = Validators.validate_full_name(full_name)
    if not is_valid:
        return False, f"Full Name: {error_msg}"
    
    # Validate role ID format
    is_valid, error_msg = Validators.validate_role_id(data.get('role_id'))
    if not is_valid:
        return False, f"Role: {error_msg}"
    
    # ===== UNIQUENESS VALIDATION PHASE =====
    # Check if username already exists
    if User.username_exists(username):
        return False, f"The username '{username}' is already taken. Please choose a different username."
    
    # Check if email already exists
    if User.email_exists(email):
        return False, f"The email '{email}' is already registered. Please use a different email address."
    
    return True, ""


class CreateUserAccountController:
    @staticmethod
    def create(data):
        """
        Create a new user account with comprehensive validation
        
        Process:
        1. Validate data format and uniqueness
        2. Sanitize input
        3. Call Entity layer for database operations
        4. Handle response and provide clear error messages
        
        Args:
            data: User data from HTTP request
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # ===== Validate HTTP format =====
            if not data:
                return ResponseHelpers.error_response(
                    message='Request body is required',
                    error_code='EMPTY_BODY',
                    status_code=400
                )
            
            # ===== Validate data format and uniqueness =====
            is_valid, error_msg = validate_create_user_data(data)
            if not is_valid:
                return ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
            
            # ===== Sanitize input data =====
            sanitized = Sanitizers.sanitize_user_data(data)
            
            # ===== CALL Entity LAYER =====
            # User.create_user() performs final validation and inserts into database
            result = User.create_user(
                username=sanitized['username'],
                password=sanitized['password'],
                email=sanitized['email'],
                full_name=sanitized['full_name'],
                role_id=sanitized['role_id']
            )

            # ===== Handle Entity layer structured response =====
            # Success
            if result and isinstance(result, dict) and 'data' in result:
                created = result['data']
                response_data = DataHelpers.format_user_response(created)

                # Log the creation for audit trail (best-effort)
                try:
                    User.log_user_activity(
                        created.get('id'),
                        'user_created',
                        f"User account created with username: {sanitized['username']}"
                    )
                except Exception:
                    pass

                return ResponseHelpers.success_response(
                    data=response_data,
                    message='User account created successfully',
                    status_code=201
                )

            # Specific duplicate username
            if result and isinstance(result, dict) and result.get('error') == 'USERNAME_EXISTS':
                return ResponseHelpers.error_response(
                    message=result.get('message', f"The username '{sanitized['username']}' is already taken."),
                    error_code='USERNAME_EXISTS',
                    status_code=409,
                    details={'field': 'username'}
                )

            # Specific duplicate email
            if result and isinstance(result, dict) and result.get('error') == 'EMAIL_EXISTS':
                return ResponseHelpers.error_response(
                    message=result.get('message', f"The email '{sanitized['email']}' is already registered."),
                    error_code='EMAIL_EXISTS',
                    status_code=409,
                    details={'field': 'email'}
                )

            # DB failure or unexpected exception
            if result and isinstance(result, dict) and result.get('error') in ('DB_INSERT_FAILED', 'EXCEPTION'):
                return ResponseHelpers.error_response(
                    message=result.get('message', 'An unexpected error occurred while creating account'),
                    error_code=result.get('error', 'CREATION_FAILED'),
                    status_code=500
                )

            # Fallback - generic creation failed
            return ResponseHelpers.error_response(
                message='Failed to create user account. Please try again.',
                error_code='CREATION_FAILED',
                status_code=400
            )

        except Exception as e:
            import traceback
            print(f"[ERROR] Create user error: {str(e)}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return ResponseHelpers.error_response(
                message='An unexpected error occurred while creating user account. Please try again.',
                error_code='SERVER_ERROR',
                status_code=500
            )
