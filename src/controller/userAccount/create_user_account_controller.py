"""
Create User Account Controller - TRUE OOP Implementation
Holds request data in memory and orchestrates user creation
"""

from typing import Tuple, Dict, List
from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import RequestHelpers, ResponseHelpers, DataHelpers


class CreateUserAccountController:
    """
    Create User Account Controller - TRUE OOP
    
    This controller holds request data in memory and orchestrates user creation.
    It demonstrates proper OOP:
    - Has instance variables (data in memory)
    - Uses instance methods
    - Creates User objects and calls their instance methods
    
    Usage:
        controller = CreateUserAccountController(request_data)
        response, status = controller.execute()
    """
    
    def __init__(self, request_data: Dict):
        """
        Initialize controller with request data
        
        Args:
            request_data: User data from HTTP request
        """
        # Instance variables (object state - data in memory)
        self.request_data = request_data
        self.user = None  # Will hold User object
        self.errors: List[str] = []
        self.sanitized_data: Dict = {}
    
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
            self.errors.append("Request body is required")
            return False
        
        # Check required fields
        required_fields = ['username', 'password', 'email', 'full_name', 'role_id']
        is_valid, error_msg, missing_fields = RequestHelpers.validate_required_fields(
            self.request_data, required_fields
        )
        if not is_valid:
            if missing_fields:
                self.errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            else:
                self.errors.append(error_msg)
            return False
        
        # Validate username format
        username = self.request_data.get('username', '').strip()
        is_valid, error_msg = Validators.validate_username(username)
        if not is_valid:
            self.errors.append(f"Username: {error_msg}")
        
        # Validate password format
        password = self.request_data.get('password', '')
        is_valid, error_msg = Validators.validate_password(password)
        if not is_valid:
            self.errors.append(f"Password: {error_msg}")
        
        # Validate email format
        email = self.request_data.get('email', '').strip()
        is_valid, error_msg = Validators.validate_email(email)
        if not is_valid:
            self.errors.append(f"Email: {error_msg}")
        
        # Validate full name format
        full_name = self.request_data.get('full_name', '').strip()
        is_valid, error_msg = Validators.validate_full_name(full_name)
        if not is_valid:
            self.errors.append(f"Full Name: {error_msg}")
        
        # Validate role ID format
        is_valid, error_msg = Validators.validate_role_id(self.request_data.get('role_id'))
        if not is_valid:
            self.errors.append(f"Role: {error_msg}")
        
        return len(self.errors) == 0
    
    def sanitize_data(self) -> None:
        """
        Sanitize input data and store in self.sanitized_data
        """
        self.sanitized_data = Sanitizers.sanitize_user_data(self.request_data)
    
    def create_user_object(self) -> None:
        """
        Create User object from sanitized data
        Stores User object in self.user (data in memory)
        """
        self.user = User()  # Create User object
        
        # Set instance variables on User object (data in memory)
        self.user.username = self.sanitized_data['username']
        self.user.password = self.sanitized_data['password']  # Will be hashed by User.save()
        self.user.email = self.sanitized_data['email']
        self.user.full_name = self.sanitized_data['full_name']
        self.user.role_id = self.sanitized_data['role_id']
        self.user.is_active = True
    
    # ============================================================================
    # MAIN EXECUTION METHOD (Instance method)
    # ============================================================================
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user creation process
        
        This is the main method that orchestrates the entire process:
        1. Validate request data
        2. Sanitize data
        3. Create User object (holds data in memory)
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
            
            # Step 2: Sanitize data
            self.sanitize_data()
            
            # Step 3: Create User object (holds data in memory)
            self.create_user_object()
            
            # Step 4: Save User object (User.save() does the actual work)
            try:
                self.user.save()  # Instance method - does actual database work
            except ValueError as e:
                # Handle validation errors from User entity
                error_msg = str(e)
                
                # Determine error code based on message
                if 'username' in error_msg.lower() and 'exists' in error_msg.lower():
                    return ResponseHelpers.error_response(
                        message=error_msg,
                        error_code='USERNAME_EXISTS',
                        status_code=409,
                        details={'field': 'username'}
                    )
                elif 'email' in error_msg.lower() and 'exists' in error_msg.lower():
                    return ResponseHelpers.error_response(
                        message=error_msg,
                        error_code='EMAIL_EXISTS',
                        status_code=409,
                        details={'field': 'email'}
                    )
                else:
                    return ResponseHelpers.error_response(
                        message=error_msg,
                        error_code='VALIDATION_ERROR',
                        status_code=400
                    )
            
            # Step 5: Log activity (best-effort)
            try:
                self.user.log_activity(
                    'user_created',
                    f"User account created with username: {self.user.username}"
                )
            except Exception as e:
                print(f"[WARNING] Failed to log activity: {str(e)}")
            
            # Step 6: Return success response
            response_data = DataHelpers.format_user_response(self.user.to_dict())
            
            return ResponseHelpers.success_response(
                data=response_data,
                message='User account created successfully',
                status_code=201
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
