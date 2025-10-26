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
    Validate user creation data
    
    Args:
        data: User data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is required"
    
    # Check required fields
    required_fields = ['username', 'password', 'email', 'full_name', 'role_id']
    is_valid, error_msg, _ = RequestHelpers.validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_msg
    
    # Validate individual fields
    is_valid, error_msg = Validators.validate_username(data['username'])
    if not is_valid:
        return False, error_msg
    
    is_valid, error_msg = Validators.validate_password(data['password'])
    if not is_valid:
        return False, error_msg
    
    is_valid, error_msg = Validators.validate_email(data['email'])
    if not is_valid:
        return False, error_msg
    
    is_valid, error_msg = Validators.validate_full_name(data['full_name'])
    if not is_valid:
        return False, error_msg
    
    is_valid, error_msg = Validators.validate_role_id(data['role_id'])
    if not is_valid:
        return False, error_msg
    
    # Check if username already exists
    if User.username_exists(data['username']):
        return False, "Username already exists"
    
    # Check if email already exists
    if User.email_exists(data['email']):
        return False, "Email already exists"
    
    return True, ""


class CreateUserAccountController:
    @create_user_account_blueprint.route('', methods=['POST'])
    @require_role(Role.USER_ADMIN)
    def create():
        """
        Create a new user account with comprehensive validation
        
        Validates:
        - Required fields presence
        - Data format (username, password, email, full_name)
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
            result = User.create_user(
                username=sanitized['username'],
                password=sanitized['password'],
                email=sanitized['email'],
                full_name=sanitized['full_name'],
                role_id=sanitized['role_id']
            )
            
            # ===== BOUNDARY: Handle CONTROL layer response =====
            if result:
                # Exclude sensitive fields from response
                response_data = ResponseHelpers.format_user_response(result)
                
                response, status = ResponseHelpers.success_response(
                    data=response_data,
                    message='User account created successfully',
                    status_code=201
                )
                return jsonify(response), status
            else:
                response, status = ResponseHelpers.error_response(
                    message='Failed to create user account',
                    error_code='CREATION_FAILED',
                    status_code=400
                )
                return jsonify(response), status

        except Exception as e:
            print(f"[ERROR] Create user endpoint error: {str(e)}")
            response, status = ResponseHelpers.error_response(
                message='An error occurred while creating user account',
                error_code='SERVER_ERROR',
                status_code=500
            )
            return jsonify(response), status
