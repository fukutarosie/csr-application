"""Create User Account Controller - Handles user creation logic"""

from typing import Tuple
from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers

create_user_account_blueprint = Blueprint('create_user_account', __name__, url_prefix='/api/userAccount')


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
    @create_user_account_blueprint.route('', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create():
        """
        Create a new user account with comprehensive validation
        
        Process:
        1. Extract JSON request data
        2. Validate HTTP format
        3. Validate data format and uniqueness (BOUNDARY)
        4. Sanitize input
        5. Call CONTROL layer for business logic
        6. Handle response and provide clear error messages
        
        Validates:
        - Required fields presence
        - Data format (username, password, email, full_name, role_id)
        - Username uniqueness
        - Email uniqueness
        - Role validity
        """
        try:
            # ===== BOUNDARY: Extract HTTP request data =====
            data = RequestHelpers.get_json_data()
            
            # ===== BOUNDARY: Validate HTTP format =====
            if not data:
                response, status = ResponseHelpers.error_response(
                    message='Request body is required',
                    error_code='EMPTY_BODY',
                    status_code=400
                )
                return jsonify(response), status
            
            # ===== BOUNDARY: Validate data format and uniqueness =====
            is_valid, error_msg = validate_create_user_data(data)
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=error_msg,
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
                return jsonify(response), status
            
            # ===== BOUNDARY: Sanitize input data =====
            sanitized = Sanitizers.sanitize_user_data(data)
            
            # ===== CALL CONTROL LAYER =====
            # User.create_user() performs final validation and inserts into database
            result = User.create_user(
                username=sanitized['username'],
                password=sanitized['password'],
                email=sanitized['email'],
                full_name=sanitized['full_name'],
                role_id=sanitized['role_id']
            )

            # ===== BOUNDARY: Handle CONTROL layer structured response =====
            # Success
            if result and isinstance(result, dict) and 'data' in result:
                created = result['data']
                response_data = ResponseHelpers.format_user_response(created)

                response, status = ResponseHelpers.success_response(
                    data=response_data,
                    message='User account created successfully',
                    status_code=201
                )

                # Log the creation for audit trail (best-effort)
                try:
                    User.log_user_activity(
                        created.get('id'),
                        'user_created',
                        f"User account created with username: {sanitized['username']}"
                    )
                except Exception:
                    pass

                return jsonify(response), status

            # Specific duplicate username
            if result and isinstance(result, dict) and result.get('error') == 'USERNAME_EXISTS':
                response, status = ResponseHelpers.error_response(
                    message=result.get('message', f"The username '{sanitized['username']}' is already taken."),
                    error_code='USERNAME_EXISTS',
                    status_code=409,
                    details={'field': 'username'}
                )
                return jsonify(response), status

            # Specific duplicate email
            if result and isinstance(result, dict) and result.get('error') == 'EMAIL_EXISTS':
                response, status = ResponseHelpers.error_response(
                    message=result.get('message', f"The email '{sanitized['email']}' is already registered."),
                    error_code='EMAIL_EXISTS',
                    status_code=409,
                    details={'field': 'email'}
                )
                return jsonify(response), status

            # DB failure or unexpected exception
            if result and isinstance(result, dict) and result.get('error') in ('DB_INSERT_FAILED', 'EXCEPTION'):
                response, status = ResponseHelpers.error_response(
                    message=result.get('message', 'An unexpected error occurred while creating account'),
                    error_code=result.get('error', 'CREATION_FAILED'),
                    status_code=500
                )
                return jsonify(response), status

            # Fallback - generic creation failed
            response, status = ResponseHelpers.error_response(
                message='Failed to create user account. Please try again.',
                error_code='CREATION_FAILED',
                status_code=400
            )
            return jsonify(response), status

        except Exception as e:
            print(f"[ERROR] Create user endpoint error: {str(e)}")
            response, status = ResponseHelpers.error_response(
                message='An unexpected error occurred while creating user account. Please try again.',
                error_code='SERVER_ERROR',
                status_code=500
            )
            return jsonify(response), status
