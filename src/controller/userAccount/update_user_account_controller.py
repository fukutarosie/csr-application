"""
Update User Account Controller - TRUE OOP Implementation
Holds request data in memory and orchestrates user update
"""

from typing import Dict, Tuple, List
from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers, DataHelpers


class UpdateUserAccountController:
    """
    Update User Account Controller - TRUE OOP
    
    This controller holds request data in memory and orchestrates user update.
    It demonstrates proper OOP:
    - Has instance variables (data in memory)
    - Uses instance methods
    - Loads User objects and calls their instance methods
    
    Usage:
        controller = UpdateUserAccountController(user_id, request_data)
        response, status = controller.execute()
    """
    
    def __init__(self, user_id: int, request_data: Dict):
        """
        Initialize controller with user ID and request data
        
        Args:
            user_id: ID of user to update
            request_data: Update data from HTTP request
        """
        # Instance variables (object state - data in memory)
        self.user_id = user_id
        self.request_data = request_data
        self.user = None  # Will hold User object
        self.errors: List[str] = []
        self.updates: Dict = {}
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate_request_data(self) -> bool:
        """
        Validate request data
        
        Returns:
            True if valid, False otherwise (errors stored in self.errors)
        """
        if not self.request_data:
            self.errors.append('Request body is required')
            return False
        
        # Validate email if provided
        if 'email' in self.request_data and self.request_data['email']:
            email = self.request_data['email']
            is_valid, error = Validators.validate_email(email)
            if not is_valid:
                self.errors.append(error)
                return False
            
            # Check if email already exists for a different user
            existing_user = User.find_by_email(email)
            if existing_user and existing_user.id != self.user_id:
                self.errors.append('Email already in use')
                return False
            
            self.updates['email'] = email
        
        # Validate full_name if provided
        if 'full_name' in self.request_data:
            full_name = self.request_data['full_name']
            is_valid, error = Validators.validate_full_name(full_name)
            if not is_valid:
                self.errors.append(error)
                return False
            
            self.updates['full_name'] = full_name
        
        # Validate role_id if provided
        if 'role_id' in self.request_data:
            role_id = self.request_data['role_id']
            is_valid, error = Validators.validate_role_id(role_id)
            if not is_valid:
                self.errors.append(error)
                return False
            
            self.updates['role_id'] = role_id
        
        # Check if at least one field is being updated
        if not self.updates:
            self.errors.append('No fields to update')
            return False
        
        return True
    
    def load_user(self) -> bool:
        """
        Load User object from database
        
        Returns:
            True if user found, False otherwise
        """
        self.user = User.find(self.user_id)
        if not self.user:
            self.errors.append('User not found')
            return False
        return True
    
    def apply_updates(self) -> None:
        """
        Apply updates to User object (data in memory)
        """
        if 'email' in self.updates:
            self.user.email = self.updates['email']
        if 'full_name' in self.updates:
            self.user.full_name = self.updates['full_name']
        if 'role_id' in self.updates:
            self.user.role_id = self.updates['role_id']
    
    # ============================================================================
    # MAIN EXECUTION METHOD (Instance method)
    # ============================================================================
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user update process
        
        This is the main method that orchestrates the entire process:
        1. Validate request data
        2. Load User object (holds data in memory)
        3. Apply updates to User object
        4. Save User object (User does the actual database work)
        5. Log activity
        6. Return response
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Step 1: Validate request data
            if not self.validate_request_data():
                return ResponseHelpers.error_response(
                    message='; '.join(self.errors),
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
            
            # Step 2: Load User object (holds data in memory)
            if not self.load_user():
                return ResponseHelpers.error_response(
                    message='; '.join(self.errors),
                    error_code='USER_NOT_FOUND',
                    status_code=404
                )
            
            # Step 3: Apply updates to User object
            self.apply_updates()
            
            # Step 4: Save User object (User.save() does the actual work)
            try:
                self.user.save()  # Instance method - does actual database work
            except ValueError as e:
                return ResponseHelpers.error_response(
                    message=str(e),
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
            
            # Step 5: Log activity (best-effort)
            try:
                self.user.log_activity(
                    'user_updated',
                    f"User account updated: {', '.join(self.updates.keys())}"
                )
            except Exception as e:
                print(f"[WARNING] Failed to log activity: {str(e)}")
            
            # Step 6: Return success response
            response_data = DataHelpers.format_user_response(self.user.to_dict())
            
            return ResponseHelpers.success_response(
                data=response_data,
                message='User account updated successfully',
                status_code=200
            )
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Update user error: {str(e)}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return ResponseHelpers.error_response(
                message='An unexpected error occurred while updating user account',
                error_code='SERVER_ERROR',
                status_code=500
            )
