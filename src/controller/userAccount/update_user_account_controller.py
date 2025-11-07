"""Update User Account Controller - Business logic for user update"""

from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers, DataHelpers


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
    def update(user_id, data):
        """
        Update user account details
        
        Args:
            user_id: ID of user to update
            data: Update data from HTTP request
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate data presence
            if not data:
                return ResponseHelpers.error_response(
                    message='Request body cannot be empty',
                    error_code='EMPTY_BODY',
                    status_code=400
                )
            
            # Check if user exists
            user = User.get_user_by_id(user_id)
            if not user:
                return ResponseHelpers.error_response(
                    message=f'User with ID {user_id} not found',
                    error_code='USER_NOT_FOUND',
                    status_code=404
                )
            
            # Sanitize data
            sanitized = Sanitizers.sanitize_user_data(data)
            
            # Validate updates
            is_valid, result = validate_update_user_data(sanitized, user_id)
            if not is_valid:
                return ResponseHelpers.error_response(
                    message=result,
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
            
            # Extract validated updates
            updates = result
            
            # Update user in Entity layer
            updated_user = User.update_user(user_id, updates)
            
            if updated_user:
                # Log activity
                try:
                    User.log_user_activity(
                        user_id=user_id,
                        activity_type='PROFILE_UPDATE',
                        activity_details=f'Updated fields: {", ".join(updates.keys())}'
                    )
                except Exception:
                    pass
                
                # Format response
                return ResponseHelpers.success_response(
                    data=DataHelpers.format_user_response(updated_user),
                    message='User account updated successfully',
                    status_code=200
                )
            else:
                return ResponseHelpers.error_response(
                    message='Failed to update user account',
                    error_code='UPDATE_FAILED',
                    status_code=400
                )
        
        except Exception as e:
            return ResponseHelpers.error_response(
                message=str(e),
                error_code='SERVER_ERROR',
                status_code=500
            )
