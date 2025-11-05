"""Update User Account Controller - Handles user update logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers, DataHelpers

update_user_account_blueprint = Blueprint('update_user_account', __name__, url_prefix='/api/userAccount')


def validate_update_user_data(data, current_user_id):
    """
    Validate user update data
    
    Args:
        data (dict): User data to validate
        current_user_id (int): ID of the user being updated
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    updates = {}
    
    # Check if email exists and validate
    if 'email' in data and data['email']:
        email = data['email']
        is_valid, error = Validators.validate_email(email)
        if not is_valid:
            return False, error
        
        # Check if email already exists (optional - only if different from current)
        existing_email = User.get_by_email(email)
        if existing_email:
            # If email exists, only block if it belongs to a DIFFERENT user
            existing_user_id = existing_email.get('id')
            if existing_user_id != current_user_id:
                print(f"[DEBUG] Email '{email}' already exists for user {existing_user_id}, current user is {current_user_id}")
                return False, 'Email already in use'
            print(f"[DEBUG] Email '{email}' belongs to same user {current_user_id}, allowing update")
        
        updates['email'] = email
    
    # Check if full_name exists and validate
    if 'full_name' in data:
        full_name = data['full_name']
        is_valid, error = Validators.validate_full_name(full_name)
        if not is_valid:
            return False, error
        
        updates['full_name'] = full_name
    
    # Check if role_id exists and validate
    if 'role_id' in data:
        role_id = data['role_id']
        is_valid, error = Validators.validate_role_id(role_id)
        if not is_valid:
            return False, error
        
        updates['role_id'] = role_id
    
    # Check if at least one field is being updated
    if not updates:
        return False, 'No fields to update'
    
    return True, updates

class UpdateUserAccountController:
    @staticmethod
    @update_user_account_blueprint.route('/<int:user_id>', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def update(user_id):
        """
        Update user account details
        
        Validates:
        - JSON format
        - Required fields presence
        - Field format validation (email, full_name, role_id)
        - Email uniqueness
        
        Sanitizes:
        - All input data
        
        Returns:
        - 200: User updated successfully
        - 400: Validation error
        - 404: User not found
        - 500: Server error
        """
        try:
            # Validate JSON format
            data = RequestHelpers.get_json_data()
            if not data:
                response, status = ResponseHelpers.error_response(
                    message='Request body cannot be empty',
                    error_code='EMPTY_BODY',
                    status_code=400
                )
                return jsonify(response), status
            
            # Check if user exists
            user = User.get_by_id(user_id)
            if not user:
                response, status = ResponseHelpers.error_response(
                    message=f'User with ID {user_id} not found',
                    error_code='USER_NOT_FOUND',
                    status_code=404
                )
                return jsonify(response), status
            
            # Add current user ID for uniqueness check
            data['current_user_id'] = user_id
            
            # Sanitize data
            sanitized = Sanitizers.sanitize_user_data(data)
            
            # Validate updates - pass user_id directly
            is_valid, result = validate_update_user_data(sanitized, user_id)
            if not is_valid:
                response, status = ResponseHelpers.error_response(
                    message=result,
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
                return jsonify(response), status
            
            # Extract validated updates
            updates = result
            
            # Update user in CONTROL layer
            updated_user = User.update_user(user_id, updates)
            
            if updated_user:
                # Log activity
                User.log_user_activity(
                    user_id=user_id,
                    activity_type='PROFILE_UPDATE',
                    activity_details=f'Updated fields: {", ".join(updates.keys())}'
                )
                
                # Format response
                response, status = ResponseHelpers.success_response(
                    data=DataHelpers.format_user_response(updated_user),
                    message='User account updated successfully',
                    status_code=200
                )
                return jsonify(response), status
            else:
                response, status = ResponseHelpers.error_response(
                    message='Failed to update user account',
                    error_code='UPDATE_FAILED',
                    status_code=400
                )
                return jsonify(response), status
        
        except Exception as e:
            response, status = ResponseHelpers.error_response(
                message=str(e),
                error_code='SERVER_ERROR',
                status_code=500
            )
            return jsonify(response), status
